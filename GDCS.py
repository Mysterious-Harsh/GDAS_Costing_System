import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from HomePage import HomePage
import sqlite3
from CheckRegistration import checkRegistration
from Validate import Validation


class SplashScreen( QtWidgets.QMainWindow ):

	def __init__( self, *args, **kwargs ):
		super().__init__( *args, **kwargs )
		uic.loadUi( "UI/SplashScreen.ui", self )
		self.initVariables()
		self.config()

	def initVariables( self ):
		self.counter = 0

	def config( self ):
		self.frame.setCurrentWidget( self.SplashScreen )
		self.setWindowFlag( QtCore.Qt.FramelessWindowHint )
		self.setAttribute( QtCore.Qt.WA_TranslucentBackground )
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
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect( self.progress )
		self.timer.start( 30 )
		self.ReqCancelPBT.clicked.connect( self.exit )
		self.RequestPBT.clicked.connect( self.request )
		self.ValCancelPBT.clicked.connect( self.exit )
		self.RegisterPBT.clicked.connect( self.register )

		self.createDatabase()

	def checkRegister( self ):
		self.cr = checkRegistration()
		flag = self.cr.check()
		if flag:
			self.homepage = HomePage()
			self.homepage.show()
			self.close()
		else:
			self.frame.setCurrentWidget( self.RequestKey )

		pass

	def request( self, event=None ):
		name = self.ReqNameENT.text()
		if name in [ " ", "" ]:
			QMessageBox.information( self, "Empty", "Kindly enter your name !" )
		else:
			self.validate = Validation()
			flag = self.validate.sendKey( name )
			if flag == True:
				QMessageBox.information( self, "Sent", "Requested for Key !" )
			else:
				QMessageBox.information( self, "Error", flag )

			self.frame.setCurrentWidget( self.Validate )

	def register( self, event=None ):
		key = self.ValidateKeyENT.text()
		if key in [ " ", "" ]:
			QMessageBox.information( self, "Empty", "Kindly enter registration key !" )
		else:
			flag = self.validate.compare( key )
			if flag:
				f = self.cr.Register( key )
				if f:
					QMessageBox.information(
					    self, "Success", "Congratulation, Your PC is registerd."
					    )
					self.homepage = HomePage()
					self.homepage.show()
					self.close()

			else:
				QMessageBox.critical( self, "Error", "Invalid Key!" )

	def createDatabase( self ):
		if not os.path.exists( "Data" ):
			os.mkdir( "Data" )

		try:
			self.DBHandler = sqlite3.connect(
			    "Data/GDAS.data", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
			    )
			self.DBHandler.execute( 'pragma foreign_keys=ON' )
		except:
			QMessageBox.critical(
			    self,
			    "App Name - Error!",
			    "Database Error: %s" % self.DBHandler.lastError().databaseText(),
			    )
			sys.exit( 1 )

		self.DBHandler.execute(
		    ''' create table if not exists materials(material_id INTEGER  PRIMARY KEY UNIQUE NOT NULL,
		    date timestamp not null, code text not null unique, name text not null, unit text not null,
			quantity text not null,thickness real not null)'''
		    )
		self.DBHandler.execute(
		    ''' create table if not exists accessories(accessory_id INTEGER  PRIMARY KEY UNIQUE NOT NULL,
		    date timestamp not null, code text not null unique,name text not null, unit text not null,
			quantity real not null,rate real not null,currency text not null)'''
		    )
		self.DBHandler.execute(
		    """create table if not exists material_group(name text not null, group_id INTEGER NOT NULL, product_id INTEGER not null,
		 material_id integer not null ,formula text not null, FOREIGN KEY (material_id)
       REFERENCES materials(material_id))"""
		    )
		self.DBHandler.execute(
		    """create table if not exists accessory_group(name text not null, group_id INTEGER NOT NULL, product_id INTEGER not null,
		    accessory_id integer not null , formula text not null,FOREIGN KEY (accessory_id)
       REFERENCES accessories(accessory_id) )"""
		    )
		self.DBHandler.execute(
		    """create table if not exists products(product_id INTEGER PRIMARY KEY UNIQUE NOT NULL, date timestamp not null,
		     name text not null, profile text not null, comment text,
		    materialgroup text NOT NULL, accessorygroup text not null )"""
		    )

		self.DBHandler.execute(
		    """create table if not exists quotations(quotation_id INTEGER PRIMARY KEY UNIQUE NOT NULL, ref_no text not null ,
		    date timestamp not null,currency text not null, name text not null, tel_no text, email text, address text, profile text ,
		    finish text, project text , mesh text ,net_total real not null,overhead real not null,transport real not null,
		    profit real not null,vat real not null, grand_total real not null )"""
		    )

		self.DBHandler.execute(
		    """create table if not exists quotation_products(quotation_id INTEGER not null, quotation_product_id INTEGER not null, product_id integer not null, product_name text not null,
		    rate real not null, width real not null, height real not null, qty integer not null, vent_flag text not null, vent_height real not null,
		    fix_flag text not null, fix_height real not null, total_width real not null, total_height real not null, total_sqm real not null,
		    mat_group text not null, acc_group text not null, aluminium real not null, accessory real not null, total real not null,
		    group_sqm real not null, net_amount real not null,currency text not null, glass_type text not null, glass_rate real not null,
		    comment text, materialgroup text NOT NULL, accessorygroup text not null,
		    FOREIGN KEY (quotation_id) REFERENCES quotations(quotation_id), FOREIGN KEY (product_id) REFERENCES products(product_id))"""
		    )

		self.DBHandler.execute(
		    """create table if not exists quotation_products_materials( quotation_id INTEGER not null, quotation_product_id INTEGER not null, group_id INTEGER NOT NULL, gname text not null,
		    product_id INTEGER not null, material_id integer not null ,code text not null, mname text not null, unit text not null, qty text not null,
		    thickness real not null, formula text not null, FOREIGN KEY (material_id) REFERENCES materials(material_id))"""
		    )
		self.DBHandler.execute(
		    """create table if not exists quotation_products_accessories( quotation_id INTEGER not null, quotation_product_id INTEGER not null, group_id INTEGER NOT NULL, gname text not null,
		    product_id INTEGER not null, accessory_id integer not null, code text not null, aname text not null, unit text not null, qty real not null,
		    rate real not null, currency text not null, formula text not null,FOREIGN KEY (accessory_id) REFERENCES accessories(accessory_id) )"""
		    )

		self.DBHandler.execute(
		    """create table if not exists currency(name text not null unique,rate real not null)"""
		    )

		self.DBHandler.execute(
		    """create table if not exists glass(glass_id INTEGER PRIMARY KEY UNIQUE NOT NULL, name text not null unique,rate real not null)"""
		    )

		self.DBHandler.execute(
		    """create table if not exists termsandconditions(name text not null unique, tc1 text,tc2 text,tc3 text,tc4 text,tc5 text,tc6 text,tc7 text)"""
		    )

		self.DBHandler.commit()
		self.DBHandler.close()

	def progress( self ):

		self.progressBar.setValue( self.counter )

		if self.counter > 100:
			self.timer.stop()
			# self.homepage = HomePage()
			# self.homepage.show()
			self.checkRegister()
			# self.close()

		self.counter += 1

	def exit( self, event=None ):
		self.close()


if __name__ == "__main__":

	app = QtWidgets.QApplication( sys.argv )
	window = SplashScreen()
	window.show()
	app.exec_()
