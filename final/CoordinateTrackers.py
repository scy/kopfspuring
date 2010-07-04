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
Co-ordinate tracker:
-SingleCoordinateTracker should be used for a single wiimote
-DoubleCoordinateTracker should be used for two or more
-Both do some error correction to give sensible results.
-CoordinateTrackercontains common code for single and double
 which both inherit from CoordinateTracker
 If your unsure how many wiimotes you will have at run time , use 
 CoordinateTrackerFactory. This is a factory method that  will return
 a SingleCoordinateTracker or DoubleCoordinateTracker depending on its argument n. 
-SingleIRRawCoordinates just returns the parsed data from the wiimote 

A Co-ordinate tracker should satisfy the following interface:

CoordinateTracker:

	getCoordinates() -> coordinatePair
	process([coordinate],[coordinate]) 
	
	where:
		coordinate :: (int,int,int)
		coordinatePair :: (coordinate,coordinate)
	The two lists passed to process should be a list of each wiimotes 
	view of two ir dots (eg, if there is only one wiimte the args might be this:
	process( [ (34,100) ] , [ (560,76) ] )
	This could be updated to support four dots.
	
"""
import time
from math import sin,cos,tan,atan,pi,sqrt
def cross(v1,v2):
	return v1[0]*v2[0] + v1[1]*v2[1]

def arcTan(a,b):
	if b == 0: 
		if a>0: result =  pi/2
		else: result =  -pi/2
	else: result =  atan(a/b)
	return result

class CoordinateTracker:
	radiansPerPixel = (pi / 4) / 1024.0
	def length(self):
		"""Returns the length between the two points"""	
		
	def getMidpointinCartesian(self):
		"""Return the midpoint of the two points in cartesian coordinates.
			The origin can be arbitrary
			"""
	
	def getYaw(self):
		"""Returns the yaw in radians
		-p1/2 < yaw < pi/2
		"""
		 
	def getTilt(self):
		"""Returns tilt (roll) in radians
		-p1/2 < tilt < pi/2
		"""
		
	def getMidpointInPolar(self):
		"""Returns the midpoint between the two points in polar coordinates
			theta,phi,z 
			theta is the horizontal angle, phi is vertical. 
			-pi < theta,phi < pi
			0 <= z
		"""
	def getListOfCartesianCoordinates(self):
		"""Returns the cartesian coordinates of each point"""
		
	
	def process(*args):
		raise Error("Usage Error: CoordinateTracker must be subclassed to use process")

class SingleIRRawCoordinates( CoordinateTracker ):
	##this class will just return the coordinate data form the wiimote
	## without any error correction, 1023s and all. (1023 is what the 
	## wiimote sends if it can't see any IR dots
	def process(self, xys1, xys2 ):
		self.x1,self.y1 = xys1[0][0],xys1[0][1]
		self.dx,self.dy = xys2[0][0]-self.x1,xys2[0][1]-self.y1
		## self.z1,z2 = 0 always. 
			
			
class SingleCoordinateTracker( CoordinateTracker ):	

	distBetweenDots = 150

	def __init__(self):
		self.tilt = 0
		self.yaw =  0
		self.thetaX = 0
		self.thetaY = 0
		self.z = 0
		self.dx,self.dy = 0,0
	def length(self):
		return self.distBetweenDots
		
	def getMidpointInCartesian(self):
		cx,sx = cos(self.thetaX), sin(self.thetaX)
		cy,sy = cos(self.thetaY), sin(self.thetaY)
		z = self.z
		return z*sx*cy, z*cx*sy, z*cx*cy
		
		
	def getYaw(self):
		 return self.yaw
		 
	def getTilt(self):
		return self.tilt
		
	def getMidpointInPolar(self):
		return self.thetaX, self.thetaY, self.z
		
	def getListOfCartesianCoordinates(self):
		cx,sx = cos(self.thetaX), sin(self.thetaX)
		cy,sy = cos(self.thetaY), sin(self.thetaY)
		z = self.z
		midX,midY,midZ = -z*sx*cy, z*cx*sy, z*cx*cy
		l = self.distBetweenDots/2
		dx = -l*cos(self.tilt)*cos(self.yaw)
		dy = l*sin(self.tilt)#*cos(self.yaw)
		dz = l*cos(self.tilt)*sin(self.yaw)
		return (midX + dx, midY + dy, midZ + dz),(midX - dx, midY - dy, midZ - dz)
		
	def  process(self, xys1,xys2 ):
		"""This sets up the variables used in each of the above methods"""
	
		x1,y1,x2,y2 = xys1[0][0],xys1[0][1],xys2[0][0],xys2[0][1]

		if not 1023 in(x1,x2):
			self.thetaX = (x1 + x2 -1024)*self.radiansPerPixel/2.0
			self.thetaY = (y1 + y2 - 768)*self.radiansPerPixel/2.0
			self.yaw = -self.thetaX

			self.dx = (x2-x1)*self.radiansPerPixel
			self.dy = (y2-y1)*self.radiansPerPixel
			
		elif x1 != 1023:
			self.thetaX = (self.dx + (2*x1 - 1024)*self.radiansPerPixel)/2.0
			self.thetaY = (self.dy + (2*y1 - 768) *self.radiansPerPixel)/2.0
			
		elif x2 != 1023:
			self.thetaX = (-self.dx + (2*x2 - 1024)*self.radiansPerPixel)/2.0
			self.thetaY = (-self.dy + (2*y2 - 768) *self.radiansPerPixel)/2.0
			
		self.tilt = arcTan(self.dy,self.dx)
		tanX = tan(self.dx)
		tanY = tan(self.dy)
		
		if self.dx != 0 or self.dy != 0: 
			z = self.distBetweenDots/( 2*sqrt(tanX * tanX + tanY * tanY) ) 
			self.z = z

		

class DoubleCoordinateTracker( CoordinateTracker ):	

	distanceBetweenWiimotes = 37
	switch = 0
	visible = 15
	def __init__(self):
		self.x1,self.y1,self.z1 = 0,0,0
		self.x2,self.y2,self.z2 = 0,0,0
		self.dx,self.dy,self.dz = 0,0,0
		self.oldVectors = (0,0,0),(0,0,0)
	def length(self):
		return sqrt(self.dx**2+self.dy**2+self.dz**2)
	
	def getListOfCartesianCoordinates(self):
		return (self.x1,self.y1,self.z1), (
				self.x1 + self.dx,
				self.y1 + self.dy,
				self.z1 + self.dz)
				
	def getMidpointInCartesian(self):
		return (self.x1+self.x2)/2, (self.y1+self.y2)/2,(self.z1+self.z2)/2

	def getYaw(self):
		s = sqrt(self.dx**2 + self.dy**2)
		return arcTan(self.dz,s)
		
	def getTilt(self):
		s = sqrt(self.dx**2 + self.dz**2)
		return arcTan(self.dy,s)
		
	def getMidpointInPolar(self):
			theta = arcTan(self.x1+self.x2,self.z1+self.z2)
			phi = arcTan(self.y1+self.y2,self.z1+self.z2)
			dx,dy,dz =  (self.x1+self.x2)/2, (self.y1+self.y2)/2,(self.z1+self.z2)/2
			R = sqrt(dx*dx+dy*dy+dz*dz)
			return theta,phi,R
	
	def convertTo3d(self,xA,xB,yA,yB):
			"""See documentation for an explanation of the maths here"""
			thetaAx = (xA-512)*self.radiansPerPixel
			thetaBx = (xB-512)*self.radiansPerPixel
			thetaAy = (yA-384)*self.radiansPerPixel
			thetaBy = (yB-384)*self.radiansPerPixel
					
			t = abs(tan(thetaAx) - tan(thetaBx) )
			if t!= 0:
				z = self.distanceBetweenWiimotes / t
				x = z * tan(thetaAx) - self.distanceBetweenWiimotes/2
				y = z * (tan(thetaAy) + tan(thetaBy)) /2
				return -x,y,z
			return 0,0,0
	
	def process(self, xys1,xys2 ):
	
		xA1,xB1,= xys1[0][0],xys1[1][0] ## the first x coordinate from each remote
		xA2,xB2 = xys2[0][0],xys2[1][0] ## the second x coordinate from each remote
		yA1,yB1,= xys1[0][1],xys1[1][1] ## the first y coordinate from each remote
		yA2,yB2 = xys2[0][1],xys2[1][1] ## the second y coordinate from each remote

		## update tells us if we have enough info to update the coordinates
		update  = True
		## visible is a bitmask of the points that are visible
		visible = reduce((lambda x,y: (x << 1) + (y!=1023)),(xA1,xB1,xA2,xB2),0)
		if visible == 15: self.visible = 15 ## we can see everything
		else: self.visible &=visible ## take away the points we can't see
		update &= self.visible not in (0,1,2,4,8) ##If we've lost sight of three
		## or more dots, then we don't want to update until we see then all again
		

		
		if 1023 not in (xA1,xB1,xA2,xB2):
			## this is a way of telling if we have the two dots mixed
			## up from one remote. It uses the dot product to tell if 
			## the vectors  (xA1,yA1)->(xA2,yA2) and (xB1,yB1)->(xB2,yB2) 
			## point in the same direction			
			v1,v2 = ((xA2-xA1),(yA2-yA1)), ((xB2-xB1),(yB2-yB1))
			v3,v4 = self.oldVectors
			if cross(v1,v2) < 0:
				## The cross product of two vectors in R2 is negative
				## iff the angle between them is greater than pi/2
				## or less than -pi/2
				if   cross(v1,v3) <= 0 and cross(v2,v4) >=0:
					self.switch = 1
					self.oldVectors = (-v1[0],-v1[1]),v2
				elif cross(v1,v3) >= 0 and cross(v2,v4) <=0:
					## This almost never happens. 
					self.switch = 2
					self.oldVectors = v1,(-v2[0],-v2[1])
				else: 
					## Something's gone a bit wrong. 
					self.update = 0
			else: 
				self.switch = 0
				if cross(v1,v3) <= 0 and cross(v2,v4) <=0:
					if self.switch != 0: self.switch =  3
					self.oldVectors = (-v1[0],-v1[1]),(-v2[0],-v2[1])
				else:
					self.oldVectors = v1,v2
	
		else: update = 0
		if   self.switch == 1:
				xA1,xA2,yA1,yA2 = xA2,xA1,yA2,yA1
		elif self.switch == 2:
				xB1,xB2,yB1,yB2 = xB2,xB1,yB2,yB1
		elif self.switch == 3:
				xA1,xA2,yA1,yA2 = xA2,xA1,yA2,yA1
				xB1,xB2,yB1,yB2 = xB2,xB1,yB2,yB1
				self.switch = 0
				
		if update and 1023 not in (xA1,xB1):
			self.x1,self.y1,self.z1 = self.convertTo3d(xA1,xB1,yA1,yB1)
		if update and 1023 not in (xA2,xB2):
			self.x2,self.y2,self.z2 = self.convertTo3d(xA2,xB2,yA2,yB2)
			
		self.dx = self.x2 - self.x1
		self.dy = self.y2 - self.y1
		self.dz = self.z2 - self.z1

def CoordinateTrackerFactory(n,raw = False):
	if n <= 0: 
		print "Cannot parse data of zero length!"
		return SingleIRRawCoordinates()
	if n == 1: 
		if raw:
			return SingleIRRawCoordinates()
		else:
			return SingleCoordinateTracker()
	if n == 2: 
		return DoubleCoordinateTracker()
	if n > 2:
		##Umm....
		return DoubleCoordinateTracker()
		
