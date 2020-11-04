#!/usr/bin/python
import json
import os
import sys
import datetime

checker_name = 'Balancer'
def init(_w3):
    global w3
    w3 = _w3

with open(os.path.dirname(__file__) + "/../erc20.abi.json") as f:
    erc20_json = json.load(f)

ETH_DECIMALS = 18
pools = {
            'MKR63/WETH37': {
                'name': 'MKR63/WETH37',
                'balancer_contract': '0xe0E6B25b22173849668c85E06BC2ce1f69BaFf8c',
                'tokens': [
                    {
                        'name': 'WETH',
                        'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
                        'share': 0.37
                    },
                    {
                        'name': 'MKR',
                        'address': '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2',
                        'share': 0.63
                    },
                ],
            },
            'MKR60/WETH40': {
                'name': 'MKR60/WETH40',
                'balancer_contract': '0x9866772A9BdB4Dc9d2c5a4753e8658B8B0Ca1fC3',
                'tokens': [
                    {
                        'name': 'WETH',
                        'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
                        'share': 0.4
                    },
                    {
                        'name': 'MKR',
                        'address': '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2',
                        'share': 0.6
                    },
                ],
            },
            'BAL80/WETH20': {
                'name': 'BAL80/WETH20',
                'balancer_contract': '0x59A19D8c652FA0284f44113D0ff9aBa70bd46fB4',
                'tokens': [
                    {
                        'name': 'WETH',
                        'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
                        'share': 0.2
                    },
                    {
                        'name': 'BAL',
                        'address': '0xba100000625a3754423978a60c9317c58a424e3D',
                        'share': 0.8
                    },
                ],
            },
            'BAL50/WETH50': {
                'name': 'BAL50/WETH50',
                'balancer_contract': '0xe867bE952ee17d2D294F2de62b13B9F4aF521e9a',
                'tokens': [
                    {
                        'name': 'WETH',
                        'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
                        'share': 0.5
                    },
                    {
                        'name': 'BAL',
                        'address': '0xba100000625a3754423978a60c9317c58a424e3D',
                        'share': 0.5
                    },
                ],
            },
            'WBTC50/WETH50': {
                'name': 'WBTC50/WETH50',
                'balancer_contract': '0x1efF8aF5D577060BA4ac8A29A13525bb0Ee2A3D5',
                'tokens': [
                    {
                        'name': 'WETH',
                        'address': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
                        'share': 0.5
                    },
                    {
                        'name': 'WBTC',
                        'address': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
                        'share': 0.5
                    },
                ],
            },
}

            
def get_token_info(name, user, cfg=dict()):
    if name not in pools:
        raise ValueError('Pool does not exist')
    pool = pools[name]
    balancer_contract_address = pool['balancer_contract']


    balancer_token_contract = w3.eth.contract(address=balancer_contract_address, abi=erc20_json)
    balancer_token_user_supply = balancer_token_contract.functions.balanceOf(user).call()

    decimals = balancer_token_contract.functions.decimals().call()

    if 'token_amount' in cfg:
        balancer_token_user_supply = int(cfg['token_amount'] * (10**decimals))

    if 'token_amount_subtract' in cfg:
        balancer_token_user_supply -= int(cfg['token_amount_subtract'] * (10**decimals))

    token_shares = []

    if balancer_token_user_supply > 0:
        balancer_token_total_supply = balancer_token_contract.functions.totalSupply().call()
        if balancer_token_total_supply != 0:
            for token in pool['tokens']:
                contract_address = token['address']
                token_contract = w3.eth.contract(address=contract_address, abi=erc20_json)
                token_decimals = token_contract.functions.decimals().call()

                balancer_token_total_holdings = token_contract.functions.balanceOf(balancer_contract_address).call()

                token_share = balancer_token_total_holdings * (balancer_token_user_supply / balancer_token_total_supply) / (10**token_decimals)
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
        print("%s\t%f %s + %f %s" % (str(datetime.datetime.now()), token_shares[0]['share'], token_shares[0]['name'], token_shares[1]['share'], token_shares[1]['name']))

if __name__=='__main__':
    main()
