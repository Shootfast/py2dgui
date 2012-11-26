#!/usr/bin/env python
import sys
sys.path.append('./python')
from py2dgui import *
from py2dgui import animations

from OpenGL.GL import glClearColor, glClear, GL_COLOR_BUFFER_BIT, glViewport
from OpenGL import GLUT	

from time import time
	 
	 
	 
class MyStage(Stage):
	'''
	Stage that uses glut to render
	'''
	def __init__(self, width, height):
		super(MyStage, self).__init__(width, height)
		
		# Record when we last printed FPS
		#self.lastPrinted = time()
	
	def render(self):
		'''
		Render the geometry for the scene
		'''
		# Clear the buffer
		glClearColor(0, 0, 0, 1)
		glClear(GL_COLOR_BUFFER_BIT);
		
		# render the stage
		super(MyStage, self).render()
		
		# Swap GLUT buffers
		GLUT.glutSwapBuffers()
		
		# Print FPS every 5 seconds
		now = time()
		#if now - self.lastPrinted > 5:
			#self.lastPrinted = now
			#print "FPS: %s" % self.fps
		
	def resize(self, w, h):
		glViewport(0,0,w,h)
		super(MyStage, self).resize(w,h)
	  
	  
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
	GLUT.glutReshapeFunc(stage.resize)
	
	
	# Make a shape
	#shape = BorderedSquare(color=Color(0.3, 0.3, 0.3), border_width=2)
	#shape.translate(Point(320, 240))
	#shape.scale(Point(.2,.8,.2))
	#shape.rotate(Point(z=15))
	
	
	# Make a red square
	#shape2 = Square(color=Color(1.0))
	#shape2.scale(Point(-.5, -.5, -.5))
	#shape2.translate(Point(0,25))
	#shape.addChild(shape2)
	
	# Add it to the stage
	#stage.add_actor(shape)
	#stage.add_actor(shape2)

	text = TextActor('./fonts/LiberationSerif-Regular.ttf', 48, text="Hello World!", color=Color(1))
	text.translate(Point(10,100))
	stage.addActor(text)
	
	f = animations.FadeIn(text, 1)
	stage.addAnimation(f)
	
	#image = ImageActor('./Pictures/success_kid.png', alpha=.5)
	#image.translate(Point(10,10))
	#stage.addActor(image)

	# Enter the main loop
	GLUT.glutMainLoop()
	
	
		
			
				
		
	
