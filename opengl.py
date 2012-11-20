#!/usr/bin/env python

import numpy
from freetype import *
import OpenGL.GL as gl
import OpenGL.GLUT as glut
from OpenGL.arrays import vbo
from OpenGL.GL import shaders

vertex = """
#version 120
 
attribute vec4 coord;
varying vec2 texpos;
 
void main(void) {
  gl_Position = vec4(coord.xy, 0, 1);
  texpos = coord.zw;
}
"""

fragment = """
#version 120
 
varying vec2 texpos;
uniform sampler2D tex;
uniform vec4 color;
 
void main(void) {
  gl_FragColor = vec4(1, 1, 1, texture2D(tex, texpos).a) * color;
}
"""



class Atlas(object):
	def __init__(self, filename, size):
		# Size of the atlas texture
		self.w = 0
		self.h = 0
		
		# GL id assigned to texture buffer
		self.texid = 0
		
		# Font details
		self.filename = filename
		self.size = size
		
		# Dictionary of char to CharInfo objects
		self.c = {}
		self.setup()
		
	def setup(self):
		'''
		Construct the texture atlas for the font
		'''
		face = Face(self.filename)
		face.set_pixel_sizes(0, self.size)
	
		rowh, roww = 0,0
		
		# Determine image size
		for i in xrange(32,128):
			face.load_char( chr(i), FT_LOAD_RENDER)
			bitmap	= face.glyph.bitmap
			
			if roww + bitmap.width + 1 >= 1024: # max texture width
				self.w  = max(self.w, roww)
				self.h	+= rowh
				roww = 0
				rowh = 0
			roww += bitmap.width + 1
			rowh = max(rowh, bitmap.rows)
			
		self.w = max(self.w, roww)
		self.h += rowh
	
		# Use the shader
		gl.glUseProgram(shader)
		
		## Create texture to hold ASCII glyphs
		
		# Ensure no texture is currently selected
		gl.glActiveTexture(gl.GL_TEXTURE0) 
		self.texid = gl.glGenTextures(1)
		gl.glBindTexture(gl.GL_TEXTURE_2D, self.texid)
		
		# Change tex color to black
		texUniform = gl.glGetUniformLocation(shader, 'tex')
		gl.glUniform1i(texUniform, 0)
		
		gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_ALPHA, self.w, self.h, 0, gl.GL_ALPHA, gl.GL_UNSIGNED_BYTE, 0)
		
		# We require 1 byte alignment when uploading texture data
		gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
		
		# Clamping to edges is important to prevent artifacts when scaling
		gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
		gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
		
		# Linear filtering looks better for text
		gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
		gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
		
	
		# Add glyphs to texture
		ox = 0
		oy = 0
		rowh = 0
		
		# class to hold data
		class CharInfo:
			pass
		
		for i in xrange(32,128):
			face.load_char( chr(i), FT_LOAD_RENDER)
			g = face.glyph
			bitmap = g.bitmap
			
			if ox + bitmap.width + 1 >= 1024: # max texture width
				oy += rowh
				rowh = 0
				ox = 0		
			
			gl.glTexSubImage2D(gl.GL_TEXTURE_2D, 0, ox, oy, bitmap.width, bitmap.rows, gl.GL_ALPHA, gl.GL_UNSIGNED_BYTE, bitmap.buffer)
			
			ci = CharInfo()
			ci.ax = float(g.advance.x >> 6)
			ci.ay = float(g.advance.y >> 6)
			
			ci.bw = float(bitmap.width)
			ci.bh = float(bitmap.rows)
			
			ci.bl = float(g.bitmap_left)
			ci.bt = float(g.bitmap_top)
			
			ci.tx = float(ox) / float(self.w)
			ci.ty = float(oy) / float(self.h)
			self.c[chr(i)] = ci
			
			rowh = max(rowh, bitmap.rows)
			ox += bitmap.width + 1

		# Finish using the shader
		gl.glUseProgram(0)
		
		print "Generated a %d x %d (%d kb) texture atlas" % (self.w, self.h, self.w * self.h / 1024)
		
		
# globals
freesans48 = None
liberationSerif48 = None
liberationMono48 = None


shader = None
myvbo = None
width = 640
height = 480



def init():
	gl.glEnable(gl.GL_BLEND)
	gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
	
	global shader
	VERTEX_SHADER = shaders.compileShader(vertex, gl.GL_VERTEX_SHADER)
	FRAGMENT_SHADER = shaders.compileShader(fragment, gl.GL_FRAGMENT_SHADER)
	shader = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)
	
	global myvbo
	myvbo = vbo.VBO(numpy.array([], 'f'))
	
	global freesans48
	global liberationSerif48
	global liberationMono48
	
	freesans48 = Atlas('./fonts/FreeSans.ttf', 48)
	liberationSerif48 = Atlas('./fonts/LiberationSerif-Regular.ttf', 48)
	liberationMono48 = Atlas('./fonts/LiberationMono-Regular.ttf', 48)
	

def display():
	sx = 2.0 / float(width)
	sy = 2.0/ float(height)
	
	gl.glUseProgram(shader)
	
	# White background
	gl.glClearColor(1, 1, 1, 1)
	gl.glClear(gl.GL_COLOR_BUFFER_BIT)
		
	colorUniform = gl.glGetUniformLocation(shader, 'color')
	texUniform   = gl.glGetUniformLocation(shader, 'tex')
	coordAttrib  = gl.glGetAttribLocation(shader, 'coord')
	
	# Set text color to black
	gl.glUniform4fv(colorUniform, 1, [0.0, 0.0, 0.0, 1.0])
	gl.glUniform1i(texUniform, 0)
	
	myvbo.bind()
	try:
		gl.glEnableVertexAttribArray(coordAttrib)
		gl.glVertexAttribPointer(coordAttrib, 4, gl.GL_FLOAT, False, 0, myvbo)
		
		render_text("The Quick Brown Fox Jumps Over The Lazy Dog", freesans48, -1 + 8 * sx,   1 - 50 * sy,    sx, sy)
		render_text("The Quick Brown Fox Jumps Over The Lazy Dog", liberationSerif48, -1 + 8 * sx,   1 - 100 * sy,    sx, sy)
		render_text("The Quick Brown Fox Jumps Over The Lazy Dog", liberationMono48, -1 + 8 * sx,   1 - 150 * sy,    sx, sy)
		
		gl.glDisableVertexAttribArray(coordAttrib)
	
	finally:
		myvbo.unbind()
		
	gl.glUseProgram(0)
	
	glut.glutSwapBuffers()
	
	
def resize( w, h ):
	global width, height
	width = w
	height = h
	gl.glViewport(0, 0, width, height)
	

def render_text(text, atlas, x, y, sx, sy):
	# Bind to the correct texture
	gl.glBindTexture(gl.GL_TEXTURE_2D, atlas.texid)
	a = atlas
	
	coords = []
	for p in text:
		# Get char positions from charinfo
		x2 = float(x) +  a.c[p].bl * float(sx)
		y2 = float(-y) - a.c[p].bt * float(sy)
		w = a.c[p].bw * float(sx)
		h = a.c[p].bh * float(sy)
		
		# Advance cursor to the start of the next character
		x += a.c[p].ax * float(sx)
		y += a.c[p].ay * float(sy)
		
		# Skip glyphs that have no pixels
		if w == 0 or h == 0:
			continue
			
		coords.extend([x2    , -y2    , a.c[p].tx                           , a.c[p].ty            ]) 
		coords.extend([x2 + w, -y2    , a.c[p].tx + (a.c[p].bw / float(a.w)), a.c[p].ty            ])
		coords.extend([x2    , -y2 - h, a.c[p].tx						    , a.c[p].ty + (a.c[p].bh / a.h)])
		coords.extend([x2 + w, -y2    , a.c[p].tx + (a.c[p].bw / float(a.w)), a.c[p].ty           ])
		coords.extend([x2    , -y2 - h, a.c[p].tx						    , a.c[p].ty + (a.c[p].bh / a.h)])
		coords.extend([x2 + w, -y2 - h, a.c[p].tx + (a.c[p].bw / float(a.w)), a.c[p].ty + (a.c[p].bh / a.h)])
		
	coordsarray = numpy.array(coords,'f')
	gl.glBufferData(gl.GL_ARRAY_BUFFER, len(coordsarray) * 4, coordsarray, gl.GL_DYNAMIC_DRAW)
	gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(coordsarray) / 4)
	
	

if __name__ == '__main__':
	import sys
	glut.glutInit(sys.argv)
	glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGBA | glut.GLUT_ALPHA )
	glut.glutInitWindowSize(width, height)
	glut.glutCreateWindow("Marks OpenGL Text test")
	init()
	
	
	glut.glutDisplayFunc(display)
	glut.glutReshapeFunc(resize)
	#glut.glutReshapeWindow(width, height)
	
	glut.glutMainLoop()
