#!/usr/bin/python
import json
import os
import sys
import datetime

checker_name = 'BalancedAMMPool'

class BalancedAMMPool:
    """ This class models a Balanced Automatic Market Maker, which weighs every token equally.
    Normally two tokens with 50/50 in one pool.
    """
    ETH_DECIMALS = 18

    def __init__(self, _w3, _contract, _tokens):
        self.w3 = _w3
        self.contract = _contract
        assert isinstance(_tokens, list), "_tokens must be a list!"
        self.tokens = _tokens
        with open(os.path.dirname(__file__) + "/../erc20.abi.json") as f:
            self.erc20_json = json.load(f)

        self.token_contract = self.w3.eth.contract(address=self.contract, abi=self.erc20_json)
        self.decimals = self.token_contract.functions.decimals().call()

        for token in self.tokens:
            assert 'address' in token, "token does not contain address"
            assert 'name' in token, "token does not contain name"
            token['token_contract'] = self.w3.eth.contract(address=token['address'], abi=self.erc20_json)

    def get_user_shares(self, user, cfg=dict()):
        if user != 'totals':
            token_user_supply = self.token_contract.functions.balanceOf(user).call()
        else:
            token_user_supply = self.token_contract.functions.totalSupply().call()

        if 'token_amount' in cfg:
            token_user_supply = int(cfg['token_amount'] * (10**self.decimals))

        if 'token_amount_subtract' in cfg:
            token_user_supply -= int(cfg['token_amount_subtract'] * (10**self.decimals))

        amm_token_total_supply = self.token_contract.functions.totalSupply().call()

        return amm_token_total_supply, token_user_supply

    def get_token_pool_total_holdings(self, user, token_contract, cfg=dict()):
        return token_contract.functions.balanceOf(self.contract).call()

    def get_token_info(self, user, cfg=dict()):

        token_shares = []

        amm_token_total_supply, token_user_supply = self.get_user_shares(user, cfg)

        if token_user_supply > 0:
            if amm_token_total_supply != 0:
                for token in self.tokens:
                    token_contract = token['token_contract']
                    token_decimals = token_contract.functions.decimals().call()

                    token_total_holdings = self.get_token_pool_total_holdings(user, token_contract, cfg)

                    token_share = token_total_holdings * (token_user_supply / amm_token_total_supply) / (10**token_decimals)
                    token_shares.append({'name': token['name'], 'share': token_share})
        
        return token_shares
            
    def get_info_string(self, user, cfg=dict()):
        if 't' not in cfg:
            cfg['t'] = datetime.datetime.now()
        token_shares = self.get_token_info(user, cfg)
        ret_list = [str(cfg['t'])]
        for tkn_share in token_shares:
            ret_list += [tkn_share['share'], tkn_share['name']]
        
        ret_string = ("%s\t" + " + ".join(["%f %s"] * len(token_shares))) % tuple(ret_list)
        return [ret_string]

Checker = BalancedAMMPool

def main():
    pass
"""
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
"""

if __name__=='__main__':
    main()
