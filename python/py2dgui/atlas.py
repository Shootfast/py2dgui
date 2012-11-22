from freetype import Face, FT_LOAD_RENDER

from OpenGL.GL import 	glActiveTexture,          \
						 GL_TEXTURE0,             \
						 GL_TEXTURE_2D,           \
						 GL_ALPHA,                \
						 GL_LINEAR,               \
						 GL_UNSIGNED_BYTE,        \
						 glBindTexture,           \
						 glGenTextures,           \
						 glTexImage2D,            \
						 glTexSubImage2D,         \
						 glPixelStorei,           \
						 GL_UNPACK_ALIGNMENT,     \
						 glTexParameteri,         \
						 GL_TEXTURE_WRAP_S,       \
						 GL_TEXTURE_WRAP_T,       \
						 GL_CLAMP_TO_EDGE,        \
						 GL_TEXTURE_MIN_FILTER,   \
						 GL_TEXTURE_MAG_FILTER
						
						
						

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
	
	
		## Create texture to hold ASCII glyphs
		
		# Ensure no texture is currently selected
		glActiveTexture(GL_TEXTURE0) 
		self.texid = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, self.texid)
		
		glTexImage2D(GL_TEXTURE_2D, 0, GL_ALPHA, self.w, self.h, 0, GL_ALPHA, GL_UNSIGNED_BYTE, 0)
		
		# We require 1 byte alignment when uploading texture data
		glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
		
		# Clamping to edges is important to prevent artifacts when scaling
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
		
		# Linear filtering looks better for text
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
		glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
		
	
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
			
			glTexSubImage2D(GL_TEXTURE_2D, 0, ox, oy, bitmap.width, bitmap.rows, GL_ALPHA, GL_UNSIGNED_BYTE, bitmap.buffer)
			
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

		
