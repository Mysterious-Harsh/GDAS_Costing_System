import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from datetime import *
import sqlite3
# from ProductsPage import ProductsPageFunctions


class AllproductsPageFunctions:

	def initAllproductsPage( self, event ):
		self.Heading.setText( "Allproducts" )
		# self.DBHandler = DBHandler
		self.rowid = None
		self.stackedWidget.setCurrentWidget( self.AllproductsPage )
		self.AllproductReset()

	def AllproductReset( self, event=None ):

		n = self.AllproductsTable.rowCount()
		for i in range( n ):
			self.AllproductsTable.removeRow( 0 )

		result = self.DBHandler.execute( """select date from products ORDER BY date(date) ASC """
		                                ).fetchall()
		if result != []:

			self.AllproductsfromDatetime.setDateTime( result[ 0 ][ 0 ] )
			self.AllproductstoDatetime.setDateTime( result[ len( result ) - 1 ][ 0 ] )
			self.fetchProductsDatewise()
		else:
			QMessageBox.information( self, "Empty", "Products Not Found !" )

	def fetchProductsDatewise( self, event=None ):
		n = self.AllproductsTable.rowCount()
		for i in range( n ):
			self.AllproductsTable.removeRow( 0 )

		result = self.DBHandler.execute(
		    """select * from products where date between ? and ?""", (
		        self.AllproductsfromDatetime.dateTime().toPyDateTime(),
		        self.AllproductstoDatetime.dateTime().toPyDateTime()
		        )
		    )

		for row in result:
			temp = self.AllproductsTable.rowCount()
			self.AllproductsTable.insertRow( temp )
			self.AllproductsTable.setItem( temp, 0, QTableWidgetItem( str( row[ 0 ] ) ) )
			self.AllproductsTable.setItem( temp, 1, QTableWidgetItem( str( row[ 1 ] ) ) )
			self.AllproductsTable.setItem( temp, 2, QTableWidgetItem( str( row[ 2 ] ) ) )
			self.AllproductsTable.setItem( temp, 3, QTableWidgetItem( str( row[ 3 ] ) ) )
			self.AllproductsTable.setItem( temp, 4, QTableWidgetItem( str( row[ 4 ] ) ) )

	def EditAllProducts( self, event=None ):
		if self.AllproductsTable.currentRow() >= 0:
			n = self.AllproductsTable.currentRow()
			self.initEditProductPage( int( self.AllproductsTable.item( n, 0 ).text() ) )
		else:
			QMessageBox.information( self, "Invalid Row", "Please select Product from table !" )

	def DeleteProductPermenent( self, event=None ):
		if self.AllproductsTable.currentRow() >= 0:
			n = self.AllproductsTable.currentRow()
			ID = int( self.AllproductsTable.item( n, 0 ).text() )
			buttonReply = QMessageBox.question(
			    self, 'Delete', "Are you sure, you want to Delete ?",
			    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
			    )
			if buttonReply == QMessageBox.Yes:
				try:
					self.DBHandler.execute( "delete from products where product_id=?", ( ID, ) )
					self.DBHandler.execute(
					    "delete from material_group where product_id=?", ( ID, )
					    )
					self.DBHandler.execute(
					    "delete from accessory_group where product_id=?", ( ID, )
					    )
					self.DBHandler.commit()
					self.DBHandler.execute( "VACUUM" )
				except Exception as e:
					QMessageBox.critical(
					    self,
					    "GDAS - Error!",
					    "Database Error: %s" % e,
					    )
				self.AllproductReset()

		else:
			QMessageBox.information( self, "Invalid Row", "Please select Quotation from table !" )
