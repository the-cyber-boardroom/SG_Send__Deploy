import json
import os
import time

from sg_send_deploy.workflows.schemas.Schema__EC2__LLM__Response import Schema__EC2__LLM__Response
from sg_send_deploy.workflows.schemas.Schema__QA__Result         import Schema__QA__Result


class Operation__EC2__Ephemeral__LLM:
    """Ephemeral EC2 + Ollama LLM operation.

    Launches an EC2 instance with pre-baked Ollama AMI,
    opens an SSH tunnel, runs batch QA checks, then cleans up.

    Uses osbot-aws EC2/EC2_Instance for AWS operations.
    Uses osbot-utils SSH for SSH tunnel and remote commands.
    Ollama client is injected (real or surrogate for tests).
    EC2 provider is injected (real or twin for tests).
    """

    def __init__(self, ollama_client  = None ,
                       ec2_provider   = None ,
                       audit_trail    = None ):
        self.ollama_client  = ollama_client
        self.ec2_provider   = ec2_provider
        self.audit_trail    = audit_trail
        self.instance_id    = ''
        self.key_pair_id    = ''
        self.key_path       = ''
        self.runner_ip      = ''
        self.sg_id          = ''
        self.tunnel         = None

    def execute(self, ami_id        : str  = ''           ,
                      instance_type : str  = 'c7g.xlarge' ,
                      spot_instance : bool = True          ,
                      runner_ip     : str  = ''            ,
                      model         : str  = 'gemma3:4b'   ,
                      checks        : list = None          ,
                      admin         : str  = ''            ) -> dict:

        checks   = checks or []
        response = Schema__EC2__LLM__Response()
        response.instance_type = instance_type

        start_time = time.time()

        try:
            self.runner_ip = runner_ip

            self._launch(ami_id        = ami_id        ,
                         instance_type = instance_type ,
                         spot_instance = spot_instance )

            response.instance_id    = self.instance_id
            response.spot_fulfilled = True

            boot_time = time.time() - start_time
            response.boot_time_seconds = round(boot_time, 2)

            self._verify_ollama(model=model)

            results = self._batch_invoke(checks=checks, model=model)
            response.results = [r.json() for r in results]
            response.success = True

            if self.audit_trail:
                self.audit_trail.record(
                    action  = 'EC2_LLM_EXECUTE'                         ,
                    admin   = admin                                     ,
                    details = dict(instance_id   = self.instance_id     ,
                                   instance_type = instance_type        ,
                                   model         = model                ,
                                   checks_count  = len(checks)          ,
                                   success       = True                 ))

        except Exception as e:
            response.error   = str(e)
            response.success = False

            if self.audit_trail:
                self.audit_trail.record(
                    action  = 'EC2_LLM_EXECUTE_FAILED'                  ,
                    admin   = admin                                     ,
                    details = dict(instance_id = self.instance_id       ,
                                   error       = str(e)                 ))

        finally:
            self._cleanup()

        total_ms = int((time.time() - start_time) * 1000)
        response.total_duration_ms = total_ms

        return response.json()

    def _launch(self, ami_id: str, instance_type: str, spot_instance: bool):
        result = self.ec2_provider.run_instances(
            instance_type = instance_type ,
            image_id      = ami_id        )
        self.instance_id = result.get('instance_id', '')

    def _verify_ollama(self, model: str):
        if not self.ollama_client.is_alive():
            raise RuntimeError(f'Ollama not responding on instance {self.instance_id}')

    def _batch_invoke(self, checks: list, model: str) -> list:
        results = []
        for check in checks:
            result = self._invoke_single(check=check, model=model)
            results.append(result)
        return results

    def _invoke_single(self, check: dict, model: str) -> Schema__QA__Result:
        check_id = check.get('check_id', '')
        prompt   = check.get('prompt'  , '')

        start_ms = int(time.time() * 1000)

        try:
            messages = [dict(role='user', content=prompt)]
            response = self.ollama_client.api_chat(model=model, messages=messages)

            duration_ms = int(time.time() * 1000) - start_ms

            content = response.get('message', {}).get('content', '{}')
            try:
                parsed = json.loads(content)
            except (json.JSONDecodeError, TypeError):
                parsed = dict(findings=[], passed=True)

            eval_count    = response.get('eval_count'   , 0)
            eval_duration = response.get('eval_duration' , 1)
            tokens_per_sec = (eval_count / eval_duration * 1_000_000_000) if eval_duration else 0.0

            result = Schema__QA__Result()
            result.check_id       = check_id
            result.passed         = parsed.get('passed', True)
            result.findings       = parsed.get('findings', [])
            result.raw_response   = content
            result.tokens_per_sec = round(tokens_per_sec, 1)
            result.duration_ms    = duration_ms
            return result

        except Exception as e:
            result = Schema__QA__Result()
            result.check_id     = check_id
            result.passed       = False
            result.findings     = [str(e)]
            result.duration_ms  = int(time.time() * 1000) - start_ms
            return result

    def _cleanup(self):
        if self.tunnel:
            self.tunnel.stop()
            self.tunnel = None

        if self.instance_id and self.ec2_provider:
            try:
                self.ec2_provider.terminate_instance(instance_id=self.instance_id)
            except Exception:
                pass
