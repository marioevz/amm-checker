#!/usr/bin/python
import os
import sys
import json

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from balanced_amm import BalancedAMMPool

VaultAddress = "0xBA12222222228d8Ba445958a75a0704d566BF2C8"

class Checker(BalancedAMMPool):
    def __init__(self, _w3, _contract, _tokens):
        BalancedAMMPool.__init__(self, _w3, _contract, _tokens)
        
        with open(os.path.dirname(__file__) + "/balancervault.abi.json") as f:
            self.vault_json = json.load(f)
        
        self.vault_contract = self.w3.eth.contract(address=VaultAddress, abi=self.vault_json)

    def get_token_pool_total_holdings(self, user, token_contract, cfg=dict()):
        poolid = None
        if 'poolid' in cfg:
            poolid = cfg['poolid']
        ret = self.vault_contract.functions.getPoolTokens(poolid).call()
        addresses = ret[0]
        totals = ret[1]
        for i in range(len(addresses)):
            if addresses[i].lower() == token_contract.address.lower():
                return totals[i]
        return 0

def main():
    from web3 import Web3
    args = sys.argv[:]
    args.pop(0)
    user_address = args.pop(0)
    pool_contract_address = args.pop(0)
    pool_id = args.pop(0)
    web3_address = args.pop(0)
    w3 = Web3(Web3.HTTPProvider(web3_address, request_kwargs={'timeout': 60}))
    tokens = [
        {
        "name": "WETH",
        "address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "share": 0.20
      },
      {
        "name": "BAL",
        "address": "0xba100000625a3754423978a60c9317c58a424e3D",
        "share": 0.80
      }
    ]
    checker = Checker(w3, pool_contract_address, tokens)
    cfg = {
        "poolid": pool_id
    }
    print(checker.get_token_info(user_address, cfg))

if __name__=='__main__':
    main()
