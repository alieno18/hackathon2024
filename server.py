import json
import xrpl
import interaction


class Server:
    def __init__(self, seed: str):
        self.wallet = xrpl.wallet.Wallet.from_seed(seed)
    
    def register(self, guest_seed: str, check_in: str, check_out: str, services: dict[str, bool]) -> tuple[str, dict]:
        """ Register the guest to the service and return the address of the guest """
        # the following actions are performed by the server and guest by interacting
        # here we are just simulating the interaction
        guest_wallet = interaction.get_account(guest_seed)  # register the guest
        uri = {
            "check_in": check_in,
            "check_out": check_out,
            "services": services
        }
        uri = json.dumps(uri)
        # Create an NFT with the URI
        nft = interaction.create_nft(self.wallet.seed, uri)
        # Send the NFT to the guest
        offer_id = interaction.send_nft(self.wallet.seed, nft["NFTokenID"], guest_wallet.address)
        # Check if the guest received the NFT
        if not interaction.get_nft(guest_seed, nft["NFTokenID"], offer_id):
            raise ValueError("NFT not received by the guest")
        guest_address = xrpl.core.keypairs.derive_classic_address(guest_wallet.public_key)
        return guest_address, nft
