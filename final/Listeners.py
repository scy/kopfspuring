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

"""
A few example listeners
A listener should satisfy the following interface:
 Listener:
 	 refresh(coordinate,coordinate) -> bool
 	 
 	 where:
 	 	coordinate :: (int,int,int)

"""
class Socket:
	## This sends out the refresh data on the specified port
	## usage:
	## 	talker.register( Socket() )
	##	talker.register( Socket( port = 5035) 
	## etc..
	def __init__(self,port=4440,host = ""):
		## will raise a socket error if the port isn't available
		import sys, socket
		self.data = None
		self.mySocket = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
		self.mySocket.connect ( ( host, port ) )
			
			
	def refresh(self,(x1,y1,z1),(x2,y2,z2)):
		if (x1,y1,z1,x2,y2,z2)!= self.data:
			self.mySocket.send("x:%i,y:%i,z:%i,X:%i,Y:%i,Z:%i:1\n" % (x1,y1,z1,x2,y2,z2))
			self.data = (x1,y1,z1,x2,y2,z2)
			return True		
			
class Printer:
	## This is an example of a listener. Its refresh method simply prints the data
	## if it has changed, and returns True to indicate success.
	def __init__(self):
		self.oldData = None
	def refresh(self,(x1,y1,z1),(x2,y2,z2)):
			if (x1,y1,z1,x2,y2,z2) != self.oldData:
				print "x:%i,y:%i,z:%i,X:%i,Y:%i,Z:%i:1" % (x1,y1,z1,x2,y2,z2)
				self.oldData = (x1,y1,z1,x2,y2,z2)
			return True

