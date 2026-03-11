from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes

from sg_send_deploy.ec2.actions.Service__EC2_Key_Pairs import Service__EC2_Key_Pairs

TAG__ROUTES_KEY_PAIRS = 'ec2-key-pairs'

ROUTES_PATHS__KEY_PAIRS = [f'/{TAG__ROUTES_KEY_PAIRS}/key-pairs'                  ,
                           f'/{TAG__ROUTES_KEY_PAIRS}/key-pairs/{{key_pair_id}}'  ]


class Routes__EC2_Key_Pairs(Fast_API__Routes):
    tag                : str                     = TAG__ROUTES_KEY_PAIRS
    service_key_pairs  : Service__EC2_Key_Pairs

    def key_pairs(self) -> list:                                                    # GET /ec2-key-pairs/key-pairs
        return self.service_key_pairs.list_key_pairs()

    def create_key_pair(self, key_name: str) -> dict:                               # POST /ec2-key-pairs/create-key-pair
        return self.service_key_pairs.create_key_pair(key_name=key_name)

    def delete__key_pair_id(self, key_pair_id: str) -> dict:                        # DELETE /ec2-key-pairs/delete/{key_pair_id}
        return self.service_key_pairs.delete_key_pair(key_pair_id=key_pair_id)

    def setup_routes(self):
        self.add_route_get   (self.key_pairs         )
        self.add_route_post  (self.create_key_pair   )
        self.add_route_delete(self.delete__key_pair_id)
        return self
