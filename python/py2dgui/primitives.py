from py2dgui.actor import PrimitiveActor
from py2dgui.base import Point, Color



class Triangle(PrimitiveActor):
	def __init__(self, points=[], colors=[], *args, **kwargs):
		
		# Check points
		if points != []:
			if len(points) != 3:
				raise Exception("Triangle needs 3 points, %d provided" % len(points))
			
		# Set default points
		else:
			points = [
						Point(-50, -25),
						Point(25, 25),
						Point(50, -25)
					]
			
		# Create the triangle
		super(Triangle, self).__init__(points, colors, *args, **kwargs)		
	


class Square(PrimitiveActor):
	def __init__(self, points=[], colors=[], *args, **kwargs):
		
		# Check points
		if points != []:
			if len(points) != 4:
				raise Exception("Square needs 4 points, %d provided" % len(points))
			
		# Set default points
		else:
			points = [
						Point(-100.0, 100.0),
						Point(100.0, 100.0),
						Point(100.0, -100.0),
						Point(-100.0, -100.0),
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




class BorderedSquare(PrimitiveActor):
	def __init__(self, border_color=None, border_width=1, points=[], colors=[], *args, **kwargs):
		
		# Check points
		if points != []:
			if len(points) != 4:
				raise Exception("BorderedSquare needs 4 points, %d provided" % len(points))
		else:	
			points = [
						Point(-100, 100),  #TL
						Point(100, 100),   #TR
						Point(100, -100),  #BR
						Point(-100, -100), #BL
					]
			
		# Check border details
		if border_color == None:
			border_color = Color(1.0, 1.0, 1.0)
			
		# Named point mapping
		n = {	'TL': points[0],
				'TR': points[1],
				'BR': points[2],
				'BL': points[3],
			}
		# Create the inner points
		bw = border_width
	
		n['ITL'] = Point(points[0].x + bw, points[0].y - bw)
		n['ITR'] = Point(points[1].x - bw, points[1].y - bw)
		n['IBR'] = Point(points[2].x -bw, points[2].y + bw)
		n['IBL'] = Point(points[3].x + bw, points[3].y + bw)
			
		# Add the vertex data
		p = []
		p.extend([	n['TL'], n['ITR'], n['ITL'], 
					n['TL'], n['TR'], n['ITR'],
					n['TR'], n['IBR'], n['ITR'],
					n['TR'], n['BR'], n['IBR'],
					n['BR'], n['IBL'], n['IBR'],
					n['BR'], n['BL'], n['IBL'],
					n['BL'], n['ITL'], n['IBL'],
					n['BL'], n['TL'], n['ITL'],					
				])
		
		# Add the color data
		c = [border_color] * 24
		
		# Do the inner square
		ip = [n['ITL'],n['ITR'],n['IBR'],n['IBL']]
		for i in [0,1,2,0,2,3]:
			point = ip[i]
			p.append(point)
			try:
				color = colors[i]
				c.append(color)
			except IndexError:
				pass
		
		# Create the bordered square
		super(BorderedSquare, self).__init__(p, c, *args, **kwargs)	