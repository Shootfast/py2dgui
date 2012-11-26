import time

class Animation(object):
	def __init__(self, actor, duration):
			
		self.actor = actor
		self.duration = duration		
		self.start = time.time()
				
		# Flag to say if this animation is complete
		self.complete = False


	def _calcCompletionRatio(self, time):
		'''
		Return value between 0 and 1
		'''
		i = time - self.start
		ratio = i / self.duration
		if ratio > 1:
			ratio = 1
			self.complete = True
		return ratio

	def update(self, time):
		raise NotImplementedError


class FadeIn(Animation):
	'''
	Animation to fade in an actor
	'''
		
	def update(self, time):
		ratio = self._calcCompletionRatio(time)
		self.actor.alpha = ratio
		
		