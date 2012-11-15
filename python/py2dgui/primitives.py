from py2dgui.actor import Actor
from py2dgui.base import Point, Color



class Triangle(Actor):
	def __init__(self, points=[], colors=[], *args, **kwargs):
		
		# Check points
		if points != []:
			if len(points) != 3:
				raise Exception("Triangle needs 3 points, %d provided" % len(points))
			
		# Set default points
		else:
			points = [
						Point(0.0, 50.0, -1.0),
						Point(-50.0, -36.6, -1.0),
						Point(50.0, -36.6, -1.0)
					]
			
		# Create the triangle
		super(Triangle, self).__init__(points, colors, *args, **kwargs)		
	

class Square(Actor):
	def __init__(self, points=[], colors=[], *args, **kwargs):
		
		# Check points
		if points != []:
			if len(points) != 4:
				raise Exception("Square needs 4 points, %d provided" % len(points))
			
		# Set default points
		else:
			points = [
						Point(-100.0, 100.0, -1.0),
						Point(100.0, 100.0, -1.0),
						Point(100.0, -100.0, -1.0),
						Point(-100.0, -100.0, -1.0),
					]
		
		
		# Convert the 4 outside points into 2 tris
		# TODO, replace this with a more general purpose algo
		p, c = [],[]
				
		for i in [0,1,2,0,2,3]:
			point = points[i]
			p.append(point)
			try:
				color = colors[i]
				c.append(color)
			except IndexError:
				pass
			
		# Create the square
		super(Square, self).__init__(p, c, *args, **kwargs)		
