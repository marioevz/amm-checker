#!/usr/bin/python
import json
import os
import sys
import datetime

checker_name = 'Uniswap V2 Staking'
def init(_w3):
    global w3
    w3 = _w3
    syncObj = w3.eth.syncing

    if not isinstance(syncObj, bool):
        raise Exception("Node is syncing")

with open(os.path.dirname(__file__) + "/../erc20.abi.json") as f:
    erc20_json = json.load(f)

with open(os.path.dirname(__file__) + "/stake.abi.json") as f:
    stake_json = json.load(f)

ETH_DECIMALS = 18
UNISWAP_FACTORY_ADDRESS = '0xc0a47dFe034B400B47bDaD5FecDa2621de6c4d95'
pairs = {
            'WBTC/WETH': {
                'name': 'WBTC/WETH',
                'univ2_stake_contract': '0xCA35e32e7926b96A9988f61d510E038108d8068e',
                'univ2_contract': '0xBb2b8038a1640196FbE3e38816F3e67Cba72D940',
                'tokens': [
                    {
                        'name': 'WETH',
                        'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
                    },
                    {
                        'name': 'WBTC',
                        'address': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
                    },
                ],
                'earnings': {
                    'name': 'UNI',
                    'address': '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984'
                }
            }
}
            
def get_token_info(name, user):
    if name not in pairs:
        raise ValueError('pair does not exist')

    pair = pairs[name]

    univ2_stake_contract_address = pair['univ2_stake_contract']
    univ2_contract_address = pair['univ2_contract']

    univ2_stake_contract = w3.eth.contract(address=univ2_stake_contract_address, abi=stake_json)
    univ2_token_contract = w3.eth.contract(address=univ2_contract_address, abi=erc20_json)
    if user != 'totals':
        univ2_token_user_supply = univ2_stake_contract.functions.balanceOf(user).call()
    else:
        univ2_token_user_supply = univ2_token_contract.functions.totalSupply().call()

    token_shares = []

    if univ2_token_user_supply > 0:
        univ2_token_total_supply = univ2_token_contract.functions.totalSupply().call()
        if univ2_token_total_supply != 0:
            for token in pair['tokens']:
                contract_address = token['address']
                token_contract = w3.eth.contract(address=contract_address, abi=erc20_json)
                token_decimals = token_contract.functions.decimals().call()

                univ2_token_total_holdings = token_contract.functions.balanceOf(univ2_contract_address).call()

                token_share = univ2_token_total_holdings * (univ2_token_user_supply / univ2_token_total_supply) / (10**token_decimals)
                token_shares.append({'name': token['name'], 'share': token_share})
            earnings = univ2_stake_contract.functions.earned(user).call()
            earnings_contract = w3.eth.contract(address=pair['earnings']['address'], abi=erc20_json)
            earnings_decimals = earnings_contract.functions.decimals().call()
            token_shares.append({'name': pair['earnings']['name'], 'earnings': earnings/(10**earnings_decimals)})
    
    return token_shares
        
def get_info_string(name, user):
    token_shares = get_token_info(name.upper(), user)
    ret_string = "%s\t%f %s + %f %s" % (str(datetime.datetime.now()), token_shares[0]['share'], token_shares[0]['name'], token_shares[1]['share'], token_shares[1]['name'])
    ret_string += "\n"
    ret_string += "Earnings\t%f %s" % (token_shares[2]['earnings'], token_shares[2]['name'])
    return ret_string

def main():
    args = sys.argv[:]
    args.pop(0)
    if len(args) < 2:
        raise ValueError('Incorrect number of arguments')
    check_address = args.pop(0)
    for token in args:
        token = token.upper()
        token_shares = get_token_info(token, check_address)
        if check_address != 'totals':
            print("%s\t%f %s + %f %s" % (str(datetime.datetime.now()), token_shares[0]['share'], token_shares[0]['name'], token_shares[1]['share'], token_shares[1]['name']))
            print("Earnings %s\t%f %s" % (str(datetime.datetime.now()), token_shares[2]['name'], token_shares[2]['earnings']))
        else:
            print("%s\t%f %s + %f %s, %f ratio" % (str(datetime.datetime.now()), token_shares[0]['share'], token_shares[0]['name'], token_shares[1]['share'], token_shares[1]['name'], token_shares[1]['share']/token_shares[0]['share']))


if __name__=='__main__':
    main()
