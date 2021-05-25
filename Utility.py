import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sqlite3
from PrintQuotation import PrintQuotation


class UtilityWindow( QtWidgets.QMainWindow ):

	def __init__( self, *args, **kwargs ):
		super().__init__( *args, **kwargs )
		uic.loadUi( "UI/UtilityWindow.ui", self )
		self.initVariables()
		self.config()

	def initVariables( self ):
		self.desktop = QApplication.desktop()
		self.screenRect = self.desktop.screenGeometry()
		self.height = self.screenRect.height()
		self.width = self.screenRect.width()
		# print( ( self.width - ( self.width * 0.05 ) ), ( self.height - ( self.height * 0.05 ) ) )

	def config( self ):
		self.setWindowFlag( QtCore.Qt.FramelessWindowHint )
		self.setAttribute( QtCore.Qt.WA_TranslucentBackground )
		self.resize(
		    ( self.width - ( self.width * 0.1 ) ), ( self.height - ( self.height * 0.1 ) )
		    )
		fg = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		fg.moveCenter( cp )
		self.move( fg.topLeft() )
		self.shadow = QGraphicsDropShadowEffect( self )
		self.shadow.setBlurRadius( 40 )
		self.shadow.setXOffset( 0 )
		self.shadow.setYOffset( 0 )
		self.shadow.setColor( QColor( 0, 0, 0, 180 ) )
		self.frame.setGraphicsEffect( self.shadow )

	def CurrencyWindow( self, DBHandler ):
		self.DBHandler = DBHandler
		self.CurrencyRateENT.setValidator( QDoubleValidator() )
		self.stackedWidget.setCurrentWidget( self.CurrencyPage )
		self.CurrencySavePBT.clicked.connect( self.saveCurrency )
		self.CurrencyEditPBT.clicked.connect( self.editCurrency )
		self.CurrencyDeletePBT.clicked.connect( self.deleteCurrency )
		self.CurrencyClosePBT.clicked.connect( self.exit )
		CurrencyTableHeader = self.CurrencyTable.horizontalHeader()
		CurrencyTableHeader.setSectionResizeMode( 0, QHeaderView.Stretch )
		CurrencyTableHeader.setSectionResizeMode( 1, QHeaderView.Stretch )
		self.CurrencyTable.doubleClicked.connect( self.editCurrency )
		self.fillCurrencyTable()

	def resetCurrencyForm( self, event=None ):
		self.CurrencySavePBT.setText( "Save" )
		self.CurrencySavePBT.clicked.disconnect()
		self.CurrencySavePBT.clicked.connect( self.saveCurrency )
		self.CurrencyClosePBT.setText( "Close" )
		self.CurrencyClosePBT.clicked.disconnect()
		self.CurrencyClosePBT.clicked.connect( self.exit )
		self.CurrencyNameENT.clear()
		self.CurrencyRateENT.clear()
		self.fillCurrencyTable()

	def saveCurrency( self, event=None ):
		if self.CurrencyRateENT.hasAcceptableInput() and self.CurrencyNameENT.text() not in [
		    "", " "
		    ]:
			self.DBHandler.execute(
			    """insert into currency (name,rate) values (?,?)""", (
			        self.CurrencyNameENT.text(),
			        float( self.CurrencyRateENT.text().replace( ',', '' ) )
			        )
			    )
			self.DBHandler.commit()
			self.DBHandler.execute( "VACUUM" )
			self.resetCurrencyForm()
		else:
			QMessageBox.information( self, "Empty", "Empty Field !" )

	def updateCurrency( self, event=None ):
		if self.CurrencyRateENT.hasAcceptableInput() and self.CurrencyNameENT.text() not in [
		    "", " "
		    ]:
			if self.CurrencyTable.currentRow() >= 0:

				n = self.CurrencyTable.currentRow()
				self.DBHandler.execute(
				    """update currency set name =?, rate =? where name == ?""", (
				        self.CurrencyNameENT.text(),
				        float( self.CurrencyRateENT.text().replace( ',', '' )
				              ), self.CurrencyTable.item( n, 0 ).text()
				        )
				    )
				self.DBHandler.commit()
				self.DBHandler.execute( "VACUUM" )
				self.resetCurrencyForm()
		else:
			QMessageBox.information( self, "Empty", "Please check your input !" )

	def editCurrency( self, event=None ):
		if self.CurrencyTable.currentRow() >= 0:

			n = self.CurrencyTable.currentRow()
			if self.CurrencyTable.item( n, 0 ).text() == "USD":
				QMessageBox.information(
				    self, "Error", "You are not able to edit 'USD' currency !"
				    )
			else:
				self.CurrencySavePBT.setText( "Update" )
				self.CurrencySavePBT.clicked.disconnect()
				self.CurrencySavePBT.clicked.connect( self.updateCurrency )
				self.CurrencyClosePBT.setText( "Reset" )
				self.CurrencyClosePBT.clicked.disconnect()
				self.CurrencyClosePBT.clicked.connect( self.resetCurrencyForm )

				result = self.DBHandler.execute(
				    """select * from currency where name == ?""",
				    ( self.CurrencyTable.item( n, 0 ).text(), )
				    ).fetchone()
				self.CurrencyNameENT.setText( result[ 0 ] )
				self.CurrencyRateENT.setText( "{:,.2f}".format( result[ 1 ] ) )
		else:
			QMessageBox.information( self, "Invalid Row", "Please select currency from table !" )

	def deleteCurrency( self, event=None ):
		if self.CurrencyTable.currentRow() >= 0:
			n = self.CurrencyTable.currentRow()
			if self.CurrencyTable.item( n, 0 ).text() == "USD":
				QMessageBox.information(
				    self, "Error", "You are not able to delete 'USD' currency !"
				    )
			else:
				self.DBHandler.execute(
				    """delete from currency where name == ?""",
				    ( self.CurrencyTable.item( n, 0 ).text(), )
				    )
				self.DBHandler.commit()
				self.DBHandler.execute( "VACUUM" )
				self.resetCurrencyForm()

		else:
			QMessageBox.information( self, "Invalid Row", "Please select currency from table !" )

	def fillCurrencyTable( self ):
		n = self.CurrencyTable.rowCount()
		for i in range( n ):
			self.CurrencyTable.removeRow( 0 )
		flag = True
		result = self.DBHandler.execute( """select * from currency""" ).fetchall()
		for cur in result:
			name = cur[ 0 ]
			rate = "{:,.2f}".format( cur[ 1 ] )
			temp = self.CurrencyTable.rowCount()
			self.CurrencyTable.insertRow( temp )
			self.CurrencyTable.setItem( temp, 0, QTableWidgetItem( name ) )
			self.CurrencyTable.setItem( temp, 1, QTableWidgetItem( rate ) )
			if name == "USD":
				flag = False
		if flag:
			self.DBHandler.execute(
			    """insert into currency (name,rate) values (?,?)""", ( "USD", 1 )
			    )
			self.DBHandler.commit()
			self.DBHandler.execute( "VACUUM" )
			self.fillCurrencyTable()

	def TCWindow( self, DBHandler ):
		self.DBHandler = DBHandler
		self.stackedWidget.setCurrentWidget( self.TCPage )

		self.TCSavePBT.clicked.connect( self.saveTC )
		self.TCResetPBT.clicked.connect( self.resetTC )

		self.TCDeletePBT.clicked.connect( self.deleteTC )
		self.TCClosePBT.clicked.connect( self.exit )

		self.resetTC()

	def saveTC( self, event=None ):
		self.DBHandler.execute(
		    """insert into termsandconditions (name,tc1,tc2,tc3,tc4,tc5,tc6,tc7) values (?,?,?,?,?,?,?,?)""",
		    (
		        self.TCNameENT.text(), self.TC1ENT.text(), self.TC2ENT.text(), self.TC3ENT.text(),
		        self.TC4ENT.text(), self.TC5ENT.text(), self.TC6ENT.text(), self.TC7ENT.text()
		        )
		    )
		self.DBHandler.commit()
		self.resetTC()

	def updateTC( self, event=None ):
		self.DBHandler.execute(
		    """update termsandconditions set name=?,tc1=?,tc2=?,tc3=?,tc4=?,tc5=?,tc6=?,tc7=?) where name == ?""",
		    (
		        self.TCNameENT.text(), self.TC1ENT.text(), self.TC2ENT.text(), self.TC3ENT.text(),
		        self.TC4ENT.text(), self.TC5ENT.text(), self.TC6ENT.text(), self.TC7ENT.text(),
		        self.TCSelectCB.currentText()
		        )
		    )
		self.DBHandler.commit()
		self.resetTC()

	def resetTC( self ):
		self.TCSavePBT.setText( "Save" )
		self.TCSavePBT.clicked.disconnect()
		self.TCSavePBT.clicked.connect( self.saveTC )
		self.TCClosePBT.setText( "Close" )
		self.TCClosePBT.clicked.disconnect()
		self.TCClosePBT.clicked.connect( self.exit )
		self.TCNameENT.clear()
		self.TC1ENT.clear()
		self.TC2ENT.clear()
		self.TC3ENT.clear()
		self.TC4ENT.clear()
		self.TC5ENT.clear()
		self.TC6ENT.clear()
		self.TC7ENT.clear()
		try:
			self.TCSelectCB.currentIndexChanged.disconnect()
		except:
			pass
		result = self.DBHandler.execute( """select * from termsandconditions""" ).fetchall()
		self.TCSelectCB.clear()
		for tc in result:
			self.TCSelectCB.addItem( tc[ 0 ] )

		self.TCSelectCB.activated.connect( self.TCChanged )

	def deleteTC( self, event=None ):
		buttonReply = QMessageBox.question(
		    self, 'Delete', "Are you sure, you want to delete ?", QMessageBox.Yes | QMessageBox.No,
		    QMessageBox.No
		    )
		if buttonReply == QMessageBox.Yes:
			self.DBHandler.execute(
			    """delete from termsandconditions where name == ?""",
			    ( self.TCSelectCB.currentText(), )
			    )
			self.DBHandler.commit()
			self.DBHandler.execute( "VACUUM" )
			self.resetTC()

	def TCChanged( self, event=None ):
		result = self.DBHandler.execute(
		    """select * from termsandconditions where name == ?""",
		    ( self.TCSelectCB.currentText(), )
		    ).fetchone()
		if result != None:
			self.TCSavePBT.setText( "Update" )
			self.TCSavePBT.clicked.disconnect()
			self.TCSavePBT.clicked.connect( self.updateTC )

			self.TCNameENT.setText( result[ 0 ] )
			self.TC1ENT.setText( result[ 1 ] )
			self.TC2ENT.setText( result[ 2 ] )
			self.TC3ENT.setText( result[ 3 ] )
			self.TC4ENT.setText( result[ 4 ] )
			self.TC5ENT.setText( result[ 5 ] )
			self.TC6ENT.setText( result[ 6 ] )
			self.TC7ENT.setText( result[ 7 ] )

	def PrintWindow( self, DBHandler, Qtano ):
		self.DBHandler = DBHandler
		self.PQ = PrintQuotation( self.DBHandler, Qtano )
		self.stackedWidget.setCurrentWidget( self.PrintPage )
		result = DBHandler.execute(
		    """select name,quotation_id,ref_no,date,grand_total from quotations where quotation_id == ?""",
		    ( Qtano, )
		    ).fetchone()
		self.PrintNameENT.setText( result[ 0 ] )
		self.PrintQtaENT.setText( str( Qtano ) )
		self.PrintRefENT.setText( result[ 2 ] )
		self.PrintDateENT.setText( result[ 3 ].strftime( "%d-%m-%Y" ) )
		self.PrintGrandENT.setText( "{:,.2f}".format( result[ 4 ] ) )
		result = self.DBHandler.execute( """select * from termsandconditions""" ).fetchall()
		self.PrintTCCB.clear()
		for tc in result:
			self.PrintTCCB.addItem( tc[ 0 ] )

		# self.TCSavePBT.clicked.connect( self.saveTC )
		# self.TCDeletePBT.clicked.connect( self.deleteTC )
		self.PrintWSRPBT.clicked.connect( self.PrintwithSqm )
		self.PrintWoSRPBT.clicked.connect( self.PrintwithoutSqm )
		self.PrintMALPBT.clicked.connect( self.PrintMAList )

		self.PrintClosePBT.clicked.connect( self.exit )

	def PrintwithoutSqm( self, event=None ):
		if self.PrintTCCB.currentText() not in [ "", " ", None ]:
			self.PQ.printQuotation( False, self.PrintTCCB.currentText() )
		else:
			QMessageBox.information( self, "Empty", "No Terms and Condition is selected !" )

	def PrintwithSqm( self, event=None ):
		if self.PrintTCCB.currentText() not in [ "", " ", None ]:
			self.PQ.printQuotation( True, self.PrintTCCB.currentText() )
		else:
			QMessageBox.information( self, "Empty", "No Terms and Condition is selected !" )
		# self.PQ.printQuotation( True, self.PrintTCCB.currentText() )

	def PrintMAList( self, event=None ):
		self.PQ.printQuotationwithMaterials()

	def GlassWindow( self, DBHandler ):
		self.DBHandler = DBHandler
		self.GlassRateENT.setValidator( QDoubleValidator() )
		self.stackedWidget.setCurrentWidget( self.GlassPage )
		self.GlassSavePBT.clicked.connect( self.saveGlass )
		self.GlassEditPBT.clicked.connect( self.editGlass )
		self.GlassDeletePBT.clicked.connect( self.deleteGlass )
		self.GlassClosePBT.clicked.connect( self.exit )
		GlassTableHeader = self.GlassTable.horizontalHeader()
		GlassTableHeader.setSectionResizeMode( 0, QHeaderView.ResizeToContents )
		GlassTableHeader.setSectionResizeMode( 1, QHeaderView.Stretch )
		GlassTableHeader.setSectionResizeMode( 2, QHeaderView.Stretch )
		self.GlassTable.doubleClicked.connect( self.editGlass )
		self.resetGlassForm()

	def resetGlassForm( self, event=None ):
		result = self.DBHandler.execute(
		    """select glass_id from glass order by glass_id DESC limit 1"""
		    ).fetchone()
		if result == None:

			self.GlassIDENT.setText( str( 1 ) )
		else:
			self.GlassIDENT.setText( str( result[ 0 ] + 1 ) )

		self.GlassSavePBT.setText( "Save" )
		self.GlassSavePBT.clicked.disconnect()
		self.GlassSavePBT.clicked.connect( self.saveGlass )
		self.GlassClosePBT.setText( "Close" )
		self.GlassClosePBT.clicked.disconnect()
		self.GlassClosePBT.clicked.connect( self.exit )
		self.GlassNameENT.clear()
		self.GlassRateENT.clear()
		self.fillGlassTable()

	def saveGlass( self, event=None ):
		if self.GlassRateENT.hasAcceptableInput() and self.GlassNameENT.text() not in [ "", " " ]:
			self.DBHandler.execute(
			    """insert into glass (glass_id,name,rate) values (?,?,?)""", (
			        int( self.GlassIDENT.text() ), self.GlassNameENT.text(),
			        float( self.GlassRateENT.text().replace( ',', '' ) )
			        )
			    )
			self.DBHandler.commit()
			self.DBHandler.execute( "VACUUM" )
			self.resetGlassForm()
		else:
			QMessageBox.information( self, "Empty", "Empty Field !" )

	def updateGlass( self, event=None ):
		if self.GlassRateENT.hasAcceptableInput() and self.GlassNameENT.text() not in [ "", " " ]:
			if self.GlassTable.currentRow() >= 0:

				n = self.GlassTable.currentRow()
				self.DBHandler.execute(
				    """update glass set name =?, rate =? where glass_id == ?""", (
				        self.GlassNameENT.text(),
				        float( self.GlassRateENT.text().replace( ',', '' )
				              ), int( self.GlassIDENT.text() )
				        )
				    )
				self.DBHandler.commit()
				self.DBHandler.execute( "VACUUM" )
				self.resetGlassForm()
		else:
			QMessageBox.information( self, "Empty", "Please check your input !" )

	def editGlass( self, event=None ):
		if self.GlassTable.currentRow() >= 0:

			n = self.GlassTable.currentRow()

			self.GlassSavePBT.setText( "Update" )
			self.GlassSavePBT.clicked.disconnect()
			self.GlassSavePBT.clicked.connect( self.updateGlass )
			self.GlassClosePBT.setText( "Reset" )
			self.GlassClosePBT.clicked.disconnect()
			self.GlassClosePBT.clicked.connect( self.resetGlassForm )

			result = self.DBHandler.execute(
			    """select * from glass where glass_id == ?""",
			    ( self.GlassTable.item( n, 0 ).text(), )
			    ).fetchone()

			self.GlassIDENT.setText( str( result[ 0 ] ) )
			self.GlassNameENT.setText( result[ 1 ] )
			self.GlassRateENT.setText( "{:,.2f}".format( result[ 2 ] ) )
		else:
			QMessageBox.information( self, "Invalid Row", "Please select glass from table !" )

	def deleteGlass( self, event=None ):
		if self.GlassTable.currentRow() >= 0:
			n = self.GlassTable.currentRow()

			self.DBHandler.execute(
			    """delete from glass where glass_id == ?""",
			    ( int( self.GlassTable.item( n, 0 ).text() ), )
			    )
			self.DBHandler.commit()
			self.DBHandler.execute( "VACUUM" )
			self.resetGlassForm()

		else:
			QMessageBox.information( self, "Invalid Row", "Please select glass from table !" )

	def fillGlassTable( self ):
		n = self.GlassTable.rowCount()
		for i in range( n ):
			self.GlassTable.removeRow( 0 )

		result = self.DBHandler.execute( """select * from glass""" ).fetchall()
		for cur in result:

			Id = cur[ 0 ]
			name = cur[ 1 ]
			rate = "{:,.2f}".format( cur[ 2 ] )
			temp = self.GlassTable.rowCount()
			self.GlassTable.insertRow( temp )
			self.GlassTable.setItem( temp, 0, QTableWidgetItem( str( Id ) ) )
			self.GlassTable.setItem( temp, 1, QTableWidgetItem( name ) )
			self.GlassTable.setItem( temp, 2, QTableWidgetItem( rate ) )

	def exit( self, event ):
		self.close()
