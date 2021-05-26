from time import sleep
from random import randint
import sys

wheel_temp = {}

def wh_tmp(sign):
	return wheel_temp[sign]

def input_tmp(signature): #choose signature
	return None


class Temperature_dot():
	def __init__(self, signature):
		self.signature = signature
		self.temperature = 120

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
			self.tmps["tmp{}".format(i)] = Temperature_dot(cont_sign * 10 + i) #choose signature

	def update(self, temp):
		for i in self.tmps:
			self.tmps[i].tmp_upd(temp)
		return None

	def display_all(self):
		print('\r' + '\t'.join([str(self.tmps[i].temp()) for i in self.tmps.keys()]))
		return '\r' + '\t'.join([str(self.tmps[i].temp()) for i in self.tmps.keys()])

	def display(self):
		return sum([self.tmps[i].temp() for i in self.tmps.keys()]) / len(self.tmps)


class Wheel():
	def __init__(self, signature):
		global wheel_temp
		self.signature = signature
		self.contoure_1 = Temperature_contoure(signature)
		self.contoure_2 = Temperature_contoure(signature)
		self.contoure_3 = Temperature_contoure(signature)
		self.contoure_4 = Temperature_contoure(signature)
		wheel_temp[signature] = {
			"contoure_1": self.contoure_1,
			"contoure_2": self.contoure_2,
			"contoure_3": self.contoure_3,
			"contoure_4": self.contoure_4
		}

	def temp_update(self, sign, argue):
		for i in wheel_temp[sign]:
			wheel_temp[sign][i].update(argue)