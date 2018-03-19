import sys

# #left extension is for numbers (<--N), right for data ("D-->") (same as paading)
def extend(symbol, length, data, left=False):
	if left:
		return (symbol*length+data)[-length:]
	else:
		return (data+symbol*length)[:length]

class Tarball():
	def __init__(self, data=None, rechecksum=True):
		if not data: data="\x00"*512*2 #empty tarball

		assert( not(len(data) % 512) )
		self.sectors = []

		while data:
			sector = Tarsector(data[:512])
			if rechecksum and (not sector.ispadding()): 
				sector.calculate_checksum() #we strip extra header and  stuff we dont know, so we need new checksum
			self.sectors.append(sector)
			data = data[512:]

	def sectortypes(self):
		sectortype = []
		datacountdown = 0 #number of sectors containing data

		for sector in self.sectors:

			if not datacountdown: #we are not skipping data
				if sector.ispadding(): #all 00, its padding
					sectortype.append("padding")

				else: #this should be a file header
					sectortype.append("header")
					size = int(sector.filesize, 8)
					datacountdown = size / 512
					if size % 512: datacountdown += 1

			else: #we are skipping data entries
				sectortype.append("data")
				datacountdown -= 1

		return sectortype

	def getslicefromindex(self, index):
		sectortypes = self.sectortypes()

		#determine file slice
		numfile = -1
		start = None

		for i in range(len(sectortypes)):
			if sectortypes[i] == "header": 
				numfile += 1

			if numfile == index:
				if start == None: 
					start = i
					stop = i
				if sectortypes[i] == "data": 
					stop = i

		if start == None: 
			raise IndexError("No such file entry")

		return start, stop+1

	def __setitem__(self, index, value):
		start, stop = self.getslicefromindex(index)
		self.sectors = self.sectors[:start] + value + self.sectors[stop:]

	def __getitem__(self, index):
		start, stop = self.getslicefromindex(index)
		return self.sectors[start:stop]

	def append(self, data):
		x = self.sectortypes()
		paddingcount = 0

		while x and (x[-1] == "padding"):
			paddingcount += 1
			x.pop()

		cutpoint = len(self.sectors) - paddingcount
		self.sectors = self.sectors[:cutpoint] + data + self.sectors[cutpoint:]

	def __delitem__(self, index):
		start, stop = self.getslicefromindex(index)
		self.sectors = self.sectors[:start] + self.sectors[stop:]
		
	def dumps(self):
		return "".join( map(str, self.sectors) )



class Tarsector():
	def __mkblob(self):
		assert(len(self.filename) == 100)
		assert(len(self.filemode) == 8)
		assert(len(self.userid) == 8)
		assert(len(self.groupid) == 8)
		assert(len(self.filesize) == 12)
		assert(len(self.timestamp) == 12)
		assert(len(self.checksum) == 8)
		assert(len(self.linkindicator) == 1)
		assert(len(self.linkedfilename) == 100)

		return extend("\x00", 512, "".join([self.filename, self.filemode, self.userid, self.groupid, self.filesize, self.timestamp, self.checksum, self.linkindicator, self.linkedfilename]) )

	def __init__(self, data=["\x00"]*512):
		assert(len(data) == 512)

		self.filename = data[0:100]
		self.filemode = data[100:108] #ends 00
		self.userid = data[108:116] #ends 00
		self.groupid = data[116:124] #ends 00
		self.filesize = data[124:136] #ends 00
		self.timestamp = data[136:148] #ends 00
		self.checksum = data[148:156] #ends 0020
		self.linkindicator = data[156:157] #single octal digit
		self.linkedfilename = data[157:257]

	def __str__(self):
		return self.__mkblob()		

	def calculate_checksum(self):
		self.checksum = "\x00"*8
		blob = self.__mkblob()
		checksum = oct(0x100 + sum(map(ord, blob)))# 0x100 is needed somehow
		self.checksum = extend("0", 6, checksum, True) + "\x00\x20"

	@staticmethod
	def num2tar(num, length):
		return extend("0", length-1, oct(num), True) + "\x00"

	@staticmethod
	def str2tar(string, length):
		return extend("\x00", length, string)

	def ispadding(self):
		return not bool(sum(map(ord, str(self.__mkblob()))))
