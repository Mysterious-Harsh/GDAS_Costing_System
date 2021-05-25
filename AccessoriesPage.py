import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from datetime import *
import sqlite3


class AccessoriesPageFunctions:

	def initAccessoryPage( self, event ):
		self.Heading.setText( "Accessories" )
		self.accessoryID = 0
		self.stackedWidget.setCurrentWidget( self.AccessoriesPage )
		self.validateAccessoryInput()
		self.resetAccessoryTable()
		self.resetAccessoryForm()

	def reconnectAccessory( self, signal, newhandler=None, oldhandler=None ):
		try:
			if oldhandler is not None:
				signal.disconnect( oldhandler )
			else:
				signal.disconnect()
		except Exception as e:
			print( "reconnectAccessory : ", e )

		if newhandler is not None:
			signal.connect( newhandler )

	def resetAccessoryForm( self ):
		result = self.DBHandler.execute(
		    """select accessory_id from accessories order by accessory_id DESC limit 1"""
		    ).fetchone()

		if result == None:
			self.accessoryID = 1
		else:
			self.accessoryID = result[ 0 ] + 1

		self.AccessoryIDENT.setText( str( self.accessoryID ) )
		self.AccessoryIDENT.setReadOnly( True )

		self.AccessoryDatetime.setDateTime( QtCore.QDateTime.currentDateTime() )
		self.AccessoryCodeENT.clear()

		self.AccessoryNameENT.clear()
		self.AccessoryQtyENT.clear()
		self.AccessoryRateENT.clear()
		self.AccessoryCurrencyCB.clear()
		result = self.DBHandler.execute( """select * from currency""" ).fetchall()
		for cur in result:
			self.allCurrency[ cur[ 0 ] ] = float( cur[ 1 ] )
		for cur in self.allCurrency.keys():
			self.AccessoryCurrencyCB.addItem( cur )

	def resetAccessoryTable( self ):
		n = self.AccessoryTable.rowCount()
		for i in range( n ):
			self.AccessoryTable.removeRow( 0 )

		result = self.DBHandler.execute(
		    """select accessory_id,code ,name, unit, quantity, rate, currency from accessories"""
		    )

		for row in result:
			temp = self.AccessoryTable.rowCount()
			self.AccessoryTable.insertRow( temp )
			self.AccessoryTable.setItem( temp, 0, QTableWidgetItem( str( row[ 0 ] ) ) )
			self.AccessoryTable.setItem( temp, 1, QTableWidgetItem( str( row[ 1 ] ) ) )
			self.AccessoryTable.setItem( temp, 2, QTableWidgetItem( str( row[ 2 ] ) ) )
			self.AccessoryTable.setItem( temp, 3, QTableWidgetItem( str( row[ 3 ] ) ) )
			self.AccessoryTable.setItem( temp, 4, QTableWidgetItem( str( row[ 4 ] ) ) )
			self.AccessoryTable.setItem( temp, 5, QTableWidgetItem( str( row[ 5 ] ) ) )
			self.AccessoryTable.setItem( temp, 6, QTableWidgetItem( str( row[ 6 ] ) ) )

	def validateAccessoryInput( self, event=None ):
		if not self.AccessoryIDENT.hasAcceptableInput():
			self.AccessoryIDENT.setStyleSheet( "border: 1px solid red;" )
		else:
			self.AccessoryIDENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )

		if not self.AccessoryCodeENT.hasAcceptableInput():
			self.AccessoryCodeENT.setStyleSheet( "border: 1px solid red;" )
		else:
			self.AccessoryCodeENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )

		if self.AccessoryNameENT.text() in [ "", " " ]:
			self.AccessoryNameENT.setStyleSheet( "border: 1px solid red;" )
		else:
			self.AccessoryNameENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )

		if not self.AccessoryQtyENT.hasAcceptableInput():
			self.AccessoryQtyENT.setStyleSheet( "border: 1px solid red;" )
		else:
			self.AccessoryQtyENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )

		if not self.AccessoryRateENT.hasAcceptableInput():
			self.AccessoryRateENT.setStyleSheet( "border: 1px solid red;" )
		else:
			self.AccessoryRateENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )

	def checkAccessoryForm( self ):
		if self.AccessoryIDENT.hasAcceptableInput() and self.AccessoryCodeENT.hasAcceptableInput(
		) and self.AccessoryNameENT.hasAcceptableInput(
		) and self.AccessoryQtyENT.hasAcceptableInput(
		) and self.AccessoryRateENT.hasAcceptableInput() and self.AccessoryCurrencyCB.currentText(
		) not in [ "", " " ]:
			return True
		else:
			return False

	def resetAccessory( self, event=None ):
		self.AccessorySavePBT.setText( "Save" )
		self.reconnectAccessory( self.AccessorySavePBT.clicked, self.saveAccessory )
		self.AccessoryClosePBT.setText( "Close" )
		self.reconnectAccessory( self.AccessoryClosePBT.clicked, self.ShowMainPage )
		self.resetAccessoryTable()
		self.resetAccessoryForm()

	def saveAccessory( self, event=None ):
		if self.checkAccessoryForm():
			if self.accessoryID != int( self.AccessoryIDENT.text() ):
				result = self.DBHandler.execute(
				    """select accessory_id from accessories order by accessory_id DESC limit 1"""
				    ).fetchone()

				if result == None:
					self.accessoryID = 1
				else:
					self.accessoryID = result[ 0 ] + 1
				self.AccessoryIDENT.setText( str( self.accessoryID ) )

			self.DBHandler.execute(
			    """insert into accessories (accessory_id,date,code,name,unit,quantity,rate,currency) values (?,?,?,?,?,?,?,?)""",
			    (
			        self.accessoryID, self.AccessoryDatetime.dateTime().toPyDateTime(),
			        self.AccessoryCodeENT.text(), self.AccessoryNameENT.text(),
			        self.AccessoryUnitCB.currentText(), float( self.AccessoryQtyENT.text() ),
			        float( self.AccessoryRateENT.text() ), self.AccessoryCurrencyCB.currentText()
			        )
			    )
			self.DBHandler.commit()
			self.resetAccessory()

		else:
			QMessageBox.information(
			    self, "Invalid Input", "Name : Any String <br> Quentity : 00.00 <br> Rate : 00.00"
			    )

	def updateAccessory( self, event=None ):
		if self.checkAccessoryForm():

			self.DBHandler.execute(
			    """update accessories set date=?,code=?,name=?,unit=?,quantity=?,rate=?,currency=? where accessory_id = ?""",
			    (
			        self.AccessoryDatetime.dateTime().toPyDateTime(), self.AccessoryCodeENT.text(),
			        self.AccessoryNameENT.text(), self.AccessoryUnitCB.currentText(),
			        float( self.AccessoryQtyENT.text() ), float( self.AccessoryRateENT.text() ),
			        self.AccessoryCurrencyCB.currentText(), self.accessoryID
			        )
			    )

			self.DBHandler.commit()
			self.resetAccessory()

		else:
			QMessageBox.information(
			    self, "Invalid Input",
			    "Code : GDIL 0000\(x) <br> Name : Any String <br> Quentity : 00.00/00.00 <br> Rate : 00.00"
			    )

	def editAccessory( self, event=None ):

		if self.AccessoryTable.currentRow() >= 0:
			n = self.AccessoryTable.currentRow()
			if self.AccessoryTable.item( n, 0 ).text() == "1":
				QMessageBox.information(
				    self, "Error", "You are not able to edit Glass accessory !"
				    )
			else:
				self.AccessorySavePBT.setText( "Update" )
				self.reconnectAccessory( self.AccessorySavePBT.clicked, self.updateAccessory )
				self.AccessoryClosePBT.setText( "Reset" )
				self.reconnectAccessory( self.AccessoryClosePBT.clicked, self.resetAccessory )

				self.accessoryID = int( self.AccessoryTable.item( n, 0 ).text() )

				result = self.DBHandler.execute(
				    """select * from accessories where accessory_id = ?""", ( self.accessoryID, )
				    ).fetchone()

				self.AccessoryIDENT.setText( str( result[ 0 ] ) )

				self.AccessoryDatetime.setDateTime( result[ 1 ] )
				self.AccessoryCodeENT.setText( result[ 2 ] )

				self.AccessoryNameENT.setText( str( result[ 3 ] ) )
				index = self.AccessoryUnitCB.findText(
				    str( result[ 4 ] ), QtCore.Qt.MatchFixedString
				    )
				if index >= 0:
					self.AccessoryUnitCB.setCurrentIndex( index )
				self.AccessoryQtyENT.setText( str( result[ 5 ] ) )
				self.AccessoryRateENT.setText( str( result[ 6 ] ) )
				index = self.AccessoryCurrencyCB.findText(
				    str( result[ 7 ] ), QtCore.Qt.MatchFixedString
				    )
				if index >= 0:
					self.AccessoryCurrencyCB.setCurrentIndex( index )

		else:
			QMessageBox.information( self, "Invalid Row", "Please select accessory from table !" )

	def deleteAccessory( self, event=None ):
		# self.AccessoryClosePBT.setText( "Cancel" )
		# self.reconnectAccessory( self.AccessoryClosePBT.clicked, self.resetAccessory )

		if self.AccessoryTable.currentRow() >= 0:
			n = self.AccessoryTable.currentRow()
			if self.AccessoryTable.item( n, 0 ).text() == "1":
				QMessageBox.information(
				    self, "Error", "You are not able to delete Glass accessory !"
				    )
			else:

				self.accessoryID = int( self.AccessoryTable.item( n, 0 ).text() )

				buttonReply = QMessageBox.question(
				    self, 'Delete', "Are you sure, you want to delete ?",
				    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
				    )
				if buttonReply == QMessageBox.Yes:
					try:
						self.DBHandler.execute(
						    "delete from accessories where accessory_id=?", ( self.accessoryID, )
						    )
						self.DBHandler.commit()
						self.DBHandler.execute( "VACUUM" )
					except Exception as e:
						QMessageBox.critical(
						    self,
						    "GDAS - Error!",
						    "Database Error: %s" % e,
						    )

				self.resetAccessory()
		else:
			QMessageBox.information( self, "Invalid Row", "Please select accessory from table !" )
