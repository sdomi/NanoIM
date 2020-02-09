#!/usr/bin/python3
from os import path as path
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import requests
import json
from datetime import datetime

with open('config.json') as f:
	config = json.load(f)

Ui_MainWindow, QtBaseClass = uic.loadUiType("list.ui")
PMWindow, PMWindowQtBaseClass = uic.loadUiType("priv.ui")
contacts = []


class NanoListWindow(QtWidgets.QMainWindow, Ui_MainWindow):
	def __init__(self):
		QtWidgets.QMainWindow.__init__(self)
		Ui_MainWindow.__init__(self)
		self.setupUi(self)
		self.listWidget.clicked.connect(lambda: self.openPMWindow(self.listWidget.selectedItems()))

	def resizeEvent(self, event):
		self.listWidget.resize(self.width()-20, self.height()-50)

	def addContact(self, text, id, type):
		_translate = QtCore.QCoreApplication.translate
		item = QtWidgets.QListWidgetItem()
		self.listWidget.addItem(item)
		item = self.listWidget.item(self.listWidget.count()-1)
		item.setText(_translate(None, text))
		item.setData(0x0100, id)
		item.setData(0x0101, type)

	def populateContacts(self):
		c = []
		if config["networks"]["matrix"] == "true":
			c += NanoNet.getContacts('matrix')
		for i in c:
			self.addContact(i['name'], i['id'], i['type'])

	def openPMWindow(self, selected):
		id = selected[0].data(0x0100)
		type = selected[0].data(0x0101)
		name = selected[0].text()
		self.pm=NanoPMWindow(id, name, type)

class NanoNet():
	def getContacts(type):
		r = requests.post(config["remote"]+"getContacts", data= {'token': config["token"], 'type': type})
		return r.json()

	def getHistory(self, number):
		r = requests.post(config["remote"]+"getHistory", data = {'number':number, 'token': config["token"], 'type': self.type})
		raw='<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head>'
		for i in r.json():
			
			timestamp = datetime.fromtimestamp(int(i["timestamp"])).strftime('%Y-%m-%d %H:%M:%S')
			try:
				if(i['type']=="m.image"):
					raw+=f'<span title="{timestamp}"><b>{i["sender"]}</b>: <a href="{i["images"]["orig"]}"><img src="{NanoNet.getPicture(i["images"]["thumb"], i["images"]["name"])}"></a></span><br>'
				else:
					raw+=f'<span title="{timestamp}"><b>{i["sender"]}</b>: {i["body"]}</span><br>'
			except:
				raw=raw+"<u>Invalid data received from server!</u><br>"
		content = raw.replace('\n','<br />\n')
		_translate = QtCore.QCoreApplication.translate
		self.textBrowser.setText(_translate(None, content))
		NanoPMWindow.scrollDown(self)

	def sendMsg(self):
		msg = NanoPMWindow.getMessageText(self).strip()
		NanoPMWindow.clearMessageText(self)
		r = requests.post(config["remote"]+"sendMessage", data = {'recipient': self.number, 'msg': msg, 'token': config["token"], 'type': self.type})
		NanoNet.getHistory(self, self.number)

	def getPicture(picture,name):
		prefix='cache/'
		filename=prefix+name.replace("/","")
		if not path.isfile(filename):
			print('lauraisVERYcute')
			r = requests.get(picture)
			with open(filename, 'wb') as f:
				f.write(r.content)
		return filename

class NanoPMWindow(QtWidgets.QMainWindow, PMWindow):
	def __init__(self, number, name, type):
		QtWidgets.QDialog.__init__(self)
		self.setupUi(self)
		self.setWindowTitle(f'{name} - NanoIM')
		self.number = number
		self.name = name
		self.type = type
		self.plainTextEdit.installEventFilter(self)
		self.textBrowser.setOpenExternalLinks(True)
		self.pushButton.clicked.connect(lambda: NanoNet.sendMsg(self))
		self.refreshButton.clicked.connect(lambda: NanoNet.getHistory(self,number))
		self.show()
		NanoNet.getHistory(self, number)
		self.scrollDown()

	def resizeEvent(self, event):
		self.textBrowser.resize(self.width(), self.height()-55)
		self.plainTextEdit.resize(self.width()-self.pushButton.width(),self.height()-self.textBrowser.height())
		self.plainTextEdit.move(5,self.height()-self.plainTextEdit.height())
		self.pushButton.move(self.plainTextEdit.width()+5,self.height()-self.plainTextEdit.height())
		self.refreshButton.move(self.plainTextEdit.width()+5,self.height()-self.refreshButton.height())

	def eventFilter(self, obj, event):
		if event.type() == QtCore.QEvent.KeyPress and obj is self.plainTextEdit:
			if event.key() == QtCore.Qt.Key_Return and self.plainTextEdit.hasFocus():
				if not QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
					NanoNet.sendMsg(self)
					NanoPMWindow.clearMessageText(self)
					return True
		return False

	def mousePressEvent(self, QMouseEvent):
		print(QMouseEvent.pos())

	def getMessageText(self):
		return self.plainTextEdit.toPlainText()

	def clearMessageText(self):
		self.plainTextEdit.clear()

	def scrollDown(self):
		self.textBrowser.verticalScrollBar().setValue(self.textBrowser.verticalScrollBar().maximum())


if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = NanoListWindow()
	window.show()
	window.populateContacts()
	sys.exit(app.exec_())