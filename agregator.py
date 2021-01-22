from time import sleep
from random import randint
import sys

def input_tmp(signature): #choose signature
	return None


class Temperature_dot():
	def __init__(self, signature):
		self.signature = signature
		self.temperature = 0

	def temp(self):
		return self.temperature

	def sign(self):
		return self.signature

	def tmp_upd(self, data):
		self.temperature = data


class Temperature_contoure():
	def __init__(self, cont_sign):
		self.contoure_signature = cont_sign
		self.tmps = {}
		for i in range(8):
			self.tmps["tmp{}".format(i)] = Temperature_dot(None) #choose signature

	def update(self):
		for i in self.tmps:
			self.tmps[i] = input_tmp(self.tmps[i].sign())
		return None

	def display(self):
		pass


class Wheel():
	def __init__(self):
		self.contoure_1 = Temperature_contoure(None)
		self.contoure_2 = Temperature_contoure(None)
		self.contoure_3 = Temperature_contoure(None)
		self.contoure_4 = Temperature_contoure(None)


wheel_1 = Wheel()
while True:
  sys.stdout.write('\r' + '\t'.join([str(x) for x in [wheel_1.contoure_1.tmps[f"tmp{i}"].temperature for i in range(8)]]))
  sleep(1)
  for i in range(8):
    last_tmp = wheel_1.contoure_1.tmps[f"tmp{i}"].temperature
    wheel_1.contoure_1.tmps[f"tmp{i}"].tmp_upd(last_tmp - randint(-5, 5))