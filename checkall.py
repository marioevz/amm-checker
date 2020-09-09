#!/usr/bin/env python
import os
import json
import sys

def loadCheckers(provider_uri):
    res = {}
    lst = os.listdir(os.path.join(os.path.dirname(__file__), "amm-checker", "checkers"))
    dir = []
    for d in lst:
        s = os.path.abspath(os.path.join(os.path.dirname(__file__), "amm-checker", "checkers")) + os.sep + d
        if os.path.isdir(s) and os.path.exists(s + os.sep + "__init__.py"):
            dir.append(d)
    sys.path.append(os.path.dirname(__file__))
    for d in dir:
        res[d] = __import__("amm-checker.checkers." + d, fromlist = ["*"])
        res[d].init(provider_uri)
    return res

def loadConfig():
    for d in os.curdir, os.path.expanduser("~"):
        try:
            with open(d + os.sep + "amm-checker.conf") as json_file:
                data = json.load(json_file)
                return data
        except:
            pass
    return {}

cfg = loadConfig()
checkers = loadCheckers(cfg["WEB3_PROVIDER_URI"])

checkaccounts = cfg["checkaccounts"]

for chk in checkaccounts:
    if len(checkaccounts[chk]) > 0:
        print("=== %s" % checkers[chk].checker_name)
    for acc in checkaccounts[chk]:
        if len(checkaccounts[chk][acc]) > 0:
            print(acc)
        for pair in checkaccounts[chk][acc]:
            ret_str = checkers[chk].get_info_string(pair, acc)
            print(ret_str)

