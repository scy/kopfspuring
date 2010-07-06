#!/usr/bin/env python

# This code is a work in progress.
# Several ideas regarding projection and perspective have been tried, and not
# all of the variables and calculations are actually used. Be aware.

from OpenGL.GL import *
from OpenGL.GLU import *

from math import *

import pygame
import sys
import time

from final.Wiimote3dTracking import Wiimote3dTracker

dotdistance = 200 # in mm
screenheigth = 190
radiansperpixel = pi / 4.0 / 1024.0

# Bluetooth IDs. Find yours with "hcitool scan".
wiimotes = ('00:22:D7:FA:E8:A8', '00:1E:A9:61:08:57')
tracker = Wiimote3dTracker(wiimotes[0], wiimotes[1])
tracker.connect()

# This will get notified after a new Wiimote reading has been processed.
class Listener:
	def __init__(self):
		self.limits = [0.5, 0.5, 5] # Maximum values for x, y, z.
		self.factors = [1.0, 1.0, 1.0] # Initial multiplication factor.
		self.head = [0, 0, 1] # Position of the head.
		self.fovy = 120 # Field of view (y) in degrees.
		self.valid = False # Whether both Wiimotes see both points.
	def refresh(self, pos1, pos2):
		# Calculate and auto-limit x, y, z.
		x = (pos1[0] + pos2[0]) / self.factors[0]
		if x > self.limits[0]:
			nu = (pos1[0] + pos2[0]) / self.limits[0]
			if nu > self.factors[0]:
				self.factors[0] = nu
				x = self.limits[0]
		elif x < -1 * self.limits[0]:
			nu = (pos1[0] + pos2[0]) / (-1 * self.limits[0])
			if nu > self.factors[0]:
				self.factors[0] = nu
				x = self.limits[0] * -1
		y = (pos1[1] + pos2[1]) / self.factors[1]
		if y > self.limits[1]:
			nu = (pos1[1] + pos2[1]) / self.limits[1]
			if nu > self.factors[1]:
				self.factors[1] = nu
				y = self.limits[1]
		elif y < -1 * self.limits[1]:
			nu = (pos1[1] + pos2[1]) / (-1 * self.limits[1])
			if nu > self.factors[1]:
				self.factors[1] = nu
				y = self.limits[1] * -1
		z = (pos1[2] + pos2[2]) / self.factors[2]
		if z > self.limits[2]:
			nu = (pos1[2] + pos2[2]) / self.limits[2]
			if nu > self.factors[2]:
				self.factors[2] = nu
				z = self.limits[2]
		# Protect us from division by zero. Silly, but works.
		if z == 0:
			z = 0.05
		# The world position the camera is aimed at.
		self.lookat = [x, y, 0.0]
		# Where in the world our head is assumed to be.
		self.head = [x, y, z / 3.5]
		# Whether that Wiimote reading was actually valid.
		self.valid = tracker.valid

# Register our Listener.
motes = Listener()
tracker.register(motes)

# Get a nice fullscreen surface.
pygame.init()
sur = pygame.display.set_mode((0,0), pygame.OPENGL|pygame.DOUBLEBUF|pygame.HWSURFACE|pygame.FULLSCREEN)

# Set to True to exit the main loop.
done = False


# Draws a cuboid. Pass left bottom back and right top front coordinates.
def drawCuboid(x1, y1, z1, x2, y2, z2):
    # Some faces are facing in the wrong direction.
    glBegin(GL_QUADS)
    # back
    glNormal3f(0, 0, -1)
    glVertex3f(x1, y1, z1)
    glVertex3f(x1, y2, z1)
    glVertex3f(x2, y2, z1)
    glVertex3f(x2, y1, z1)
    # right
    glNormal3f(1, 0, 0)
    glVertex3f(x2, y1, z1)
    glVertex3f(x2, y2, z1)
    glVertex3f(x2, y2, z2)
    glVertex3f(x2, y1, z2)
    # top
    glNormal3f(0, 1, 0)
    glVertex3f(x1, y2, z1)
    glVertex3f(x1, y2, z2)
    glVertex3f(x2, y2, z2)
    glVertex3f(x2, y2, z1)
    # left
    glNormal3f(-1, 0, 0)
    glVertex3f(x1, y2, z1)
    glVertex3f(x1, y1, z1)
    glVertex3f(x1, y1, z2)
    glVertex3f(x1, y2, z2)
    # down
    glNormal3f(0, -1, 0)
    glVertex3f(x1, y1, z1)
    glVertex3f(x1, y1, z2)
    glVertex3f(x2, y1, z2)
    glVertex3f(x2, y1, z1)
    # front
    glNormal3f(0, 0, 1)
    glVertex3f(x1, y2, z2)
    glVertex3f(x1, y1, z2)
    glVertex3f(x2, y1, z2)
    glVertex3f(x2, y2, z2)
    glEnd()

# Draw a sphere. Pass center and radius.
def drawSphere(x, y, z, r):
    glPushMatrix()
    glTranslatef(x, y, z)
    gluSphere(gluNewQuadric(), r, 80, 80)
    glPopMatrix()

# Vary some value between -num and num over time ms.
def vary(num, time):
    return sin((pygame.time.get_ticks() % time) / float(time) * 2 * pi) * num

# Universal color-setting function for flat and lighted surfaces.
def setColor(r, g, b, a):
    glColor4fv([r, g, b, a])
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [r, g, b, a])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.5, 0.5, 0.5, 1])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, [0.6])

# Wait an amount of time to achieve the desired fps.
def chill(fps):
    if not hasattr(chill, 'time'):
        chill.time = pygame.time.get_ticks()
    now = pygame.time.get_ticks()
    took = (now - chill.time)
    rest = (1000 / fps) - took
    if (rest > 0):
        pygame.time.wait(rest)
    chill.time = now



# Initialize the world, lighting and GL options.
glClearColor(0.0, 0.0, 0.0, 0.0)
glShadeModel(GL_SMOOTH)
glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 0.9])
glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.5, 0.5, 0.5, 0.9])
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)
glCullFace(GL_BACK)
height = sur.get_height()
width = sur.get_width()
aspect = width / height
nearplane = 0.05

while not done:
	tracker.refresh()

	# A swinging light.
	lp = vary(0.5, 2000)
	glLightfv(GL_LIGHT0, GL_POSITION, [0 + lp, 0.5, 2, 1])

	glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
	
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	gluLookAt(motes.head[0], motes.head[1], motes.head[2], motes.head[0], motes.head[1], 0, 0, 1, 0)
	
	# Room container?
	setColor(0.7, 0.3, 0, 0.6)
	#drawCuboid(-0.5, -0.5, 0, 0.5, 0.5, 1)
	
	# Floor cuboid, changes color depending on whether tracking works.
	cuboidColor = (0, 1, 0.8, 0.5)
	if not motes.valid:
		cuboidColor = (1, 0.2, 0, 0.5)
	setColor(*cuboidColor)
	drawCuboid(-0.4, -0.5, 0.2, 0.1, -0.4, 0.6)
	
	# Red sphere.
	setColor(0.5, 0, 0, 0.7)
	drawSphere(-0.3, -0.3, 0.8, 0.1)
	
	# Green hovering sphere.
	setColor(0, 1, 0, 0.5)
	drawSphere(0.2, vary(0.2, 10000), 0.4, 0.3)

	# Purple flying cuboid.
	setColor(0.5, 0, 0.5, 0.8)
	drawCuboid(0.2, 0.2, 0.5, 0.5, 0.5, 0.9)
	
	# Perspective foo.
	glViewport(0, 0, width, height)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(motes.fovy, aspect, 0.1, 100)
	(x, y, z) = motes.head
	frustum = (nearplane*(-.5*aspect+x)/z, nearplane*(.5*aspect+x)/z, nearplane*(-.5-y)/z, nearplane*(.5-y)/z, nearplane, 100)
	#glFrustum(*frustum)
	print (motes.head, frustum)
	# Switch buffers.
	pygame.display.flip()
	chill(30)
	event = pygame.event.poll()
	if event.type == pygame.KEYDOWN:
		# On keypress, quit.
		done = True

# Disconnect and exit.
tracker.disconnect()
sys.exit(0)

