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
## 

from Tkinter import *
	
def getListOfListenersFromFileName(fileName):
	from os.path import split
	import sys
	
	directory,module =  split(fileName)
	sys.path.append(directory)
	exec("import %s as _module" % module.rsplit('.',1)[0])
	vars = [ eval("_module.%s" %ob) for ob in dir(_module) ]
	vars = [ob for ob in vars if  str(type(ob))  == "<type 'classobj'>"]
	vars = [ob for ob in vars if  hasattr(ob,'refresh')]
	vars = [ob for ob in vars if hasattr(ob.refresh,'func_code') ]
	
	return vars

	

def lookupListener(parent):
	from tkFileDialog import askopenfilename
	from tkMessageBox import showerror
	from tkSimpleDialog import askstring
	newWindow = Toplevel(parent)
	#newWindow.title( "Select listener" )


	while 1:
		fileName = askopenfilename()
		if fileName == (): return None
		listeners = getListOfListenersFromFileName(fileName)
		if len(listeners) == 0:
			showerror("Error!","No listeners found in %s"%fileName)
		else:
			break
	l = Listbox(newWindow,height = len(listeners))
	
	def quit(*args):
		globals().update({'listener': listeners[int(l.curselection()[0])]})
		args = ''
		if listener.__init__.func_code.co_argcount >1:
			args = askstring('Entry', 'Please enter constructor arguments:')
		globals().update({'args':args})
		newWindow.quit()
		newWindow.withdraw()
		
	l.bind("<Double-Button-1>", quit)
	b = Button(newWindow,text = "ok",command = quit )
	newWindow.lift()
	for ob in listeners:
		l.insert(END,str(ob).split('.')[-1])
	l.selection_set(0)
	l.pack()
	b.pack()

	newWindow.mainloop()
	return eval("listener(%s)"%args)
	

