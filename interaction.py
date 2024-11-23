import os
import xrpl

URL = os.getenv("RIPPLE_URL", "https://s.altnet.rippletest.net:51234")


def get_account(seed):
    """ Get an account generated from the seed """
    global URL
    wallet = xrpl.wallet.Wallet.from_seed(seed)
    client = xrpl.clients.JsonRpcClient(URL)
    wallet = xrpl.wallet.generate_faucet_wallet(client, wallet)
    return wallet


def get_new_account():
    """ Get an account generated with any seed """
    global URL
    client = xrpl.clients.JsonRpcClient(URL)
    wallet = xrpl.wallet.generate_faucet_wallet(client)
    return wallet


def get_account_info(account_address: str):
    """ Get account info """
    global URL
    client = xrpl.clients.JsonRpcClient(URL)
    acct_info = xrpl.models.requests.account_info.AccountInfo(
        account=account_address,
        ledger_index="validated"
    )
    response = client.request(acct_info)
    return response.result['account_data']


def get_account_nfts(account_address: str) -> list:
    """ Get the NFTs owned by an account """
    global URL
    client = xrpl.clients.JsonRpcClient(URL)
    request = xrpl.models.requests.AccountNFTs(account=account_address)
    response = client.request(request)
    return response.result.get("account_nfts", [])


def get_ledger_time() -> str:
    """ Get the last ledger time """
    global URL
    client = xrpl.clients.JsonRpcClient(URL)
    response = client.request(xrpl.models.requests.ServerInfo())
    ledger_time = response.result["info"]["time"]
    return ledger_time


def create_nft(minter_seed: str, uri: str, flags: int = 0, transfer_fee: str = "0", taxon: str = "0") -> dict:
    """ Create an NFT with the given parameters and return the NFT ID """
    global URL
    minter_wallet = xrpl.wallet.Wallet.from_seed(minter_seed)
    client = xrpl.clients.JsonRpcClient(URL)
    # Define the mint transaction
    mint_transaction = xrpl.models.transactions.NFTokenMint(
        account=minter_wallet.address,
        uri=xrpl.utils.str_to_hex(uri),
        flags=int(flags),
        transfer_fee=int(transfer_fee),
        nftoken_taxon=int(taxon)
    )
    # Submit the transaction and get results
    try:
        xrpl.transaction.submit_and_wait(mint_transaction, client, minter_wallet)
    except xrpl.transaction.XRPLReliableSubmissionException as e:
        raise e
    # Get the NFT ID and return it
    nfts = get_account_nfts(minter_wallet.address)
    assert len(nfts) > 0 and isinstance(nfts, list)
    nft = nfts.pop()
    return nft


def send_nft(owner_seed: str, nft_id: str, buyer_address: str = "", expiration_seconds: int = None, amount: str = "0") -> str:
    """ Send an NFT to the buyer and return the offer ID """
    global URL
    import datetime
    owner_wallet = xrpl.wallet.Wallet.from_seed(owner_seed)
    client = xrpl.clients.JsonRpcClient(URL)
    expiration_date = datetime.datetime.now() + datetime.timedelta(seconds=expiration_seconds) if expiration_seconds is not None else None
    # Define the sell offer
    sell_offer = xrpl.models.transactions.NFTokenCreateOffer(
        account=owner_wallet.address,
        nftoken_id=nft_id,
        amount=amount,
        destination=buyer_address if buyer_address != '' else None,
        expiration=None if expiration_date is None else xrpl.utils.datetime_to_ripple_time(expiration_date),
        flags=1
    )
    # Submit the transaction and report the results
    try:
        response = xrpl.transaction.submit_and_wait(sell_offer, client, owner_wallet)
    except xrpl.transaction.XRPLReliableSubmissionException as e:
        raise e
    # Get the offer ID and return it
    offer_id = response.result['meta']['offer_id']
    return offer_id


def get_nft(buyer_seed: str, nft_id: str, offer_id: str) -> bool:
    global URL
    buyer_wallet = xrpl.wallet.Wallet.from_seed(buyer_seed)
    client = xrpl.clients.JsonRpcClient(URL)
    # Define the accept offer transaction
    accept_offer = xrpl.models.transactions.NFTokenAcceptOffer(
       account=buyer_wallet.classic_address,
       nftoken_sell_offer=offer_id
    )
    # Submit the transaction and report the results
    try:
        xrpl.transaction.submit_and_wait(accept_offer, client, buyer_wallet)
    except xrpl.transaction.XRPLReliableSubmissionException as e:
        raise e
    # Check if the NFT is in the buyer's account
    nfts = get_account_nfts(buyer_wallet.address)
    assert len(nfts) > 0 and isinstance(nfts, list)
    for nft in nfts:
        if nft["NFTokenID"] == nft_id:
            return True
    return False

