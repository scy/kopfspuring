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
"""This is a group of wrappers for various operating systems"""
from os import name
def newSocket():
		
		if name == "posix":
			return __LinuxL2CAPSocket()
		if name == "nt" or name =="ce": 
			return __WindowsL2CAPSocket()
		if name == "mac": 
			return __MacL2CAPSocket()
		## Other names: dos, os2, java, riscos
		## os.uname()[0] is another option but I think this will do.  
		
		## No support for OS, but lets try linux...
		Warning("Operating system not supported")
		return __LinuxL2CAPSocket()
		
		
class __LinuxL2CAPSocket:
	"""Linux L2CAP wrapper"""
	from bluetooth import BluetoothSocket,L2CAP	
	def __init__(self):
		self.sock = self.BluetoothSocket( self.L2CAP )
	
	def connect(self,address,port):
		self.sock.connect((address,port))
		
	def close(self):
		self.sock.close()
		
	def receive(self,length):
		return self.sock.recv(length)
		
	def send(self,string):
		self.sock.send(string)
	
class __WindowsL2CAPSocket():
	"""Windows L2CAP wrapper"""	
	def __init__(self):
		raise OSError("Sorry, Windows is not currently supported") 
	
	def connect(self,address,port):
		pass
		
	def close(self):
		pass
		
	def receive(self,length):
		pass
		
	def send(self,string):
		pass
		
class __MacL2CAPSocket():
	"""Mac L2CAP wrapper"""	
	def __init__(self):
		raise OSError("Sorry, Macs are not currently supported") 
	
	def connect(self,address,port):
		pass
		
	def close(self):
		pass
		
	def receive(self,length):
		pass
		
	def send(self,string):
		pass
		
def __linuxSearch():
		from bluetooth import discover_devices,lookup_name
		import time, threading
		## Threads are used to look up names to avoid the 
		## problem of waiting for each device to respond before
		## moving on to the next which may have left 'discoverable'
		## mode. It may be possible to get this info when we do the
		## initial search...
		
		class LinuxNameGetter(threading.Thread):
			
			def __init__(self,address):
				print "Address: ",address
				self.name = None
				## set up the stuff needed for threading
				threading.Thread.__init__ (self) 
				self.addr = address
			def run(self):
				print "Starting thread for addr %s" % self.addr
				self.name = lookup_name(self.addr)
				print "addr %s --> %s" %(self.addr,self.name)
				
		print "Searching for wiimotes..."
		addresses = discover_devices(0)
		print "Found %i devices" % len(addresses)
		## create the thread things
		threads = [LinuxNameGetter(x) for x in addresses]
		for t in threads: t.start()
		while any([t.isAlive() for t in threads]): ## checks if any threads are still running
			time.sleep(0.1)
		return [(t.addr,t.name) for t in threads]
		

	
		
def searchForWiimotes():
		""" Returns a platform specific function that will return a list of all wiimotes in range
		"""
		## Each __[os]Search  should return a list of tuples 
		## in the following format:
		## (address, name) 
		## for each available bluetooth device in range. 
		if name == "posix":
			search =  __linuxSearch
		elif name == "nt" or name =="ce": 
			search = __windowsSearch
		elif name == "mac": 
			search = __macSearch
		## No support for OS, but lets try linux...
		else:
			Warning("Operating system not supported")
			devices = __LinuxSearch()
		
		return lambda dummy: [e[0] for e in search() if e[1] == 'Nintendo RVL-CNT-01']
