import numpy
import math
import copy


class Point(object):
	def __init__(self, x=0.0, y=0.0, z=0.0, w=1.0):
		self.data = numpy.array([x,y,z,w],'f')	
		
	def __setitem__(self, item, value):
		if int(item) > 3 or int(item) < 0:
			raise Exception("Index must be integer between 0 and 3")
		self.data[item] = value
	
	def __getitem__(self, item):
		return self.data[item] 
	
	def __add__(self, other):
		return Point(*self.data + other.data)
		
	def __sub__(self, other):
		return Point(*self.data - other.data)
		
	def __mul__(self, other):
		return Point(*self.data.dot(other.data))
		
	def __str__(self):
		return "Point X:%s Y:%s Z:%s W:%s" % (self.x, self.y, self.z, self.w)
		
	x = property(lambda self: self[0], lambda self, value: self.setitem(0, value))
	y = property(lambda self: self[1], lambda self, value: self.setitem(1, value))
	z = property(lambda self: self[2], lambda self, value: self.setitem(2, value))
	w = property(lambda self: self[3], lambda self, value: self.setitem(3, value))

	

class Color(Point):
	def __init__(self, r=0.0, g=0.0, b=0.0, a=1.0):
		super(Color, self).__init__(r,g,b,a)
		
	r = property(lambda self: self.x, lambda self, value: setattr(self,'x',value))
	g = property(lambda self: self.y, lambda self, value: setattr(self,'y',value))
	b = property(lambda self: self.z, lambda self, value: setattr(self,'z',value))
	a = property(lambda self: self.w, lambda self, value: setattr(self,'w',value))
	
	
	
class MatrixStack(object):
	def __init__(self):
		self.current = numpy.identity(4, 'f')
		self.stack = []
	
	def top(self):
		return self.current
	
	def rotatex(self, degree):
		'''
		Rotate matrix around X axis
		'''
		radians = math.radians(degree);
		cos = math.cos(radians);
		sin = math.sin(radians);

		matrix =  numpy.identity(4, 'f')
		matrix[1][1] = cos
		matrix[1][2] = -sin
		matrix[2][1] = sin 
		matrix[2][2] = cos	
		self.current = self.current.dot(matrix)
		
		
	def rotatey(self, degree):
		'''
		Rotate matrix around Y axis
		'''
		radians = math.radians(degree);
		cos = math.cos(radians);
		sin = math.sin(radians);

		matrix = numpy.identity(4, 'f')
		matrix[0][0] = cos
		matrix[0][2] = sin
		matrix[2][0] = -sin
		matrix[2][2] = cos;
		self.current = self.current.dot(matrix)
	
	
	def rotatez(self, degree):
		'''
		Rotate matrix around Z axis
		'''
		radians = math.radians(degree);
		cos = math.cos(radians);
		sin = math.sin(radians);

		matrix = numpy.identity(4, 'f')
		matrix[0][0] = cos 
		matrix[0][1] = -sin
		matrix[1][0] = sin 
		matrix[1][1] = cos
		self.current = self.current.dot(matrix)

		
	def scale(self, vector):
		'''
		Scale matrix by Vector
		'''
		matrix = numpy.identity(4, 'f')
		matrix[0][0] = vector[0]
		matrix[1][1] = vector[1]
		matrix[2][2] = vector[2]

		self.current = self.current.dot(matrix)


	def translate(self, vector):
		'''
		Translate matrix along vector
		'''
		matrix = numpy.identity(4, 'f')
		matrix[0][3] = vector[0]
		matrix[1][3] = vector[1]
		matrix[2][3] = vector[2]
		matrix[3][3] = 1.0
		self.current = self.current.dot(matrix)

				
	def push(self):
		matrix = copy.deepcopy(self.current)
		self.stack.insert(0, matrix)
		
	def pop(self):
		self.current = self.stack.pop(0)

