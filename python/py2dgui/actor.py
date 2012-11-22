from OpenGL.GL import   glDrawArrays,			      \
						glBufferData,                 \
						glBindTexture,                \
						glTexImage2D,                 \
						glPixelStorei,                \
						glTexParameteri,              \
						glActiveTexture,              \
						glGenTextures,                \
						GL_TEXTURE0,                  \
						GL_TRIANGLES,		          \
						GL_ARRAY_BUFFER,              \
						GL_TEXTURE_2D,                \
       					GL_UNPACK_ALIGNMENT,          \
       					GL_UNSIGNED_BYTE,             \
       					GL_TEXTURE_MIN_FILTER,        \
       					GL_TEXTURE_MAG_FILTER,        \
       					GL_LINEAR,                    \
       					GL_RGB,                       \
       					GL_RGBA
				
									
from OpenGL.arrays import vbo   
from numpy import array

import Image

from py2dgui.base import Point, Color
from py2dgui.atlas import Atlas
#from OpenGL.raw.GL.annotations import glGenTextures




						
class BaseActor(object):
	'''
	Base for all actor instances to build from
	'''
	
	# Actortype (used to determine shader)
	actortype = None
	
	def __init__(self):
		
		# Place holder for VBO object
		self.vbo = None
		
		# Is the VBO ready to render with current data
		self.ready = False
		
		# Transformation values
		self._translation = Point()
		self._rotation = Point()		
		self._scale = Point(1,1,1)
		
		# Matrix from model to camera (provided in _render)
		self.matrixStack = None
		self.modelCameraMatrix = None
		
		# Projection matrix
		self.projection_matrix = None
		
		# Child actors
		self.children = []
		
		# Safety flags
		self.preRenderRan = False
		self.postRenderRan = True
		
		
	def translate(self, value):
		self._translation = value
		
	def getTranslation(self):
		return self._translation
		
	def rotate(self, value):
		self._rotation = value
		
	def getRotation(self):
		return self._rotation
	
	def scale(self, value):
		self._scale = value
	
	def getScale(self):
		return self._scale
		
	def addChild(self, child):
		self.children.append(child)
		
	def removeChild(self, child):
		if child in self.children:
			self.children.remove(child)
			
		
	def _assignVBO(self, a):
		'''
		Assign the data in the VBO for this object
		'''
			
		# Assign VBO
		self.vbo = vbo.VBO(
						   array(a, 'f')
						   )
		# Setup is complete
		self.ready = True 
			
	def _prerender(self, stage, projection_matrix, matrixStack):
		'''
		Sets up the OpenGL environment to render this actor
		returns the shader used
		'''
		# Check flags
		if self.postRenderRan != True:
			raise Exception("_postrender was not called after previous _render")
		# reset flag for postrender
		self.postRenderRan = False
		
		# Check if this object has been setup yet
		if not self.ready:
			raise Exception("_render called before _assignVBO")
				
		# Push the current state of the matrix stack before we start changing things
		self.matrixStack = matrixStack 
		self.matrixStack.push()
		
		# Apply transformations
		self.matrixStack.translate(self.getTranslation())
		self.matrixStack.rotatex(self.getRotation().x)
		self.matrixStack.rotatey(self.getRotation().y)
		self.matrixStack.rotatez(self.getRotation().z)
		self.matrixStack.scale(self.getScale())	
		
		# Calculate the camera2model matrix for this actor
		self.modelCamera_matrix = self.matrixStack.top()
		
		# Assign the projection matrix
		self.projection_matrix = projection_matrix
		
		# Get the correct shader from the stage
		shader = stage.getShader(self.actortype)
		
		# Bind the VBO 
		self.vbo.bind()
		
		# Run the setup for the shader
		shader.setup(self)
		
		# set this flag to say the prerender ran
		self.preRenderRan = True
		
		return shader


	def _render(self, stage, projection_matrix, modelCamera_matrix):
		'''
		Render this Actor
		(should be overridden by child classes)
		'''
		raise NotImplementedError
		
		
	def _postrender(self, stage, shader):
		'''
		Cleans up the OpenGL environment after rendering this actor
		'''
		#Check flags
		if self.preRenderRan == False:
			raise Exception("_prerender was not called before _render")
		# reset flag
		self.preRenderRan = False			
	
		shader.cleanup()
		
		self.vbo.unbind()	
			
		# Render children
		for child in self.children:
			child._render(stage, self.projection_matrix, self.matrixStack)
			
		# Pop the matrix stack back to what it was
		self.matrixStack.pop()
		
		# Set this flag to say the postrender ran
		self.postRenderRan = True




class PrimitiveActor(BaseActor):
	'''
	Actor for primitive shapes
	'''
	# Actortype (used to determine shader)
	actortype = 'primitive'
	
	def __init__(self, points, colors=[], color=Color(0.5, 0.5, 0.5, 1.0)):
		super(PrimitiveActor, self).__init__()
		
		# list of points
		self.points = points
		# list of colors
		self.colors = colors
				
		# Default color
		self.default_color = color
		
		# Assign the VBO
		self._assignVBO()
		

	def _assignVBO(self):
		'''
		Assign the data in the VBO for this object
		'''
		# array to build for vbo 
		a = []
		
		# First add the vertex points
		for point in self.points:
			if not isinstance(point, Point):
				raise Exception("Non Point object found")
			a.append(point.data)
		
		# Then add the colors
		if self.colors != []:
			if len(self.colors) > len(self.points):
				raise Exception("Too many colors provided")
			for color in self.colors:
				if not isinstance(color, Color) or not isinstance(color, Point):
					raise Exception("None Color object found")
				a.append(color.data)
				
		# For any missing colors, apply the default color
		for color in xrange(len(self.points) - len(self.colors)):
			a.append(self.default_color.data)
		
		# Call the base method
		super(PrimitiveActor, self)._assignVBO(a)
		
	
	def _render(self, stage, projection_matrix, modelCamera_matrix):
		# Run the pre-render
		shader = super(PrimitiveActor, self)._prerender(stage, projection_matrix, modelCamera_matrix)
		
		# Render
		glDrawArrays(GL_TRIANGLES, 0, len(self.vbo) / 2)
		
		# Post render
		super(PrimitiveActor, self)._postrender(stage, shader)
		



class Group(BaseActor):
	'''
	Actor for groups of other actors
	'''	
	actortype = 'group'

	def _render(self, stage, projection_matrix, modelCamera_matrix):
		
		# Set the modelCamera_matrix
		self.matrixStack = modelCamera_matrix 
		self.matrixStack.push()
		
		# Apply transformations
		self.matrixStack.translate(self.getTranslation())
		self.matrixStack.rotatex(self.getRotation().x)
		self.matrixStack.rotatey(self.getRotation().y)
		self.matrixStack.rotatez(self.getRotation().z)
		self.matrixStack.scale(self.getScale())	
		
		# Calculate the camera2model matrix for this actor
		self.modelCamera_matrix = self.matrixStack.top()
		
		# Assign the projection matrix
		self.projection_matrix = projection_matrix
		
		# Render children
		for child in self.children:
			child._render(stage, self.projection_matrix, self.matrixStack)
			
		# Pop the matrix stack back to what it was
		self.matrixStack.pop()

		

	
class TextActor(BaseActor):
	'''
	Actor for text
	'''
	# Actortype (used to determine shader)
	actortype = 'text'
	
	
	def __init__(self, fontfile, size, text="", color=Color(1, 1, 1, 1)):
		super(TextActor, self).__init__()
		
		# Text to render
		self.text = text
				
		# Text color
		self.color = color
		
		# Create an OpenGL bitmap texture atlas of ascii glyphs  
		self.atlas = Atlas(fontfile, size)
		
		a = self._getVertexData()		
		# Assign the VBO
		super(TextActor, self)._assignVBO(a)
		
	
		
	def _getVertexData(self):
		'''
		Get the vertex data for this object
		'''
				
		a = self.atlas
		# All text objects are made at the origin
		x = 0
		y = 0
				
		coords = []
		for p in self.text:
			# Get char positions from charinfo
			x2 = float(x) +  a.c[p].bl
			y2 = float(-y) - a.c[p].bt
			w = a.c[p].bw
			h = a.c[p].bh
			
			# Advance cursor to the start of the next character
			x += a.c[p].ax
			y += a.c[p].ay
			
			# Skip glyphs that have no pixels
			if w == 0 or h == 0:
				continue
			
			# Create points X, Y, Z, W
			# X and Y are for the quad, Z/W are for the texture map
			# These are split up in the vertex shader
			# There are 6 points here, to make 2 tris 
			coords.extend([x2    , -y2    , a.c[p].tx                           , a.c[p].ty            ]) 
			coords.extend([x2 + w, -y2    , a.c[p].tx + (a.c[p].bw / float(a.w)), a.c[p].ty            ])
			coords.extend([x2    , -y2 - h, a.c[p].tx						    , a.c[p].ty + (a.c[p].bh / a.h)])
			coords.extend([x2 + w, -y2    , a.c[p].tx + (a.c[p].bw / float(a.w)), a.c[p].ty           ])
			coords.extend([x2    , -y2 - h, a.c[p].tx						    , a.c[p].ty + (a.c[p].bh / a.h)])
			coords.extend([x2 + w, -y2 - h, a.c[p].tx + (a.c[p].bw / float(a.w)), a.c[p].ty + (a.c[p].bh / a.h)])
			
		return coords
				

		
	def _render(self, stage, projection_matrix, modelCamera_matrix):
		# Run the pre-render
		shader = super(TextActor, self)._prerender(stage, projection_matrix, modelCamera_matrix)
		
		# Update the values in the VBO
		a = self._getVertexData()
		self.vbo.set_array(array(a, 'f'))
		
		# Render
		glDrawArrays(GL_TRIANGLES, 0, len(self.vbo) / 4)
		
		# Post render
		super(TextActor, self)._postrender(stage, shader)

		
class ImageActor(BaseActor):
	'''
	Actor for image billboards
	'''
	# Actortype (used to determine shader)
	actortype = 'image'
	
	def __init__(self, imagefile, points=[], alpha=1.0):
		super(ImageActor, self).__init__()
		
		im = Image.open(imagefile)
		# Try to open the image file
		try:
			ix, iy, image = im.size[0], im.size[1], im.tostring("raw", "RGBA", 0, -1)
		except SystemError:
			ix, iy, image = im.size[0], im.size[1], im.tostring("raw", "RGBX", 0, -1)
		
		# get a texture buffer	
		glActiveTexture(GL_TEXTURE0) 
		self.texid = glGenTextures(1)
		# Bind the texture
		glBindTexture(GL_TEXTURE_2D, self.texid)
		glPixelStorei(GL_UNPACK_ALIGNMENT,1)
		
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		
		# Upload the image
		glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
		
		# Generate the points for the billboard
		if points == []:
			points = [Point(0,iy), Point(ix,iy), Point(ix,0), Point(0,0)]
		if len(points) != 4:
			raise Exception("Image needs 4 points, %d provided" % len(points))
		
		# Generate the UV map
		uv = [Point(0,1), Point(1,1), Point(1,0), Point(0,0)]
		
		a = []
		for i in [0,1,2,0,2,3]:
			point = points[i]
			tex = uv[i]
			a.extend([point.x, point.y, tex.x, tex.y])
		
		# Assign the VBO
		super(ImageActor, self)._assignVBO(a)
		
		self.alpha = float(alpha)
		
	
	
	def _render(self, stage, projection_matrix, modelCamera_matrix):
		# Run the pre-render
		shader = super(ImageActor, self)._prerender(stage, projection_matrix, modelCamera_matrix)
		
		# Render
		glDrawArrays(GL_TRIANGLES, 0, len(self.vbo) / 2)
		
		# Post render
		super(ImageActor, self)._postrender(stage, shader)

		
		
