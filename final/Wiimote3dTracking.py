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

import threading
from Wiimote import Wiimote
from CoordinateTrackers import CoordinateTrackerFactory
from IRparser import IRparser
from BluetoothSupport import searchForWiimotes
import time

class Wiimote3dTracker(threading.Thread):
	useNormalisation = False
	def __init__(self,*addresses,**raw ):
		## Accepts an arbitrary number of wiimote addresses as an argument
		## Currently, any remotes past the first two are ignored, as the IR
		## parser doesn't know what to do with them. Neither do I actually...

		self.badcoords = (1023, 1023)
		self.valid = False
		self.adrs=addresses
		if len(self.adrs) ==1 and type(self.adrs[0]) == list:
			self.adrs = self.adrs[0]
		if len(self.adrs) ==0 : self.adrs = Wiimote3dTracker.search()
		
		self.wiimotes= [Wiimote(adr) for adr in self.adrs]
		self.coordinateTracker = CoordinateTrackerFactory(len(self.wiimotes),raw = raw)
		self.irParser = IRparser()
		self.polarListeners = []
		self.cartesianListeners = []
		
		## set up the stuff needed for threading:
		threading.Thread.__init__ (self)
		
	def connect(self, listOfAddresses = None):
		## Tries to connect to each address and returns true if everything went ok.
		## listOfAddresses is an optional list of addresses to connect to
		print "Connecting to wiimotes..."
		if listOfAddresses:
			self.wiimotes= [Wiimote(adr) for adr in listOfAddresses]
		result = not False in [ wm.connect() for wm in self.wiimotes]
		if result:
			for i in range(len(self.wiimotes)):
				self.wiimotes[i].setLEDinBinary(i)
		return result
		
	## searchForWiimotes() returns a function. 
	## classmethod means search is 'static' i,e. no instance 
	## of a Wiimote3dTracker is needed
	search = classmethod(searchForWiimotes())
		
	def disconnect(self):
		# Disconnects from all wiimotes.
		self._Thread__stop
		for wm in self. wiimotes: wm.disconnect()
		print "Disconnecting"
		

	def run(self,pause = 0.004):
		while 1: 	
			self.refresh()
			time.sleep(pause)
	
	def refresh(self):
		## refresh retrieves the data from each wiimote, parses them and 
		## sends them to whoever is listening via the refresh method.
		## if any listener returns false, then we disconnect and quit. 
		
		if all([wm.updated for wm in self.wiimotes]):
			data  = [wm.getData() for wm in self.wiimotes]
			xys1, xys2 = self.irParser.parseWiiData( data )
			if xys1 and xys2:
				self.valid = xys1[0] != self.badcoords and xys1[1] != self.badcoords and xys2[0] != self.badcoords and xys2[1] != self.badcoords
				self.coordinateTracker.process( xys1, xys2 )
			result = True
			if len(self.cartesianListeners) > 0:
				pos1,pos2 = self.coordinateTracker.getListOfCartesianCoordinates()
				pos1,pos2 = self.scale(pos1),self.scale(pos2)
				for l in self.cartesianListeners:
					result &= (l.refresh(pos1,pos2) != False)
					## The '!= False' allows listeners to return None (no return) 
					## as None != False
			if len(self.polarListeners) > 0:
				midInPolar = self.coordinateTracker.getMidpointInPolar()
				midInCart  = self.coordinateTracker.getMidpointInCartesian()
				midInCart = self.scale( midInCart ) 
				tilt = self.coordinateTracker.getTilt()
				yaw = self.coordinateTracker.getYaw()
				for l in self.polarListeners:
						result &= (l.refresh(midInPolar,midInCart,yaw,tilt) != False)	
						## The '!= False' allows listeners to return None (no return) 
						## as None != False
						
			## if one of the listeners wants us to exit,  then exit.
			if not result:# or self.irParser.checkButtonA(data): 
				self.disconnect()
				import sys
				sys.exit()	

	def scale(self,p): return p
	
	def calibrate(self,(minX,minY,minZ),(maxX,maxY,maxZ),duration = 5,integer = True):
		""" Collects position values for 'duration' number of seconds and works out a scaling based on these values to fit inside the box boundes by (minX,minY,minZ),(maxX,maxY,maxZ).
			It then replaces 'scale' to use these values
		"""
		t0 = time.time()
		minXYZ,maxXYZ = [2*31]*3,[-2**31]*3##+- inf...not nice but it will do...
		while time.time() - t0 < duration: ## Probably not the best guard
			self.refresh()
			points =  self.coordinateTracker.getListOfCartesianCoordinates()
			minXYZ = [ min ([minXYZ[i]] + [point[i] for point in points]) for i in [0,1,2] ]
			maxXYZ = [ max ([maxXYZ[i]] + [point[i] for point in points]) for i in [0,1,2] ]
		factor = max([abs(maxXYZ[i] - minXYZ[i]) for i in [0,1,2]])
		
		def scale((x,y,z)):
			## Yeah, I know this /could/ be re-factored.
			## But this is simpler. 
			if factor != 0:
				x = float(x) - (minXYZ[0]+maxXYZ[0])/2 
				x = x/factor
				x = x*abs(maxX - minX)
				x = x+(maxX + minX)/2
			
				y = float(y) - (maxXYZ[1] + minXYZ[1])/2
				y = y/factor
				y = y*abs(maxY - minY)
				y = y+(maxY + minY)/2

				z = float(z) - (maxXYZ[2]+ minXYZ[2])/2
				z = z/factor
				z = z*abs(maxZ - minZ)
				z = z+(maxZ + minZ)/2
			if integer: return map(int,(x,y,z))
			else: return x,y,z
		self.scale = scale
		
	def register(self, listener):
		""" Adds a listener to the tracker. 
			Whenever Wiimote3dTracker.refresh is called, listener.refresh gets called with one of the folowing sets of arguments: 
			> listener.refresh((x1,y1,z1),(x2,y2,z2))
			where (x1,y1,z1),(x2,y2,z2) are the cartesian coordinates of the two LEDs being tracked
			or
			> listener.refresh((theta,phi,R),(x,y,z),yaw,tilt)
			where 'theta' is the horizontal angle in radians towards the midpoint of the two LEDs being tracked, 'phi' is the vertical angle and 'R' is the distance to the midpoint. ('x','y','z') are the cartesian coordinates of the midpoint. 'yaw' is the horizontal angle between the LEDs and 'tilt' is the vertical angle.
			
			The listeners 'refresh' method must accept either two or four arguments and will be called with the corresponding set of values.
			"""
			## This tests weather the listener has a 'refresh' method	 
		if not hasattr(listener,'refresh') or not hasattr(listener.refresh,'func_code'):
			raise AttributeError("%s does not have a 'refresh' method.\n Type help(Wiimote3DTracker.register) for more information on refresh methods."% listener.__class__)
		## Ok, so we have a refresh method (probably) but we need to make sure 
		## it has the correct number of 	arguments
		elif listener.refresh.func_code.co_argcount == 3: 
			if listener not in self.cartesianListeners:
				self.cartesianListeners += [listener]
		elif listener.refresh.func_code.co_argcount == 5:
			if listener not in self.polarListeners:
				self.polarListeners += [listener]
		else:
			print listener.refresh.func_code.co_argcount
			raise AttributeError("%s does not have a valid 'refresh' method.\n Type help(Wiimote3DTracker.register) for more information on refresh methods." % listener.__class__)			
	
	def unregister(self,listener):
		"""Removes 'listener' from the list of registered listeners"""
		if listener in self.cartesianListeners:
			self.cartesianListeners.remove(listener)
		if listener in self.polarListeners:
			self.polarListeners.remove(listener)
			
			
	def getNumberOfWiimotes(self):
		return len(self.adrs)
		
	def getWiimoteAddresses(self):
		return self.adrs
		
	def vibrate(self,address,duration = 1):
		"""Vibrates the specified wiimote for 'duration' seconds"""
		if not address in self.adrs: return
		i = self.adrs.index(address)
		self.wiimotes[i].vibrate(duration)
		

