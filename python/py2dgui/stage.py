from py2dgui.shaders import vertex, fragment
from OpenGL.GL import   shaders,			 \
						GL_VERTEX_SHADER,	\
						GL_FRAGMENT_SHADER
						
from time import time

from numpy import array

class Stage(object):
	'''
	Main object from which all other RVPY2 objects are rendered
	'''
	def __init__(self, width=0, height=0):
		self.width = 0
		self.height = 0
		
		self.actors = []
		
		self.shader = None
		self.projection_matrix = None
		
		# Time the stage was constructed
		self.startTime = time()
		
		self.fps = 0
		self.frameFinishTime = 0
		
		self.setup()
		self.resize(width, height)
		
	def setup(self):
		'''
		Compile the shader program
		'''
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
		
		zNear = 0.5
		zFar  = 3.0
		
		# recalculate Orthogonal projection matrix
		self.projection_matrix = array([
									
				[2/float(width),        0,                0,         0          ],
				[     0,         2/float(height),         0,         0          ],
				[     0,                0,        1/(zFar - zNear), -zNear / (zFar - zNear)],
				[     0,                0,      0,     1 ]
										],'f')
		
		self.identity_matrix = array([
									[1,0,0,0],
									[0,1,0,0],
									[0,0,1,0],
									[0,0,0,1]
									],'f')
		
		# Use the identity matrix till I can fix this :/
		#self.projection_matrix = self.identity_matrix
		
		
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
		
		# Create a FrameInfo object
		frameInfo = FrameInfo(self, self.shader, self.projection_matrix)
		
		# Render our actors
		for actor in self.actors:
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
	def __init__(self, stage, shader, projection_matrix):
		self.stage = stage
		self.frameFinishTime = stage.frameFinishTime
		self.shader = shader
		self.projection_matrix = projection_matrix
