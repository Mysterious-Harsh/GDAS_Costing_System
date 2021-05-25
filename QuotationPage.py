import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from datetime import *
import sqlite3
import math
from Utility import UtilityWindow
import copy
# import dictdiffer


class QuotationSubWindow( QtWidgets.QMainWindow ):

	def __init__( self, *args, **kwargs ):
		super().__init__( *args, **kwargs )
		uic.loadUi( "UI/QuotationSubWindow.ui", self )
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
		    ( self.width - ( self.width * 0.03 ) ), ( self.height - ( self.height * 0.03 ) )
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

		# self.ProMatClosePBT.clicked.connect( self.exit )
		# self.ProAccClosePBT.clicked.connect( self.exit )

	def exit( self, event ):
		self.close()


class QuotationPageFunctions:

	def initQuotationPage( self, event ):
		self.Heading.setText( "Quotation" )
		# self.DBHandler = DBHandler

		self.stackedWidget.setCurrentWidget( self.QuotationPage )
		self.QuotationSavePBT.setText( "Save" )
		try:
			self.QuotationSavePBT.clicked.disconnect()
		except:
			pass
		self.QuotationSavePBT.clicked.connect( self.saveQuotation )
		self.quotationID = 0

		self.Products = {}
		self.ProductMaterialGroups = {}
		self.ProductAccessoryGroups = {}
		self.QuotationItems = {}
		self.DeletedQuoProducts = []
		self.Glasses = []
		self.Glass = ()
		# self.associateIDS = {}

		self.getProducts()
		# self.resetQuotationTree()
		self.validateQuotationInput()
		self.resetQuotationForm()
		self.currencyChanged()

		# self.QuotationAccessories = {}

	def initEditQuotationPage( self, quotationID ):
		self.Products = {}
		self.ProductMaterialGroups = {}
		self.ProductAccessoryGroups = {}
		self.QuotationItems = {}
		self.rowid = {}
		self.quotationID = quotationID
		self.QuoProductID = 0
		self.DeletedQuoProducts = []
		self.stackedWidget.setCurrentWidget( self.QuotationPage )
		self.QuotationSavePBT.setText( "Update" )
		try:
			self.QuotationSavePBT.clicked.disconnect()
		except:
			pass
		self.QuotationSavePBT.clicked.connect( self.updateQuotation )

		self.getProducts()
		self.validateQuotationInput()

		Quotation = self.DBHandler.execute(
		    """select * from quotations where quotation_id == ?""", ( self.quotationID, )
		    ).fetchone()

		self.QuotationQtanoENT.setText( str( Quotation[ 0 ] ) )
		self.QuotationRefnoENT.setText( Quotation[ 1 ] )
		self.QuotationDatetime.setDateTime( Quotation[ 2 ] )
		self.QuotationCurrencyCB.clear()

		result = self.DBHandler.execute( """select * from currency""" ).fetchall()
		for cur in result:
			self.allCurrency[ cur[ 0 ] ] = float( cur[ 1 ] )
		for cur in self.allCurrency.keys():
			self.QuotationCurrencyCB.addItem( cur )
		index = self.QuotationCurrencyCB.findText(
		    str( Quotation[ 3 ] ), QtCore.Qt.MatchFixedString
		    )
		if index >= 0:
			self.QuotationCurrencyCB.setCurrentIndex( index )
		self.QuotationNameENT.setText( Quotation[ 4 ] )
		self.QuotationTelnoENT.setText( Quotation[ 5 ] )
		self.QuotationEmailENT.setText( Quotation[ 6 ] )
		self.QuotationAddENT.setText( Quotation[ 7 ] )
		self.QuotationProfileENT.setText( Quotation[ 8 ] )
		self.QuotationFinishENT.setText( Quotation[ 9 ] )
		self.QuotationProjectENT.setText( Quotation[ 10 ] )
		self.QuotationMeshENT.setText( Quotation[ 11 ] )

		result = self.DBHandler.execute(
		    """select quotation_product_id, product_id, product_name,rate,width,
			height,qty,vent_flag,vent_height,fix_flag,fix_height,total_width,total_height,total_sqm,
			mat_group,acc_group,aluminium,accessory,total,group_sqm,net_amount,currency,glass_type,
			glass_rate,comment,materialgroup,accessorygroup,rowid from quotation_products where quotation_id == ? ORDER BY quotation_product_id ASC""",
		    ( self.quotationID, )
		    ).fetchall()

		QuoProduct = map( list, result )
		# tempdict = {}
		templist = []
		for product in QuoProduct:
			templist = []
			quoProductId = int( product.pop( 0 ) )
			productId = int( product[ 0 ] )
			if product[ 6 ] == "True":
				product[ 6 ] = True
			else:
				product[ 6 ] = False

			if product[ 8 ] == "True":
				product[ 8 ] = True
			else:
				product[ 8 ] = False

			product[ 13 ] = list( map( int, product[ 13 ].split( ',' ) ) )
			product[ 14 ] = list( map( int, product[ 14 ].split( ',' ) ) )

			materialgroup = product[ -3 ].split( "," )
			accessorygroup = product[ -2 ].split( "," )
			# print( product )

			templist.append( product )
			mg = {}
			for mid in materialgroup:
				result = self.DBHandler.execute(
				    """select group_id, gname, product_id, material_id, code, mname, unit, qty, thickness, formula
				    from quotation_products_materials where quotation_id==? and quotation_product_id == ? and
				    product_id == ? and group_id == ? ORDER BY material_id ASC""",
				    ( self.quotationID, quoProductId, productId, int( mid ) )
				    ).fetchall()
				material_group = list( map( list, result ) )
				mg[ int( mid ) ] = material_group
			templist.append( mg )

			ag = {}
			for aid in accessorygroup:
				result = self.DBHandler.execute(
				    """select group_id, gname, product_id, accessory_id, code, aname, unit, qty, rate, currency, formula
				    from quotation_products_accessories where quotation_id==? and quotation_product_id == ? and
				    product_id == ? and group_id == ? ORDER BY accessory_id ASC""",
				    ( self.quotationID, quoProductId, productId, int( aid ) )
				    ).fetchall()
				accessory_group = list( map( list, result ) )
				ag[ int( aid ) ] = accessory_group
			templist.append( ag )

			# tempdict[ quoProductId ] = templist

			if productId not in self.QuotationItems.keys():
				self.QuotationItems[ productId ] = {}

			self.QuotationItems[ productId ][ quoProductId ] = templist

			# print( len( self.QuotationItems[ self.QuoProductID ] ) )
		# print( self.QuotationItems )
		self.compareChanges()
		self.resetQuotationTable()

	def compareChanges( self ):

		buttonReply = QMessageBox.question(
		    self, 'Changed', "There are changes in old and new data.\nDo you want to update ?",
		    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
		    )
		for productId, productGroup in self.QuotationItems.items():
			for quoProId, product in productGroup.items():
				materialGroupOld = product[ 1 ]
				accessoryGroupOld = product[ 2 ]
				# print( accessoryGroupOld )

				materialGroupNew = self.ProductMaterialGroups[ productId ]
				accessoryGroupNew = self.ProductAccessoryGroups[ productId ]
				# print( accessoryGroupNew )

				# matGroupChanges = list( dictdiffer.diff( materialGroupOld, materialGroupNew ) )
				# accGroupChanges = list( dictdiffer.diff( accessoryGroupOld, accessoryGroupNew ) )

				if buttonReply == QMessageBox.Yes:
					product[ 1 ] = materialGroupNew
					product[ 2 ] = accessoryGroupNew
					self.editQuotationProdect( QuoProductID="{}:{}".format( quoProId, productId ) )
					self.addQuoProduct()

				elif buttonReply == QMessageBox.No:
					self.ProductMaterialGroups[ productId ] = product[ 1 ]
					self.ProductAccessoryGroups[ productId ] = product[ 2 ]

				# print( oldAccSet ^ newAccSet )

	def getProducts( self ):
		self.Glasses = []
		self.Products = {}
		self.ProductMaterialGroups = {}
		self.ProductAccessoryGroups = {}

		self.Glasses = self.DBHandler.execute( """select * from glass""" ).fetchall()

		result = self.DBHandler.execute(
		    """select product_id, name, materialgroup, accessorygroup from products"""
		    ).fetchall()
		products = list( map( list, result ) )

		for product in products:
			product_id = product[ 0 ]
			self.Products[ product_id ] = product
			temp = {}
			mgid = product[ 2 ].split( ',' )
			try:
				mgid.remove( '' )
			except:
				pass
			for material_id in mgid:
				result = self.DBHandler.execute(
				    """select group_id, material_group.name, product_id, material_group.material_id, code, materials.name,
				    unit, quantity, thickness, formula from material_group inner join materials on
					materials.material_id = material_group.material_id
					where product_id == ? and group_id == ? ORDER BY material_group.material_id ASC""",
				    ( product[ 0 ], int( material_id ) )
				    ).fetchall()
				material_group = list( map( list, result ) )
				group_id = material_group[ 0 ][ 0 ]
				temp[ group_id ] = material_group

			self.ProductMaterialGroups[ product_id ] = temp

			temp = {}
			agid = product[ 3 ].split( ',' )
			try:
				agid.remove( '' )
			except:
				pass
			for accessory_id in agid:
				result = self.DBHandler.execute(
				    """select group_id, accessory_group.name, product_id, accessory_group.accessory_id, code, accessories.name,
				    unit, quantity, rate, currency, formula from accessory_group inner join accessories on
					accessories.accessory_id = accessory_group.accessory_id
					where product_id == ? and group_id == ? ORDER BY accessory_group.accessory_id ASC""",
				    ( product[ 0 ], int( accessory_id ) )
				    ).fetchall()
				accessory_group = list( map( list, result ) )
				group_id = accessory_group[ 0 ][ 0 ]
				temp[ group_id ] = accessory_group

			self.ProductAccessoryGroups[ product_id ] = temp

		# print( self.ProductMaterialGroups )

	def validateQuotationInput( self, event=None ):
		if not self.QuotationQtanoENT.hasAcceptableInput():
			self.QuotationQtanoENT.setStyleSheet( "border: 1px solid red;" )
		else:
			self.QuotationQtanoENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )

		if self.QuotationNameENT.text() in [ "", " " ]:
			self.QuotationNameENT.setStyleSheet( "border: 1px solid red;" )
		else:
			self.QuotationNameENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )

		if self.QuotationRefnoENT.text() in [ "", " " ]:
			self.QuotationRefnoENT.setStyleSheet( "border: 1px solid red;" )
		else:
			self.QuotationRefnoENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )

	def resetQuotationForm( self ):
		self.QuotationItems = {}
		self.QuoProductID = 0
		self.ProductMaterialsTableParentObjects = {}
		self.ProductMaterialsTableChildObjects = {}
		self.ProductAccessoriesTableParentObjects = {}
		self.ProductAccessoriesTableChildObjects = {}

		result = self.DBHandler.execute(
		    """select quotation_id from quotations order by quotation_id DESC limit 1"""
		    ).fetchone()
		self.QuotationNameENT.clear()
		self.QuotationTelnoENT.clear()
		self.QuotationEmailENT.clear()
		self.QuotationAddENT.clear()
		self.QuotationProfileENT.clear()
		self.QuotationFinishENT.clear()
		self.QuotationProjectENT.clear()
		self.QuotationMeshENT.clear()

		if result == None:
			self.quotationID = 1
		else:
			self.quotationID = result[ 0 ] + 1

		self.QuotationQtanoENT.setText( str( self.quotationID ) )
		self.QuotationDatetime.setDateTime( QtCore.QDateTime.currentDateTime() )
		self.QuotationRefnoENT.setText(
		    "GDAS/00/{:05d}/{:04d}".format(
		        int( self.QuotationQtanoENT.text() ), int( self.QuotationDatetime.date().year() )
		        )
		    )
		self.QuotationQtanoENT.setReadOnly( True )
		self.QuotationCurrencyCB.clear()
		result = self.DBHandler.execute( """select * from currency""" ).fetchall()
		for cur in result:
			self.allCurrency[ cur[ 0 ] ] = float( cur[ 1 ] )
		for cur in self.allCurrency.keys():
			self.QuotationCurrencyCB.addItem( cur )
		self.QuotationCurrencyCB.setCurrentIndex( 0 )

	def resetQuotationTable( self ):
		n = self.QuotationTable.rowCount()
		for i in range( n ):
			self.QuotationTable.removeRow( 0 )

		for productId, productGroup in self.QuotationItems.items():

			SQM = 0
			for quoProId, product in productGroup.items():
				product = product[ 0 ]
				name = product[ 1 ]
				metal_rate = product[ 2 ]
				wid = product[ 3 ]
				hei = product[ 4 ]
				sqm = wid * hei
				qty = product[ 5 ]
				tot_sqm = product[ 12 ]
				rate_P_unit = product[ 17 ] / qty
				amo = product[ 17 ]

				temp = self.QuotationTable.rowCount()
				self.QuotationTable.insertRow( temp )
				self.QuotationTable.setItem(
				    temp, 0, QTableWidgetItem( "{}:{}".format( quoProId, productId ) )
				    )
				self.QuotationTable.setItem(
				    temp, 1,
				    QTableWidgetItem(
				        "{} : {} : {}".format( str( name ), product[ 21 ], product[ 23 ] )
				        )
				    )
				self.QuotationTable.setItem(
				    temp, 2, QTableWidgetItem( "{:,.2f}".format( metal_rate ) )
				    )
				self.QuotationTable.setItem( temp, 3, QTableWidgetItem( "{:.4f}".format( wid ) ) )
				self.QuotationTable.setItem( temp, 4, QTableWidgetItem( "{:.4f}".format( hei ) ) )
				self.QuotationTable.setItem( temp, 5, QTableWidgetItem( "{:.2f}".format( sqm ) ) )
				self.QuotationTable.setItem( temp, 6, QTableWidgetItem( str( qty ) ) )
				self.QuotationTable.setItem( temp, 7, QTableWidgetItem( str( tot_sqm ) ) )

				sqm_rate = amo / tot_sqm
				self.QuotationTable.setItem(
				    temp, 8, QTableWidgetItem( "{:,.2f}".format( sqm_rate ) )
				    )

				clientSqmRate = product[ 19 ] / product[ 18 ]
				self.QuotationTable.setItem(
				    temp, 9, QTableWidgetItem( "{:,.2f}".format( clientSqmRate ) )
				    )

				self.QuotationTable.setItem(
				    temp, 10, QTableWidgetItem( "{:,.2f}".format( rate_P_unit ) )
				    )

				self.QuotationTable.setItem(
				    temp, 11,
				    QTableWidgetItem( "{:,.2f}".format( clientSqmRate * ( tot_sqm / qty ) ) )
				    )

				self.QuotationTable.setItem( temp, 12, QTableWidgetItem( "{:,.2f}".format( amo ) ) )
		self.calculatTotal()

	def calculatTotal( self ):
		netTotal = 0
		totalSQM = 0
		overhead = 0
		transport = 0
		total = 0
		profit = 0
		vat = 0
		grandTotal = 0

		try:
			for productId, productGroup in self.QuotationItems.items():

				for quoProId, product in productGroup.items():
					product = product[ 0 ]
					netTotal += product[ 17 ]
					totalSQM += product[ 12 ]

			# for product_id, product in self.QuotationItems.items():
			# 	net_total += product[ 17 ]
			# 	total_sqm += product[ 12 ]

			self.QuotationNetENT.setText( "{:,.2f}".format( netTotal ) )

			overhead = float( self.QuotationOverENT.text().replace( ',', '' ) ) * totalSQM
			if self.currency != "USD":
				overhead = self.convertCurrency( "USD", self.currency, overhead )

			transport = float( self.QuotationTransportENT.text().replace( ',', '' ) )
			total = netTotal + overhead + transport
			profit = ( float( self.QuotationProfitENT.text().replace( ',', '' ) ) / 100 ) * total
			vat = ( float( self.QuotationVatENT.text().replace( ',', '' ) ) /
			        100 ) * ( profit + total )

			grandTotal = total + profit + vat
		except Exception as e:
			# print( "Calculate Total : " + e )
			pass

		self.QuotationwithOverENT.setText( "{:,.2f}".format( overhead ) )
		self.QuotationTransportENT.setText( "{:,.2f}".format( transport ) )
		self.QuotationwithProfitENT.setText( "{:,.2f}".format( profit ) )
		self.QuotationwithVatENT.setText( "{:,.2f}".format( vat ) )
		self.QuotationGrandENT.setText( "{:,.2f}".format( math.ceil( grandTotal ) ) )

	def convertCurrency( self, src, des, value ):
		return ( ( self.allCurrency[ des ] * value ) / self.allCurrency[ src ] )

	def currencyChanged( self ):
		self.currency = self.QuotationCurrencyCB.currentText()
		self.QuotationNetL.setText( self.currency )
		self.QuotationTransportL.setText( self.currency )
		self.QuotationGrandL.setText( self.currency )

		for productId, productGroup in self.QuotationItems.items():
			for quoProId, product in productGroup.items():

				if product[ 0 ][ 20 ] != self.currency:
					product[ 0 ][ 2 ] = self.convertCurrency(
					    product[ 0 ][ 20 ], self.currency, product[ 0 ][ 2 ]
					    )
					product[ 0 ][ 15 ] = self.convertCurrency(
					    product[ 0 ][ 20 ], self.currency, product[ 0 ][ 15 ]
					    )
					product[ 0 ][ 16 ] = self.convertCurrency(
					    product[ 0 ][ 20 ], self.currency, product[ 0 ][ 16 ]
					    )
					product[ 0 ][ 17 ] = self.convertCurrency(
					    product[ 0 ][ 20 ], self.currency, product[ 0 ][ 17 ]
					    )
					product[ 0 ][ 19 ] = self.convertCurrency(
					    product[ 0 ][ 20 ], self.currency, product[ 0 ][ 19 ]
					    )
					product[ 0 ][ 20 ] = self.currency

		# print( self.QuotationItems.values() )
		self.resetQuotationTable()

	def deleteQuotationProduct( self, event=None ):
		if self.QuotationTable.currentRow() >= 0:
			buttonReply = QMessageBox.question(
			    self, 'Delete', "Are you sure, you want to delete ?",
			    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
			    )
			if buttonReply == QMessageBox.Yes:
				n = self.QuotationTable.currentRow()
				temp = self.QuotationTable.item( n, 0 ).text().split( ":" )

				QuoProductID = int( temp[ 0 ] )
				productId = int( temp[ 1 ] )

				if len( self.QuotationItems[ productId ][ QuoProductID ][ 0 ] ) == 27:

					self.DeletedQuoProducts.append(
					    self.QuotationItems[ productId ][ QuoProductID ][ 0 ][ -1 ]
					    )

				del self.QuotationItems[ productId ][ QuoProductID ]
				newID = 0

				templist = list( self.QuotationItems.values() )
				deletedkeys = []

				for productId, productGroup in self.QuotationItems.items():
					total_amo = 0
					total_sqm = 0

					for key, Products in productGroup.items():
						total_amo += Products[ 0 ][ 17 ]
						total_sqm += Products[ 0 ][ 12 ]

					tempdict = {}
					if len( productGroup ) == 0:
						deletedkeys.append( productId )

					for quoProductId, product in productGroup.items():
						product[ 0 ][ 18 ] = total_sqm
						product[ 0 ][ 19 ] = total_amo
						tempdict[ newID ] = product
						newID += 1

					self.QuotationItems[ productId ] = tempdict

				for i in deletedkeys:
					del self.QuotationItems[ i ]

				# print( self.DeletedQuoProducts )
				self.resetQuotationTable()
		else:
			QMessageBox.information( self, "Invalid Row", "Please select Product from table !" )

	def printQuotation( self, event=None ):
		result = self.DBHandler.execute(
		    """select name from quotations where quotation_id == ?""", ( self.quotationID, )
		    ).fetchone()
		# print( result )
		if result == None:
			self.saveQuotation()

		pq = UtilityWindow( parent=self )
		pq.show()
		pq.PrintWindow( self.DBHandler, self.quotationID )

	def checkQuotationInput( self ):
		if self.QuotationRefENT.hasAcceptableInput() and self.QuotationNameENT.hasAcceptableInput(
		) and self.QuotationQtyENT.hasAcceptableInput(
		) and self.QuotationRateENT.hasAcceptableInput():
			return True
		else:
			return False

	def saveQuotation( self, event=None ):
		if self.QuotationRefnoENT.hasAcceptableInput() and self.QuotationNameENT.hasAcceptableInput(
		) and self.QuotationItems != {}:
			self.DBHandler.execute(
			    """insert into quotations (quotation_id,ref_no,date,currency,name,tel_no,email,address,
			   profile,finish,project,mesh,net_total,overhead,transport,profit,vat,grand_total)
			   values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
			        self.quotationID, self.QuotationRefnoENT.text(),
			        self.QuotationDatetime.dateTime().toPyDateTime(), self.currency,
			        self.QuotationNameENT.text(), self.QuotationTelnoENT.text(),
			        self.QuotationEmailENT.text(), self.QuotationAddENT.text(),
			        self.QuotationProfileENT.text(), self.QuotationFinishENT.text(),
			        self.QuotationProjectENT.text(), self.QuotationMeshENT.text(),
			        float( self.QuotationNetENT.text().replace( ',', '' )
			              ), float( self.QuotationOverENT.text().replace( ',', '' )
			                       ), float( self.QuotationTransportENT.text().replace( ',', '' ) ),
			        float( self.QuotationProfitENT.text().replace( ',', '' )
			              ), float( self.QuotationVatENT.text().replace( ',', '' )
			                       ), float( self.QuotationGrandENT.text().replace( ',', '' ) )
			        )
			    )

			# quotation_ID = int( self.QuotationQtanoENT.text() )
			for productId, productGroup in self.QuotationItems.items():
				for quoProductId, product in productGroup.items():
					productInfo = product[ 0 ]
					materialGroup = product[ 1 ]
					accessoryGroup = product[ 2 ]
					self.DBHandler.execute(
					    """insert into quotation_products (quotation_id, quotation_product_id, product_id, product_name,
					    rate,width,height,qty,vent_flag,vent_height,fix_flag,fix_height,total_width,total_height,total_sqm,
					    mat_group,acc_group,aluminium,accessory,total, group_sqm, net_amount, currency, glass_type, glass_rate,
					    comment, materialgroup,accessorygroup)values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
					    (
					        self.quotationID, quoProductId, int( productInfo[ 0 ]
					                                            ), productInfo[ 1 ],
					        productInfo[ 2 ], productInfo[ 3 ], productInfo[ 4 ], productInfo[ 5 ],
					        str( productInfo[ 6 ] ), productInfo[ 7 ], str( productInfo[ 8 ] ),
					        productInfo[ 9 ], productInfo[ 10 ], productInfo[ 11 ],
					        productInfo[ 12 ], ','.join( map( str, productInfo[ 13 ] ) ), ','.join(
					            map( str, productInfo[ 14 ] )
					            ), productInfo[ 15 ], productInfo[ 16 ], productInfo[ 17 ],
					        productInfo[ 18 ], productInfo[ 19 ], productInfo[ 20 ],
					        productInfo[ 21 ], productInfo[ 22 ], productInfo[ 23 ],
					        productInfo[ 24 ], productInfo[ 25 ]
					        )
					    )
					# print( materialGroup )
					for mid, matGroup in materialGroup.items():
						for mat in matGroup:
							self.DBHandler.execute(
							    """insert into quotation_products_materials(quotation_id, quotation_product_id, group_id,
							    gname, product_id, material_id, code, mname, unit, qty, thickness, formula) values
							    (?,?,?,?,?,?,?,?,?,?,?,?)""", (
							        self.quotationID, quoProductId, mid, mat[ 1 ], mat[ 2 ],
							        mat[ 3 ], mat[ 4 ], mat[ 5 ], mat[ 6 ], mat[ 7 ], mat[ 8 ],
							        mat[ 9 ]
							        )
							    )

					for aid, accGroup in accessoryGroup.items():
						for acc in accGroup:
							self.DBHandler.execute(
							    """insert into quotation_products_accessories(quotation_id, quotation_product_id, group_id,
							    gname, product_id, accessory_id,code, aname, unit, qty, rate, currency, formula) values
							    (?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
							        self.quotationID, quoProductId, aid, acc[ 1 ], acc[ 2 ],
							        acc[ 3 ], acc[ 4 ], acc[ 5 ], acc[ 6 ], acc[ 7 ], acc[ 8 ],
							        acc[ 9 ], acc[ 10 ]
							        )
							    )

			self.DBHandler.commit()

			buttonReply = QMessageBox.question(
			    self, 'Print', "Do you want to print ?", QMessageBox.Yes | QMessageBox.No,
			    QMessageBox.No
			    )
			if buttonReply == QMessageBox.Yes:
				self.printQuotation()
			self.resetQuotationForm()
			self.resetQuotationTable()

		else:
			QMessageBox.information( self, "Empty", "Please check form for empty fields !" )

	def updateQuotation( self, event=None ):
		if self.QuotationRefnoENT.hasAcceptableInput() and self.QuotationNameENT.hasAcceptableInput(
		) and self.QuotationItems != {}:

			buttonReply = QMessageBox.question(
			    self, 'Delete', "Are you sure, you want to Update ?",
			    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
			    )
			if buttonReply == QMessageBox.Yes:
				self.DBHandler.execute(
				    """update quotations set ref_no=?,date=?,currency=?,name=?,tel_no=?,email=?,address=?,
				   profile=?,finish=?,project=?,mesh=?,net_total=?,overhead=?,transport=?,profit=?,vat=?,grand_total=?
				   where quotation_id == ?""", (
				        self.QuotationRefnoENT.text(),
				        self.QuotationDatetime.dateTime().toPyDateTime(), self.currency,
				        self.QuotationNameENT.text(), self.QuotationTelnoENT.text(),
				        self.QuotationEmailENT.text(), self.QuotationAddENT.text(),
				        self.QuotationProfileENT.text(), self.QuotationFinishENT.text(),
				        self.QuotationProjectENT.text(), self.QuotationMeshENT.text(),
				        float( self.QuotationNetENT.text().replace( ',', '' )
				              ), float( self.QuotationOverENT.text().replace( ',', '' ) ),
				        float( self.QuotationTransportENT.text().replace( ',', '' )
				              ), float( self.QuotationProfitENT.text().replace( ',', '' )
				                       ), float( self.QuotationVatENT.text().replace( ',', '' ) ),
				        float( self.QuotationGrandENT.text().replace( ',', '' ) ), self.quotationID
				        )
				    )

				self.DBHandler.execute(
				    "delete from quotation_products_materials where quotation_id=?",
				    ( self.quotationID, )
				    )
				self.DBHandler.execute(
				    "delete from quotation_products_accessories where quotation_id=?",
				    ( self.quotationID, )
				    )

				# quotation_ID = self.quotationID
				for productID, productGroup in self.QuotationItems.items():

					for quoProductId, product in productGroup.items():
						productInfo = product[ 0 ]
						materialGroup = product[ 1 ]
						accessoryGroup = product[ 2 ]
						if len( productInfo ) == 27:
							self.DBHandler.execute(
							    """update quotation_products set quotation_id=?, quotation_product_id=?, product_id=?, product_name=?,
						    rate=?,width=?,height=?,qty=?,vent_flag=?,vent_height=?,fix_flag=?,fix_height=?,total_width=?,total_height=?,total_sqm=?,
						    mat_group=?,acc_group=?,aluminium=?,accessory=?,total=?, group_sqm=?, net_amount=?, currency=?, glass_type=?, glass_rate=?,
						    comment=?, materialgroup=?,accessorygroup=? where rowid == ?""", (
							        self.quotationID, quoProductId, int( productInfo[ 0 ] ),
							        productInfo[ 1 ], productInfo[ 2 ], productInfo[ 3 ],
							        productInfo[ 4 ], productInfo[ 5 ], str( productInfo[ 6 ] ),
							        productInfo[ 7 ], str( productInfo[ 8 ] ), productInfo[ 9 ],
							        productInfo[ 10 ], productInfo[ 11 ], productInfo[ 12 ],
							        ','.join( map( str, productInfo[ 13 ] ) ), ','.join(
							            map( str, productInfo[ 14 ] )
							            ), productInfo[ 15 ], productInfo[ 16 ], productInfo[ 17 ],
							        productInfo[ 18 ], productInfo[ 19 ], productInfo[ 20 ],
							        productInfo[ 21 ], productInfo[ 22 ], productInfo[ 23 ],
							        productInfo[ 24 ], productInfo[ 25 ], productInfo[ 26 ]
							        )
							    )
						else:

							self.DBHandler.execute(
							    """insert into quotation_products (quotation_id, quotation_product_id, product_id, product_name,
							    rate,width,height,qty,vent_flag,vent_height,fix_flag,fix_height,total_width,total_height,total_sqm,
							    mat_group,acc_group,aluminium,accessory,total, group_sqm, net_amount, currency, glass_type, glass_rate,
							    comment, materialgroup,accessorygroup)values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
							    (
							        self.quotationID, quoProductId, int( productInfo[ 0 ] ),
							        productInfo[ 1 ], productInfo[ 2 ], productInfo[ 3 ],
							        productInfo[ 4 ], productInfo[ 5 ], str( productInfo[ 6 ] ),
							        productInfo[ 7 ], str( productInfo[ 8 ] ), productInfo[ 9 ],
							        productInfo[ 10 ], productInfo[ 11 ], productInfo[ 12 ],
							        ','.join( map( str, productInfo[ 13 ] ) ), ','.join(
							            map( str, productInfo[ 14 ] )
							            ), productInfo[ 15 ], productInfo[ 16 ], productInfo[ 17 ],
							        productInfo[ 18 ], productInfo[ 19 ], productInfo[ 20 ],
							        productInfo[ 21 ], productInfo[ 22 ], productInfo[ 23 ],
							        productInfo[ 24 ], productInfo[ 25 ]
							        )
							    )
						# print( materialGroup )

						for mid, matGroup in materialGroup.items():
							for mat in matGroup:
								self.DBHandler.execute(
								    """insert into quotation_products_materials(quotation_id, quotation_product_id, group_id,
								    gname, product_id, material_id, code, mname, unit, qty, thickness, formula) values
								    (?,?,?,?,?,?,?,?,?,?,?,?)""", (
								        self.quotationID, quoProductId, mid, mat[ 1 ], mat[ 2 ],
								        mat[ 3 ], mat[ 4 ], mat[ 5 ], mat[ 6 ], mat[ 7 ], mat[ 8 ],
								        mat[ 9 ]
								        )
								    )

						for aid, accGroup in accessoryGroup.items():
							for acc in accGroup:
								self.DBHandler.execute(
								    """insert into quotation_products_accessories(quotation_id, quotation_product_id, group_id,
								    gname, product_id, accessory_id,code, aname, unit, qty, rate, currency, formula) values
								    (?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
								        self.quotationID, quoProductId, aid, acc[ 1 ], acc[ 2 ],
								        acc[ 3 ], acc[ 4 ], acc[ 5 ], acc[ 6 ], acc[ 7 ], acc[ 8 ],
								        acc[ 9 ], acc[ 10 ]
								        )
								    )
				for i in self.DeletedQuoProducts:
					self.DBHandler.execute( "delete from quotation_products where rowid=?", ( i, ) )
				self.DBHandler.commit()
				self.DBHandler.execute( "VACUUM" )
				buttonReply = QMessageBox.question(
				    self, 'Print', "Do you want to print ?", QMessageBox.Yes | QMessageBox.No,
				    QMessageBox.No
				    )
				if buttonReply == QMessageBox.Yes:
					self.printQuotation()
				self.resetQuotationForm()
				self.resetQuotationTable()
				self.stackedWidget.setCurrentWidget( self.AllquotationsPage )
				self.AllquotationsReset()

		else:
			QMessageBox.information( self, "Empty", "Please check form for empty fields !" )

# ----------------------------------------------------Start Product SubWindow------------------------------------------------

	def showQuotationSubWindow( self, event=None ):
		self.HomeFrame.setEnabled( False )
		self.QuoProWindow = QuotationSubWindow( parent=self )
		self.QuoProWindow.show()
		self.mode = "add"
		self.QuoProductID = 0
		for i in self.QuotationItems.values():
			self.QuoProductID += len( i )

		self.resetQuoProForm()
		self.configureQuoProductWindow()

	def editQuotationProdect( self, event=None, QuoProductID=None ):

		if QuoProductID or self.QuotationTable.currentRow() >= 0:

			self.HomeFrame.setEnabled( False )
			self.QuoProWindow = QuotationSubWindow( parent=self )

			self.QuoProWindow.show()
			self.resetQuoProForm()
			self.configureQuoProductWindow()

			self.QuoProWindow.QuoProAddPBT.setText( "Update" )

			if QuoProductID == None:
				n = self.QuotationTable.currentRow()
				temp = self.QuotationTable.item( n, 0 ).text().split( ":" )
			else:
				temp = QuoProductID.split( ":" )

			self.QuoProductID = int( temp[ 0 ] )
			self.productId = int( temp[ 1 ] )
			self.mode = "update"

			temp = self.QuotationItems[ self.productId ][ self.QuoProductID ][ 0 ]

			index = self.QuoProWindow.QuoProductCB.findText(
			    str( temp[ 1 ] ), QtCore.Qt.MatchFixedString
			    )
			if index >= 0:
				self.QuoProWindow.QuoProductCB.setCurrentIndex( index )

			self.QuoProWindow.QuoProMRENT.setText( str( "{:.2f}".format( temp[ 2 ] ) ) )
			self.QuoProWindow.QuoProWidthENT.setText( str( temp[ 3 ] ) )
			self.QuoProWindow.QuoProHeightENT.setText( str( temp[ 4 ] ) )
			self.QuoProWindow.QuoProQtyENT.setText( str( temp[ 5 ] ) )

			if temp[ 6 ]:
				self.QuoProWindow.QuoProVentCB.setCheckState( Qt.Checked )
				self.QuoProWindow.QuoProVHENT.setText( str( temp[ 7 ] ) )
			else:
				self.QuoProWindow.QuoProVentCB.setCheckState( Qt.Unchecked )
				self.QuoProVent()
			if temp[ 8 ]:
				self.QuoProWindow.QuoProFixCB.setCheckState( Qt.Checked )
				self.QuoProWindow.QuoProFHENT.setText( str( temp[ 9 ] ) )
			else:
				self.QuoProWindow.QuoProFixCB.setCheckState( Qt.Unchecked )
				self.QuoProFix()

			index = self.QuoProWindow.QuoProGlassCB.findText(
			    str( temp[ 21 ] ), QtCore.Qt.MatchFixedString
			    )
			if index >= 0:
				self.QuoProWindow.QuoProGlassCB.setCurrentIndex( index )

			self.QuoProWindow.QuoProGlassrateENT.setText( str( temp[ 22 ] ) )

			self.QuoProWindow.QuoProCommentENT.setText( temp[ 23 ] )

			# product_name = temp[ 1 ]

			product = self.ProductMaterialGroups[ self.productId ]
			for groupId in product.keys():
				parentObj = self.ProductMaterialsTableParentObjects[ groupId ]
				material_group = product[ groupId ]

				if material_group[ 0 ][ 0 ] in temp[ 13 ]:
					parentObj.setCheckState( 0, Qt.Checked )
				else:
					parentObj.setCheckState( 0, Qt.Unchecked )

			product = self.ProductAccessoryGroups[ self.productId ]
			for groupId in product.keys():
				parentObj = self.ProductAccessoriesTableParentObjects[ groupId ]
				accessory_group = product[ groupId ]

				if accessory_group[ 0 ][ 0 ] in temp[ 14 ]:
					parentObj.setCheckState( 0, Qt.Checked )
				else:
					parentObj.setCheckState( 0, Qt.Unchecked )
		else:
			QMessageBox.information( self, "Invalid Row", "Please select Product from table !" )

	def configureQuoProductWindow( self ):
		self.QuoProWindow.QuoProMRENT.setValidator( QDoubleValidator() )
		self.QuoProWindow.QuoProWidthENT.setValidator( QDoubleValidator() )
		self.QuoProWindow.QuoProHeightENT.setValidator( QDoubleValidator() )
		self.QuoProWindow.QuoProQtyENT.setValidator( QIntValidator() )

		self.QuoProWindow.QuoProVHENT.setValidator( QDoubleValidator() )
		self.QuoProWindow.QuoProHWVENT.setValidator( QDoubleValidator() )
		self.QuoProWindow.QuoProVSENT.setValidator( QDoubleValidator() )
		self.QuoProWindow.QuoProTHWVENT.setValidator( QDoubleValidator() )
		self.QuoProWindow.QuoProTSWVENT.setValidator( QDoubleValidator() )

		self.QuoProWindow.QuoProFHENT.setValidator( QDoubleValidator() )
		self.QuoProWindow.QuoProHWFENT.setValidator( QDoubleValidator() )
		self.QuoProWindow.QuoProFSENT.setValidator( QDoubleValidator() )
		self.QuoProWindow.QuoProTHWFENT.setValidator( QDoubleValidator() )
		self.QuoProWindow.QuoProTSWFENT.setValidator( QDoubleValidator() )

		self.QuoProWindow.QuoProHWVFENT.setValidator( QDoubleValidator() )
		self.QuoProWindow.QuoProTHWVFENT.setValidator( QDoubleValidator() )
		self.QuoProWindow.QuoProTSWVFENT.setValidator( QDoubleValidator() )
		self.QuoProWindow.QuoProTWENT.setValidator( QDoubleValidator() )
		self.QuoProWindow.QuoProTHENT.setValidator( QDoubleValidator() )
		self.QuoProWindow.QuoProTSENT.setValidator( QDoubleValidator() )
		self.QuoProWindow.QuoProTAluENT.setValidator( QDoubleValidator() )
		self.QuoProWindow.QuoProTAccENT.setValidator( QDoubleValidator() )
		self.QuoProWindow.QuoProAmountENT.setValidator( QDoubleValidator() )
		self.QuoProWindow.QuoProGlassrateENT.setValidator( QDoubleValidator() )

		self.QuoProWindow.QuoProCurrencyENT.setText( self.QuotationCurrencyCB.currentText() )

		QuoProductTableHeader = self.QuoProWindow.QuoProductTable.header()
		QuoProductTableHeader.setSectionResizeMode( 0, QHeaderView.ResizeToContents )
		QuoProductTableHeader.setSectionResizeMode( 1, QHeaderView.ResizeToContents )
		QuoProductTableHeader.setSectionResizeMode( 2, QHeaderView.ResizeToContents )
		QuoProductTableHeader.setSectionResizeMode( 3, QHeaderView.Stretch )
		QuoProductTableHeader.setSectionResizeMode( 4, QHeaderView.ResizeToContents )
		QuoProductTableHeader.setSectionResizeMode( 5, QHeaderView.ResizeToContents )
		QuoProductTableHeader.setSectionResizeMode( 6, QHeaderView.ResizeToContents )
		QuoProductTableHeader.setSectionResizeMode( 7, QHeaderView.ResizeToContents )
		QuoProductTableHeader.setSectionResizeMode( 8, QHeaderView.ResizeToContents )
		QuoProductTableHeader.setSectionResizeMode( 9, QHeaderView.ResizeToContents )
		QuoProductTableHeader.setSectionResizeMode( 10, QHeaderView.ResizeToContents )
		QuoProductTableHeader.setSectionResizeMode( 11, QHeaderView.ResizeToContents )
		QuoProductTableHeader.setSectionResizeMode( 12, QHeaderView.ResizeToContents )

		self.QuoProWindow.QuoProductCB.currentIndexChanged.connect( self.resetQuoProductTree )
		self.QuoProWindow.QuoProductTable.itemChanged.connect( self.checkCheckboxStatus )
		self.QuoProWindow.QuoProVentCB.stateChanged.connect( self.QuoProVent )
		self.QuoProWindow.QuoProFixCB.stateChanged.connect( self.QuoProFix )
		self.QuoProWindow.QuoProMRENT.textChanged.connect( self.autoFillQuoProductForm )
		self.QuoProWindow.QuoProWidthENT.textChanged.connect( self.autoFillQuoProductForm )
		self.QuoProWindow.QuoProHeightENT.textChanged.connect( self.autoFillQuoProductForm )
		self.QuoProWindow.QuoProQtyENT.textChanged.connect( self.autoFillQuoProductForm )
		self.QuoProWindow.QuoProVHENT.textChanged.connect( self.autoFillQuoProductForm )
		self.QuoProWindow.QuoProFHENT.textChanged.connect( self.autoFillQuoProductForm )

		self.QuoProWindow.QuoProHWVENT.textChanged.connect( self.autoFillQuoProductForm )
		self.QuoProWindow.QuoProVSENT.textChanged.connect( self.autoFillQuoProductForm )
		self.QuoProWindow.QuoProTHWVENT.textChanged.connect( self.autoFillQuoProductForm )
		self.QuoProWindow.QuoProTSWVENT.textChanged.connect( self.autoFillQuoProductForm )
		self.QuoProWindow.QuoProHWFENT.textChanged.connect( self.autoFillQuoProductForm )
		self.QuoProWindow.QuoProFSENT.textChanged.connect( self.autoFillQuoProductForm )
		self.QuoProWindow.QuoProTHWFENT.textChanged.connect( self.autoFillQuoProductForm )
		self.QuoProWindow.QuoProTSWFENT.textChanged.connect( self.autoFillQuoProductForm )
		self.QuoProWindow.QuoProHWVFENT.textChanged.connect( self.autoFillQuoProductForm )
		self.QuoProWindow.QuoProTHWVFENT.textChanged.connect( self.autoFillQuoProductForm )
		self.QuoProWindow.QuoProTSWVFENT.textChanged.connect( self.autoFillQuoProductForm )

		self.QuoProWindow.QuoProGlassCB.currentIndexChanged.connect( self.setGlass )
		self.QuoProWindow.QuoProGlassrateENT.textChanged.connect( self.addGlass )

		self.QuoProWindow.QuoProTWENT.textChanged.connect( self.autoFillQuoProductForm )
		self.QuoProWindow.QuoProTHENT.textChanged.connect( self.autoFillQuoProductForm )
		self.QuoProWindow.QuoProTSENT.textChanged.connect( self.autoFillQuoProductForm )

		self.QuoProWindow.QuoProHWVENT.setReadOnly( True )
		self.QuoProWindow.QuoProVSENT.setReadOnly( True )
		self.QuoProWindow.QuoProTHWVENT.setReadOnly( True )
		self.QuoProWindow.QuoProTSWVENT.setReadOnly( True )
		self.QuoProWindow.QuoProHWFENT.setReadOnly( True )
		self.QuoProWindow.QuoProFSENT.setReadOnly( True )
		self.QuoProWindow.QuoProTHWFENT.setReadOnly( True )
		self.QuoProWindow.QuoProTSWFENT.setReadOnly( True )
		self.QuoProWindow.QuoProHWVFENT.setReadOnly( True )
		self.QuoProWindow.QuoProTHWVFENT.setReadOnly( True )
		self.QuoProWindow.QuoProTSWVFENT.setReadOnly( True )
		self.QuoProWindow.QuoProTWENT.setReadOnly( True )
		self.QuoProWindow.QuoProTHENT.setReadOnly( True )
		self.QuoProWindow.QuoProTSENT.setReadOnly( True )
		self.QuoProWindow.QuoProTAluENT.setReadOnly( True )
		self.QuoProWindow.QuoProTAccENT.setReadOnly( True )
		self.QuoProWindow.QuoProAmountENT.setReadOnly( True )

		self.QuoProWindow.QuoProClosePBT.clicked.connect( self.closeQuoProductWindow )
		self.QuoProWindow.QuoProAddPBT.clicked.connect( self.addQuoProduct )

		temp = list( self.Products.values() )
		# print( temp )
		for i in range( len( temp ) ):
			self.QuoProWindow.QuoProductCB.insertItem( i, temp[ i ][ 1 ] )

		for i in range( len( self.Glasses ) ):
			self.QuoProWindow.QuoProGlassCB.insertItem( i, self.Glasses[ i ][ 1 ] )

	def resetQuoProForm( self ):
		self.QuoProWindow.QuoProMRENT.setText( '0' )
		self.QuoProWindow.QuoProWidthENT.setText( '0' )
		self.QuoProWindow.QuoProHeightENT.setText( '0' )
		self.QuoProWindow.QuoProQtyENT.setText( '1' )
		self.QuoProWindow.QuoProVHENT.setText( '0' )
		self.QuoProWindow.QuoProHWVENT.setText( '0' )
		self.QuoProWindow.QuoProVSENT.setText( '0' )
		self.QuoProWindow.QuoProTHWVENT.setText( '0' )
		self.QuoProWindow.QuoProTSWVENT.setText( '0' )

		self.QuoProWindow.QuoProFHENT.setText( '0' )
		self.QuoProWindow.QuoProHWFENT.setText( '0' )
		self.QuoProWindow.QuoProFSENT.setText( '0' )
		self.QuoProWindow.QuoProTHWFENT.setText( '0' )
		self.QuoProWindow.QuoProTSWFENT.setText( '0' )

		self.QuoProWindow.QuoProHWVFENT.setText( '0' )
		self.QuoProWindow.QuoProTHWVFENT.setText( '0' )
		self.QuoProWindow.QuoProTSWVFENT.setText( '0' )

		self.QuoProWindow.QuoProTWENT.setText( '0' )
		self.QuoProWindow.QuoProTHENT.setText( '0' )
		self.QuoProWindow.QuoProTSENT.setText( '0' )

		self.QuoProWindow.QuoProTAluENT.setText( '0' )
		self.QuoProWindow.QuoProTAccENT.setText( '0' )
		self.QuoProWindow.QuoProAmountENT.setText( '0' )

		self.QuoProWindow.QuoProVentCB.setCheckState( Qt.Unchecked )
		self.QuoProVent()
		self.QuoProWindow.QuoProFixCB.setCheckState( Qt.Unchecked )
		self.QuoProFix()

	def QuoProVent( self, event=None ):

		if self.QuoProWindow.QuoProVentCB.isChecked():
			self.QuoProWindow.QuoProVHENT.setReadOnly( False )
			self.vent = True
		else:
			self.QuoProWindow.QuoProVHENT.setReadOnly( True )
			self.vent = False
		self.autoFillQuoProductForm()

	def QuoProFix( self, event=None ):

		if self.QuoProWindow.QuoProFixCB.isChecked():
			self.QuoProWindow.QuoProFHENT.setReadOnly( False )
			self.fix = True
		else:
			self.QuoProWindow.QuoProFHENT.setReadOnly( True )
			self.fix = False
		self.autoFillQuoProductForm()

	def setGlass( self, event=None ):

		self.Glass = self.Glasses[ self.QuoProWindow.QuoProGlassCB.currentIndex() ]
		self.QuoProWindow.QuoProGlassrateENT.setText( str( self.Glass[ 2 ] ) )

	def addGlass( self, event=None ):
		# print( "Glass :", self.QuoProductID )
		for productId, accessorygroup in self.ProductAccessoryGroups.items():
			tempdict = {}
			for groupId, groupList in accessorygroup.items():
				# templist = []
				for acc in groupList:
					if acc[ 4 ] == "GD 0000/":
						# print( "yes" )
						acc[ 5 ] = self.Glass[ 1 ]
						acc[ 8 ] = float( self.QuoProWindow.QuoProGlassrateENT.text() )

		self.resetQuoProductTree()

	def resetQuoProductTree( self, event=None ):
		self.ProductMaterialsTableParentObjects = {}
		self.ProductMaterialsTableChildObjects = {}
		self.ProductAccessoriesTableParentObjects = {}
		self.ProductAccessoriesTableChildObjects = {}

		self.QuotationProductMaterialGroups = {}
		self.QuotationProductAccessoriesGroups = {}

		for i in range( self.QuoProWindow.QuoProductTable.topLevelItemCount() ):
			item = self.QuoProWindow.QuoProductTable.takeTopLevelItem( 0 )
		productId = self.QuoProWindow.QuoProductCB.currentIndex() + 1

		psrno = 1
		for groupId, groupList in self.ProductMaterialGroups[ productId ].items():
			parent = QtWidgets.QTreeWidgetItem(
			    self.QuoProWindow.QuoProductTable,
			    [ str( psrno ), "Material Group", "", groupList[ 0 ][ 1 ] ]
			    )
			self.ProductMaterialsTableParentObjects[ groupId ] = parent
			parent.setCheckState( 0, Qt.Checked )
			csrno = 1
			temp_list = []
			for temp in groupList:
				child = QtWidgets.QTreeWidgetItem(
				    parent, [
				        str( csrno ),
				        "Material",
				        str( temp[ 4 ] ),
				        str( temp[ 5 ] ),
				        str( temp[ 6 ] ),
				        str( temp[ 7 ] ),
				        str( 0 ),
				        str( temp[ 9 ] ),
				        str( 0 ),
				        str( 0 ),
				        str( 0 ),
				        str( 0 ),
				        str( 0 ),
				        ]
				    )
				temp_list.append( child )

				csrno += 1
			self.ProductMaterialsTableChildObjects[ groupId ] = temp_list

			psrno += 1

		for groupId, groupList in self.ProductAccessoryGroups[ productId ].items():
			parent = QtWidgets.QTreeWidgetItem(
			    self.QuoProWindow.QuoProductTable,
			    [ str( psrno ), "Accessory Group", '', groupList[ 0 ][ 1 ] ]
			    )
			self.ProductAccessoriesTableParentObjects[ groupId ] = parent
			parent.setCheckState( 0, Qt.Checked )

			csrno = 1
			temp_list = []
			for temp in groupList:
				child = QtWidgets.QTreeWidgetItem(
				    parent, [
				        str( csrno ),
				        "Accessory",
				        str( temp[ 4 ] ),
				        str( temp[ 5 ] ),
				        str( temp[ 6 ] ),
				        str( temp[ 7 ] ),
				        str( temp[ 8 ] ),
				        str( temp[ 10 ] ),
				        str( "-" ),
				        str( "-" ),
				        str( "-" ),
				        str( 0 ),
				        str( 0 ),
				        ]
				    )
				temp_list.append( child )
				csrno += 1
			self.ProductAccessoriesTableChildObjects[ groupId ] = temp_list

			psrno += 1
		self.autoFillQuoProductForm()

	def autoFillQuoProductForm( self, event=None ):
		w = h = qty = vh = hwv = vs = thwv = tswv = fh = hwf = fs = thwf = tswf = hwvf = thwvf = tswvf = tw = th = ts = 0

		if self.QuoProWindow.QuoProWidthENT.hasAcceptableInput():
			w = float( self.QuoProWindow.QuoProWidthENT.text() )
			self.QuoProWindow.QuoProWidthENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )
		else:
			w = 0
			self.QuoProWindow.QuoProWidthENT.setStyleSheet( "border: 1px solid red;" )

		if self.QuoProWindow.QuoProHeightENT.hasAcceptableInput():
			h = float( self.QuoProWindow.QuoProHeightENT.text() )
			self.QuoProWindow.QuoProHeightENT.setStyleSheet(
			    "border: 1px solid rgb(85, 170, 255);"
			    )
		else:
			h = 0
			self.QuoProWindow.QuoProHeightENT.setStyleSheet( "border: 1px solid red;" )

		if self.QuoProWindow.QuoProQtyENT.hasAcceptableInput():
			qty = int( self.QuoProWindow.QuoProQtyENT.text() )
			self.QuoProWindow.QuoProQtyENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )
		else:
			qty = 1
			self.QuoProWindow.QuoProQtyENT.setStyleSheet( "border: 1px solid red;" )

		if self.vent:

			if self.QuoProWindow.QuoProVHENT.hasAcceptableInput(
			) and float( self.QuoProWindow.QuoProVHENT.text() ) < h - fh:
				vh = float( self.QuoProWindow.QuoProVHENT.text() )
				self.QuoProWindow.QuoProVHENT.setStyleSheet(
				    "border: 1px solid rgb(85, 170, 255);"
				    )
			else:
				vh = 0
				self.QuoProWindow.QuoProVHENT.setStyleSheet( "border: 1px solid red;" )

			if self.QuoProWindow.QuoProHWVENT.hasAcceptableInput():
				hwv = float( self.QuoProWindow.QuoProHWVENT.text() )
				self.QuoProWindow.QuoProHWVENT.setStyleSheet(
				    "border: 1px solid rgb(85, 170, 255);"
				    )
			else:
				hwv = 0
				self.QuoProWindow.QuoProHWVENT.setStyleSheet( "border: 1px solid red;" )

		else:
			vh = 0
			hwv = 0
			vs = 0
			thwv = 0
			tswv = 0

		if self.fix:
			if self.QuoProWindow.QuoProFHENT.hasAcceptableInput(
			) and float( self.QuoProWindow.QuoProFHENT.text() ) < h - vh:
				fh = float( self.QuoProWindow.QuoProFHENT.text() )
				self.QuoProWindow.QuoProFHENT.setStyleSheet(
				    "border: 1px solid rgb(85, 170, 255);"
				    )
			else:
				fh = 0
				self.QuoProWindow.QuoProFHENT.setStyleSheet( "border: 1px solid red;" )

			if self.QuoProWindow.QuoProHWFENT.hasAcceptableInput():
				hwf = float( self.QuoProWindow.QuoProHWFENT.text() )
				self.QuoProWindow.QuoProHWFENT.setStyleSheet(
				    "border: 1px solid rgb(85, 170, 255);"
				    )
			else:
				hwf = 0
				self.QuoProWindow.QuoProHWFENT.setStyleSheet( "border: 1px solid red;" )

		else:
			fh = 0
			hwF = 0
			fs = 0
			thwF = 0
			tswF = 0

		if self.QuoProWindow.QuoProHWVFENT.hasAcceptableInput():
			hwvf = float( self.QuoProWindow.QuoProHWVFENT.text() )
			self.QuoProWindow.QuoProHWVFENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )
		else:
			hwvf = 0
			self.QuoProWindow.QuoProHWVFENT.setStyleSheet( "border: 1px solid red;" )

		if self.vent:
			self.QuoProWindow.QuoProHWVENT.setText( "{:.4f}".format( h - fh ) )
			self.QuoProWindow.QuoProVSENT.setText( "{:.4f}".format( w * vh ) )
			self.QuoProWindow.QuoProTHWVENT.setText( "{:.4f}".format( hwv * qty ) )
			self.QuoProWindow.QuoProTSWVENT.setText( "{:.4f}".format( w * hwv * qty ) )
		else:
			self.QuoProWindow.QuoProVHENT.setText( '0' )
			self.QuoProWindow.QuoProHWVENT.setText( '0' )
			self.QuoProWindow.QuoProVSENT.setText( '0' )
			self.QuoProWindow.QuoProTHWVENT.setText( '0' )
			self.QuoProWindow.QuoProTSWVENT.setText( '0' )

		if self.fix:
			self.QuoProWindow.QuoProHWFENT.setText( "{:.4f}".format( h - vh ) )
			self.QuoProWindow.QuoProFSENT.setText( "{:.4f}".format( w * fh ) )
			self.QuoProWindow.QuoProTHWFENT.setText( "{:.4f}".format( hwf * qty ) )
			self.QuoProWindow.QuoProTSWFENT.setText( "{:.4f}".format( w * hwf * qty ) )
		else:
			self.QuoProWindow.QuoProFHENT.setText( '0' )
			self.QuoProWindow.QuoProHWFENT.setText( '0' )
			self.QuoProWindow.QuoProFSENT.setText( '0' )
			self.QuoProWindow.QuoProTHWFENT.setText( '0' )
			self.QuoProWindow.QuoProTSWFENT.setText( '0' )

		self.QuoProWindow.QuoProHWVFENT.setText( "{:.4f}".format( h - vh - fh ) )
		self.QuoProWindow.QuoProTHWVFENT.setText( "{:.4f}".format( hwvf * qty ) )
		self.QuoProWindow.QuoProTSWVFENT.setText( "{:.4f}".format( w * hwvf * qty ) )

		self.QuoProWindow.QuoProTWENT.setText( "{:.4f}".format( w * qty ) )
		self.QuoProWindow.QuoProTHENT.setText( "{:.4f}".format( h * qty ) )
		self.QuoProWindow.QuoProTSENT.setText( "{:.4f}".format( w * h * qty ) )

		try:
			MetalRate = float( self.QuoProWindow.QuoProMRENT.text() )
			w = float( self.QuoProWindow.QuoProWidthENT.text() )
			h = float( self.QuoProWindow.QuoProHeightENT.text() )
			qty = int( self.QuoProWindow.QuoProQtyENT.text() )
			vh = float( self.QuoProWindow.QuoProVHENT.text() )
			hwv = float( self.QuoProWindow.QuoProHWVENT.text() )
			vs = float( self.QuoProWindow.QuoProVSENT.text() )
			thwv = float( self.QuoProWindow.QuoProTHWVENT.text() )
			tswv = float( self.QuoProWindow.QuoProTSWVENT.text() )
			fh = float( self.QuoProWindow.QuoProFHENT.text() )
			hwf = float( self.QuoProWindow.QuoProHWFENT.text() )
			fs = float( self.QuoProWindow.QuoProFSENT.text() )
			thwf = float( self.QuoProWindow.QuoProTHWFENT.text() )
			tswf = float( self.QuoProWindow.QuoProTSWFENT.text() )
			hwvf = float( self.QuoProWindow.QuoProHWVFENT.text() )
			thwvf = float( self.QuoProWindow.QuoProTHWVFENT.text() )
			tswvf = float( self.QuoProWindow.QuoProTSWVFENT.text() )
			tw = float( self.QuoProWindow.QuoProTWENT.text() )
			th = float( self.QuoProWindow.QuoProTHENT.text() )
			ts = float( self.QuoProWindow.QuoProTSENT.text() )
			totalalu = float( self.QuoProWindow.QuoProTAluENT.text().replace( ',', '' ) )
			totalacc = float( self.QuoProWindow.QuoProTAccENT.text().replace( ',', '' ) )
			amount = float( self.QuoProWindow.QuoProAmountENT.text().replace( ',', '' ) )
		except Exception as e:
			print( "1: ", e )

		try:
			# print( self.QuoProWindow.QuoProductCB.currentIndex() )
			product = self.ProductMaterialGroups[ self.QuoProWindow.QuoProductCB.currentIndex() +
			                                      1 ]

			for groupId in product.keys():
				parentObj = self.ProductMaterialsTableParentObjects[ groupId ]
				childObjs = self.ProductMaterialsTableChildObjects[ groupId ]
				total_weight = 0
				total_amount = 0
				material_group = product[ groupId ]
				l = len( childObjs )
				for childid in range( l ):
					childObj = childObjs[ childid ]
					matList = material_group[ childid ]

					formula = matList[ 9 ]
					result = eval( formula )
					extra = result + ( result * 0.1 )

					childObj.setText( 6, str( MetalRate ) )
					childObj.setText( 8, "{:.4f}".format( result ) )
					childObj.setText( 9, "{:.4f}".format( extra ) )

					unit = matList[ 7 ].split( '/' )
					kg = float( unit[ 0 ] )
					mtr = float( unit[ 1 ] )
					# pcs = math.ceil( extra / mtr )
					pcs = ( extra / mtr )

					childObj.setText( 10, "{:.2f}".format( pcs ) )
					weight = pcs * kg
					childObj.setText( 11, "{:.2f}".format( weight ) )
					amount = weight * MetalRate
					childObj.setText( 12, "{:,.2f}".format( amount ) )

					total_weight += weight
					total_amount += amount

				parentObj.setText( 11, "{:.2f}".format( total_weight ) )
				parentObj.setText( 12, "{:,.2f}".format( total_amount ) )
		except Exception as e:
			print( "2: ", e )
		try:
			product = self.ProductAccessoryGroups[ self.QuoProWindow.QuoProductCB.currentIndex() +
			                                       1 ]
			for groupId in product.keys():
				parentObj = self.ProductAccessoriesTableParentObjects[ groupId ]
				childObjs = self.ProductAccessoriesTableChildObjects[ groupId ]
				total_amount = 0
				accessory_group = product[ groupId ]
				l = len( childObjs )
				for childid in range( l ):
					childObj = childObjs[ childid ]
					acc = accessory_group[ childid ]

					formula = acc[ 10 ]
					unit = float( acc[ 7 ] )
					rate = float( acc[ 8 ] )
					currency = acc[ 9 ]

					if currency != self.currency:
						rate = self.convertCurrency( currency, self.currency, rate )

					result = float( eval( formula ) )
					total_qty = result * unit
					childObj.setText( 11, "{:.4f}".format( total_qty ) )
					amount = total_qty * rate
					childObj.setText( 12, "{:,.2f}".format( amount ) )
					total_amount += amount

				parentObj.setText( 12, "{:,.2f}".format( total_amount ) )
		except Exception as e:
			print( "3: ", e )

	def checkCheckboxStatus( self, event=None ):
		amount = 0
		aluminium = 0
		accessory = 0
		for obj in self.ProductMaterialsTableParentObjects.values():
			if obj.checkState( 0 ) == Qt.Checked:
				try:
					temp = float( obj.text( 12 ).replace( ',', '' ) )
					aluminium += temp
				except:
					pass

			else:
				print( 'item {} is Unchecked'.format( obj.text( 3 ) ) )

		for obj in self.ProductAccessoriesTableParentObjects.values():
			if obj.checkState( 0 ) == Qt.Checked:
				try:
					temp = float( obj.text( 12 ).replace( ',', '' ) )
					accessory += temp
				except:
					pass
			else:
				print( 'item {} is Unchecked'.format( obj.text( 3 ) ) )

		# aluminium = math.ceil( aluminium )
		# accessory = math.ceil( accessory )
		amount = aluminium + accessory
		self.QuoProWindow.QuoProTAluENT.setText( "{:,.2f}".format( aluminium ) )
		self.QuoProWindow.QuoProTAccENT.setText( "{:,.2f}".format( accessory ) )
		self.QuoProWindow.QuoProAmountENT.setText( "{:,.2f}".format( amount ) )

		self.QuoProWindow.QuoProTAluENT.setReadOnly( True )
		self.QuoProWindow.QuoProTAccENT.setReadOnly( True )
		self.QuoProWindow.QuoProAmountENT.setReadOnly( True )

	def addQuoProduct( self, event=None ):

		if float( self.QuoProWindow.QuoProMRENT.text() ) > 0 and float(
		    self.QuoProWindow.QuoProWidthENT.text()
		    ) > 0 and float( self.QuoProWindow.QuoProHeightENT.text()
		                    ) > 0 and int( self.QuoProWindow.QuoProQtyENT.text() ) > 0:
			productId = self.QuoProWindow.QuoProductCB.currentIndex() + 1
			product_name = self.Products[ productId ][ 1 ]
			MetalRate = float( self.QuoProWindow.QuoProMRENT.text() )
			w = float( self.QuoProWindow.QuoProWidthENT.text() )
			h = float( self.QuoProWindow.QuoProHeightENT.text() )
			qty = int( self.QuoProWindow.QuoProQtyENT.text() )
			vcheck = self.vent
			vh = float( self.QuoProWindow.QuoProVHENT.text() )
			fcheck = self.fix
			fh = float( self.QuoProWindow.QuoProFHENT.text() )
			tw = float( self.QuoProWindow.QuoProTWENT.text() )
			th = float( self.QuoProWindow.QuoProTHENT.text() )
			ts = float( self.QuoProWindow.QuoProTSENT.text() )
			glassRate = float( self.QuoProWindow.QuoProGlassrateENT.text() )

			materialCheck = []
			product = self.ProductMaterialGroups[ productId ]
			for groupId in product.keys():
				parentObj = self.ProductMaterialsTableParentObjects[ groupId ]
				if parentObj.checkState( 0 ) == Qt.Checked:
					# material_group = product[ groupId ]
					materialCheck.append( groupId )

			accessoryCheck = []
			product = self.ProductAccessoryGroups[ productId ]
			for groupId in product.keys():
				parentObj = self.ProductAccessoriesTableParentObjects[ groupId ]
				if parentObj.checkState( 0 ) == Qt.Checked:
					# accessory_group = product[ groupId ]
					accessoryCheck.append( groupId )

			totalalu = float( self.QuoProWindow.QuoProTAluENT.text().replace( ',', '' ) )
			totalacc = float( self.QuoProWindow.QuoProTAccENT.text().replace( ',', '' ) )
			amount = float( self.QuoProWindow.QuoProAmountENT.text().replace( ',', '' ) )
			total_amo = amount
			total_sqm = ts
			itemInfo = [ [], {}, {} ]
			rowid = None

			if self.mode == "add":
				self.QuoProductID = 0
				for i in self.QuotationItems.values():
					self.QuoProductID += len( i )
			elif self.mode == "update":
				if productId != self.productId:
					t1 = 0
					t2 = 0
					if len( self.QuotationItems[ self.productId ][ self.QuoProductID ][ 0 ] ) == 27:
						rowid = self.QuotationItems[ self.productId ][ self.QuoProductID
						                                              ][ 0 ][ -1 ]

					del self.QuotationItems[ self.productId ][ self.QuoProductID ]

					for key, Products in self.QuotationItems[ self.productId ].items():

						t1 += Products[ 0 ][ 17 ]
						t2 += Products[ 0 ][ 12 ]

					for i in self.QuotationItems[ self.productId ].keys():
						self.QuotationItems[ self.productId ][ i ][ 0 ][ 18 ] = t2
						self.QuotationItems[ self.productId ][ i ][ 0 ][ 19 ] = t1

			if materialCheck != [] and accessoryCheck != []:

				if productId in self.QuotationItems.keys():
					temp = self.QuotationItems[ productId ]
					if self.QuoProductID in temp.keys():
						itemInfo = temp[ self.QuoProductID ]

				else:
					temp = {}

				for key, Products in temp.items():
					if key != self.QuoProductID:
						total_amo += Products[ 0 ][ 17 ]
						total_sqm += Products[ 0 ][ 12 ]

				for i in temp.keys():
					temp[ i ][ 0 ][ 18 ] = total_sqm
					temp[ i ][ 0 ][ 19 ] = total_amo

				if len( itemInfo[ 0 ] ) == 27 or rowid != None:
					if rowid == None:
						rowid = itemInfo[ 0 ][ -1 ]
					item = [
					    productId, product_name, MetalRate, w, h, qty, vcheck, vh, fcheck, fh, tw,
					    th, ts, materialCheck, accessoryCheck, totalalu, totalacc, amount,
					    total_sqm, total_amo, self.currency, self.Glass[ 1 ], glassRate,
					    self.QuoProWindow.QuoProCommentENT.text(), self.Products[ productId ][ 2 ],
					    self.Products[ productId ][ 3 ], rowid
					    ]
				else:
					item = [
					    productId, product_name, MetalRate, w, h, qty, vcheck, vh, fcheck, fh, tw,
					    th, ts, materialCheck, accessoryCheck, totalalu, totalacc, amount,
					    total_sqm, total_amo, self.currency, self.Glass[ 1 ], glassRate,
					    self.QuoProWindow.QuoProCommentENT.text(), self.Products[ productId ][ 2 ],
					    self.Products[ productId ][ 3 ]
					    ]

				# matGroupCopy = self.ProductMaterialGroups[ productId ].copy()
				# accGroupCopy = self.ProductAccessoryGroups[ productId ].copy()
				matGroupCopy = copy.deepcopy( self.ProductMaterialGroups[ productId ] )
				accGroupCopy = copy.deepcopy( self.ProductAccessoryGroups[ productId ] )

				itemInfo = [ item, matGroupCopy, accGroupCopy ]

				temp[ self.QuoProductID ] = itemInfo

				self.QuotationItems[ productId ] = temp

			else:
				QMessageBox.information(
				    self, "Unchecked", "No material or accessory group selected !"
				    )

			# print( self.QuotationItems )
			if self.mode == "update":
				self.HomeFrame.setEnabled( True )
				self.QuoProWindow.close()
			self.resetQuotationTable()
		else:
			QMessageBox.information( self, "Invalis", "Kindly, check your input !" )

	def closeQuoProductWindow( self, event=None ):
		self.HomeFrame.setEnabled( True )
		self.QuoProWindow.close()


# ----------------------------------------------------End Product SubWindow---------------------------------------------------
