
# Main vertex shader
vertex = """
#version 330

layout (location = 0) in vec4 position;
layout (location = 1) in vec4 color;

uniform vec2 offset;

smooth out vec4 theColor;

void main()
{
	// Apply the position offset
	vec4 totalOffset = vec4(offset.x, offset.y, 0.0, 0.0);
	gl_Position = position + totalOffset;
	
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