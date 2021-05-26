from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QTableWidget, QProgressBar, QLCDNumber
from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel, QComboBox, QTableWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, QSize, Qt
from threading import Thread, Event
from PyQt5 import uic
from PIL import Image
from time import sleep
from random import randint
import sqlite3
import sys
from math import pi, sqrt, sin, radians

from agregator import Temperature_dot, Temperature_contoure, Wheel, wh_tmp


signatures = {"rfw": 0, "lfw": 1, "rbw": 2, "lbw": 3}

def average_temp(arr):
	summ = 0
	for i in arr:
		summ += arr[i].display()
	return summ // len(arr)


def int_round(num):
	num = int(num)
	if num % 10 > 5:
		num += 10 - num % 10
	if num % 10 <= 5:
		num -= num % 10
	return num


class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		uic.loadUi('TWControl.ui',self)
		Thread.__init__(self)

		self.percent = 0
		self.percent_1 = 0
		self.percent_2 = 0
		self.percent_3 = 0
		self.seconds = 0
		self.angle = 0
		self.speed = 0
		self.weight = 768
		self.temperature = 120
		self.events = []
		self.signature = 0
		self.event_flag = 0
		self.damage = 0
		self.q_turn = 0
		self.damage_max = 100
		self.row = -1

		self.wear_percent.setValue(0)
		self.wear_percent_1.setValue(0)
		self.wear_percent_2.setValue(0)
		self.wear_percent_3.setValue(0)
		self.timer = QTimer(self)

		self.stopFlag = Event()
		self.thread = MyThread(self.stopFlag, self.rtrn_tmp, self.signature)
		self.thread2 = MyThread(self.stopFlag, self.table_upd, self.signature)
		self.thread.start()
		self.thread2.start()

		# History of events--------------------------------------------------

		self.lap_stats.setColumnCount(4)
		self.lap_stats.setRowCount(len(self.events))

		self.lap_stats.setHorizontalHeaderLabels(["Turn", "Angle", "Speed", "Damage"])

		self.lap_stats.horizontalHeaderItem(0).setToolTip("Turn sequence number")
		self.lap_stats.horizontalHeaderItem(1).setToolTip("Angle at the moment of rotation (average)")
		self.lap_stats.horizontalHeaderItem(2).setToolTip("Turn speed (in apex)")

		self.lap_stats.horizontalHeaderItem(0).setTextAlignment(Qt.AlignHCenter)
		self.lap_stats.horizontalHeaderItem(1).setTextAlignment(Qt.AlignHCenter)
		self.lap_stats.horizontalHeaderItem(2).setTextAlignment(Qt.AlignHCenter)
		self.lap_stats.horizontalHeaderItem(3).setTextAlignment(Qt.AlignHCenter)


		#--------------------------------------------------------------------


		# self.rfw.clicked.connect(lambda: self.change("rfw"))
		# self.lfw.clicked.connect(lambda: self.change("lfw"))
		# self.rbw.clicked.connect(lambda: self.change("rbw"))
		# self.lbw.clicked.connect(lambda: self.change("lbw"))

		self.rfw.clicked.connect(lambda: self.wear("rfw"))
		self.lfw.clicked.connect(lambda: self.wear("lfw"))
		self.rbw.clicked.connect(lambda: self.wear("rbw"))
		self.lbw.clicked.connect(lambda: self.wear("lbw"))

		self.plus_sec.clicked.connect(self.plus_sec_func)
		self.minus_sec.clicked.connect(self.minus_sec_func)
		self.plus_speed.clicked.connect(self.plus_speed_func)
		self.minus_speed.clicked.connect(self.minus_speed_func)

		self.turn.clicked.connect(self.turned)
		self.reset.clicked.connect(self.res)
		self.streeting.valueChanged.connect(self.angle_change)
		self.lap.clicked.connect(self.lap_upd)

		self.lap_stats.clicked.connect(self.clicked_table)

	def clicked_table(self):
		rows = sorted(set(index.row() for index in
		                  self.lap_stats.selectedIndexes()))
		self.event_flag = -1
		for row in rows:
			self.row = row


	def res(self):
		self.streeting.setValue(0)


	def lap_upd(self):
		damage = 0
		for i in range(len(self.events)):
			damage += self.events[i]["damage"]
		self.laps.display(self.damage_max // damage)
		self.event_flag = 1


	def angle_change(self):
		getValue = self.streeting.value()
		self.angle = getValue
		self.angle_lcd.display(getValue)

	# def change(self, argue):
	# 	if argue == "rfw": self.signature = 0; self.stopFlag.set()
	# 	if argue == "lfw": self.signature = 1; self.stopFlag.set()
	# 	if argue == "rbw": self.signature = 2; self.stopFlag.set()
	# 	if argue == "lbw": self.signature = 3; self.stopFlag.set()
	# 	self.stopFlag.set()
	# 	self.thread = MyThread(self.stopFlag, self.rtrn_tmp, self.signature)
	# 	self.thread.start()


	def plus_sec_func(self):
		self.seconds += 1
		self.seconds_lcd.display(self.seconds)

	def minus_sec_func(self):
		self.seconds -= 1
		if self.seconds < 0:
			self.seconds = 0
		self.seconds_lcd.display(self.seconds)


	def plus_speed_func(self):
		self.speed += 5
		self.speed_lcd.display(self.speed)

	def minus_speed_func(self):
		self.speed -= 5
		if self.speed < 0:
			self.speed = 0
		self.speed_lcd.display(self.speed)


	def turned(self):
		if self.event_flag == 1:
			self.events = []
			self.event_flag = 0
			self.turn = 0


		damage = 1
		P = 4.8 / abs(sin(radians(self.angle)))
		R = P / (2 * pi)
		print(R)
		Vc = sqrt(9.8 * 7 * R) * 3.6 * 2.4
		print(self.speed, Vc)
		if self.speed >= Vc:
			self.percent_3 += (self.speed - Vc) * 0.1
			self.wear_percent_3.setValue(self.percent_3)
			damage = (self.speed - Vc) * 0.1
			self.percent_2 += (self.speed - Vc) * 0.1
			self.wear_percent_2.setValue(self.percent_2)
		else:
			damage = self.speed * 0.01 * sin(radians(self.angle))

		if abs(self.angle) > 15 and self.speed > 120:
			self.percent += 2
			self.wear_percent.setValue(self.percent)
			damage += 1
			self.percent_1 += 2
			self.wear_percent_1.setValue(self.percent_1)

		damage = abs(round(damage, 2))
		self.damage += damage
		print(damage)

		if self.event_flag == 0:
			self.q_turn += 1
			self.events.append({"turn": self.q_turn, "angle": self.angle, "speed": self.speed, "damage": damage})
		if self.event_flag == -1:
			self.events[self.row] = {"turn": self.events[self.row]["turn"],
			                         "angle": self.angle, "speed": self.speed, "damage": damage}
			self.row = 0
			self.event_flag = 0
		self.table_upd()


	def table_upd(self):
		self.lap_stats.setColumnCount(4)
		self.lap_stats.setRowCount(len(self.events))

		self.lap_stats.setHorizontalHeaderLabels(["Turn", "Angle", "Speed", "Damage"])

		self.lap_stats.horizontalHeaderItem(0).setToolTip("Turn sequence number")
		self.lap_stats.horizontalHeaderItem(1).setToolTip("Angle at the moment of rotation (average)")
		self.lap_stats.horizontalHeaderItem(2).setToolTip("Turn speed (in apex)")

		self.lap_stats.horizontalHeaderItem(0).setTextAlignment(Qt.AlignHCenter)
		self.lap_stats.horizontalHeaderItem(1).setTextAlignment(Qt.AlignHCenter)
		self.lap_stats.horizontalHeaderItem(2).setTextAlignment(Qt.AlignHCenter)

		for i in range(len(self.events)):
			self.lap_stats.setItem(i, 0, QTableWidgetItem(str(self.events[i]["turn"])))
			self.lap_stats.setItem(i, 1, QTableWidgetItem(str(self.events[i]["angle"])))
			self.lap_stats.setItem(i, 2, QTableWidgetItem(str(self.events[i]["speed"])))
			self.lap_stats.setItem(i, 3, QTableWidgetItem(str(self.events[i]["damage"])))


	def wear(self, signature):
		self.temperature = average_temp(wh_tmp(signatures[signature]))
		self.coff = (self.temperature / 100) * (self.speed / 200) * 0.7
		self.speed = int_round(self.speed - 0.7 * 9.8 * self.seconds)
		self.speed_lcd.display(self.speed)
		print(signatures[signature])

		if signatures[signature] == 0:
			self.percent += self.coff * self.seconds
			if self.percent > 100: self.percent = 100
			self.wear_percent.setValue(self.percent)

		if signatures[signature] == 1:
			self.percent_1 += self.coff * self.seconds
			if self.percent_1 > 100: self.percent_1 = 100
			self.wear_percent_1.setValue(self.percent_1)

		if signatures[signature] == 2:
			self.percent_2 += self.coff * self.seconds
			if self.percent_2 > 100: self.percent_2 = 100
			self.wear_percent_2.setValue(self.percent_2)

		if signatures[signature] == 3:
			self.percent_3 += self.coff * self.seconds
			if self.percent_3 > 100: self.percent_3 = 100
			self.wear_percent_3.setValue(self.percent_3)

		self.damage_max -= self.seconds * self.speed / 100


	def rtrn_tmp(self):
		self.temp_contour1.display(average_temp(wh_tmp(0)))
		self.temp_contour2.display(average_temp(wh_tmp(1)))
		self.temp_contour3.display(average_temp(wh_tmp(2)))
		self.temp_contour4.display(average_temp(wh_tmp(3)))


wheel_1 = Wheel(signature=0)
wheel_2 = Wheel(signature=1)
wheel_3 = Wheel(signature=2)
wheel_4 = Wheel(signature=3)



# while True:
# 	sys.stdout.write(wheel_1.contoure_1.display_all())
# 	sleep(1)
# 	for i in range(8):
# 		last_tmp = wheel_1.contoure_1.tmps[f"tmp{i}"].temperature
# 		wheel_1.contoure_1.tmps[f"tmp{i}"].tmp_upd(last_tmp - randint(-5, 5))



class MyThread(Thread):
	def __init__(self, event, callback, argue):
		Thread.__init__(self)
		self.stopped = event
		self.callback = callback
		self.argue = argue

	def run(self):
		while not self.stopped.wait(0.5):
			self.callback()



app = QApplication(sys.argv)
ex = MainWindow()
ex.show()
sys.exit(app.exec())