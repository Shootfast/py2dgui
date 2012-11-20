from OpenGL.GL import   glDrawArrays,			      \
						GL_TRIANGLES,			      \
						glVertexAttribPointer,	      \
						glEnableVertexAttribArray,    \
						glDisableVertexAttribArray,   \
						glGetAttribLocation,	      \
						GL_FLOAT,				      \
						glGetUniformLocation,         \
						glUniformMatrix4fv,           \
						GL_TRUE
						
						
from OpenGL.arrays import vbo   
from numpy import array

from py2dgui.base import Point, Color
from math import sin, cos


						
class Actor(object):
	def __init__(self, points, colors=[], color=Color(0.5, 0.5, 0.5, 1.0)):
		
		# list of points
		self._points = points
		# list of colors
		self._colors = colors
				
		# Default color
		self.default_color = color
		
		# Is the VBO ready to render with current data
		self.ready = False
		
		self._translation = Point()
		self._rotation = Point()		
		self._scale = Point(1,1,1)
		
		# Child actors
		self.children = []
		
	
	@property
	def points(self):
		'''
		Get the verticies for this object
		'''
		return self._points
	
	@points.setter
	def points(self, value):
		'''
		Set the verticies for this object
		'''
		self._points = value
		self.ready = False
		
	@property
	def colors(self):
		'''
		Get the colors for this object
		'''
		return self._colors

	@colors.setter
	def colors(self, value):
		'''
		Set the colors for this object
		'''
		self._colors = value
		self.ready = False
		
		
	def translate(self, value):
		self._translation += value
		
	def getTranslation(self):
		return self._translation
		
	def rotate(self, value):
		self._rotation += value
		
	def getRotation(self):
		return self._rotation
	
	def scale(self, value):
		self._scale += value
	
	def getScale(self):
		return self._scale
		
	def addChild(self, child):
		self.children.append(child)
		
	def removeChild(self, child):
		if child in self.children:
			self.children.remove(child)
			
		
	def _updateVBO(self):
		'''
		Update the data in the VBO for this object
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
				
		# Assign VBO
		self.vbo = vbo.VBO(
						   array(a, 'f')
						   )
		# Setup is complete
		self.ready = True 
			
	
	
	
	def _render(self, stage, matrixstack):
		'''
		Render this Actor (to be called by stage!)
		'''
		# Check if this object has been setup yet
		if not self.ready:
			self._updateVBO()
				
		# Push the current state of the matrix stack before we start changing things
		matrixstack.push()
		
		# Apply transformations
		matrixstack.translate(self.getTranslation())
		matrixstack.rotatex(self.getRotation().x)
		matrixstack.rotatey(self.getRotation().y)
		matrixstack.rotatez(self.getRotation().z)
		matrixstack.scale(self.getScale())	
		
		
		# Calculate the camera2model matrix for this actor
		modelCameraMatrix = matrixstack.top()
			
		# Render ourselves
		self.vbo.bind()
		try:
			
			# Get our shader entry points
			positionAttrib           = glGetAttribLocation(stage.shader, 'position')
			colorAttrib              = glGetAttribLocation(stage.shader, 'color')
			modelCameraMatrixUniform = glGetUniformLocation(stage.shader, 'modelToCameraMatrix');
						
			# Enable any vertex attribute arrays
			glEnableVertexAttribArray(positionAttrib)
			glEnableVertexAttribArray(colorAttrib)
			
			# colorOffset is sizeof float (4) * floats per point (4) * num of points (vbo/2)
			colorOffset = 4 * 4 * (len(self.vbo) / 2) 
						
			# Set the Attribute pointers			
			glVertexAttribPointer(positionAttrib, 4, GL_FLOAT, False, 0, self.vbo)
			glVertexAttribPointer(colorAttrib,    4, GL_FLOAT, False, 0, self.vbo + colorOffset)
						
			# Apply uniforms
			glUniformMatrix4fv(modelCameraMatrixUniform, 1, GL_TRUE, modelCameraMatrix);
			
			glDrawArrays(GL_TRIANGLES, 0, len(self.vbo) / 2)
			
			glDisableVertexAttribArray(positionAttrib)
			glDisableVertexAttribArray(colorAttrib)
			
		finally:
			self.vbo.unbind()
			
			
		# Then render our children
		for child in self.children:
			child._render(stage, matrixstack)

			
		# Pop the matrix stack back to what it was
		matrixstack.pop()
		pass


	def computePositionOffsets(self, elapsedTime):
		'''
		Compute X,Y position offsets for the vertex shader
		'''
		loopDuration = 5.0
		scale = 3.14159 * 2.0 / loopDuration;
		
		currTimeThroughLoop = float(elapsedTime) % loopDuration
		
		xOffset = cos(currTimeThroughLoop * scale) * 100.0;
		yOffset = sin(currTimeThroughLoop * scale) * 100.0;
		zOffset = 0
		
		return xOffset, yOffset, zOffset
