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
	def addContact(self, text, id):
		_translate = QtCore.QCoreApplication.translate
		item = QtWidgets.QListWidgetItem()
		self.listWidget.addItem(item)
		item = self.listWidget.item(self.listWidget.count()-1)
		item.setText(_translate(None, text))
		item.setData(0x0100,id)
	def populateContacts(self):
		c = nanoNet.getContacts()
		for i in c:
		    print(i)
		    self.addContact(i['name'],i['id'])
	def openPMWindow(self, selected):
		self.pm=nanoPMWindow(selected[0].data(0x0100),selected[0].text())

class nanoNet():
	def getContacts():
		r = requests.post(config['remote']+"getContacts", data= {'token': config['token']})
		return r.json()
	def getHistory(self, number):
		r = requests.post(config['remote']+"getHistory", data = {'number':number, 'token':config['token']})
		print(r.encoding)
		raw='<head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head>'
		for i in r.json():
			raw=raw+"<b>"+i[2]+"</b>: "+i[3]+"<br>"
		_translate = QtCore.QCoreApplication.translate
		self.textBrowser.setText(_translate(None, raw))
	def sendMsg(self):
		msg = nanoPMWindow.getMessageText(self)
		nanoPMWindow.clearMessageText(self)
		r = requests.post(config['remote']+"sendMessage", data = {'recipient':self.number,'msg':msg,'token':config['token']})
		nanoNet.getHistory(self,self.number)

class nanoPMWindow(QtWidgets.QMainWindow, PMWindow):
	def __init__(self, number, name):
		QtWidgets.QDialog.__init__(self)
		self.setupUi(self)
		self.setWindowTitle(name+" - NanoIM")
		self.number = number
		self.name = name
		self.pushButton.clicked.connect(lambda: nanoNet.sendMsg(self))
		self.show()
		nanoNet.getHistory(self, number)
	def getMessageText(self):
		return self.plainTextEdit.toPlainText()
	def clearMessageText(self):
		self.plainTextEdit.clear()

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = nanoListWindow()
	window.show()
	window.populateContacts()
	sys.exit(app.exec_())