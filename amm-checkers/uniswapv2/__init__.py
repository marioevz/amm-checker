#!/usr/bin/python
import os
import sys

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from balanced_amm import BalancedAMMPool, main

class Checker(BalancedAMMPool):
    pass

if __name__=='__main__':
    main()
