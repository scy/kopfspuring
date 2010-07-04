#!/usr/bin/env python

# This code intentionally left hackish.

from OpenGL.GL import *
from OpenGL.GLU import *

from math import *

import pygame
import sys
import time

from final.Wiimote3dTracking import Wiimote3dTracker

wiimotes = ('00:22:D7:FA:E8:A8', '00:1E:A9:61:08:57')
tracker = Wiimote3dTracker(wiimotes[0], wiimotes[1])
tracker.connect()

class Listener:
	def __init__(self):
		self.limits = [20.0, 10.0, 10.0]
		self.factors = [1.0, 1.0, 1.0]
		self.fovy = 90.0
	def refresh(self, pos1, pos2):
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
		l = -3 / (z - 3)
		wy = l * y
		wx = l * x
		self.lookat = [wx + 1.5, wy + 1.5, 0.0]
		print ((x, y, z), l, self.lookat)

motes = Listener()
tracker.register(motes)

pygame.init() 
sur = pygame.display.set_mode((0,0), pygame.OPENGL|pygame.DOUBLEBUF|pygame.HWSURFACE|pygame.FULLSCREEN)

done = False


def drawCuboid(x1, y1, z1, x2, y2, z2):
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

def drawSphere(x, y, z, r):
    glPushMatrix()
    glTranslatef(x, y, z)
    gluSphere(gluNewQuadric(), r, 80, 80)
    glPopMatrix()

def vary(num, time):
    return sin((pygame.time.get_ticks() % time) / float(time) * 2 * pi) * num

def setColor(r, g, b, a):
    glColor4fv([r, g, b, a])
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [r, g, b, a])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.5, 0.5, 0.5, 1])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SHININESS, [0.6])

def chill(fps):
    if not hasattr(chill, 'time'):
        chill.time = pygame.time.get_ticks()
    now = pygame.time.get_ticks()
    took = (now - chill.time)
    rest = (1000 / fps) - took
    if (rest > 0):
        pygame.time.wait(rest)
    chill.time = now




glClearColor(0.0, 0.0, 0.0, 0.0)
glShadeModel(GL_SMOOTH)
glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 0.9])
glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.5, 0.5, 0.5, 0.9])
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)
#glEnable(GL_DEPTH_TEST)
glCullFace(GL_BACK)
glEnable(GL_CULL_FACE)
height = sur.get_height()
width = sur.get_width()
aspect = width / height

while not done:
	tracker.refresh()
	lp = vary(1.5, 2000)
	glLightfv(GL_LIGHT0, GL_POSITION, [3, 1.5 + lp, 3, 1])
	glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
	
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	gluLookAt(1.5, 1.5, 3, motes.lookat[0], motes.lookat[1], motes.lookat[2], 0, 1, 0)
	
	setColor(0.7, 0.3, 0, 0.6)
	drawCuboid(0, 0, 0, 3, 3, 3)
	
	setColor(0, 1, 0.8, 0.5)
	drawCuboid(0.5, 0, 1, 1, 0.5, 2)
	
	setColor(0.5, 0, 0, 0.7)
	drawSphere(0.5, 0.5, 2.3, 0.5)
	
	setColor(0, 1, 0, 0.5)
	drawSphere(1.7, 1.5 + vary(0.5, 10000), 1, 1)
	
	glViewport(0, 0, width, height)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(motes.fovy, aspect, 1, 10)
	# glFrustum(0, 3, 0, 3, 1, 4)
	pygame.display.flip()
	chill(30)
	event = pygame.event.poll()
	if event.type == pygame.KEYDOWN:
		done = True

tracker.disconnect()
sys.exit(0)

