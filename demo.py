#!/usr/bin/env python
from har import *

#read har.tar (report files)
#and add nice path traversal, write output to out.tar

def traverse(filesectors):
	sector = filesectors[0] #grab 1st sector which is the file header
	sector.filename = Tarsector.str2tar("./../" + "".join(filter(lambda x: x, sector.filename)), 100) #Todo making these read / write functions more convenient (now its just raw data with 00 bytes)
	sector.calculate_checksum()

with open("har.tar", "r") as f: tarf = f.read()

src = Tarball(tarf) 
map(traverse, src)

with open("out.tar", "w") as f: f.write(src.dumps())