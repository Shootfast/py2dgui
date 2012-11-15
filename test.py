#!/usr/bin/env python
import sys
sys.path.append('./python')
from py2dgui import Stage, Triangle, Square, Color

from OpenGL.GL import glClearColor, glClear, GL_COLOR_BUFFER_BIT
from OpenGL import GLUT	

from time import time
	 
	 
class MyStage(Stage):
	'''
	Stage that uses glut to render
	'''
	def __init__(self, width, height):
		super(MyStage, self).__init__(width, height)
		
		# Record when we last printed FPS
		self.lastPrinted = time()
	
	def render(self):
		'''
		Render the geometry for the scene
		'''
		# Clear the buffer
		glClearColor(0.0, 0.0, 0.0, 0.0)
		glClear(GL_COLOR_BUFFER_BIT);
		
		# render the stage
		super(MyStage, self).render()
		
		# Swap GLUT buffers
		GLUT.glutSwapBuffers()
		
		# Print FPS every 5 seconds
		now = time()
		if now - self.lastPrinted > 5:
			self.lastPrinted = now
			print "FPS: %s" % self.fps
		
	  
	  
	  
if __name__ == "__main__":
	
	width, height = (640, 480)
	GLUT.glutInit(sys.argv)
	GLUT.glutInitDisplayMode(GLUT.GLUT_RGBA | GLUT.GLUT_DOUBLE | GLUT.GLUT_DEPTH)
	GLUT.glutInitWindowSize(width, height)
	GLUT.glutInitWindowPosition(0,0)
	
	window = GLUT.glutCreateWindow("py2dgui Test Window")
	
	stage = MyStage(width, height)
	
	GLUT.glutDisplayFunc(stage.render)
	GLUT.glutIdleFunc(stage.render)
	
	
	# Colors for shape (one color per point)
	colors = [Color(r=1.0), Color(g=1.0), Color(b=1.0)]
	
	# Make a triangle
	shape = Triangle(colors=colors)
	
	# Make a square
	shape = Square(colors=colors)
	
	# Add it to the stage
	stage.add_actor(shape)

	# Enter the main loop
	GLUT.glutMainLoop()
	
	
		
			
				
		
	
