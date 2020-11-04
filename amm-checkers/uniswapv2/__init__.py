#!/usr/bin/python
import json
import os
import sys
import datetime

checker_name = 'Uniswap V2'
def init(_w3):
    global w3
    w3 = _w3

with open(os.path.dirname(__file__) + "/../erc20.abi.json") as f:
    erc20_json = json.load(f)

ETH_DECIMALS = 18
UNISWAP_FACTORY_ADDRESS = '0xc0a47dFe034B400B47bDaD5FecDa2621de6c4d95';
pairs = {
            'MKR/WETH': {
                'name': 'MKR/WETH',
                'univ2_contract': '0xC2aDdA861F89bBB333c90c492cB837741916A225',
                'tokens': [
                    {
                        'name': 'WETH',
                        'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
                    },
                    {
                        'name': 'MKR',
                        'address': '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2',
                    },
                ],
            },
            'LINK/WETH': {
                'name': 'LINK/WETH',
                'univ2_contract': '0xa2107FA5B38d9bbd2C461D6EDf11B11A50F6b974',
                'tokens': [
                    {
                        'name': 'WETH',
                        'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
                    },
                    {
                        'name': 'LINK',
                        'address': '0x514910771AF9Ca656af840dff83E8264EcF986CA',
                    },
                ],
            },
            'MATIC/WETH': {
                'name': 'MATIC/WETH',
                'univ2_contract': '0x819f3450dA6f110BA6Ea52195B3beaFa246062dE',
                'tokens': [
                    {
                        'name': 'WETH',
                        'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
                    },
                    {
                        'name': 'MATIC',
                        'address': '0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0',
                    },
                ],
            },
            'UNI/WETH': {
                'name': 'UNI/WETH',
                'univ2_contract': '0xd3d2E2692501A5c9Ca623199D38826e513033a17',
                'tokens': [
                    {
                        'name': 'WETH',
                        'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
                    },
                    {
                        'name': 'UNI',
                        'address': '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',
                    },
                ],
            },
            'WBTC/WETH': {
                'name': 'WBTC/WETH',
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
            }
}
            
def get_token_info(name, user, cfg=dict()):
    if name not in pairs:
        raise ValueError('pair does not exist')
    pair = pairs[name]
    univ2_contract_address = pair['univ2_contract']


    univ2_token_contract = w3.eth.contract(address=univ2_contract_address, abi=erc20_json)
    if user != 'totals':
        univ2_token_user_supply = univ2_token_contract.functions.balanceOf(user).call()
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
    
    return token_shares
        
def get_info_string(name, user, cfg=dict()):
    if 't' not in cfg:
        cfg['t'] = datetime.datetime.now()
    token_shares = get_token_info(name.upper(), user, cfg)
    ret_string = "%s\t%f %s + %f %s" % (str(cfg['t']), token_shares[0]['share'], token_shares[0]['name'], token_shares[1]['share'], token_shares[1]['name'])
    return [ret_string]

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
        else:
            print("%s\t%f %s + %f %s, %f ratio" % (str(datetime.datetime.now()), token_shares[0]['share'], token_shares[0]['name'], token_shares[1]['share'], token_shares[1]['name'], token_shares[1]['share']/token_shares[0]['share']))


if __name__=='__main__':
    main()
