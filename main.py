from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QTableWidget, QProgressBar, QLCDNumber
from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel, QComboBox, QTableWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from threading import Thread, Event
from PyQt5 import uic
from PIL import Image
from time import sleep
from random import randint
import sqlite3
import sys

from agregator import Temperature_dot, Temperature_contoure, Wheel, wh_tmp


signatures = {"lfw": 0, "rfw": 1, "lbw": 2, "rbw": 3}


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

		self.wear_percent.setValue(0)
		self.timer = QTimer(self)

		self.stopFlag = Event()
		self.thread = MyThread(self.stopFlag, self.rtrn_tmp, 0)
		self.thread.start()

		self.rfw.clicked.connect(lambda: self.wear("rfw"))
		self.lfw.clicked.connect(lambda: self.wear("lfw"))
		self.rbw.clicked.connect(lambda: self.wear("rbw"))
		self.lbw.clicked.connect(lambda: self.wear("lbw"))

		self.plus_sec.clicked.connect(self.plus_sec_func)
		self.minus_sec.clicked.connect(self.minus_sec_func)
		self.plus_speed.clicked.connect(self.plus_speed_func)
		self.minus_speed.clicked.connect(self.minus_speed_func)


		self.reset.clicked.connect(self.res)
		self.streeting.valueChanged.connect(self.angle_change)


	def res(self):
		self.streeting.setValue(0)

	def angle_change(self):
		getValue = self.streeting.value()
		self.angle_lcd.display(getValue)


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


	def wear(self, wheel):
		self.coff = (self.temperature / 100) * (self.speed / 200) * 0.7
		# self.speed = self.speed * self.seconds

		if wheel == "rfw":
			self.percent += self.coff * self.seconds
			if self.percent > 100: self.percent = 100
			self.wear_percent.setValue(self.percent)

		if wheel == "lfw":
			self.percent_1 += self.coff * self.seconds
			if self.percent_1 > 100: self.percent_1 = 100
			self.wear_percent_1.setValue(self.percent_1)

		if wheel == "rbw":
			self.percent_2 += self.coff * self.seconds
			if self.percent_2 > 100: self.percent_2 = 100
			self.wear_percent_2.setValue(self.percent_2)

		if wheel == "lbw":
			self.percent_3 += self.coff * self.seconds
			if self.percent_3 > 100: self.percent_3 = 100
			self.wear_percent_3.setValue(self.percent_3)


	def rtrn_tmp(self, wheel_sign):
		tmps = wh_tmp(wheel_sign)
		self.temp_contour1.display(tmps["contoure_1"].display())
		self.temp_contour2.display(tmps["contoure_2"].display())
		self.temp_contour3.display(tmps["contoure_3"].display())
		self.temp_contour4.display(tmps["contoure_4"].display())


wheel_1 = Wheel(signature=0)
wheel_1.contoure_1.display()



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
			self.callback(0)
			self.callback(1)
			self.callback(2)
			self.callback(3)



app = QApplication(sys.argv)
ex = MainWindow()
ex.show()
sys.exit(app.exec())