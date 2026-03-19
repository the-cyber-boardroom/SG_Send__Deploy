# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Service__Ollama__Proxy
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                              import TestCase
from sg_send_deploy_local_llm.service.Service__Ollama__Proxy               import Service__Ollama__Proxy

class test_Service__Ollama__Proxy(TestCase):

    def test__init__(self):                                                # Test default URL
        with Service__Ollama__Proxy() as _:
            assert 'localhost:11434' in _.ollama_url

    def test__custom_url(self):                                            # Test URL override
        proxy = Service__Ollama__Proxy(ollama_url='http://host.docker.internal:11434')
        assert 'host.docker.internal' in proxy.ollama_url
