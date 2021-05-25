import sys, os, shutil, subprocess
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from MaterialsPage import MaterialsPageFunctions
from AccessoriesPage import AccessoriesPageFunctions
from ProductsPage import ProductsPageFunctions
from QuotationPage import QuotationPageFunctions
from AllproductsPage import AllproductsPageFunctions
from AllquotationsPage import AllquotationsPageFunctions
from Utility import UtilityWindow
import sqlite3
import logging


class HomePage(
    QtWidgets.QMainWindow, MaterialsPageFunctions, AccessoriesPageFunctions, ProductsPageFunctions,
    QuotationPageFunctions, AllproductsPageFunctions, AllquotationsPageFunctions
    ):

	def __init__( self, *args, **kwargs ):
		super().__init__( *args, **kwargs )
		uic.loadUi( "UI/HomePage.ui", self )
		self.openDatabase()
		self.initVariables()
		self.configureHomePage()

	def initVariables( self ):
		logging.basicConfig(
		    filename="GDAS_Logs.log",
		    format='%(asctime)s - %(message)s',
		    datefmt='%d-%b-%y %H:%M:%S'
		    )
		self.logger = logger = logging.getLogger()
		self.logger.setLevel( logging.DEBUG )
		self.desktop = QApplication.desktop()
		self.screenRect = self.desktop.screenGeometry()
		self.height = self.screenRect.height()
		self.width = self.screenRect.width()
		self.sqlQuery = None
		self.ProductMaterialGroups = {}
		self.ProductAccessoryGroups = {}
		self.Products = {}
		self.QuotationItems = {}
		self.DeletedProductMaterial = []
		self.DeletedProductAccessory = []

		self.ProductID = 0
		self.ProductMaterialsTableParentObjects = {}
		self.ProductMaterialsTableChildObjects = {}
		self.ProductAccessoriesTableParentObjects = {}
		self.ProductAccessoriesTableChildObjects = {}
		self.allCurrency = {}

		result = self.DBHandler.execute( """select * from currency""" ).fetchall()
		for cur in result:
			self.allCurrency[ cur[ 0 ] ] = float( cur[ 1 ] )

		self.currency = 'USD'
		self.vent = False
		self.fix = False

	def configureHomePage( self ):
		self.setMinimumWidth( self.width )
		self.setMinimumHeight( self.height )
		self.showMaximized()

		self.actionExportData.triggered.connect( self.exportData )
		self.actionImportData.triggered.connect( self.importData )

		self.actionOpenQuotationFolder.triggered.connect( self.openQuoFolder )
		self.actionDeleteStoredQuotation.triggered.connect( self.deleteStoredQuo )

		self.stackedWidget.setCurrentWidget( self.MainPage )
		self.MaterialsPBT.clicked.connect( self.initMaterialPage )
		self.AccessoriesPBT.clicked.connect( self.initAccessoryPage )
		self.GlassPBT.clicked.connect( self.initGlassPage )

		self.ProductPBT.clicked.connect( self.initProductPage )
		self.QuotationPBT.clicked.connect( self.initQuotationPage )
		self.CurrencyPBT.clicked.connect( self.initCurrencyPage )
		self.TCPBT.clicked.connect( self.initTCPage )
		self.AllProductsPBT.clicked.connect( self.initAllproductsPage )
		self.AllQuotationsPBT.clicked.connect( self.initAllquotationsPage )
		self.ExitPBT.clicked.connect( self.exit )
		self.configureMaterialsPage()
		self.configureAccessoriesPage()
		self.configureProductPage()
		self.configureQuotationPage()
		self.configureAllproductsPage()
		self.configureAllquotationsPage()

	def exportData( self, event=None ):
		folder = QFileDialog.getExistingDirectory( self, "Select Directory" )
		# print( folder )
		if folder not in [ "", " " ]:
			pwd = os.getcwd()
			shutil.copy2( os.path.join( pwd, "Data/GDAS.data" ), folder + "/GDAS.data" )

	def importData( self, event=None ):
		fname = QFileDialog.getOpenFileName( self, 'Select Data', "", "Data files (*.data )" )
		print( fname )
		if fname[ 0 ] not in [ " ", "" ]:
			pwd = os.getcwd()
			self.DBHandler.close()
			now = datetime.now().strftime( "%I%M%S" )
			os.rename(
			    os.path.join( pwd, "Data/GDAS.data" ),
			    os.path.join( pwd, "Data/GDAS_{}.data".format( now ) )
			    )
			shutil.copy2( fname[ 0 ], os.path.join( pwd, "Data/GDAS.data" ) )
			self.openDatabase()
			self.ShowMainPage()

	def openQuoFolder( self, event=None ):
		# os.startfile( "Quotations" )
		path = os.path.join( os.getcwd(), "Quotations" )
		print( path )
		if os.name == "nt":
			os.startfile( path )
		elif os.name == "posix":
			subprocess.call( [ 'open', path ] )
			# os.system( "open {}".format( path ) )

	def deleteStoredQuo( self, event=None ):
		buttonReply = QMessageBox.question(
		    self, 'Delete', "Are you sure, you want to delete ?", QMessageBox.Yes | QMessageBox.No,
		    QMessageBox.No
		    )
		if buttonReply == QMessageBox.Yes:
			dirpath = os.path.join( os.getcwd(), "Quotations" )
			for path, subfolders, files in os.walk( dirpath ):
				for f in files:
					os.remove( os.path.join( path, f ) )

	def configureMaterialsPage( self ):
		self.MaterialIDENT.setValidator( QIntValidator() )
		self.MaterialIDENT.textChanged.connect( self.validateMaterialInput )

		self.MaterialNameENT.textChanged.connect( self.validateMaterialInput )
		self.MaterialCodeENT.textChanged.connect( self.validateMaterialInput )
		self.MaterialQtyENT.textChanged.connect( self.validateMaterialInput )
		self.MaterialThicknessENT.textChanged.connect( self.validateMaterialInput )

		self.MaterialTableHeader = self.MaterialTable.horizontalHeader()
		self.MaterialTableHeader.setSectionResizeMode( 0, QtWidgets.QHeaderView.ResizeToContents )
		self.MaterialTableHeader.setSectionResizeMode( 1, QtWidgets.QHeaderView.ResizeToContents )
		self.MaterialTableHeader.setSectionResizeMode( 2, QtWidgets.QHeaderView.Stretch )
		self.MaterialTableHeader.setSectionResizeMode( 3, QtWidgets.QHeaderView.ResizeToContents )
		self.MaterialTableHeader.setSectionResizeMode( 4, QtWidgets.QHeaderView.ResizeToContents )
		self.MaterialTableHeader.setSectionResizeMode( 5, QtWidgets.QHeaderView.ResizeToContents )
		self.MaterialTableHeader.setVisible( True )
		self.MaterialTable.verticalHeader().setVisible( True )

		self.MaterialClosePBT.clicked.connect( self.ShowMainPage )
		self.MaterialSavePBT.clicked.connect( self.saveMaterial )
		self.MaterialEditPBT.clicked.connect( self.editMaterial )
		self.MaterialDeletePBT.clicked.connect( self.deleteMaterial )

		self.MaterialTable.doubleClicked.connect( self.editMaterial )

	def configureAccessoriesPage( self ):
		self.AccessoryIDENT.setValidator( QIntValidator() )
		self.AccessoryIDENT.textChanged.connect( self.validateAccessoryInput )
		self.AccessoryCodeENT.textChanged.connect( self.validateAccessoryInput )
		self.AccessoryNameENT.textChanged.connect( self.validateAccessoryInput )
		self.AccessoryQtyENT.textChanged.connect( self.validateAccessoryInput )
		self.AccessoryQtyENT.setValidator( QDoubleValidator() )
		self.AccessoryRateENT.textChanged.connect( self.validateAccessoryInput )
		self.AccessoryRateENT.setValidator( QDoubleValidator() )

		# self.AccessoryTable.setStyleSheet( "min-width:{}px".format( self.width * 0.8 ) )

		self.AccessoryTableHeader = self.AccessoryTable.horizontalHeader()
		self.AccessoryTableHeader.setSectionResizeMode( 0, QtWidgets.QHeaderView.ResizeToContents )
		self.AccessoryTableHeader.setSectionResizeMode( 1, QtWidgets.QHeaderView.ResizeToContents )
		self.AccessoryTableHeader.setSectionResizeMode( 2, QtWidgets.QHeaderView.Stretch )
		self.AccessoryTableHeader.setSectionResizeMode( 3, QtWidgets.QHeaderView.ResizeToContents )
		self.AccessoryTableHeader.setSectionResizeMode( 4, QtWidgets.QHeaderView.ResizeToContents )
		self.AccessoryTableHeader.setSectionResizeMode( 5, QtWidgets.QHeaderView.ResizeToContents )
		self.AccessoryTableHeader.setSectionResizeMode( 6, QtWidgets.QHeaderView.ResizeToContents )
		self.AccessoryTableHeader.setVisible( True )
		self.AccessoryTable.verticalHeader().setVisible( True )

		self.AccessoryClosePBT.clicked.connect( self.ShowMainPage )
		self.AccessorySavePBT.clicked.connect( self.saveAccessory )
		self.AccessoryEditPBT.clicked.connect( self.editAccessory )
		self.AccessoryDeletePBT.clicked.connect( self.deleteAccessory )
		self.AccessoryTable.doubleClicked.connect( self.editAccessory )

	def configureProductPage( self ):
		self.ProductIDENT.setValidator( QIntValidator() )
		self.ProductIDENT.textChanged.connect( self.validateProductInput )
		self.ProductNameENT.textChanged.connect( self.validateProductInput )
		self.ProductProfileENT.textChanged.connect( self.validateProductInput )
		self.ProductCommentENT.textChanged.connect( self.validateProductInput )

		self.ProductMGPBT.clicked.connect( self.showAddMaterialWindow )
		self.ProductAGPBT.clicked.connect( self.showAddAccessoryWindow )
		self.ProductSavePBT.clicked.connect( self.saveProduct )
		self.ProductEditPBT.clicked.connect( self.editGroup )
		self.ProductTable.doubleClicked.connect( self.editGroup )
		self.ProductClosePBT.clicked.connect( self.ShowMainPage )
		self.ProductDeletePBT.clicked.connect( self.deleteGroup )

		ProductTableHeader = self.ProductTable.header()
		ProductTableHeader.setSectionResizeMode( 0, QHeaderView.ResizeToContents )
		ProductTableHeader.setSectionResizeMode( 1, QHeaderView.ResizeToContents )
		ProductTableHeader.setSectionResizeMode( 2, QHeaderView.Stretch )
		ProductTableHeader.setSectionResizeMode( 3, QHeaderView.ResizeToContents )
		ProductTableHeader.setSectionResizeMode( 4, QHeaderView.ResizeToContents )
		ProductTableHeader.setSectionResizeMode( 5, QHeaderView.ResizeToContents )
		ProductTableHeader.setSectionResizeMode( 6, QHeaderView.ResizeToContents )
		ProductTableHeader.setSectionResizeMode( 7, QHeaderView.ResizeToContents )

	def configureQuotationPage( self ):
		self.QuotationQtanoENT.setValidator( QIntValidator() )
		self.QuotationTelnoENT.setValidator( QIntValidator() )

		self.QuotationRefnoENT.textChanged.connect( self.validateQuotationInput )
		self.QuotationNameENT.textChanged.connect( self.validateQuotationInput )

		self.QuotationOverENT.setValidator( QDoubleValidator() )
		self.QuotationProfitENT.setValidator( QDoubleValidator() )
		self.QuotationVatENT.setValidator( QDoubleValidator() )

		self.QuotationNetENT.setValidator( QDoubleValidator() )
		self.QuotationwithOverENT.setValidator( QDoubleValidator() )
		self.QuotationTransportENT.setValidator( QDoubleValidator() )
		self.QuotationwithProfitENT.setValidator( QDoubleValidator() )
		self.QuotationwithVatENT.setValidator( QDoubleValidator() )
		self.QuotationGrandENT.setValidator( QDoubleValidator() )

		self.QuotationNetENT.setReadOnly( True )
		self.QuotationwithOverENT.setReadOnly( True )
		self.QuotationwithProfitENT.setReadOnly( True )
		self.QuotationwithVatENT.setReadOnly( True )
		self.QuotationGrandENT.setReadOnly( True )

		self.QuotationNetENT.textChanged.connect( self.calculatTotal )
		self.QuotationTransportENT.textChanged.connect( self.calculatTotal )
		self.QuotationOverENT.textChanged.connect( self.calculatTotal )
		self.QuotationProfitENT.textChanged.connect( self.calculatTotal )
		self.QuotationVatENT.textChanged.connect( self.calculatTotal )
		self.QuotationCurrencyCB.currentIndexChanged.connect( self.currencyChanged )
		self.QuotationTable.doubleClicked.connect( self.editQuotationProdect )
		self.QuotationAddPBT.clicked.connect( self.showQuotationSubWindow )
		self.QuotationSavePBT.clicked.connect( self.saveQuotation )
		self.QuotationEditPBT.clicked.connect( self.editQuotationProdect )
		self.QuotationPrintPBT.clicked.connect( self.printQuotation )

		self.QuotationClosePBT.clicked.connect( self.ShowMainPage )
		self.QuotationDeletePBT.clicked.connect( self.deleteQuotationProduct )
		self.QuotationCurrencyCB.clear()
		result = self.DBHandler.execute( """select * from currency""" ).fetchall()
		for cur in result:
			self.allCurrency[ cur[ 0 ] ] = float( cur[ 1 ] )
		for cur in self.allCurrency.keys():
			self.QuotationCurrencyCB.addItem( cur )

		QuotationTableHeader = self.QuotationTable.horizontalHeader()
		QuotationTableHeader.setSectionResizeMode( 0, QHeaderView.ResizeToContents )
		QuotationTableHeader.setSectionResizeMode( 1, QHeaderView.Stretch )
		QuotationTableHeader.setSectionResizeMode( 2, QHeaderView.ResizeToContents )
		QuotationTableHeader.setSectionResizeMode( 3, QHeaderView.ResizeToContents )
		QuotationTableHeader.setSectionResizeMode( 4, QHeaderView.ResizeToContents )
		QuotationTableHeader.setSectionResizeMode( 5, QHeaderView.ResizeToContents )
		QuotationTableHeader.setSectionResizeMode( 6, QHeaderView.ResizeToContents )
		QuotationTableHeader.setSectionResizeMode( 7, QHeaderView.ResizeToContents )
		QuotationTableHeader.setSectionResizeMode( 8, QHeaderView.ResizeToContents )
		QuotationTableHeader.setSectionResizeMode( 9, QHeaderView.ResizeToContents )
		QuotationTableHeader.setSectionResizeMode( 10, QHeaderView.ResizeToContents )
		QuotationTableHeader.setSectionResizeMode( 11, QHeaderView.ResizeToContents )
		QuotationTableHeader.setSectionResizeMode( 12, QHeaderView.ResizeToContents )

		self.QuotationTable.hideColumn( 0 )

		self.QuotationOverENT.setText( '10' )
		self.QuotationProfitENT.setText( '30' )
		self.QuotationVatENT.setText( '18' )

	def initCurrencyPage( self, event=None ):
		cr = UtilityWindow( parent=self )
		cr.show()
		cr.CurrencyWindow( self.DBHandler )

	def initGlassPage( self, event=None ):
		gls = UtilityWindow( parent=self )
		gls.show()
		gls.GlassWindow( self.DBHandler )

	def initTCPage( self, event=None ):
		tc = UtilityWindow( parent=self )
		tc.show()
		tc.TCWindow( self.DBHandler )

	def configureAllproductsPage( self ):

		self.AllproductsTableHeader = self.AllproductsTable.horizontalHeader()
		self.AllproductsTableHeader.setSectionResizeMode(
		    0, QtWidgets.QHeaderView.ResizeToContents
		    )
		self.AllproductsTableHeader.setSectionResizeMode(
		    1, QtWidgets.QHeaderView.ResizeToContents
		    )
		self.AllproductsTableHeader.setSectionResizeMode( 2, QtWidgets.QHeaderView.Stretch )
		self.AllproductsTableHeader.setSectionResizeMode(
		    3, QtWidgets.QHeaderView.ResizeToContents
		    )
		self.AllproductsTableHeader.setSectionResizeMode( 4, QtWidgets.QHeaderView.Stretch )

		self.AllproductsfromDatetime.dateTimeChanged.connect( self.fetchProductsDatewise )
		self.AllproductstoDatetime.dateTimeChanged.connect( self.fetchProductsDatewise )

		self.AllproductsClosePBT.clicked.connect( self.ShowMainPage )

		self.AllproductsResetPBT.clicked.connect( self.AllproductReset )

		self.AllproductsEditPBT.clicked.connect( self.EditAllProducts )
		self.AllproductsDeletePBT.clicked.connect( self.DeleteProductPermenent )

		self.AllproductsTable.doubleClicked.connect( self.EditAllProducts )

	def configureAllquotationsPage( self ):

		self.AllquotationsfromDatetime.dateTimeChanged.connect( self.fetchQuotationsDatewise )
		self.AllquotationstoDatetime.dateTimeChanged.connect( self.fetchQuotationsDatewise )

		self.AllquotationsClosePBT.clicked.connect( self.ShowMainPage )
		self.AllquotationsCopyPBT.clicked.connect( self.CopyQuotation )

		self.AllquotationsResetPBT.clicked.connect( self.AllquotationsReset )

		self.AllquotationsPrintPBT.clicked.connect( self.PrintAllquotations )

		self.AllquotationsEditPBT.clicked.connect( self.EditAllquotations )
		self.AllquotationsDeletePBT.clicked.connect( self.DeleteQuotationPermenent )

		self.AllquotationsTable.doubleClicked.connect( self.EditAllquotations )

	def openDatabase( self ):
		try:
			self.DBHandler = sqlite3.connect(
			    "Data/GDAS.data", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
			    )
			self.DBHandler.execute( 'pragma foreign_keys=ON' )
		except Exception as e:
			self.logger.exception( "openDatabase", exc_info=True )
			QMessageBox.critical(
			    self,
			    "GDAS - Error!",
			    "Database Error: %s" % e,
			    )
			sys.exit( 1 )

	def ShowMainPage( self, event=None ):
		self.Heading.setText( "GDAS Costing System" )
		self.stackedWidget.setCurrentWidget( self.MainPage )

	def exit( self, event ):
		buttonReply = QMessageBox.question(
		    self, 'Exit', "Are you sure, you want to exit ?", QMessageBox.Yes | QMessageBox.No,
		    QMessageBox.No
		    )
		if buttonReply == QMessageBox.Yes:
			self.DBHandler.commit()
			self.DBHandler.close()
			sys.exit( 0 )

	def closeEvent( self, event ):

		self.DBHandler.commit()
		self.DBHandler.close()
		sys.exit( 0 )


if __name__ == "__main__":

	app = QtWidgets.QApplication( sys.argv )
	window = HomePage()
	window.show()
	app.exec_()