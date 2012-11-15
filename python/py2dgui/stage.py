from py2dgui.shaders import vertex, fragment
from OpenGL.GL import   shaders,			 \
						GL_VERTEX_SHADER,	\
						GL_FRAGMENT_SHADER
						
from time import time

class Stage(object):
	'''
	Main object from which all other RVPY2 objects are rendered
	'''
	def __init__(self, width=0, height=0):
		self.width = width
		self.height = height
		
		self.actors = []
		
		# Time the stage was constructed
		self.startTime = time()
		
		self.fps = 0
		self.frameFinishTime = 0
		
		self.setup()
		
	def setup(self):
		# Compile the Vertex Shader
		VERTEX_SHADER = shaders.compileShader(vertex, GL_VERTEX_SHADER)
		# Compile the Fragment Shader
		FRAGMENT_SHADER = shaders.compileShader(fragment, GL_FRAGMENT_SHADER)
		# Join them as the shader program
		self.shader = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)
		
	def getElapsedTime(self):
		'''
		Get the total elapsed time since stage was constructed
		'''
		return time() - self.startTime
		
	def resize(self, width, height):
		'''
		Set the size of the stage
		'''
		self.width = width
		self.height = height
		
		
	def add_actor(self, actor):
		'''
		Add an actor to the stage
		'''
		if actor not in self.actors:
			self.actors.append(actor)

	def render(self):
		'''
		Render all actors on the stage
		'''
		before = time()
		# Render our actors
		for actor in self.actors:
			frameInfo = FrameInfo(self, self.shader)
			actor.render(frameInfo)
		after = time()
		
		# record the framerate
		framerate = after - before
		self.fps = 1.0 / framerate 
		
		# Record frame finish time
		self.frameFinishTime = after
		

class FrameInfo(object):
	'''
	Object that contains all information from stage needed to render an actor
	'''
	def __init__(self, stage, shader):
		self.stage = stage
		self.frameFinishTime = stage.frameFinishTime
		self.shader = shader
