from OpenGL.GL import   shaders,                      \
						GL_VERTEX_SHADER,             \
						GL_FRAGMENT_SHADER,           \
						glVertexAttribPointer,	      \
						glEnableVertexAttribArray,    \
						glDisableVertexAttribArray,   \
						glGetAttribLocation,	      \
						GL_FLOAT,				      \
						glGetUniformLocation,         \
						glUniformMatrix4fv,           \
						glUniform4fv,                 \
						glUniform1i,                  \
						GL_TRUE,                      \
						glBindTexture,                \
						GL_TEXTURE_2D



class BaseShader(object):
	'''
	A base class for Shaders
	'''
	# Default name
	name = None
	
	def __init__(self,  vertex, fragment):
				
		# Compile the Vertex Shader
		VERTEX_SHADER = shaders.compileShader(vertex, GL_VERTEX_SHADER)
		# Compile the Fragment Shader
		FRAGMENT_SHADER = shaders.compileShader(fragment, GL_FRAGMENT_SHADER)
		# Join them as the shader program
		self.program = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)
		
	def setup(self, actor):
		'''
		Calls that should happen before any drawing
		'''
		raise NotImplementedError
		
	def cleanup(self, actor):
		'''
		Calls that should happen after any drawing
		'''
		raise NotImplementedError


class PrimitiveShader(BaseShader):
	'''
	A shader for PrimitiveActors
	'''
	# Shader name (should match actorname attribute of actor instance)
	name = 'primitive'
	
	# Vertex shader for primitiveActors
	primitiveVertex = """
#version 330

layout (location = 0) in vec4 position;
layout (location = 1) in vec4 color;

smooth out vec4 theColor;

uniform mat4 modelToCameraMatrix;
uniform mat4 projectionMatrix;



void main()
{
	// Apply the model to camera matrix
	vec4 cameraPosition = modelToCameraMatrix * position;
	
	// Then apply the projection Matrix
	gl_Position = projectionMatrix * cameraPosition;
	
	// Pass on the color value
	theColor = color;
}
"""
	# Fragment shader for primitiveActors
	primitiveFragment = """
#version 330

smooth in vec4 theColor;

out vec4 outputColor;

void main()
{
   outputColor = theColor;
}
"""

	# Constructor
	def __init__(self):
		super(PrimitiveShader, self).__init__(PrimitiveShader.primitiveVertex, PrimitiveShader.primitiveFragment)
		
		# Get our shader entry points
		self.attrib_position           = glGetAttribLocation(self.program, 'position')
		self.attrib_color              = glGetAttribLocation(self.program, 'color')
		self.uniform_modelCamera       = glGetUniformLocation(self.program, 'modelToCameraMatrix')
		self.uniform_projection        = glGetUniformLocation(self.program, 'projectionMatrix')
		
		
	def setup(self, actor):
		'''
		Setup the shader uniforms / attributes.
		Assumes actor.vbo is already bound
		'''
		# Bind the shader
		shaders.glUseProgram(self.program)

		# Enable vertex attribute arrays
		glEnableVertexAttribArray(self.attrib_position)
		glEnableVertexAttribArray(self.attrib_color)
			
		# colorOffset is sizeof float (4) * floats per point (4) * num of points (vbo/2)
		colorOffset = 4 * 4 * (len(actor.vbo) / 2) 

		# Set the Attribute pointers			
		glVertexAttribPointer(self.attrib_position, 4, GL_FLOAT, False, 0, actor.vbo)
		glVertexAttribPointer(self.attrib_color,    4, GL_FLOAT, False, 0, actor.vbo + colorOffset)

		# Apply uniforms
		glUniformMatrix4fv(self.uniform_modelCamera, 1, GL_TRUE, actor.modelCamera_matrix)
		glUniformMatrix4fv(self.uniform_projection, 1, GL_TRUE, actor.projection_matrix)
		
		
	def cleanup(self):
		'''
		Cleans up after the shader has been used
		'''
		glDisableVertexAttribArray(self.attrib_position)
		glDisableVertexAttribArray(self.attrib_color)
		
		# Unbind the shader
		shaders.glUseProgram(0)





class TextShader(BaseShader):
	'''
	A shader for freetype text atlas'
	'''
	
	# Shader name (should match actorname attribute of actor instance)
	name = 'text'
	
	# Vertext shader for text
	textVertex = """
#version 330
 
layout (location = 0) in vec4 position;

out vec2 texpos;
uniform mat4 modelToCameraMatrix;
uniform mat4 projectionMatrix;
 
void main()
{
  //Split the position vec4 into its 2 parts
  vec4 p = vec4(position.xy,0,1);
  
  // Apply the model to camera matrix
  vec4 p2 = modelToCameraMatrix * p;
  
  // Then apply the projection Matrix 
  gl_Position = projectionMatrix * p2;
  
  texpos = position.zw;
}
"""
	# Fragment shader for text
	textFragment = """
#version 330
 
in vec2 texpos;
uniform sampler2D tex;
uniform vec4 color;
 
void main() 
{
  gl_FragColor = vec4(1, 1, 1, texture2D(tex, texpos).a) * color;
  //gl_FragColor = color;
}
"""
	# Constructor
	def __init__(self):
		super(TextShader, self).__init__(TextShader.textVertex, TextShader.textFragment)
		
		# Get our shader entry points
		self.attrib_position         = glGetAttribLocation(self.program, 'position')
		self.uniform_modelCamera     = glGetUniformLocation(self.program, 'modelToCameraMatrix')
		self.uniform_projection      = glGetUniformLocation(self.program, 'projectionMatrix')
		self.uniform_color           = glGetUniformLocation(self.program, 'color')
		self.uniform_tex             = glGetUniformLocation(self.program, 'tex')


	def setup(self, actor):
		'''
		Setup the shader uniforms / attributes.
		Assumes actor.vbo is already bound
		'''
		# Bind the shader
		shaders.glUseProgram(self.program)
		
		# Enable vertex attribute array
		glEnableVertexAttribArray(self.attrib_position)
		
		# Set the Attribute pointer
		glVertexAttribPointer(self.attrib_position, 4, GL_FLOAT, False, 0, actor.vbo)
		
		# Apply Uniforms
		glUniformMatrix4fv(self.uniform_modelCamera, 1, GL_TRUE, actor.modelCamera_matrix)
		glUniformMatrix4fv(self.uniform_projection, 1, GL_TRUE, actor.projection_matrix)
		glUniform4fv(self.uniform_color, 1, actor.color.data)
		glUniform1i(self.uniform_tex, 0)
		
		# Bind to the correct texture
		glBindTexture(GL_TEXTURE_2D, actor.atlas.texid)
		
		
		
		
	def cleanup(self):
		'''
		Cleans up after the shader has been used
		'''
		glDisableVertexAttribArray(self.attrib_position)
		
		# Unbind the shader
		shaders.glUseProgram(0)
		
		
shaderlist = [PrimitiveShader, TextShader]