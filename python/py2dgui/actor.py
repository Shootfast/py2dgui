from OpenGL.GL import   glDrawArrays,			  \
						GL_TRIANGLES,			  \
						glVertexAttribPointer,	 \
						glEnableVertexAttribArray, \
						glDisableVertexAttribArray,\
						glGetAttribLocation,	   \
						GL_FLOAT,				  \
						shaders,                  \
						glGetUniformLocation,     \
						glUniform2f
						
						
from OpenGL.arrays import vbo   
from numpy import array

from py2dgui.base import Point, Color
from math import sin, cos


						
class Actor(object):
	def __init__(self, points, colors=[], color=Color(0.5, 0.5, 0.5, 1.0)):
		
		self.points = points
		self.colors = colors
				
		# Default color
		self.default_color = color
		
		# Is the VBO ready to render with current data
		self.ready = False
	
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
		
		
	def updateVBO(self):
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
			
	
	
	
	def render(self, frameInfo):
		'''
		Render this Actor (to be called by stage!)
		'''
		# Check if this object has been setup yet
		if not self.ready:
			self.updateVBO()
			
		shader = frameInfo.shader
			
		# Load our shader
		shaders.glUseProgram(shader)
		
		self.vbo.bind()
		try:
			
			# Get our shader entry points
			self.position_location = glGetAttribLocation(shader, 'position')
			self.color_location = glGetAttribLocation(shader, 'color')
			self.position_offset_location = glGetUniformLocation(shader, "offset");
			
			# Enable any vertex attribute arrays
			glEnableVertexAttribArray(self.position_location)
			glEnableVertexAttribArray(self.color_location)
			
			# colorOffset is sizeof float (4) * floats per point (4) * num of points (vbo/2)
			colorOffset = 4 * 4 * (len(self.vbo) / 2) 
						
			# Set the Attribute pointers			
			glVertexAttribPointer(self.position_location, 4, GL_FLOAT, False, 0, self.vbo)
			glVertexAttribPointer(self.color_location, 4, GL_FLOAT, False, 0, self.vbo + colorOffset)
			
			# Compute object offset and apply to uniform
			xOffsetX, yOffset = self.computePositionOffsets(frameInfo.stage.getElapsedTime())
			glUniform2f(self.position_offset_location, xOffsetX, yOffset)
			
			glDrawArrays(GL_TRIANGLES, 0, len(self.vbo) / 2)
			
			glDisableVertexAttribArray(self.position_location)
			glDisableVertexAttribArray(self.color_location)
		finally:
			self.vbo.unbind()
			#glDisableClientState(GL_VERTEX_ARRAY)
		
		# Unload our shader
		shaders.glUseProgram(0)


	def computePositionOffsets(self, elapsedTime):
		'''
		Compute X,Y position offsets for the vertex shader
		'''
		loopDuration = 5.0
		scale = 3.14159 * 2.0 / loopDuration;
		
		currTimeThroughLoop = float(elapsedTime) % loopDuration
		
		xOffset = cos(currTimeThroughLoop * scale) * 0.5;
		yOffset = sin(currTimeThroughLoop * scale) * 0.5;
		
		return xOffset, yOffset
