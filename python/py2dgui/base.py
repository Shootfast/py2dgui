class Point(object):
	def __init__(self, x=0.0, y=0.0, z=0.0, w=1.0):
		self.data = [x,y,z,w]	
		
	def __setitem__(self, item, value):
		if int(item) > 3 or int(item) < 0:
			raise Exception("Index must be integer between 0 and 3")
		self.data[item] = value
	
	def __getitem__(self, item):
		return self.data[item]
		
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
	
	
