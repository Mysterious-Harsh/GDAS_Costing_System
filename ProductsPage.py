import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from datetime import *
import sqlite3
import copy


class ProductSubWindow( QtWidgets.QMainWindow ):

	def __init__( self, *args, **kwargs ):
		super().__init__( *args, **kwargs )
		uic.loadUi( "UI/ProductSubWindow.ui", self )
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
		self.ProMatClosePBT.clicked.connect( self.exit )
		self.ProAccClosePBT.clicked.connect( self.exit )

	def exit( self, event ):
		self.close()


class ProductsPageFunctions:

	def initProductPage( self, event ):
		self.Heading.setText( "Products" )
		self.ProductMaterialGroups = {}
		self.ProductAccessoryGroups = {}
		self.DeletedProductAccessory = []
		self.DeletedProductMaterial = []
		self.productID = 0
		self.stackedWidget.setCurrentWidget( self.ProductPage )
		self.ProductDeletePBT.setEnabled( True )

		self.ProductSavePBT.setText( "Save" )
		self.ProductSavePBT.clicked.disconnect()
		self.ProductSavePBT.clicked.connect( self.saveProduct )

		self.resetProductTree()
		self.validateProductInput()
		self.resetProductForm()

	def initEditProductPage( self, productId ):

		self.Heading.setText( "Products" )
		self.stackedWidget.setCurrentWidget( self.ProductPage )
		self.ProductDeletePBT.setEnabled( False )

		self.DeletedProductAccessory = []
		self.DeletedProductMaterial = []
		self.ProductMaterialGroups = {}
		self.ProductAccessoryGroups = {}
		self.productID = productId
		self.ProductResult = self.DBHandler.execute(
		    """select * from products where product_id == ?""", ( self.productID, )
		    ).fetchall()[ 0 ]
		try:

			for MID in self.ProductResult[ 5 ].split( ',' ):

				if MID not in [ '', "", ' ', " ", None ]:
					result = self.DBHandler.execute(
					    """select materials.material_id,materials.date,materials.code,materials.name,materials.unit,materials.quantity,
						materials.thickness,material_group.formula,material_group.rowid from material_group inner join materials on
														materials.material_id = material_group.material_id
														where product_id == ? and group_id == ?""", ( self.productID, int( MID ) )
					    ).fetchall()
					material_group = list( map( list, result ) )
					gname = self.DBHandler.execute(
					    """select name from material_group
							where product_id == ? and group_id == ?""", ( self.productID, int( MID ) )
					    ).fetchone()[ 0 ]

					self.ProductMaterialGroups[ gname ] = material_group
		except Exception as e:
			print( "initEditProductPage ", e )
			self.logger.exception( "initEditProductPage", exc_info=True )

		try:

			for AID in self.ProductResult[ 6 ].split( ',' ):

				if AID not in [ '', "", ' ', " ", None ]:

					result = self.DBHandler.execute(
					    """select accessories.accessory_id,accessories.date,accessories.code,accessories.name,accessories.unit,accessories.quantity,accessories.rate,
						accessories.currency,accessory_group.formula,accessory_group.rowid from accessory_group inner join accessories on
														accessories.accessory_id = accessory_group.accessory_id
														where product_id == ? and group_id == ?""", ( self.productID, int( AID ) )
					    ).fetchall()
					accessory_group = list( map( list, result ) )
					gname = self.DBHandler.execute(
					    """select name from accessory_group
							where product_id == ? and group_id == ?""", ( self.productID, int( AID ) )
					    ).fetchone()[ 0 ]
					self.ProductAccessoryGroups[ gname ] = accessory_group
		except Exception as e:
			print( "initEditProductPage ", e )
			self.logger.exception( "initEditProductPage", exc_info=True )

		self.ProductIDENT.setText( str( self.productID ) )
		self.ProductIDENT.setReadOnly( True )
		self.ProductDatetime.setDateTime( self.ProductResult[ 1 ] )
		self.ProductNameENT.setText( self.ProductResult[ 2 ] )
		self.ProductProfileENT.setText( self.ProductResult[ 3 ] )
		self.ProductCommentENT.setText( self.ProductResult[ 4 ] )

		self.ProductSavePBT.setText( "Update" )
		self.ProductSavePBT.clicked.disconnect()
		self.ProductSavePBT.clicked.connect( self.updateProduct )
		self.resetProductTree()

	def validateProductInput( self, event=None ):
		if not self.ProductIDENT.hasAcceptableInput():
			self.ProductIDENT.setStyleSheet( "border: 1px solid red;" )
		else:
			self.ProductIDENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )

		if self.ProductNameENT.text() in [ "", " " ]:
			self.ProductNameENT.setStyleSheet( "border: 1px solid red;" )
		else:
			self.ProductNameENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )

		if self.ProductProfileENT.text() in [ "", " " ]:
			self.ProductProfileENT.setStyleSheet( "border: 1px solid red;" )
		else:
			self.ProductProfileENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )

		self.ProductCommentENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )

	def resetProductForm( self ):
		self.ProductMaterialGroups = {}
		self.ProductAccessoryGroups = {}
		self.DeletedProductAccessory = []
		self.DeletedProductMaterial = []
		result = self.DBHandler.execute(
		    """select product_id from products order by product_id DESC limit 1"""
		    ).fetchone()
		if result == None:
			self.productID = 1
		else:
			self.productID = result[ 0 ] + 1

		self.ProductIDENT.setText( str( self.productID ) )
		self.ProductIDENT.setReadOnly( True )
		self.ProductDatetime.setDateTime( QtCore.QDateTime.currentDateTime() )
		self.ProductNameENT.clear()
		self.ProductProfileENT.clear()
		self.ProductCommentENT.clear()

	def updateProduct( self, event=None ):
		if self.ProductMaterialGroups != {} and self.ProductAccessoryGroups != {} and self.ProductNameENT.text(
		) not in [ "", " " ] and self.ProductProfileENT.text() not in [ "", " " ]:
			MGList = []
			AGList = []

			ML = self.ProductResult[ 5 ].split( ',' )

			AL = self.ProductResult[ 6 ].split( ',' )

			material_iter = iter( self.ProductMaterialGroups.items() )

			for materialGroupID in ML:
				if materialGroupID.isdigit():
					try:
						gname, glist = next( material_iter )
					except:
						break
					MGList.append( str( materialGroupID ) )

					# print( gname, glist )
					for temp in glist:
						if len( temp ) == 9:
							self.DBHandler.execute(
							    """update  material_group set name=?, group_id=?, product_id=?, material_id=?, formula=? where rowid == ?""",
							    (
							        gname, int( materialGroupID ), self.productID, temp[ 0 ],
							        temp[ 7 ], temp[ 8 ]
							        )
							    )
						else:
							self.DBHandler.execute(
							    """insert into material_group (name, group_id, product_id, material_id, formula) values (?,?,?,?,?)""",
							    (
							        gname, int( materialGroupID ), self.productID, temp[ 0 ],
							        temp[ 7 ]
							        )
							    )

			materialGroupID = result = self.DBHandler.execute(
			    """select group_id from material_group order by group_id DESC limit 1"""
			    ).fetchone()[ 0 ] + 1
			for gname, glist in material_iter:
				MGList.append( str( materialGroupID ) )
				for temp in glist:
					self.DBHandler.execute(
					    """insert into material_group (name, group_id, product_id, material_id, formula) values (?,?,?,?,?)""",
					    ( gname, materialGroupID, self.productID, temp[ 0 ], temp[ 7 ] )
					    )
				materialGroupID += 1

			for i in self.DeletedProductMaterial:
				self.DBHandler.execute( "delete from material_group where rowid=?", ( i, ) )

			accessory_iter = iter( self.ProductAccessoryGroups.items() )
			for accessoryGroupID in AL:
				if accessoryGroupID.isdigit():
					try:
						gname, glist = next( accessory_iter )
					except:
						break
					AGList.append( str( accessoryGroupID ) )
					for temp in glist:
						if len( temp ) == 10:
							self.DBHandler.execute(
							    """update  accessory_group  set name=?, group_id=?, product_id=?, accessory_id=?, formula=? where rowid == ?""",
							    (
							        gname, int( accessoryGroupID ), self.productID, temp[ 0 ],
							        temp[ 8 ], temp[ 9 ]
							        )
							    )
						else:
							self.DBHandler.execute(
							    """insert into accessory_group (name, group_id, product_id, accessory_id, formula) values (?,?,?,?,?)""",
							    (
							        gname, int( accessoryGroupID ), self.productID, temp[ 0 ],
							        temp[ 8 ]
							        )
							    )

			accessoryGroupID = self.DBHandler.execute(
			    """select group_id from accessory_group order by group_id DESC limit 1"""
			    ).fetchone()[ 0 ] + 1
			for gname, glist in accessory_iter:
				AGList.append( str( accessoryGroupID ) )
				for temp in glist:
					self.DBHandler.execute(
					    """insert into accessory_group (name, group_id, product_id, accessory_id, formula) values (?,?,?,?,?)""",
					    ( gname, accessoryGroupID, self.productID, temp[ 0 ], temp[ 8 ] )
					    )
				accessoryGroupID += 1

			for i in self.DeletedProductAccessory:
				self.DBHandler.execute( "delete from accessory_group where rowid=?", ( i, ) )

			self.DBHandler.execute(
			    """update  products set date=?, name=?, profile=?, comment=?, materialgroup=?, accessorygroup=? where product_id == ?""",
			    (
			        self.ProductDatetime.dateTime().toPyDateTime(), self.ProductNameENT.text(),
			        self.ProductProfileENT.text(), self.ProductCommentENT.text(),
			        ",".join( MGList ), ",".join( AGList ), self.productID
			        )
			    )

			self.DBHandler.commit()
			self.DBHandler.execute( "VACUUM" )
			self.resetProductForm()
			self.stackedWidget.setCurrentWidget( self.AllproductsPage )
			self.AllproductReset()
		else:
			QMessageBox.information( self, "Empty", "Empty Fields !" )

	def saveProduct( self, event=None ):

		if self.ProductMaterialGroups != {} and self.ProductAccessoryGroups != {} and self.ProductNameENT.text(
		) not in [ "", " " ] and self.ProductProfileENT.text() not in [ "", " " ]:

			MGList = []
			AGList = []
			result = self.DBHandler.execute(
			    """select group_id from material_group order by group_id DESC limit 1"""
			    ).fetchone()
			if result == None:
				materialGroupID = 1
			else:
				materialGroupID = result[ 0 ] + 1

			result = self.DBHandler.execute(
			    """select group_id from accessory_group order by group_id DESC limit 1"""
			    ).fetchone()
			if result == None:
				accessoryGroupID = 1
			else:
				accessoryGroupID = result[ 0 ] + 1

			# productID = int( self.ProductIDENT.text() )

			for gname, glist in self.ProductMaterialGroups.items():
				MGList.append( str( materialGroupID ) )
				for temp in glist:
					self.DBHandler.execute(
					    """insert into material_group (name, group_id, product_id, material_id, formula) values (?,?,?,?,?)""",
					    ( gname, materialGroupID, self.productID, temp[ 0 ], temp[ 7 ] )
					    )
				materialGroupID += 1

			for gname, glist in self.ProductAccessoryGroups.items():
				AGList.append( str( accessoryGroupID ) )
				for temp in glist:
					self.DBHandler.execute(
					    """insert into accessory_group (name, group_id, product_id, accessory_id, formula) values (?,?,?,?,?)""",
					    ( gname, accessoryGroupID, self.productID, temp[ 0 ], temp[ 8 ] )
					    )
				accessoryGroupID += 1

			self.DBHandler.execute(
			    """insert into products (product_id,date, name, profile, comment, materialgroup, accessorygroup) values (?,?,?,?,?,?,?)""",
			    (
			        self.productID, self.ProductDatetime.dateTime().toPyDateTime(),
			        self.ProductNameENT.text(), self.ProductProfileENT.text(),
			        self.ProductCommentENT.text(), ",".join( MGList ), ",".join( AGList )
			        )
			    )

			self.DBHandler.commit()
			self.resetProductForm()
			self.resetProductTree()
		else:
			QMessageBox.information( self, "Empty", "Empty Fields !" )

	def editGroup( self, event=None ):

		try:
			if self.ProductTable.indexOfTopLevelItem( self.ProductTable.currentItem() ) == -1:
				parent = self.ProductTable.currentItem().parent()
				Type = parent.text( 1 )
				name = parent.text( 2 )
				item = parent.indexOfChild( self.ProductTable.currentItem() )
				# print( Type, name, item )
			else:
				parent = self.ProductTable.currentItem()
				Type = parent.text( 1 )
				name = parent.text( 2 )
				# print( Type, name, -1 )

			if Type in [ "Material Group", "Material" ]:
				self.ShowAddMaterialWindow(
				    GroupName=name,
				    MaterialGroup=copy.deepcopy( self.ProductMaterialGroups[ name ] )
				    )
			elif Type in [ "Accessory Group", "Accessory" ]:
				self.ShowAddAccessoryWindow(
				    GroupName=name,
				    AccessoryGroup=copy.deepcopy( self.ProductAccessoryGroups[ name ] )
				    )
		except Exception as e:
			QMessageBox.critical( self, "GDAS-Error", "editGroup : " + e )

	def deleteGroup( self, event=None ):

		try:
			if self.ProductTable.indexOfTopLevelItem( self.ProductTable.currentItem() ) == -1:
				parent = self.ProductTable.currentItem().parent()
				Type = parent.text( 1 )
				name = parent.text( 2 )
				item = parent.indexOfChild( self.ProductTable.currentItem() )
			else:
				parent = self.ProductTable.currentItem()
				Type = parent.text( 1 )
				name = parent.text( 2 )

			if Type in [ "Material Group", "Material" ]:
				del self.ProductMaterialGroups[ name ]

			elif Type in [ "Accessory Group", "Accessory" ]:
				del self.ProductAccessoryGroups[ name ]
		except Exception as e:
			QMessageBox.critical( self, "GDAS-Error", "deleteGroup : " + e )

		self.resetProductTree()

	def resetProductTree( self, event=None ):
		for i in range( self.ProductTable.topLevelItemCount() ):
			item = self.ProductTable.takeTopLevelItem( 0 )

		psrno = 1
		for gname, glist in self.ProductMaterialGroups.items():
			parent = QtWidgets.QTreeWidgetItem(
			    self.ProductTable, [ str( psrno ), "Material Group", gname ]
			    )
			parent.setCheckState( 0, Qt.Unchecked )
			csrno = 1
			for temp in glist:
				child = QtWidgets.QTreeWidgetItem(
				    parent, [
				        str( csrno ), "Material",
				        str( temp[ 3 ] ),
				        str( temp[ 2 ] ),
				        str( temp[ 4 ] ),
				        str( temp[ 5 ] ), "-",
				        str( temp[ 7 ] )
				        ]
				    )
				csrno += 1
			psrno += 1

		for gname, glist in self.ProductAccessoryGroups.items():
			parent = QtWidgets.QTreeWidgetItem(
			    self.ProductTable, [ str( psrno ), "Accessory Group", gname ]
			    )
			parent.setCheckState( 0, Qt.Unchecked )

			csrno = 1
			for temp in glist:
				child = QtWidgets.QTreeWidgetItem(
				    parent, [
				        str( csrno ), "Accessory",
				        str( temp[ 3 ] ),
				        str( temp[ 2 ] ),
				        str( temp[ 4 ] ),
				        str( temp[ 5 ] ),
				        str( temp[ 6 ] ),
				        str( temp[ 8 ] )
				        ]
				    )
				csrno += 1
			psrno += 1

# {'testMaterial': [[1, datetime.datetime(2021, 2, 19, 23, 42, 26, 568000), 'GDIL 5017\\',
# 'frame', 'Kg/Mtr', '07.40/06.40', 1.5, 'a+b+c'],
# [2, datetime.datetime(2021, 2, 19, 23, 44, 2, 353000), 'GDIL 5019\\', 'sutter', 'Kg/Mtr', '04.60/06.40', 1.2, 'a+b+c']]}

# {'test': [[1, datetime.datetime(2021, 2, 18, 22, 13, 21, 941000), 'roller', 'GD','NOS', '1.0', 4000.0, 'UGX', 'fasdfa']]}

	def showAddMaterialWindow( self, event=None ):
		self.HomeFrame.setEnabled( False )
		self.ShowAddMaterialWindow( MaterialGroup=[], event=event )

	def showAddAccessoryWindow( self, event=None ):
		self.HomeFrame.setEnabled( False )
		self.ShowAddAccessoryWindow( AccessoryGroup=[], event=event )

#----------------------------------------Start Add Material SubWindow--------------------------------------------------

	def ShowAddMaterialWindow( self, GroupName=None, MaterialGroup=[], event=None ):

		rowid = None
		MGWindow = ProductSubWindow( parent=self )
		MGWindow.show()
		MList = self.DBHandler.execute( """select * from materials""" ).fetchall()
		MatGroupName = None

		def fillTable( event=None ):
			n = MGWindow.ProMatGroupTable.rowCount()
			for i in range( n ):
				MGWindow.ProMatGroupTable.removeRow( 0 )
			for row in MaterialGroup:
				temp = MGWindow.ProMatGroupTable.rowCount()
				MGWindow.ProMatGroupTable.insertRow( temp )
				MGWindow.ProMatGroupTable.setItem( temp, 0, QTableWidgetItem( str( row[ 2 ] ) ) )
				MGWindow.ProMatGroupTable.setItem( temp, 1, QTableWidgetItem( str( row[ 3 ] ) ) )
				MGWindow.ProMatGroupTable.setItem( temp, 2, QTableWidgetItem( str( row[ 4 ] ) ) )
				MGWindow.ProMatGroupTable.setItem( temp, 3, QTableWidgetItem( str( row[ 5 ] ) ) )
				MGWindow.ProMatGroupTable.setItem( temp, 4, QTableWidgetItem( str( row[ 6 ] ) ) )
				MGWindow.ProMatGroupTable.setItem( temp, 5, QTableWidgetItem( str( row[ 7 ] ) ) )

		def setCode( event=None ):
			i = MGWindow.ProMatNameCB.currentIndex()
			MGWindow.ProMatCodeCB.setCurrentIndex( i )

		def setName( event=None ):
			i = MGWindow.ProMatCodeCB.currentIndex()
			MGWindow.ProMatNameCB.setCurrentIndex( i )

		def addMaterial( event=None ):
			if MList == []:
				QMessageBox.information(
				    self, "Empty", "No Materials found, kindly add material !"
				    )
			else:
				if validateFormula() and MGWindow.ProMatCodeCB.currentText() not in [
				    "", " ", None
				    ] and MGWindow.ProMatNameCB.currentText() not in [ "", " ", None ]:
					i = MGWindow.ProMatNameCB.currentIndex()
					temp = list( MList[ i ] )
					temp.append( MGWindow.ProMatQFENT.text() )
					MaterialGroup.append( temp )
					fillTable()
					resetForm()
				else:
					QMessageBox.information(
					    self, "Invalid Formula",
					    "Please check your formula and kindly follow given guide !"
					    )

		def updateMaterial( event=None ):
			if validateFormula():
				i = MGWindow.ProMatNameCB.currentIndex()
				temp = list( MList[ i ] )
				temp.append( MGWindow.ProMatQFENT.text() )
				if ( len( MaterialGroup[ globals()[ "rowid" ] ] ) == 9 ):
					temp.append( MaterialGroup[ globals()[ "rowid" ] ][ 8 ] )
				MaterialGroup[ globals()[ "rowid" ] ] = temp
				fillTable()
				resetForm()
			else:
				QMessageBox.information(
				    self, "Invalid Formula",
				    "Please check your formula and kindly follow given guide !"
				    )

		def deleteMaterial( event=None ):
			if MGWindow.ProMatGroupTable.currentRow() >= 0:
				rowid = int( MGWindow.ProMatGroupTable.currentRow() )
				if ( len( MaterialGroup[ rowid ] ) == 9 ):
					self.DeletedProductMaterial.append( MaterialGroup[ rowid ][ 8 ] )
				MaterialGroup.pop( rowid )
			else:
				QMessageBox.information(
				    self, "Invalid Row", "Please select Material from table !"
				    )
			fillTable()
			resetForm()

		def resetForm( event=None ):
			MGWindow.ProMatNameCB.setCurrentIndex( 0 )
			MGWindow.ProMatQFENT.clear()
			MGWindow.ProMatAddPBT.setText( "Add" )
			MGWindow.ProMatAddPBT.disconnect()
			MGWindow.ProMatAddPBT.clicked.connect( addMaterial )

			MGWindow.ProMatDeletePBT.setText( "Delete" )
			MGWindow.ProMatDeletePBT.disconnect()
			MGWindow.ProMatDeletePBT.clicked.connect( deleteMaterial )

		def editMaterial( event=None ):

			if MGWindow.ProMatGroupTable.currentRow() >= 0:
				globals()[ "rowid" ] = int( MGWindow.ProMatGroupTable.currentRow() )
				MGWindow.ProMatAddPBT.setText( "Update" )
				MGWindow.ProMatAddPBT.disconnect()
				MGWindow.ProMatAddPBT.clicked.connect( updateMaterial )

				MGWindow.ProMatDeletePBT.setText( "Reset" )
				MGWindow.ProMatDeletePBT.disconnect()
				MGWindow.ProMatDeletePBT.clicked.connect( resetForm )

				temp = MaterialGroup[ globals()[ "rowid" ] ]

				index = MGWindow.ProMatNameCB.findText(
				    str( temp[ 3 ] ), QtCore.Qt.MatchFixedString
				    )
				if index >= 0:
					MGWindow.ProMatNameCB.setCurrentIndex( index )

				index = MGWindow.ProMatCodeCB.findText(
				    str( temp[ 2 ][ 5 : ] ), QtCore.Qt.MatchFixedString
				    )
				if index >= 0:
					MGWindow.ProMatCodeCB.setCurrentIndex( index )
				# MGWindow.ProMatCodeENT.setText( temp[ 2 ] )

				MGWindow.ProMatQFENT.setText( temp[ 7 ] )

			else:
				QMessageBox.information(
				    self, "Invalid Row", "Please select Material from table !"
				    )

		def saveMaterialGroup( event=None ):
			temp = MGWindow.ProMatGroupNameENT.text()
			if MaterialGroup == []:
				QMessageBox.information( self, "Empty Group", "No Material Added !" )
			else:
				if temp not in [ "", " " ]:
					if temp in self.ProductMaterialGroups.keys():
						QMessageBox.information(
						    self, "Name Error", "Group Name must be a Unique from other group !"
						    )
					else:
						self.ProductMaterialGroups[ temp ] = MaterialGroup
						MGWindow.close()
						self.HomeFrame.setEnabled( True )

						self.resetProductTree()
				else:
					QMessageBox.information( self, "Empty Field", "Group Name must be a string !" )

		def updateMaterialGroup( event=None ):
			buttonReply = QMessageBox.question(
			    self, 'Exit', "Are you sure, you want to update Material Group ?",
			    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
			    )
			if buttonReply == QMessageBox.Yes:
				temp = MGWindow.ProMatGroupNameENT.text()
				if MaterialGroup == []:
					QMessageBox.information( self, "Empty Group", "No Material Added !" )
				else:
					if temp not in [ "", " " ]:
						if temp == globals()[ "MatGroupName" ]:
							self.ProductMaterialGroups[ temp ] = MaterialGroup

						else:
							buttonReply = QMessageBox.question(
							    self, 'Update', "Do you want create new copy ?",
							    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
							    )
							if buttonReply == QMessageBox.No:
								tempMaterialGroup = self.ProductMaterialGroups
								self.ProductMaterialGroups = {}
								for k, v in tempMaterialGroup.items():
									if k == globals()[ "MatGroupName" ]:
										k = temp
										v = MaterialGroup
									self.ProductMaterialGroups[ k ] = v
							elif buttonReply == QMessageBox.Yes:
								self.ProductMaterialGroups[ temp ] = MaterialGroup

						self.resetProductTree()
						MGWindow.close()
						self.HomeFrame.setEnabled( True )

					else:
						QMessageBox.information(
						    self, "Empty Field", "Group Name must be a string !"
						    )

		def closeMaterial( event=None ):
			self.HomeFrame.setEnabled( True )

		def validateFormula( event=None ):
			w = h = qty = vh = hwv = vs = thwv = tswv = fh = hwf = fs = thwf = tswf = hwvf = thwvf = tswvf = tw = th = ts = 0
			try:
				result = eval( MGWindow.ProMatQFENT.text() )
				MGWindow.ProMatQFENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )
				return True
			except:
				MGWindow.ProMatQFENT.setStyleSheet( "border: 1px solid red;" )
				return False

		def config():

			if GroupName != None:
				MGWindow.ProMatSavePBT.setText( "Update" )
				MGWindow.ProMatSavePBT.clicked.connect( updateMaterialGroup )
				MGWindow.ProMatGroupNameENT.setText( GroupName )
				globals()[ "MatGroupName" ] = GroupName
				# MGWindow.ProMatGroupNameENT.setReadOnly( True )
			else:
				MGWindow.ProMatSavePBT.clicked.connect( saveMaterialGroup )

			regexp = QtCore.QRegExp(
			    '[0-9,w,h,qty,vh,hwv,vs,thwv,tswv,fh,hwf,fs,thwf,tswf,hwvf,thwvf,tswvf,tw,th,ts,+,-,-,*,/,(,),%,.]+'
			    )
			validator = QtGui.QRegExpValidator( regexp )
			MGWindow.ProMatQFENT.setValidator( validator )
			MGWindow.ProMatQFENT.textChanged.connect( validateFormula )

			MGWindow.stackedWidget.setCurrentWidget( MGWindow.ProductAddMaterial )
			MGWindow.ProMatNameCB.currentIndexChanged.connect( setCode )
			MGWindow.ProMatCodeCB.currentIndexChanged.connect( setName )

			MGWindow.ProMatAddPBT.clicked.connect( addMaterial )
			MGWindow.ProMatEditPBT.clicked.connect( editMaterial )
			MGWindow.ProMatDeletePBT.clicked.connect( deleteMaterial )
			MGWindow.ProMatClosePBT.clicked.connect( closeMaterial )

			MGWindow.ProMatGroupTable.doubleClicked.connect( editMaterial )

			AccessoryTableHeader = MGWindow.ProMatGroupTable.horizontalHeader()
			AccessoryTableHeader.setSectionResizeMode( 0, QtWidgets.QHeaderView.ResizeToContents )
			AccessoryTableHeader.setSectionResizeMode( 1, QtWidgets.QHeaderView.Stretch )
			AccessoryTableHeader.setSectionResizeMode( 2, QtWidgets.QHeaderView.ResizeToContents )
			AccessoryTableHeader.setSectionResizeMode( 3, QtWidgets.QHeaderView.ResizeToContents )
			AccessoryTableHeader.setSectionResizeMode( 4, QtWidgets.QHeaderView.ResizeToContents )
			AccessoryTableHeader.setSectionResizeMode( 5, QtWidgets.QHeaderView.ResizeToContents )

			for i in range( len( MList ) ):
				MGWindow.ProMatNameCB.insertItem( i, MList[ i ][ 3 ] )
				MGWindow.ProMatCodeCB.insertItem( i, MList[ i ][ 2 ][ 5 : ] )

		config()
		fillTable()
		resetForm()

#----------------------------------------------------END Add Material SubWindow----------------------------------------

#----------------------------------------------------Start Add Accessory SubWindow-------------------------------------

	def ShowAddAccessoryWindow( self, GroupName=None, AccessoryGroup=[], event=None ):
		# AccessoryGroup = []
		rowid = None
		MGWindow = ProductSubWindow( parent=self )
		MGWindow.show()
		AList = self.DBHandler.execute( """select * from accessories""" ).fetchall()
		AccGroupName = None

		# print( AList )

		def fillTable( event=None ):
			n = MGWindow.ProAccGroupTable.rowCount()
			for i in range( n ):
				MGWindow.ProAccGroupTable.removeRow( 0 )
			for row in AccessoryGroup:
				temp = MGWindow.ProAccGroupTable.rowCount()
				MGWindow.ProAccGroupTable.insertRow( temp )
				MGWindow.ProAccGroupTable.setItem( temp, 0, QTableWidgetItem( str( row[ 2 ] ) ) )
				MGWindow.ProAccGroupTable.setItem( temp, 1, QTableWidgetItem( str( row[ 3 ] ) ) )
				MGWindow.ProAccGroupTable.setItem( temp, 2, QTableWidgetItem( str( row[ 4 ] ) ) )
				MGWindow.ProAccGroupTable.setItem( temp, 3, QTableWidgetItem( str( row[ 5 ] ) ) )
				MGWindow.ProAccGroupTable.setItem( temp, 4, QTableWidgetItem( str( row[ 6 ] ) ) )
				MGWindow.ProAccGroupTable.setItem( temp, 5, QTableWidgetItem( str( row[ 7 ] ) ) )
				MGWindow.ProAccGroupTable.setItem( temp, 6, QTableWidgetItem( str( row[ 8 ] ) ) )

		def setName( event=None ):
			i = MGWindow.ProAccCodeCB.currentIndex()
			MGWindow.ProAccNameCB.setCurrentIndex( i )

		def setCode( event=None ):
			i = MGWindow.ProAccNameCB.currentIndex()
			MGWindow.ProAccCodeCB.setCurrentIndex( i )

		def addAccessory( event=None ):
			if AList == []:
				QMessageBox.information(
				    self, "Empty", "No Accessories found, kindly add accessory !"
				    )
			else:
				if validateFormula() and MGWindow.ProAccCodeCB.currentText() not in [
				    "", " ", None
				    ] and MGWindow.ProAccNameCB.currentText() not in [ "", " ", None ]:
					i = MGWindow.ProAccNameCB.currentIndex()
					temp = list( AList[ i ] )
					temp.append( MGWindow.ProAccQFENT.text() )
					AccessoryGroup.append( temp )
					fillTable()
					resetForm()
				else:
					QMessageBox.information(
					    self, "Invalid Formula",
					    "Please check your formula and kindly follow given guide !"
					    )

		def updateAccessory( event=None ):
			if validateFormula():
				i = MGWindow.ProAccNameCB.currentIndex()
				temp = list( AList[ i ] )
				temp.append( MGWindow.ProAccQFENT.text() )
				if ( len( AccessoryGroup[ globals()[ "rowid" ] ] ) == 10 ):
					temp.append( AccessoryGroup[ globals()[ "rowid" ] ][ 9 ] )
				AccessoryGroup[ globals()[ "rowid" ] ] = temp
				fillTable()
				resetForm()
			else:
				QMessageBox.information(
				    self, "Invalid Formula",
				    "Please check your formula and kindly follow given guide !"
				    )

		def deleteAccessory( event=None ):
			if MGWindow.ProAccGroupTable.currentRow() >= 0:
				rowid = int( MGWindow.ProAccGroupTable.currentRow() )
				if ( len( AccessoryGroup[ rowid ] ) == 10 ):
					self.DeletedProductAccessory.append( AccessoryGroup[ rowid ][ 9 ] )
				AccessoryGroup.pop( rowid )
			else:
				QMessageBox.information(
				    self, "Invalid Row", "Please select Accessory from table !"
				    )
			fillTable()

		def resetForm( event=None ):
			MGWindow.ProAccNameCB.setCurrentIndex( 0 )
			MGWindow.ProAccQFENT.clear()
			MGWindow.ProAccAddPBT.setText( "Add" )
			MGWindow.ProAccAddPBT.disconnect()
			MGWindow.ProAccAddPBT.clicked.connect( addAccessory )

			MGWindow.ProAccDeletePBT.setText( "Delete" )
			MGWindow.ProAccDeletePBT.disconnect()
			MGWindow.ProAccDeletePBT.clicked.connect( deleteAccessory )

		def editAccessory( event=None ):

			if MGWindow.ProAccGroupTable.currentRow() >= 0:
				globals()[ "rowid" ] = int( MGWindow.ProAccGroupTable.currentRow() )
				MGWindow.ProAccAddPBT.setText( "Update" )
				MGWindow.ProAccAddPBT.disconnect()
				MGWindow.ProAccAddPBT.clicked.connect( updateAccessory )

				MGWindow.ProAccDeletePBT.setText( "Reset" )
				MGWindow.ProAccDeletePBT.disconnect()
				MGWindow.ProAccDeletePBT.clicked.connect( resetForm )

				temp = AccessoryGroup[ globals()[ "rowid" ] ]
				# MGWindow.ProAccCodeENT.setText( str( temp[ 2 ] ) )
				MGWindow.ProAccQFENT.setText( temp[ 8 ] )

				index = MGWindow.ProAccNameCB.findText(
				    str( temp[ 3 ] ), QtCore.Qt.MatchFixedString
				    )
				if index >= 0:
					MGWindow.ProAccNameCB.setCurrentIndex( index )

				index = MGWindow.ProAccCodeCB.findText(
				    str( temp[ 2 ][ 3 : ] ), QtCore.Qt.MatchFixedString
				    )
				if index >= 0:
					MGWindow.ProAccCodeCB.setCurrentIndex( index )

			else:
				QMessageBox.information(
				    self, "Invalid Row", "Please select Accessory from table !"
				    )

		def saveAccessoryGroup( event=None ):
			temp = MGWindow.ProAccGroupNameENT.text()
			if AccessoryGroup == []:
				QMessageBox.information( self, "Empty Group", "No Accessory Added !" )
			else:
				if temp not in [ "", " " ]:
					if temp in self.ProductAccessoryGroups.keys():
						QMessageBox.information(
						    self, "Name Error", "Group Name must be a Unique from other group !"
						    )
					else:
						self.ProductAccessoryGroups[ temp ] = AccessoryGroup
						MGWindow.close()
						self.HomeFrame.setEnabled( True )
						self.resetProductTree()
				else:
					QMessageBox.information( self, "Empty Field", "Group Name must be a string !" )

		def updateAccessoryGroup( event=None ):
			buttonReply = QMessageBox.question(
			    self, 'Exit', "Are you sure, you want to update Accessory Group ?",
			    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
			    )
			if buttonReply == QMessageBox.Yes:
				temp = MGWindow.ProAccGroupNameENT.text()
				if AccessoryGroup == []:
					QMessageBox.information( self, "Empty Group", "No Accessory Added !" )
				else:
					if temp not in [ "", " " ]:
						if temp == globals()[ "AccGroupName" ]:
							self.ProductAccessoryGroups[ temp ] = AccessoryGroup

						else:
							buttonReply = QMessageBox.question(
							    self, 'Update', "Do you want create new copy ?",
							    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
							    )
							if buttonReply == QMessageBox.No:
								tempAccessoryGroup = self.ProductAccessoryGroups
								self.ProductAccessoryGroups = {}
								for k, v in tempAccessoryGroup.items():
									if k == globals()[ "AccGroupName" ]:
										k = temp
										v = AccessoryGroup
									self.ProductAccessoryGroups[ k ] = v
							elif buttonReply == QMessageBox.Yes:
								self.ProductAccessoryGroups[ temp ] = AccessoryGroup

						# self.ProductAccessoryGroups[ temp ] = AccessoryGroup
						MGWindow.close()
						self.HomeFrame.setEnabled( True )
						self.resetProductTree()
					else:
						QMessageBox.information(
						    self, "Empty Field", "Group Name must be a string !"
						    )

		def closeAccessory( event=None ):
			self.HomeFrame.setEnabled( True )

		def validateFormula( event=None ):
			w = h = qty = vh = hwv = vs = thwv = tswv = fh = hwf = fs = thwf = tswf = hwvf = thwvf = tswvf = tw = th = ts = 0
			try:
				result = eval( MGWindow.ProAccQFENT.text() )
				MGWindow.ProAccQFENT.setStyleSheet( "border: 1px solid rgb(85, 170, 255);" )
				return True
			except:
				MGWindow.ProAccQFENT.setStyleSheet( "border: 1px solid red;" )
				return False

		def config():
			if GroupName != None:
				MGWindow.ProAccSavePBT.setText( "Update" )
				MGWindow.ProAccSavePBT.clicked.connect( updateAccessoryGroup )
				MGWindow.ProAccGroupNameENT.setText( GroupName )
				globals()[ "AccGroupName" ] = GroupName
				# MGWindow.ProAccGroupNameENT.setReadOnly( True )
			else:
				MGWindow.ProAccSavePBT.clicked.connect( saveAccessoryGroup )
			regexp = QtCore.QRegExp(
			    '[0-9,w,h,qty,vh,hwv,vs,thwv,tswv,fh,hwf,fs,thwf,tswf,hwvf,thwvf,tswvf,tw,th,ts,+,-,-,*,/,(,),%,.]+'
			    )
			validator = QtGui.QRegExpValidator( regexp )
			MGWindow.ProAccQFENT.setValidator( validator )
			MGWindow.ProAccQFENT.textChanged.connect( validateFormula )

			MGWindow.stackedWidget.setCurrentWidget( MGWindow.ProductAddAccessory )
			MGWindow.ProAccNameCB.currentIndexChanged.connect( setCode )
			MGWindow.ProAccCodeCB.currentIndexChanged.connect( setName )

			MGWindow.ProAccAddPBT.clicked.connect( addAccessory )
			MGWindow.ProAccEditPBT.clicked.connect( editAccessory )
			MGWindow.ProAccDeletePBT.clicked.connect( deleteAccessory )
			MGWindow.ProAccClosePBT.clicked.connect( closeAccessory )

			MGWindow.ProAccGroupTable.doubleClicked.connect( editAccessory )

			AccessoryTableHeader = MGWindow.ProAccGroupTable.horizontalHeader()
			AccessoryTableHeader.setSectionResizeMode( 0, QtWidgets.QHeaderView.ResizeToContents )
			AccessoryTableHeader.setSectionResizeMode( 1, QtWidgets.QHeaderView.Stretch )
			AccessoryTableHeader.setSectionResizeMode( 2, QtWidgets.QHeaderView.ResizeToContents )
			AccessoryTableHeader.setSectionResizeMode( 3, QtWidgets.QHeaderView.ResizeToContents )
			AccessoryTableHeader.setSectionResizeMode( 4, QtWidgets.QHeaderView.ResizeToContents )
			AccessoryTableHeader.setSectionResizeMode( 5, QtWidgets.QHeaderView.ResizeToContents )
			AccessoryTableHeader.setSectionResizeMode( 6, QtWidgets.QHeaderView.ResizeToContents )

			for i in range( len( AList ) ):
				# MGWindow.ProAccNameCB.insertItem(
				#     i,
				#     str( AList[ i ][ 2 ] ) + "-" + AList[ i ][ 3 ]
				#     )
				MGWindow.ProAccNameCB.insertItem( i, AList[ i ][ 3 ] )
				MGWindow.ProAccCodeCB.insertItem( i, AList[ i ][ 2 ][ 3 : ] )

		config()
		fillTable()
		resetForm()


#----------------------------------------------------END Add Accessory SubWindow---------------------------------------
