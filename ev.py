from  ev3.ev3dev import Motor

class ev(Motor):


	def start(self):
		self.write_value('command', self.mode)
		self.write_value('run', '1')



	def stop(self):
		self.write_value('command', 'stop')
		self.write_value('run', '0')

	def setup_position_limited(self, position_sp, speed_sp, absolute=True, **kwargs):

		self.mode = 'position'
		self.write_value('run_mode', 'position')
		if self.absolute:
			self.write_value('position_mode', 'absolute')
		else:
			self.write_value('position_mode', 'relative')

		self.write_value('position_sp', str(position_sp))

		kwargs['speed_regulation'] = True
		for k in kwargs:
			v = kwargs[k]
			if (v != None):
				setattr(self, k, v)

				
		self.speed_sp = int(speed_sp)
		self.position_sp = int(position_sp)


	def setup_time_limited(self, time_sp, speed_sp, **kwargs):
		self.mode = 'run-timed'
		for k in kwargs:
			v = kwargs[k]
			if (v != None):
				setattr(self, k, v)
		speed_regulation = self.speed_regulation
		self.write_value('run_mode', 'time')
		self.write_value('time_sp', str(time_sp))
		if (speed_regulation):
			self.speed_sp = int(speed_sp)
		else:
			self.duty_cycle_sp = int(speed_sp)
		self.time_sp = int(time_sp)

	def setup_forever(self, speed_sp, **kwargs):
		self.write_value('run_mode', 'forever')
		self.mode = 'run-forever'
		for k in kwargs:
			v = kwargs[k]
			if (v != None):
				setattr(self, k, v)
		speed_regulation = self.speed_regulation
		if (speed_regulation):
			self.speed_sp = int(speed_sp)
		else:
			self.duty_cycle_sp = int(speed_sp)