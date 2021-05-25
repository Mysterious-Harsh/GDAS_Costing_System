import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from datetime import *
import sqlite3


class MaterialsPageFunctions:

	def initMaterialPage( self, event ):
		self.Heading.setText( "Materials" )
		self.materialID = 0
		self.stackedWidget.setCurrentWidget( self.MaterialsPage )
		self.validateMaterialInput()
		self.resetMaterialTable()
		self.resetMaterialForm()

	def reconnectMaterial( self, signal, newhandler=None, oldhandler=None ):

		if oldhandler is not None:
			signal.disconnect( oldhandler )
		else:
			signal.disconnect()

		if newhandler is not None:
			signal.connect( newhandler )

	def resetMaterialForm( self ):
		result = self.DBHandler.execute(
		    """select material_id from materials order by material_id DESC limit 1"""
		    ).fetchone()
		if result == None:

			self.materialID = 1
		else:
			self.materialID = result[ 0 ] + 1
		self.MaterialIDENT.setText( str( self.materialID ) )

		self.MaterialIDENT.setReadOnly( True )
		self.MaterialDatetime.setDateTime( QtCore.QDateTime.currentDateTime() )
		self.MaterialCodeENT.clear()
		self.MaterialNameENT.clear()
		self.MaterialQtyENT.clear()
		self.MaterialThicknessENT.clear()

	def resetMaterialTable( self ):
		n = self.MaterialTable.rowCount()
		for i in range( n ):
			self.MaterialTable.removeRow( 0 )

		result = self.DBHandler.execute(
		    """select material_id, code, name, unit, quantity, thickness from materials"""
		    )

		for row in result:
			temp = self.MaterialTable.rowCount()
			self.MaterialTable.insertRow( temp )
			self.MaterialTable.setItem( temp, 0, QTableWidgetItem( str( row[ 0 ] ) ) )
			self.MaterialTable.setItem( temp, 1, QTableWidgetItem( str( row[ 1 ] ) ) )
			self.MaterialTable.setItem( temp, 2, QTableWidgetItem( str( row[ 2 ] ) ) )
			self.MaterialTable.setItem( temp, 3, QTableWidgetItem( str( row[ 3 ] ) ) )
			self.MaterialTable.setItem( temp, 4, QTableWidgetItem( str( row[ 4 ] ) ) )
			self.MaterialTable.setItem( temp, 5, QTableWidgetItem( str( row[ 5 ] ) ) )

	def validateMaterialInput( self, event=None ):
		if not self.MaterialIDENT.hasAcceptableInput():
			self.MaterialIDENT.setStyleSheet( "border: 1px solid red;" )
		else:
			self.MaterialIDENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )

		if self.MaterialNameENT.text() in [ "", " " ]:
			self.MaterialNameENT.setStyleSheet( "border: 1px solid red;" )
		else:
			self.MaterialNameENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )

		if not self.MaterialCodeENT.hasAcceptableInput():
			self.MaterialCodeENT.setStyleSheet( "border: 1px solid red;" )
		else:
			self.MaterialCodeENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )

		if not self.MaterialQtyENT.hasAcceptableInput():
			self.MaterialQtyENT.setStyleSheet( "border: 1px solid red;" )
		else:
			self.MaterialQtyENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )

		if not self.MaterialThicknessENT.hasAcceptableInput():
			self.MaterialThicknessENT.setStyleSheet( "border: 1px solid red;" )
		else:
			self.MaterialThicknessENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )

	def checkMaterialForm( self ):
		if self.MaterialIDENT.hasAcceptableInput() and self.MaterialCodeENT.hasAcceptableInput(
		) and self.MaterialNameENT.hasAcceptableInput() and self.MaterialQtyENT.hasAcceptableInput(
		) and self.MaterialThicknessENT.hasAcceptableInput():
			return True
		else:
			return False

	def resetMaterial( self, event=None ):
		self.resetMaterialForm()
		self.resetMaterialTable()
		self.MaterialSavePBT.setText( "Save" )
		self.reconnectMaterial( self.MaterialSavePBT.clicked, self.saveMaterial )
		self.MaterialClosePBT.setText( "Close" )
		self.reconnectMaterial( self.MaterialClosePBT.clicked, self.ShowMainPage )

	def saveMaterial( self, event=None ):
		if self.checkMaterialForm():
			if self.materialID != int( self.MaterialIDENT.text() ):
				result = self.DBHandler.execute(
				    """select material_id from materials order by material_id DESC limit 1"""
				    ).fetchone()
				if result == None:
					self.materialID = 1
				else:
					self.materialID = result[ 0 ] + 1
				self.MaterialIDENT.setText( str( self.materialID ) )

			self.DBHandler.execute(
			    """insert into materials (material_id,date,code,name,unit,quantity,thickness) values (?,?,?,?,?,?,?)""",
			    (
			        self.materialID, self.MaterialDatetime.dateTime().toPyDateTime(),
			        self.MaterialCodeENT.text(), self.MaterialNameENT.text(),
			        self.MaterialUnitCB.currentText(), self.MaterialQtyENT.text(),
			        float( self.MaterialThicknessENT.text()[ :-3 ] )
			        )
			    )
			self.DBHandler.commit()
			self.resetMaterial()

		else:
			QMessageBox.information(
			    self, "Invalid Input",
			    "Code : GDIL 0000\(x) <br> Name : Any String <br> Quentity : 00.00/00.00 <br> Thickness : 00.00"
			    )

	def updateMaterial( self, event=None ):
		if self.checkMaterialForm():

			self.DBHandler.execute(
			    """update materials set date=?,code=?,name=?,unit=?,quantity=?,thickness=? where material_id = ?""",
			    (
			        self.MaterialDatetime.dateTime().toPyDateTime(), self.MaterialCodeENT.text(),
			        self.MaterialNameENT.text(), self.MaterialUnitCB.currentText(),
			        self.MaterialQtyENT.text(), float( self.MaterialThicknessENT.text()[ :-3 ]
			                                          ), self.materialID
			        )
			    )
			self.DBHandler.commit()
			self.resetMaterial()
		else:
			QMessageBox.information(
			    self, "Invalid Input",
			    "Code : GDIL 0000\(x) <br> Name : Any String <br> Quentity : 00.00/00.00 <br> Thickness : 00.00"
			    )

	def editMaterial( self, event=None ):

		if self.MaterialTable.currentRow() >= 0:

			self.MaterialSavePBT.setText( "Update" )
			self.reconnectMaterial( self.MaterialSavePBT.clicked, self.updateMaterial )
			self.MaterialClosePBT.setText( "Reset" )
			self.reconnectMaterial( self.MaterialClosePBT.clicked, self.resetMaterial )

			self.materialID = int(
			    self.MaterialTable.item( self.MaterialTable.currentRow(), 0 ).text()
			    )

			result = self.DBHandler.execute(
			    """select * from materials where material_id = ?""", ( self.materialID, )
			    ).fetchone()

			self.MaterialIDENT.setText( str( result[ 0 ] ) )
			self.MaterialDatetime.setDateTime( result[ 1 ] )
			self.MaterialCodeENT.setText( str( result[ 2 ] ) )
			self.MaterialNameENT.setText( str( result[ 3 ] ) )
			index = self.MaterialUnitCB.findText( str( result[ 4 ] ), QtCore.Qt.MatchFixedString )
			if index >= 0:
				self.MaterialUnitCB.setCurrentIndex( index )
			self.MaterialQtyENT.setText( str( result[ 5 ] ) )
			self.MaterialThicknessENT.setText( str( result[ 6 ] ) )
		else:
			QMessageBox.information( self, "Invalid Row", "Please select material from table !" )

	def deleteMaterial( self, event=None ):
		# self.MaterialClosePBT.setText( "Cancel" )
		# self.reconnectMaterial( self.MaterialClosePBT.clicked, self.resetMaterial )

		if self.MaterialTable.currentRow() >= 0:
			self.materialID = int(
			    self.MaterialTable.item( self.MaterialTable.currentRow(), 0 ).text()
			    )

			buttonReply = QMessageBox.question(
			    self, 'Delete', "Are you sure, you want to delete ?",
			    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
			    )
			if buttonReply == QMessageBox.Yes:
				try:
					self.DBHandler.execute(
					    "delete from materials where material_id=?", ( self.materialID, )
					    )
					self.DBHandler.commit()
					self.DBHandler.execute( "VACUUM" )
				except Exception as e:
					QMessageBox.critical(
					    self,
					    "GDAS - Error!",
					    "Database Error: %s" % e,
					    )
			self.resetMaterial()
		else:
			QMessageBox.information( self, "Invalid Row", "Please select material from table !" )
