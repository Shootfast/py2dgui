from py2dgui.shaders import shaderlist 
from py2dgui.base import MatrixStack

from OpenGL.GL import	GL_BLEND,               \
						GL_SRC_ALPHA,           \
						GL_ONE_MINUS_SRC_ALPHA, \
						glEnable,               \
						glBlendFunc
						
from time import time

from numpy import array

class Stage(object):
	'''
	Main object from which all other py2dgui objects are rendered
	'''
	def __init__(self, width=1, height=1):
		self.width = 1
		self.height = 1
		
		# Actors on this stage
		self.actors = []
		self.animations = []
		
		self.shaders = {}
		
		# Store current matrixes
		self.projection_matrix = None
		self.modelCamera_matrix = MatrixStack()
		
		# Time the stage was constructed
		self.startTime = time()
		
		self.fps = 0
		
		self.setup()
		self.resize(width, height)
		
		
	def setup(self):
		'''
		Setup the parts of the stage
		'''		
		# Ensure that transparency is enabled 
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		
		
	def getShader(self, shadername):
		'''
		Check each actor to see if its shader 
		'''
		# If we already have the shader loaded, return it
		if shadername in self.shaders.keys():
			return self.shaders[shadername]
		
		
		# Otherwise create a new instance of the shader
		for shader in shaderlist:
			if shader.name == shadername:
				s = shader()
				self.shaders[shadername] = s
				return self.shaders[shadername]
		
		# Shader could not be found, raise exception	
		raise Exception("Could not find shader that matched '%s'" % shadername)
		
		
	def addAnimation(self, animation):
		self.animations.append(animation)
		
				
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
		
		
	def addActor(self, actor):
		'''
		Add an actor to the stage
		'''
		if actor not in self.actors:
			self.actors.append(actor)
			
	def removeActor(self, actor):
		'''
		Remove an actor from the stage
		'''
		if actor in self.actors:
			self.actors.remove(actor)
			
	def clearStage(self):
		'''
		Remove all actors from the stage
		'''
		self.actors = []
		

	def render(self):
		'''
		Render all actors on the stage
		'''
		
		before = time()
		
		# Do our animations
		remove = []
		for animation in self.animations:
			if animation.complete == True:
				remove.append(animation)
				continue
			animation.update(time())
			
		# Remove any finished animations
		for i in remove:
			self.animations.remove(i)
							
		# Render our actors
		for actor in self.actors:
			actor._render(self, self.projection_matrix, self.modelCamera_matrix)
		after = time()
		
		# record the framerate
		framerate = after - before
		if framerate > 0:
			self.fps = 1.0 / framerate
		else:
			self.fps = 0 
		
