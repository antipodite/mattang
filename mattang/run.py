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

from pathlib import Path
from pandas import read_csv

from featuremap import FeatureMap

parser = argparse.ArgumentParser()
parser.add_argument("--shapefile", help="a shapefile to draw the map on")
parser.add_argument("--features", help="spreadsheet columns to be mapped")
parser.add_argument("--colours", help="colours to use for mapping features")
parser.add_argument("--isoglosses", help="features to draw isoglosses around")

# Dummy, the datafile will always be /langdata in the container
parser.add_argument("datafile", help="a spreadsheet containing data to be mapped")

args = parser.parse_args()

df = read_csv("/langdata", sep="\t")
fm = FeatureMap()


fm.load_data(df)
fm.draw(
    "/crips.png",
    features=args.features.split(","),
)
#except ValueError as e:
 #   print("Error: " + str(e))
