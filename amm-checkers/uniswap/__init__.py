#!/usr/bin/python
import os
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from balanced_amm import BalancedAMMPool, main

ETH_DECIMALS = 18

class Checker(BalancedAMMPool):
    
    def get_token_info(self, user, cfg=dict()):
        token_shares = super().get_token_info(user, cfg)
        amm_token_total_supply, token_user_supply = self.get_user_shares(user, cfg)

        uniswap_eth_total_holdings = self.w3.eth.getBalance(self.contract)

        eth_share = uniswap_eth_total_holdings * (token_user_supply / amm_token_total_supply) / (10**ETH_DECIMALS)

        return [{'name': 'ETH', 'share': eth_share}] + token_shares

if __name__=='__main__':
    main()
