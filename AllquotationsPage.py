import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from datetime import *
import sqlite3
from Utility import UtilityWindow
# from ProductsPage import ProductsPageFunctions


class AllquotationsPageFunctions:

	def initAllquotationsPage( self, event ):
		self.Heading.setText( "Allquotations" )
		# self.DBHandler = DBHandler
		self.rowid = None
		self.stackedWidget.setCurrentWidget( self.AllquotationsPage )
		self.AllquotationsReset()

	def AllquotationsReset( self, event=None ):

		n = self.AllquotationsTable.rowCount()
		for i in range( n ):
			self.AllquotationsTable.removeRow( 0 )

		result = self.DBHandler.execute(
		    """select date from quotations ORDER BY date(date) ASC """
		    ).fetchall()
		if result != []:

			self.AllquotationsfromDatetime.setDateTime( result[ 0 ][ 0 ] )
			self.AllquotationstoDatetime.setDateTime( result[ len( result ) - 1 ][ 0 ] )
			self.fetchQuotationsDatewise()
		else:
			QMessageBox.information( self, "Empty", "Quotations Not Found !" )

	def fetchQuotationsDatewise( self, event=None ):
		n = self.AllquotationsTable.rowCount()
		for i in range( n ):
			self.AllquotationsTable.removeRow( 0 )

		result = self.DBHandler.execute(
		    """select * from quotations where date between ? and ?""", (
		        self.AllquotationsfromDatetime.dateTime().toPyDateTime(),
		        self.AllquotationstoDatetime.dateTime().toPyDateTime()
		        )
		    )
		for row in result:

			temp = self.AllquotationsTable.rowCount()
			self.AllquotationsTable.insertRow( temp )
			self.AllquotationsTable.setItem( temp, 0, QTableWidgetItem( str( row[ 0 ] ) ) )
			self.AllquotationsTable.setItem( temp, 1, QTableWidgetItem( str( row[ 1 ] ) ) )
			self.AllquotationsTable.setItem( temp, 2, QTableWidgetItem( str( row[ 2 ] ) ) )
			self.AllquotationsTable.setItem( temp, 3, QTableWidgetItem( str( row[ 3 ] ) ) )
			self.AllquotationsTable.setItem( temp, 4, QTableWidgetItem( str( row[ 4 ] ) ) )
			self.AllquotationsTable.setItem( temp, 5, QTableWidgetItem( str( row[ 10 ] ) ) )
			self.AllquotationsTable.setItem( temp, 6, QTableWidgetItem( str( row[ 5 ] ) ) )
			self.AllquotationsTable.setItem( temp, 7, QTableWidgetItem( str( row[ 6 ] ) ) )
			self.AllquotationsTable.setItem( temp, 8, QTableWidgetItem( str( row[ 7 ] ) ) )
			self.AllquotationsTable.setItem( temp, 9, QTableWidgetItem( str( row[ 8 ] ) ) )
			self.AllquotationsTable.setItem( temp, 10, QTableWidgetItem( str( row[ 11 ] ) ) )
			self.AllquotationsTable.setItem( temp, 11, QTableWidgetItem( str( row[ 17 ] ) ) )

	def EditAllquotations( self, event=None ):
		if self.AllquotationsTable.currentRow() >= 0:
			n = self.AllquotationsTable.currentRow()
			self.initEditQuotationPage( int( self.AllquotationsTable.item( n, 0 ).text() ) )
		else:
			QMessageBox.information( self, "Invalid Row", "Please select Quotation from table !" )

	def PrintAllquotations( self, event=None ):
		if self.AllquotationsTable.currentRow() >= 0:
			n = self.AllquotationsTable.currentRow()
			qtano = int( self.AllquotationsTable.item( n, 0 ).text() )
			pq = UtilityWindow( parent=self )
			pq.show()
			pq.PrintWindow( self.DBHandler, qtano )
		else:
			QMessageBox.information( self, "Invalid Row", "Please select Quotation from table !" )

	def CopyQuotation( self, event=None ):
		if self.AllquotationsTable.currentRow() >= 0:

			buttonReply = QMessageBox.question(
			    self, 'Copy', "Are you sure, you want to Copy ?", QMessageBox.Yes | QMessageBox.No,
			    QMessageBox.No
			    )
			if buttonReply == QMessageBox.Yes:
				QuotationItems = {}
				n = self.AllquotationsTable.currentRow()
				QuotationItems = {}
				self.quotationID = int( self.AllquotationsTable.item( n, 0 ).text() )
				# self.ProductID = 0

				Quotation = self.DBHandler.execute(
				    """select * from quotations where quotation_id == ?""", ( self.quotationID, )
				    ).fetchone()
				quotationID = self.DBHandler.execute(
				    """select quotation_id from quotations order by quotation_id DESC limit 1"""
				    ).fetchone()[ 0 ] + 1
				QuotationRefnoENT = "GDAS/00/{:05d}/{:04d}".format(
				    int( quotationID ), int( QtCore.QDate.currentDate().toString().split()[ -1 ] )
				    )
				QuotationDatetime = QtCore.QDateTime.currentDateTime()
				QuotationCurrencyCB = str( Quotation[ 3 ] )
				QuotationNameENT = Quotation[ 4 ]
				QuotationTelnoENT = Quotation[ 5 ]
				QuotationEmailENT = Quotation[ 6 ]
				QuotationAddENT = Quotation[ 7 ]
				QuotationProfileENT = Quotation[ 8 ]
				QuotationFinishENT = Quotation[ 9 ]
				QuotationProjectENT = Quotation[ 10 ]
				QuotationMeshENT = Quotation[ 11 ]
				QuotationNetENT = Quotation[ 12 ]
				QuotationOverENT = Quotation[ 13 ]
				QuotationTransportENT = Quotation[ 14 ]
				QuotationProfitENT = Quotation[ 15 ]
				QuotationVatENT = Quotation[ 16 ]
				QuotationGrandENT = Quotation[ 17 ]

				result = self.DBHandler.execute(
				    """select quotation_product_id, product_id, product_name,rate,width,
					height,qty,vent_flag,vent_height,fix_flag,fix_height,total_width,total_height,total_sqm,
					mat_group,acc_group,aluminium,accessory,total,group_sqm,net_amount,currency,glass_type,
					glass_rate,comment,materialgroup,accessorygroup,rowid from quotation_products where quotation_id == ? ORDER BY quotation_product_id ASC""",
				    ( self.quotationID, )
				    ).fetchall()

				QuoProduct = map( list, result )

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

					if productId not in QuotationItems.keys():
						QuotationItems[ productId ] = {}

					QuotationItems[ productId ][ quoProductId ] = templist

				self.DBHandler.execute(
				    """insert into quotations (quotation_id,ref_no,date,currency,name,tel_no,email,address,
				   profile,finish,project,mesh,net_total,overhead,transport,profit,vat,grand_total)
				   values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
				        quotationID, QuotationRefnoENT, QuotationDatetime.toPyDateTime(),
				        QuotationCurrencyCB, QuotationNameENT, QuotationTelnoENT, QuotationEmailENT,
				        QuotationAddENT, QuotationProfileENT, QuotationFinishENT,
				        QuotationProjectENT, QuotationMeshENT, float( QuotationNetENT ),
				        float( QuotationOverENT ), float( QuotationTransportENT ),
				        float( QuotationProfitENT ), float( QuotationVatENT ),
				        float( QuotationGrandENT )
				        )
				    )

				# quotation_ID = int( self.QuotationQtanoENT.text() )
				for productId, productGroup in QuotationItems.items():
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
						        quotationID, quoProductId, int( productInfo[ 0 ] ),
						        productInfo[ 1 ], productInfo[ 2 ], productInfo[ 3 ],
						        productInfo[ 4 ], productInfo[ 5 ], str( productInfo[ 6 ] ),
						        productInfo[ 7 ], str( productInfo[ 8 ] ), productInfo[ 9 ],
						        productInfo[ 10 ], productInfo[ 11 ], productInfo[ 12 ], ','.join(
						            map( str, productInfo[ 13 ] )
						            ), ','.join( map( str, productInfo[ 14 ] )
						                        ), productInfo[ 15 ], productInfo[ 16 ],
						        productInfo[ 17 ], productInfo[ 18 ], productInfo[ 19 ],
						        productInfo[ 20 ], productInfo[ 21 ], productInfo[ 22 ],
						        productInfo[ 23 ], productInfo[ 24 ], productInfo[ 25 ]
						        )
						    )
						# print( materialGroup )
						for mid, matGroup in materialGroup.items():
							for mat in matGroup:
								self.DBHandler.execute(
								    """insert into quotation_products_materials(quotation_id, quotation_product_id, group_id,
								    gname, product_id, material_id, code, mname, unit, qty, thickness, formula) values
								    (?,?,?,?,?,?,?,?,?,?,?,?)""", (
								        quotationID, quoProductId, mid, mat[ 1 ], mat[ 2 ],
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
								        quotationID, quoProductId, aid, acc[ 1 ], acc[ 2 ],
								        acc[ 3 ], acc[ 4 ], acc[ 5 ], acc[ 6 ], acc[ 7 ], acc[ 8 ],
								        acc[ 9 ], acc[ 10 ]
								        )
								    )

				self.DBHandler.commit()

				self.AllquotationsReset()
		else:
			QMessageBox.information( self, "Invalid Row", "Please select Quotation from table !" )

	def DeleteQuotationPermenent( self, event=None ):
		if self.AllquotationsTable.currentRow() >= 0:
			n = self.AllquotationsTable.currentRow()
			ID = int( self.AllquotationsTable.item( n, 0 ).text() )
			buttonReply = QMessageBox.question(
			    self, 'Delete', "Are you sure, you want to Delete ?",
			    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
			    )
			if buttonReply == QMessageBox.Yes:
				self.DBHandler.execute(
				    "delete from quotation_products_materials where quotation_id=?", ( ID, )
				    )
				self.DBHandler.execute(
				    "delete from quotation_products_accessories where quotation_id=?", ( ID, )
				    )
				self.DBHandler.execute(
				    "delete from quotation_products where quotation_id=?", ( ID, )
				    )
				self.DBHandler.execute( "delete from quotations where quotation_id=?", ( ID, ) )

				self.DBHandler.commit()
				self.DBHandler.execute( "VACUUM" )
				self.AllquotationsReset()

		else:
			QMessageBox.information( self, "Invalid Row", "Please select Quotation from table !" )
