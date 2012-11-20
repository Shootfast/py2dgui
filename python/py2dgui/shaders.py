
# Main vertex shader
vertex = """
#version 330

layout (location = 0) in vec4 position;
layout (location = 1) in vec4 color;

smooth out vec4 theColor;

uniform mat4 projectionMatrix;
uniform mat4 modelToCameraMatrix;


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

# Main fragment shader
fragment = """
#version 330

smooth in vec4 theColor;

out vec4 outputColor;

void main()
{
   outputColor = theColor;
}
"""

# Vertex shader with color
vertColor = """
#version 330

layout (location = 0) in vec4 position;
layout (location = 1) in vec4 color;

smooth out vec4 theColor;

void main()
{
	gl_Position = position;
	theColor = color;
}
"""

# Fragment shader taking color
fragColor = """
#version 330

smooth in vec4 theColor;

out vec4 outputColor;

void main()
{
	outputColor = theColor;
}"""