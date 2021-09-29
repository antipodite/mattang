#! /usr/bin/env python3
"""
Wrapper script to run Mattang CLI from the docker image
Isaac Stead 2021
"""
import argparse
import docker

from os.path import abspath, dirname, basename
from docker.types import Mount

IMAGE = "mattang:latest"

parser = argparse.ArgumentParser()
parser.add_argument("infile")
parser.add_argument("outfile")
parser.add_argument("--features", help="spreadsheet columns to be mapped")
parser.add_argument("--colours", help="colours to use for mapping features")
parser.add_argument("--isoglosses", help="features to draw isoglosses around")
parser.add_argument("--shapefile", help="shapefile to draw on map")

args = parser.parse_args()

command = ["python3 ./mattang/run.py"]
mounts = []

# Prepare the input files and output directory to be bind mounted into the container
mounts.append(Mount("/in", abspath(args.infile), type="bind", read_only=True))
mounts.append(Mount("/out", dirname(abspath(args.outfile)), type="bind"))
command.append(basename(args.outfile))

if args.shapefile:
    mounts.append(Mount("/shape", dirname(abspath(args.shapefile)), type="bind"))

# Add the optional arguments to the command string
for arg, value in vars(args).items():
    if value and arg not in ["infile", "outfile", "shapefile"]:
        command.append("-{} {}".format(arg[0], value))

client = docker.from_env()
client.containers.run(IMAGE, command=" ".join(command), mounts=mounts)
