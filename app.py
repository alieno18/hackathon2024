"""
Client that runs on the device of the user to authenticate the user with the various services.
"""

import xrpl
import json
import interaction


class Application:
    def __init__(self, seed: str):
        self.wallet = xrpl.wallet.Wallet.from_seed(seed)

    def authenticate(self, service_id: str) -> dict:
        """ Sign the current last block timestamp to prove the knowledge of the private key """
        timestamp = interaction.get_ledger_time()
        message = {
            "timestamp": timestamp,
            "service_id": service_id
        }
        message = json.dumps(message).encode().hex()
        signature = xrpl.core.keypairs.sign(message, self.wallet.private_key)
        return {
            "message": message, 
            "signature": signature, 
            "public_key": self.wallet.public_key
        }
