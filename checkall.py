#!/usr/bin/env python3
from web3 import Web3
import os
import json
import sys
import re
import datetime
from subprocess import Popen, PIPE, STDOUT

def loadCheckers():
    res = {}
    lst = os.listdir(os.path.join(os.path.dirname(__file__), "amm-checkers"))
    dir = []
    for d in lst:
        s = os.path.abspath(os.path.join(os.path.dirname(__file__), "amm-checkers")) + os.sep + d
        if os.path.isdir(s) and os.path.exists(s + os.sep + "__init__.py"):
            dir.append(d)
    sys.path.append(os.path.dirname(__file__))
    for d in dir:
        res[d] = __import__("amm-checkers." + d, fromlist = ["*"])
    return res

def loadConfig():
    fname = None
    if len(sys.argv) > 1:
        if os.path.isfile(sys.argv[1]):
            fname = sys.argv[1]
    else:
        for d in os.path.expanduser("~"), os.curdir:
            c_fname = os.path.join(d, "amm-checker.conf")
            if os.path.isfile(c_fname):
                fname = c_fname
                break

    if fname:
        with open(fname) as json_file:
            data = json.load(json_file)
            return data
    return {}

def parseConfig(cfg):
    if "normalize_timestamp" in cfg:
        cfg["t"] = datetime.datetime.now()

cfg = loadConfig()
if "web3_provider_uri" not in cfg:
    print(cfg)
    raise Exception("No WEB3 provider URI in configuration")

w3 = Web3(Web3.HTTPProvider(cfg["web3_provider_uri"], request_kwargs={'timeout': 60}))

syncObj = w3.eth.syncing

if not isinstance(syncObj, bool):
    raise Exception("Node is syncing")

checkers = loadCheckers()

checks = cfg["checks"]

parseConfig(cfg)

for chk in checks:
    c_cfg = cfg.copy()

    c_cfg = {**c_cfg, **chk}

    if 'provider' not in c_cfg:
        continue

    if '_comment' in c_cfg and c_cfg['_comment'] == True:
        continue

    checker = checkers[c_cfg['provider']].Checker(w3, c_cfg['contract'], c_cfg['tokens'])

    ret_str = checker.get_info_string(c_cfg['account'], c_cfg)
    
    print(ret_str[0])
    if "output" in c_cfg and c_cfg["output"] and c_cfg["output"][0]!="stdout":
        p = Popen(c_cfg["output"], stdin=PIPE)
        p.communicate(input=bytes(ret_str[0], 'utf-8'))

