"""
Command line interface for Mattang linguistic mapper
Isaac Stead 2021

This is launched with the shell script mattang.py in the root directory of the
repository, which spins up a docker container and then runs this script inside
that container.

Notes: 
- We want to make it as simple as possible so could avoid the shapefile by just
loading standard outline basemap and setting the extent programmatically based off
the coordinates of the languages in the data

- Ditto the colours etc, so have sensible defaults

- Attempt to guess the separator of a CSV and support MS Excel files and similar
"""
import argparse

from os.path import exists
from pandas import read_csv

from featuremap import FeatureMap, MattangError

parser = argparse.ArgumentParser()
parser.add_argument("filename", nargs="?")
parser.add_argument("-f") # Features
parser.add_argument("-c")
parser.add_argument("-i")

args = parser.parse_args()
features = args.f.split(",") if args.f else None
colours = args.c.split(",") if args.c else None
isoglosses = args.i.split(",") if args.i else None

print(args)

df = read_csv("/in", sep="\t")
fm = FeatureMap()

if exists("/shape"):
    fm.init_map(shapefile="/shape")

    
fm.load_data(df)
fm.draw(
    "/out/" + args.filename,
    features=features,
    colours=colours,
    isoglosses=isoglosses,
)

