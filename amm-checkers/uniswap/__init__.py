#!/usr/bin/python
import json
import os
import sys
import datetime

checker_name = 'Uniswap'
def init(_w3):
    global w3
    w3 = _w3
    syncObj = w3.eth.syncing

    if not isinstance(syncObj, bool):
        raise Exception("Node is syncing")

with open(os.path.dirname(__file__) + "/../erc20.abi.json") as f:
    erc20_json = json.load(f)

ETH_DECIMALS = 18
UNISWAP_FACTORY_ADDRESS = '0xc0a47dFe034B400B47bDaD5FecDa2621de6c4d95';
tokens = {
            'MKR': {
                'name': 'MKR',
                'uniswap_contract': '0x2C4Bd064b998838076fa341A83d007FC2FA50957',
                'contract': '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2',
            },
            'LINK':{
                'name': 'LINK',
                'uniswap_contract': '0xF173214C720f58E03e194085B1DB28B50aCDeeaD',
                'contract': '0x514910771AF9Ca656af840dff83E8264EcF986CA',
            },
            'SYN-ETH':{
                'name': 'SYN-ETH',
                'uniswap_contract': '0xe9Cf7887b93150D4F2Da7dFc6D502B216438F244',
                'contract': '0x5e74C9036fb86BD7eCdcb084a0673EFc32eA31cb',
            },
            'DAI':{
                'name': 'DAI',
                'uniswap_contract': '0x2a1530C4C41db0B0b2bB646CB5Eb1A67b7158667',
                'contract': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
            },
}
            
def get_token_info(name, user):
    if name not in tokens:
        raise ValueError('Token does not exist')
    token = tokens[name]
    uniswap_contract_address = token['uniswap_contract']
    contract_address = token['contract']

    uniswap_token_contract = w3.eth.contract(address=uniswap_contract_address, abi=erc20_json)
    uniswap_token_user_supply = uniswap_token_contract.functions.balanceOf(user).call()
    if uniswap_token_user_supply > 0:
        token_contract = w3.eth.contract(address=contract_address, abi=erc20_json)
        token_decimals = token_contract.functions.decimals().call()

        uniswap_token_total_supply = uniswap_token_contract.functions.totalSupply().call()

        uniswap_token_total_holdings = token_contract.functions.balanceOf(uniswap_contract_address).call()
        uniswap_eth_total_holdings = w3.eth.getBalance(uniswap_contract_address)

        token_share = 0
        eth_share = 0

        if uniswap_token_total_supply != 0:
            token_share = uniswap_token_total_holdings * (uniswap_token_user_supply / uniswap_token_total_supply) / (10**token_decimals)
            eth_share = uniswap_eth_total_holdings * (uniswap_token_user_supply / uniswap_token_total_supply) / (10**ETH_DECIMALS)
            exchange_rate = uniswap_token_total_holdings / uniswap_eth_total_holdings
    
    return eth_share, token_share
        
def get_info_string(name, user):
    eth_share, token_share = get_token_info(name.upper(), user)
    ret_string = "%s\t%f %s + %f %s" % (str(datetime.datetime.now()),eth_share, 'ETH', token_share, token)
    return ret_string

def main():
    args = sys.argv[:]
    args.pop(0)
    if len(args) < 2:
        raise ValueError('Incorrect number of arguments')
    check_address = args.pop(0)
    for token in args:
        token = token.upper()
        eth_share, token_share = get_token_info(token, check_address)
        exchange_rate = token_share / eth_share
        print("%s\t%f %s + %f %s" % (str(datetime.datetime.now()),eth_share, 'ETH', token_share, token))

if __name__=='__main__':
    main()
