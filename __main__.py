#!/usr/bin/python3
import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import requests
import json

with open('config.json') as f:
	config = json.load(f)

Ui_MainWindow, QtBaseClass = uic.loadUiType("list.ui")
PMWindow, PMWindowQtBaseClass = uic.loadUiType("priv.ui")
contacts = []


class nanoListWindow(QtWidgets.QMainWindow, Ui_MainWindow):
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
		c = nanoNet.getContacts('matrix')
		for i in c:
		    self.addContact(i['name'], i['id'], i['type'])
	def openPMWindow(self, selected):
		id = selected[0].data(0x0100)
		type = selected[0].data(0x0101)
		name = selected[0].text()
		self.pm=nanoPMWindow(id, name, type)

class nanoNet():
	def getContacts(type):
		r = requests.post(config["remote"]+"getContacts", data= {'token': config["token"], 'type': type})
		return r.json()
	def getHistory(self, number):
		r = requests.post(config["remote"]+"getHistory", data = {'number':number, 'token': config["token"], 'type': self.type})
		raw='<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head>'
		for i in r.json():
			try:
				if(i['type']=="m.image"):
					raw=raw+"<b>"+i['sender']+"</b>: <a href='"+i['images']['thumb']+"'><img src='"+i['images']['thumb']+"'></a><br>"
				else:
					raw=raw+"<b>"+i['sender']+"</b>: "+i['body']+"<br>"
			except:
				raw=raw+"<u>Invalid data received from server!</u><br>"
		_translate = QtCore.QCoreApplication.translate
		self.textBrowser.setText(_translate(None, raw))
		nanoPMWindow.scrollDown(self)
	def sendMsg(self):
		msg = nanoPMWindow.getMessageText(self)
		nanoPMWindow.clearMessageText(self)
		r = requests.post(config["remote"]+"sendMessage", data = {'recipient': self.number, 'msg': msg, 'token': config["token"], 'type': self.type})
		nanoNet.getHistory(self, self.number)
class nanoPMWindow(QtWidgets.QMainWindow, PMWindow):
	def __init__(self, number, name, type):
		QtWidgets.QDialog.__init__(self)
		self.setupUi(self)
		self.setWindowTitle(name+" - NanoIM")
		self.number = number
		self.name = name
		self.type = type
	        #self.text_box = QtWidgets.QTextEdit(self)
		self.plainTextEdit.installEventFilter(self)
		self.pushButton.clicked.connect(lambda: nanoNet.sendMsg(self))
		self.refreshButton.clicked.connect(lambda: nanoNet.getHistory(self,number))
		self.show()
		nanoNet.getHistory(self, number)
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
					nanoNet.sendMsg(self)
					return super().eventFilter(obj, event)
		return False
	def getMessageText(self):
		return self.plainTextEdit.toPlainText()
	def clearMessageText(self):
		self.plainTextEdit.clear()
	def scrollDown(self):
		self.textBrowser.verticalScrollBar().setValue(self.textBrowser.verticalScrollBar().maximum())
if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = nanoListWindow()
	window.show()
	window.populateContacts()
	sys.exit(app.exec_())