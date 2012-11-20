from py2dgui.shaders import vertex, fragment
from py2dgui.base import MatrixStack

from OpenGL.GL import   shaders,			    \
						GL_TRUE,                \
						GL_VERTEX_SHADER,	    \
						GL_FRAGMENT_SHADER,     \
						GL_BLEND,               \
						GL_SRC_ALPHA,           \
						GL_ONE_MINUS_SRC_ALPHA, \
						glEnable,               \
						glBlendFunc,            \
						glGetUniformLocation,   \
						glUniformMatrix4fv
						
from time import time

from numpy import array

class Stage(object):
	'''
	Main object from which all other py2dgui objects are rendered
	'''
	def __init__(self, width=1, height=1):
		self.width = 1
		self.height = 1
		
		self.actors = []
		
		self.shader = None
		self.projection_matrix = None
		self.modelCamera_matrix = MatrixStack()
		
		# Time the stage was constructed
		self.startTime = time()
		
		self.fps = 0
		self.frameFinishTime = 0
		
		self.setup()
		self.resize(width, height)
		
	def setup(self):
		'''
		Compile the shader programs
		'''
		
		# Compile the Vertex Shader
		VERTEX_SHADER = shaders.compileShader(vertex, GL_VERTEX_SHADER)
		# Compile the Fragment Shader
		FRAGMENT_SHADER = shaders.compileShader(fragment, GL_FRAGMENT_SHADER)
		# Join them as the shader program
		self.shader = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)
		
		# Ensure that transparency is enabled 
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		
		
	def getElapsedTime(self):
		'''
		Get the total elapsed time since stage was constructed
		'''
		return time() - self.startTime
		
	def resize(self, w, h):
		'''
		Set the size of the stage
		'''
		
		self.width = w
		self.height = h
		
		n = 0.5 # zNear
		f  = 3.0 # zFar
		
		self.projection_matrix = array([
									
				[ 2/float(w),     0,           0,            -1        ],
				[     0,      2/float(h),      0,            -1        ],
				[     0,          0,      -2/(f-n),          -1        ],
				[     0,          0,           0,             1        ]
										],'f')
		
		
	def add_actor(self, actor):
		'''
		Add an actor to the stage
		'''
		if actor not in self.actors:
			self.actors.append(actor)
			
			
	def clear_stage(self):
		'''
		Remove all actors from the stage
		'''
		self.actors = []
		

	def render(self):
		'''
		Render all actors on the stage
		'''
		before = time()
				
		# Load our shader
		shaders.glUseProgram(self.shader)
		
		# Set the projectionMatrix uniform
		projectionMatrixUniform = glGetUniformLocation(self.shader, 'projectionMatrix');
		glUniformMatrix4fv(projectionMatrixUniform, 1, GL_TRUE, self.projection_matrix);
		
		# Render our actors
		for actor in self.actors:
			actor._render(self, self.modelCamera_matrix)
		after = time()
		
		# Unload our shader
		shaders.glUseProgram(0)
		
		# record the framerate
		framerate = after - before
		self.fps = 1.0 / framerate 
		
		# Record frame finish time
		self.frameFinishTime = after
		
