class EC2_Provider:

    def run_instances(self, instance_type: str = 't3.micro'  ,
                            image_id     : str = ''          ,
                            key_name     : str = ''          ) -> dict:
        raise NotImplementedError()

    def describe_instance(self, instance_id: str) -> dict:
        raise NotImplementedError()

    def list_instances(self) -> list:
        raise NotImplementedError()

    def terminate_instance(self, instance_id: str) -> dict:
        raise NotImplementedError()

    def stop_instance(self, instance_id: str) -> dict:
        raise NotImplementedError()

    def start_instance(self, instance_id: str) -> dict:
        raise NotImplementedError()
