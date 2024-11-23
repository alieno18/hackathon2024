"""
Verifier class to verify the ownership of an NFT
"""

import xrpl
import json
import dateutil
import datetime
import interaction


class Verifier:
    def __init__(self, service_id: str, issuer_id: str):
        self.service_id = service_id
        self.issuer_id = issuer_id

    def verify(self, account_address: str, proof: dict[str, str]) -> bool:
        """ Verify the ownership of an NFT given by the application """

        now = dateutil.parser.parse(interaction.get_ledger_time())

        # 1. Verify account ownership
        if "message" not in proof or "signature" not in proof or "public_key" not in proof:
            return False
        message = proof['message']
        signature = proof['signature']
        public_key = proof['public_key']
        if account_address != xrpl.core.keypairs.derive_classic_address(public_key):
            return False
        if not xrpl.core.keypairs.is_valid_message(bytes.fromhex(message), bytes.fromhex(signature), public_key):
            return False
        message = json.loads(bytes.fromhex(message))
        if message.get("service_id", None) != self.service_id:
            return False
        timestamp = dateutil.parser.parse(message["timestamp"])
        dt = datetime.timedelta(seconds=10)
        if not timestamp <= now <= timestamp + dt:
            return False
        
        # 2. Verify NFT ownership
        nfts = interaction.get_account_nfts(account_address)
        for nft in nfts:
            data = nft["URI"]
            if nft['Issuer'] != self.issuer_id:
                continue
            try:
                data = json.loads(bytes.fromhex(data))
                check_in = dateutil.parser.parse(data["check_in"])
                check_out = dateutil.parser.parse(data["check_out"])
                services = data["services"]
            except (KeyError, ValueError):
                continue
            if check_in <= now <= check_out and (self.service_id is None or services.get(self.service_id, False)):
                return True
        return False
