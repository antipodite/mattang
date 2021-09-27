"""
Command line interface for Mattang linguistic mapper
Isaac Stead 2021

This is launched with the shell script mattang.py in the root directory of the
repository, which spins up a docker container and then runs this script inside
that container.
"""
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--data", help="a spreadsheet file to create a map from")

args = parser.parse_args()

print(args)
