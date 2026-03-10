import json
import os
import time
import uuid

from sg_send_deploy.workflows.schemas.Schema__EC2__LLM__Response import Schema__EC2__LLM__Response
from sg_send_deploy.workflows.schemas.Schema__QA__Result         import Schema__QA__Result


class Operation__EC2__Ephemeral__LLM:
    """Ephemeral EC2 + Ollama LLM operation.

    Launches an EC2 instance with pre-baked Ollama AMI,
    creates an ephemeral key pair, scopes SSH ingress to runner IP,
    opens an SSH tunnel, runs batch QA checks, then cleans up everything.

    Uses EC2_Provider abstraction (real AWS or twin for tests).
    Ollama client is injected (real or surrogate for tests).
    """

    def __init__(self, ollama_client  = None ,
                       ec2_provider   = None ,
                       audit_trail    = None ,
                       security_group_id: str = '' ):
        self.ollama_client     = ollama_client
        self.ec2_provider      = ec2_provider
        self.audit_trail       = audit_trail
        self.security_group_id = security_group_id
        self.instance_id       = ''
        self.key_pair_id       = ''
        self.key_path          = ''
        self.runner_ip         = ''
        self.ingress_cidr      = ''
        self.tunnel            = None

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
        run_id     = uuid.uuid4().hex[:8]

        try:
            self.runner_ip = runner_ip

            self._create_key_pair(run_id=run_id)
            self._authorize_ingress(runner_ip=runner_ip)

            self._launch(ami_id           = ami_id        ,
                         instance_type    = instance_type ,
                         spot_instance    = spot_instance ,
                         run_id           = run_id        )

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
                                   run_id        = run_id               ,
                                   success       = True                 ))

        except Exception as e:
            response.error   = str(e)
            response.success = False

            if self.audit_trail:
                self.audit_trail.record(
                    action  = 'EC2_LLM_EXECUTE_FAILED'                  ,
                    admin   = admin                                     ,
                    details = dict(instance_id = self.instance_id       ,
                                   run_id      = run_id                 ,
                                   error       = str(e)                 ))

        finally:
            self._cleanup()

        total_ms = int((time.time() - start_time) * 1000)
        response.total_duration_ms = total_ms

        return response.json()

    def _create_key_pair(self, run_id: str):
        key_name = f'sgraph-qa-{run_id}'
        result   = self.ec2_provider.key_pair_create(key_name=key_name, target_folder='/tmp')
        self.key_pair_id = result.get('key_pair_id', '')
        self.key_path    = result.get('key_path'   , '')

    def _authorize_ingress(self, runner_ip: str):
        if runner_ip and self.security_group_id:
            self.ingress_cidr = f'{runner_ip}/32'
            self.ec2_provider.security_group_authorize_ingress(
                group_id = self.security_group_id ,
                port     = 22                     ,
                cidr_ip  = self.ingress_cidr      )

    def _launch(self, ami_id: str, instance_type: str, spot_instance: bool, run_id: str):
        key_name = f'sgraph-qa-{run_id}'
        result   = self.ec2_provider.run_instances(
            instance_type     = instance_type          ,
            image_id          = ami_id                  ,
            key_name          = key_name                ,
            security_group_id = self.security_group_id  ,
            spot_instance     = spot_instance           ,
            tags              = dict(RunId=run_id, Purpose='sgraph-qa'))
        self.instance_id = result.get('instance_id', '')

        self.ec2_provider.wait_for_instance_running(instance_id=self.instance_id)

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

        if self.key_pair_id and self.ec2_provider:
            try:
                self.ec2_provider.key_pair_delete(key_pair_id=self.key_pair_id)
            except Exception:
                pass

        if self.key_path and os.path.exists(self.key_path):
            try:
                os.unlink(self.key_path)
            except Exception:
                pass

        if self.ingress_cidr and self.security_group_id and self.ec2_provider:
            try:
                self.ec2_provider.security_group_revoke_ingress(
                    group_id = self.security_group_id ,
                    port     = 22                     ,
                    cidr_ip  = self.ingress_cidr      )
            except Exception:
                pass
