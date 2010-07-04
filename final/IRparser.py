## This file is part of the htdp project as part of Google Summer of Code
## Copyright (C) 2008 Chris Nicholls
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import math

class IRparser:

	def __getXYfromWiiData(self, data):
		data = list(data)
		## data three bytes of raw input from the remotes
		## it comes in the form xxxxxxxx yyyyyyyy YYXXssss
		## where x,y are the ls bits of the x,y data, X,Y the ms bits 
		## and s is size data 
		## The following converts this into a more usable format
		data[0] = ord(data[0][0])
		data[1] = ord(data[1][0])
		data[2] = ord(data[2][0])
		
		x1 = data[0]
		y1 = data[1]
		
		x2 = (data[2]>>4) & 3
		y2 = data[2]>>6
		
		x= (x2<<8 ) + x1
		y= (y2<<8 ) + y1
		
		# size is discarded. 4 bits isn't that useful. 
		return x,y
		
	def parseWiiData(self,data):
		for d in data:
			if not d: return None,None
			if len(d) != 19: return None,None
		## the public method for the parser. Takes a list of raw wiimote IR data
		## and uses up to the first two. What to do with more than 2 data is 
		## undefined so they are just ignored. 

		##data[7:10] contains the data for the first set of points
		##data[10:13] contains the second. 
		xys1 = [self.__getXYfromWiiData(d[7:10]) for d in data]
		xys2 = [self.__getXYfromWiiData(d[10:13]) for d in data]
		return xys1,xys2
		
	def checkButtonA(self,data):
		if data == None or data ==[]: return False
		##on every channel, bytes 2 & 3 are button bytes. 
		##we're actually going to look at just the A button
		f = lambda e,d: ord(d[3]) & 0x08 or e
		return reduce(f,data, False)


		

