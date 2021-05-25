from fpdf import FPDF
from datetime import datetime
import sqlite3
import math
import os


class PDF( FPDF ):

	def header( self ):
		self.image( 'Images/Logo.png', 8, 2.5, 30 )
		self.set_font( 'Arial', 'B', 34 )
		self.set_y( 17.5 )
		self.cell( 0, 0, 'G Das Industries Ltd.', 0, 1, 'R' )
		self.set_font( 'Arial', '', 12 )
		self.set_y( 25 )
		self.cell( 0, 0, 'Aluminium Architectural Profile Extruders & Fabricators', 0, 1, 'R' )
		self.set_line_width( 0.5 )
		self.rect( 3, 3, 204, 291 )
		self.line( 3, 32, 207, 32 )
		self.image( 'Images/watermark.png', 30, 71, 150 )

		self.ln( 6 )

	def footer( self ):
		self.set_y( -21 )
		self.set_font( 'Arial', 'B', 9 )
		self.set_x( 3 )
		self.cell( 30, 6, 'Prepared By', 1, 0, 'C' )
		self.cell( 58, 6, '', 1, 0, 'C' )
		self.cell( 58, 6, '', 'TR', 0, 'C' )
		self.cell( 58, 6, '', 'TL', 0, 'C' )
		self.ln()
		self.set_x( 3 )
		self.cell( 30, 6, 'Checked By', 1, 0, 'C' )
		self.cell( 58, 6, '', 1, 0, 'C' )
		self.cell( 58, 6, '', 'R', 0, 'C' )
		self.cell( 58, 6, '', 'L', 0, 'C' )
		self.ln()
		self.set_x( 3 )
		self.cell( 30, 6, 'Date', 1, 0, 'C' )
		self.cell( 58, 6, '', 1, 0, 'C' )
		self.cell( 58, 6, 'Authorized Signatory', 1, 0, 'C' )
		self.cell( 58, 6, 'Client\'s Signature', 1, 0, 'C' )


class PrintQuotation:

	def __init__( self, DBHandler, QuotationID ):
		self.Products = {}
		self.ProductMaterialGroups = {}
		self.ProductAccessoryGroups = {}
		self.QuotationItems = {}
		self.QuotationInfo = []
		self.allCurrency = {}
		self.quotationID = QuotationID
		self.DBHandler = DBHandler
		if not os.path.exists( "Quotations" ):
			os.mkdir( "Quotations" )
		self.getData()

	def getData( self ):
		result = self.DBHandler.execute( """select * from currency""" ).fetchall()
		for cur in result:
			self.allCurrency[ cur[ 0 ] ] = float( cur[ 1 ] )

		self.Products = {}
		# self.ProductMaterialGroups = {}
		# self.ProductAccessoryGroups = {}
		self.QuotationItems = {}
		self.QuotationInfo = []
		self.MaterialQty = {}
		self.AccessoryQty = {}
		self.GlassQty = {}

		# result = self.DBHandler.execute( """select * from products""" ).fetchall()
		# products = list( map( list, result ) )

		# for product in products:
		# 	product_name = product.pop( 2 )
		# 	self.Products[ product_name ] = product
		# 	temp = {}
		# 	# print( product )
		# 	for material_id in product[ 4 ].split( ',' ):
		# 		result = self.DBHandler.execute(
		# 		    """select * from material_group inner join materials on
		# 			materials.material_id = material_group.material_id
		# 			where product_id == ? and group_id == ?""", ( product[ 0 ], int( material_id ) )
		# 		    ).fetchall()
		# 		material_group = list( map( list, result ) )
		# 		group_name = material_group[ 0 ][ 0 ]
		# 		temp[ group_name ] = material_group

		# 	self.ProductMaterialGroups[ product_name ] = temp
		# 	# print( "Materials : ", self.ProductMaterialGroups )
		# 	temp = {}
		# 	for accessory_id in product[ 5 ].split( ',' ):
		# 		result = self.DBHandler.execute(
		# 		    """select * from accessory_group inner join accessories on
		# 			accessories.accessory_id = accessory_group.accessory_id
		# 			where product_id == ? and group_id == ?""", ( product[ 0 ], int( accessory_id ) )
		# 		    ).fetchall()
		# 		accessory_group = list( map( list, result ) )
		# 		print( product )
		# 		group_name = accessory_group[ 0 ][ 0 ]
		# 		temp[ group_name ] = accessory_group

		# 	self.ProductAccessoryGroups[ product_name ] = temp

		self.QuotationInfo = self.DBHandler.execute(
		    """select * from quotations where quotation_id == ?""", ( self.quotationID, )
		    ).fetchone()

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
			print( product )

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

			if productId not in self.QuotationItems.keys():
				self.QuotationItems[ productId ] = {}

			self.QuotationItems[ productId ][ quoProductId ] = templist

		# print( self.Products )
		# print( self.ProductMaterialGroups )
		# print( self.ProductAccessoryGroups )
		# print( self.QuotationInfo )
		# print( self.QuotationItems )

	def getQuontity( self ):
		# try:

		for productId, productGroup in self.QuotationItems.items():
			for quoProductId, product in productGroup.items():

				# product = self.ProductMaterialGroups[ QuoPro[ 1 ] ]
				QuoPro = product[ 0 ]
				MaterialGroup = product[ 1 ]
				AccessoryGroup = product[ 2 ]

				matgroups = QuoPro[ 13 ]
				accgroups = QuoPro[ 14 ]

				# for groupname in product.keys():
				w = h = qty = vh = hwv = vs = thwv = tswv = fh = hwf = fs = thwf = tswf = hwvf = thwvf = tswvf = tw = th = ts = 0

				w = QuoPro[ 3 ]
				h = QuoPro[ 4 ]
				qty = QuoPro[ 5 ]
				if QuoPro[ 6 ]:
					vh = QuoPro[ 7 ]

				if QuoPro[ 8 ]:
					fh = QuoPro[ 9 ]

				if QuoPro[ 6 ]:
					hwv = h - fh
					vs = w * vh
					thwv = hwv * qty
					tswv = w * hwv * qty

				if QuoPro[ 8 ]:
					hwf = h - vh
					fs = w * fh
					thwf = hwf * qty
					tswf = w * hwf * qty

				hwvf = h - vh - fh
				thwvf = hwvf * qty
				tswvf = w * hwvf * qty

				tw = w * qty
				th = h * qty
				ts = w * h * qty

				total_weight = 0
				total_amount = 0
				total_pcs = 0
				# material_group = product[ groupname ]
				for MGId, material_group in MaterialGroup.items():
					if MGId in matgroups:
						for material in material_group:
							code = material[ 4 ]
							name = material[ 5 ]
							formula = material[ 9 ]
							result = eval( formula )
							extra = result + ( result * 0.1 )
							unit = material[ 7 ].split( '/' )
							kg = float( unit[ 0 ] )
							mtr = float( unit[ 1 ] )
							pcs = extra / mtr
							weight = pcs * kg

							total_weight += weight
							total_pcs += pcs
							if code in self.MaterialQty.keys():
								self.MaterialQty[ code ][ 3 ] += result
								self.MaterialQty[ code ][ 4 ] += extra
								self.MaterialQty[ code ][ 5 ] += pcs
								self.MaterialQty[ code ][ 6 ] += weight
							else:
								self.MaterialQty[ code ] = [
								    name, material[ 6 ], material[ 7 ], result, extra, pcs, weight
								    ]

				for AGId, accessory_group in AccessoryGroup.items():
					# accessory_group = product[ groupname ]
					# print( accessory_group )
					if AGId in accgroups:
						for accessory in accessory_group:
							print( accessory )
							code = accessory[ 4 ]
							name = accessory[ 5 ]
							formula = accessory[ 10 ]
							unit = float( accessory[ 7 ] )
							result = float( eval( formula ) )
							pcs = result * unit
							print( self.GlassQty )

							if code == "GD 0000/":
								if name in self.GlassQty.keys():
									self.GlassQty[ name ][ 3 ] += pcs
								else:
									self.GlassQty[ name ] = [
									    name, accessory[ 6 ], accessory[ 7 ], pcs
									    ]

							if code in self.AccessoryQty.keys():
								self.AccessoryQty[ code ][ 3 ] += pcs

							else:
								self.AccessoryQty[ code ] = [
								    name, accessory[ 6 ], accessory[ 7 ], pcs
								    ]
		# except Exception as e:
		# 	print( "2: ", e )

		# 	try:
		# 		for QuoProID, QuoPro in self.QuotationItems.items():
		# 			product = self.ProductAccessoryGroups[ QuoPro[ 1 ] ]

		# 			for groupname in product.keys():
		# 				w = h = qty = vh = hwv = vs = thwv = tswv = fh = hwf = fs = thwf = tswf = hwvf = thwvf = tswvf = tw = th = ts = 0

		# 				w = QuoPro[ 3 ]
		# 				h = QuoPro[ 4 ]
		# 				qty = QuoPro[ 5 ]
		# 				if QuoPro[ 6 ]:
		# 					vh = QuoPro[ 7 ]

		# 				if QuoPro[ 8 ]:
		# 					fh = QuoPro[ 9 ]

		# 				if QuoPro[ 6 ]:
		# 					hwv = h - fh
		# 					vs = w * vh
		# 					thwv = hwv * qty
		# 					tswv = w * hwv * qty

		# 				if QuoPro[ 8 ]:
		# 					hwf = h - vh
		# 					fs = w * fh
		# 					thwf = hwf * qty
		# 					tswf = w * hwf * qty

		# 				hwvf = h - vh - fh
		# 				thwvf = hwvf * qty
		# 				tswvf = w * hwvf * qty

		# 				tw = w * qty
		# 				th = h * qty
		# 				ts = w * h * qty

		# 				accessory_group = product[ groupname ]
		# 				# print( accessory_group )
		# 				if accessory_group[ 0 ][ 1 ] in accgroups:

		# 					for accessory in accessory_group:
		# 						code = accessory[ 7 ]
		# 						name = accessory[ 8 ]
		# 						formula = accessory[ 4 ]
		# 						unit = float( accessory[ 10 ] )
		# 						result = float( eval( formula ) )
		# 						pcs = result * unit

		# 						if code in self.AccessoryQty.keys():
		# 							self.AccessoryQty[ code ][ 3 ] += pcs

		# 						else:
		# 							self.AccessoryQty[ code ] = [
		# 							    name, accessory[ 9 ], accessory[ 10 ], pcs
		# 							    ]
		# except Exception as e:
		# 	print( "3: ", e )

		print( self.MaterialQty )
		print( self.AccessoryQty )

	def convertCurrency( self, src, des, value ):
		return ( ( self.allCurrency[ des ] * value ) / self.allCurrency[ src ] )

	def printQuotation( self, sqm_flag=False, TC=None ):
		self.TC = TC
		count = 1
		pdf = PDF()
		pdf.alias_nb_pages()
		pdf.add_page()
		pdf.set_line_width( 0.5 )
		pdf.set_fill_color( 180, 199, 231 )

		pdf.set_font( 'Arial', 'bu', 10 )
		pdf.text( 4, 36, "Extrusion Factory" )
		pdf.text( 149, 36, "Sales Outlet / Fabrication Division" )

		pdf.set_font( 'Arial', 'b', 8 )
		pdf.text( 4, 40.5, "Block 295 (Model Farm)" )
		pdf.text( 119, 40.5, "Plot No-155-165,Near DFCU Bank, Sixth Street, Kampala, Uganda" )

		pdf.text( 4, 44, "Plot - 321,498-504,506, Kyaggwe,Mibiko,Njeru " )
		pdf.text( 131.3, 44, "Tel : + 256 757614545 E-Mail : info@gdasindustries.com" )

		pdf.text( 4, 47.5, "PO Box 1069, Jinja, Uganda" )
		pdf.text( 160.5, 47.5, "Wesite : www.gdasindustries.com" )

		# pdf.rect( 3, 49, 204, 7, "DF" )
		pdf.set_font( 'Arial', 'b', 16 )
		# pdf.text( 92, 54.5, "Quotation" )
		pdf.ln( 18 )
		pdf.set_x( 3 )

		pdf.multi_cell( 204, 7, "Quotation", 1, 0, 'C', True )

		pdf.set_font( 'Arial', 'b', 9 )
		pdf.set_line_width( 0.3 )
		pdf.set_xy( 3, 56 )
		pdf.multi_cell( 18, 5, "Name", 1, 'L' )
		pdf.multi_cell( 64, 5, self.QuotationInfo[ 4 ], 1, 'L' )
		pdf.multi_cell( 16, 5, "Profile", 1, 'L' )
		pdf.multi_cell( 50, 5, self.QuotationInfo[ 8 ], 1, 'L' )
		pdf.multi_cell( 18, 5, "Qta No.", 1, 'L' )
		pdf.multi_cell( 38, 5, "{:05d}".format( self.QuotationInfo[ 0 ] ), 1, 'L' )
		pdf.ln()
		pdf.set_x( 3 )
		pdf.multi_cell( 18, 5, "Tel No.", 1, 'L' )
		pdf.multi_cell( 64, 5, self.QuotationInfo[ 5 ], 1, 'L' )
		pdf.multi_cell( 16, 5, "Finish", 1, 'L' )
		pdf.multi_cell( 50, 5, self.QuotationInfo[ 9 ], 1, 'L' )
		pdf.multi_cell( 18, 5, "Ref No.", 1, 'L' )
		pdf.multi_cell( 38, 5, self.QuotationInfo[ 1 ], 1, 'L' )
		pdf.ln()
		pdf.set_x( 3 )
		pdf.multi_cell( 18, 5, "Email", 1, 'L' )
		pdf.multi_cell( 64, 5, self.QuotationInfo[ 6 ], 1, 'L' )
		pdf.multi_cell( 16, 5, "Glass", 1, 'L' )
		pdf.multi_cell( 50, 5, self.QuotationInfo[ 10 ], 1, 'L' )
		pdf.multi_cell( 18, 5, "Date", 1, 'L' )
		pdf.multi_cell( 38, 5, self.QuotationInfo[ 2 ].strftime( "%d-%m-%Y" ), 1, 'L' )
		pdf.ln()
		pdf.set_x( 3 )
		pdf.multi_cell( 18, 5, "Address", 1, 'L' )
		pdf.multi_cell( 64, 5, self.QuotationInfo[ 7 ], 1, 'L' )
		pdf.multi_cell( 16, 5, "Mesh", 1, 'L' )
		pdf.multi_cell( 50, 5, self.QuotationInfo[ 11 ], 1, 'L' )
		pdf.multi_cell( 18, 5, "Currency", 1, 'L' )
		pdf.multi_cell( 38, 5, self.QuotationInfo[ 3 ], 1, 'L' )

		pdf.set_font( 'Arial', 'b', 9 )
		pdf.set_line_width( 0.3 )

		pdf.ln()
		pdf.set_xy( 3, 78 )
		if sqm_flag:
			pdf.multi_cell( 8, 5, "No.", 1, 'C' )
			pdf.multi_cell( 68, 5, "Item Description", 1, 'C' )
			pdf.multi_cell( 15, 5, "Width", 1, 'C' )
			pdf.multi_cell( 15, 5, "Height", 1, 'C' )
			pdf.multi_cell( 13, 5, "Sqm", 1, 'C' )
			pdf.multi_cell( 11, 5, "Qty", 1, 'C' )
			pdf.multi_cell( 17, 5, "Total Sqm", 1, 'C' )
			pdf.multi_cell( 17, 5, "Sqm Rate", 1, 'C' )

			pdf.multi_cell( 20, 5, "Unit Rate", 1, 'C' )
			pdf.multi_cell( 20, 5, "Amount", 1, 'C' )
		else:
			pdf.multi_cell( 10, 5, "No.", 1, 'C' )
			pdf.multi_cell( 73, 5, "Item Description", 1, 'C' )
			pdf.multi_cell( 15, 5, "Width", 1, 'C' )
			pdf.multi_cell( 15, 5, "Height", 1, 'C' )
			pdf.multi_cell( 13, 5, "Sqm", 1, 'C' )
			pdf.multi_cell( 11, 5, "Qty", 1, 'C' )
			pdf.multi_cell( 17, 5, "Total Sqm", 1, 'C' )
			pdf.multi_cell( 25, 5, "Unit Rate", 1, 'C' )
			pdf.multi_cell( 25, 5, "Amount", 1, 'C' )

		total_sqm = 0
		for i in self.QuotationItems.values():
			total_sqm += i[ 12 ]

		if self.QuotationInfo[ 3 ] != "USD":
			total_sqm = self.convertCurrency( "USD", self.QuotationInfo[ 3 ], total_sqm )

		net_total = self.QuotationInfo[ 12 ]
		overhead = total_sqm * self.QuotationInfo[ 13 ]
		transport = self.QuotationInfo[ 14 ]
		total = net_total + overhead + transport
		profit = ( float( self.QuotationInfo[ 15 ] ) / 100 ) * total

		div = ( overhead + transport + profit ) / len( self.QuotationItems.keys() )

		print( total, total_sqm, profit, div )
		pdf.set_font( 'Arial', '', 9 )

		for no, item in self.QuotationItems.items():
			sqm = item[ 12 ] / item[ 5 ]
			ur = ( div / item[ 5 ] ) + ( item[ 17 ] / item[ 5 ] )
			amo = item[ 17 ] + div
			sqm_rate = amo / item[ 12 ]

			pdf.ln()
			pdf.set_x( 3 )
			if sqm_flag:
				pdf.multi_cell( 8, 5, str( no ), 1, 'C' )
				pdf.multi_cell( 68, 5, item[ 1 ], 1, 'C' )
				pdf.multi_cell( 15, 5, "{:.4f}".format( item[ 3 ] ), 1, 'C' )
				pdf.multi_cell( 15, 5, "{:.4f}".format( item[ 4 ] ), 1, 'C' )
				pdf.multi_cell( 13, 5, "{:.2f}".format( sqm ), 1, 'C' )
				pdf.multi_cell( 11, 5, str( int( item[ 5 ] ) ), 1, 'C' )
				pdf.multi_cell( 17, 5, "{:.2f}".format( item[ 12 ] ), 1, 'C' )
				pdf.multi_cell( 17, 5, "{:,.2f}".format( sqm_rate ), 1, 'C' )
				pdf.multi_cell( 20, 5, "{:,.2f}".format( ur ), 1, 'R' )
				pdf.multi_cell( 20, 5, "{:,.2f}".format( amo ), 1, 'R' )
			else:
				pdf.multi_cell( 10, 5, str( no ), 1, 'C' )
				pdf.multi_cell( 73, 5, item[ 1 ], 1, 'C' )
				pdf.multi_cell( 15, 5, "{:.4f}".format( item[ 3 ] ), 1, 'C' )
				pdf.multi_cell( 15, 5, "{:.4f}".format( item[ 4 ] ), 1, 'C' )
				pdf.multi_cell( 13, 5, "{:.2f}".format( sqm ), 1, 'C' )
				pdf.multi_cell( 11, 5, str( int( item[ 5 ] ) ), 1, 'C' )
				pdf.multi_cell( 17, 5, "{:.2f}".format( item[ 12 ] ), 1, 'C' )
				pdf.multi_cell( 25, 5, "{:,.2f}".format( ur ), 1, 'R' )
				pdf.multi_cell( 25, 5, "{:,.2f}".format( amo ), 1, 'R' )
			count += 1
		for i in range( 25 - count ):
			pdf.ln()
			pdf.set_x( 3 )
			if sqm_flag:
				pdf.multi_cell( 8, 5, "", 0, 'C' )
				pdf.multi_cell( 68, 5, "", 0, 'C' )
				pdf.multi_cell( 15, 5, "", 0, 'C' )
				pdf.multi_cell( 15, 5, "", 0, 'C' )
				pdf.multi_cell( 13, 5, "", 0, 'C' )
				pdf.multi_cell( 11, 5, "", 0, 'C' )
				pdf.multi_cell( 17, 5, "", 0, 'C' )
				pdf.multi_cell( 17, 5, "", 0, 'C' )
				pdf.multi_cell( 20, 5, "", 0, 'R' )
				pdf.multi_cell( 20, 5, "", 0, 'R' )
			else:
				pdf.multi_cell( 10, 5, "", 0, 'C' )
				pdf.multi_cell( 73, 5, "", 0, 'C' )
				pdf.multi_cell( 15, 5, "", 0, 'C' )
				pdf.multi_cell( 15, 5, "", 0, 'C' )
				pdf.multi_cell( 13, 5, "", 0, 'C' )
				pdf.multi_cell( 11, 5, "", 0, 'C' )
				pdf.multi_cell( 17, 5, "", 0, 'C' )
				pdf.multi_cell( 25, 5, "", 0, 'R' )
				pdf.multi_cell( 25, 5, "", 0, 'R' )

		pdf.ln()

		net_total = net_total + overhead + transport + profit
		pdf.set_font( 'Arial', 'B', 11 )
		pdf.set_x( 3 )
		pdf.multi_cell( 147, 5, "Net Total", 1, 'R' )
		pdf.multi_cell( 17, 5, self.QuotationInfo[ 3 ], 1, 'C' )
		pdf.multi_cell( 40, 5, "{:,.2f}".format( net_total ), 1, 'R' )
		pdf.ln()
		pdf.set_x( 3 )
		vat = ( self.QuotationInfo[ 16 ] / 100 ) * ( net_total )
		pdf.multi_cell( 147, 5, "Vat " + str( self.QuotationInfo[ 16 ] ) + "%", 1, 'R' )
		pdf.multi_cell( 17, 5, self.QuotationInfo[ 3 ], 1, 'C' )
		pdf.multi_cell( 40, 5, "{:,.2f}".format( vat ), 1, 'R' )
		pdf.ln()
		pdf.set_x( 3 )
		pdf.multi_cell( 147, 5, "Grand Total", 1, 'R', True )
		pdf.multi_cell( 17, 5, self.QuotationInfo[ 3 ], 1, 'C', True )
		pdf.multi_cell( 40, 5, "{:,.2f}".format( math.ceil( net_total + vat ) ), 1, 'R', True )
		# pdf.rect( 5, 198, 200, 15 )

		pdf.ln()

		pdf.set_line_width( 0.3 )
		pdf.set_font( 'Arial', 'B', 9 )
		pdf.set_x( 3 )
		pdf.multi_cell( 204, 5, "Terms & Conditions", 1, 'L', True )
		pdf.set_font( 'Arial', '', 7 )
		result = self.DBHandler.execute(
		    """select * from termsandconditions where name == ?""", ( self.TC, )
		    ).fetchone()
		i = 0
		for tc in result[ 1 : ]:
			pdf.ln()
			pdf.set_x( 3 )
			pdf.multi_cell( 5, 4, str( i + 1 ), 1, 'C' )
			pdf.multi_cell( 199, 4, tc, 1, 'L' )
			i += 1

		pdf.set_x( 3, )
		pdf.ln()
		pdf.set_x( 3 )
		pdf.set_font( 'Arial', 'B', 9 )
		pdf.multi_cell( 8, 5, "No.", 1, 'C', True )
		pdf.multi_cell( 56, 5, "BANK NAME", 1, 'C', True )
		pdf.multi_cell( 56, 5, "ACCOUNT NUMBER", 1, 'C', True )
		pdf.multi_cell( 28, 5, "SWIFT CODE", 1, 'C', True )
		pdf.multi_cell( 28, 5, "CURRENCY", 1, 'C', True )
		pdf.multi_cell( 28, 5, "BRANCH", 1, 'C', True )
		pdf.set_font( 'Arial', '', 8 )

		pdf.ln()
		pdf.set_x( 3 )
		pdf.multi_cell( 8, 5, "1", 1, 'C' )
		pdf.multi_cell( 56, 5, "BANK Of BARODA (U) LTD.", 1, 'C' )
		pdf.multi_cell( 56, 5, "95030400000152", 1, 'C' )
		pdf.multi_cell( 28, 5, "BARBUGKA", 1, 'C' )
		pdf.multi_cell( 28, 5, "UGX", 1, 'C' )
		pdf.multi_cell( 28, 5, "JINJA", 1, 'C' )

		pdf.ln()
		pdf.set_x( 3 )
		pdf.multi_cell( 8, 5, "2", 1, 'C' )
		pdf.multi_cell( 56, 5, "BANK Of BARODA (U) LTD.", 1, 'C' )
		pdf.multi_cell( 56, 5, "95030400000150", 1, 'C' )
		pdf.multi_cell( 28, 5, "BARBUGKA", 1, 'C' )
		pdf.multi_cell( 28, 5, "USD", 1, 'C' )
		pdf.multi_cell( 28, 5, "JINJA", 1, 'C' )

		pdf.ln()
		pdf.set_x( 3 )
		pdf.multi_cell( 8, 5, "3", 1, 'C' )
		pdf.multi_cell( 56, 5, "DFCU BANK", 1, 'C' )
		pdf.multi_cell( 56, 5, "02463657216211", 1, 'C' )
		pdf.multi_cell( 28, 5, "DFCUUGKA", 1, 'C' )
		pdf.multi_cell( 28, 5, "USD", 1, 'C' )
		pdf.multi_cell( 28, 5, "JINJA", 1, 'C' )

		pdf.ln()
		pdf.set_x( 3 )
		pdf.multi_cell( 8, 5, "4", 1, 'C' )
		pdf.multi_cell( 56, 5, "DFCU BANK", 1, 'C' )
		pdf.multi_cell( 56, 5, "01463657215799", 1, 'C' )
		pdf.multi_cell( 28, 5, "DFCUUGKA", 1, 'C' )
		pdf.multi_cell( 28, 5, "UGX", 1, 'C' )
		pdf.multi_cell( 28, 5, "JINJA", 1, 'C' )

		now = datetime.now().strftime( "%I%M%S" )
		fileName = "Quotations\\" + r"{}_{}_{}.pdf".format(
		    self.QuotationInfo[ 4 ], self.QuotationInfo[ 1 ], now
		    ).replace( '/', '-' )

		pdf.output( fileName, 'F' )

		os.startfile( fileName )

	def printQuotationwithMaterials( self ):
		self.getQuontity()
		pdf = PDF()
		pdf.alias_nb_pages()
		pdf.add_page()
		pdf.set_line_width( 0.5 )
		pdf.set_fill_color( 180, 199, 231 )

		pdf.set_font( 'Arial', 'bu', 10 )
		pdf.text( 4, 36, "Extrusion Factory" )
		pdf.text( 149, 36, "Sales Outlet / Fabrication Division" )

		pdf.set_font( 'Arial', 'b', 8 )
		pdf.text( 4, 40.5, "Block 295 (Model Farm)" )
		pdf.text( 119, 40.5, "Plot No-155-165,Near DFCU Bank, Sixth Street, Kampala, Uganda" )

		pdf.text( 4, 44, "Plot - 321,498-504,506, Kyaggwe,Mibiko,Njeru " )
		pdf.text( 131.3, 44, "Tel : + 256 757614545 E-Mail : info@gdasindustries.com" )

		pdf.text( 4, 47.5, "PO Box 1069, Jinja, Uganda" )
		pdf.text( 160.5, 47.5, "Wesite : www.gdasindustries.com" )

		# pdf.rect( 3, 49, 204, 7, "DF" )
		pdf.set_font( 'Arial', 'b', 16 )
		# pdf.text( 92, 54.5, "Quotation" )

		pdf.ln( 18 )
		# pdf.set_x( 3 )
		pdf.set_xy( 3, 49 )
		pdf.multi_cell( 204, 7, "Used Materials and Accessories", 1, 'C', True )

		pdf.set_font( 'Arial', 'b', 9 )
		pdf.set_line_width( 0.3 )
		pdf.set_xy( 3, 56 )
		pdf.multi_cell( 18, 5, "Name", 1, 'L' )
		pdf.set_xy( 21, 56 )
		pdf.multi_cell( 64, 5, self.QuotationInfo[ 4 ], 1, 'L' )
		pdf.set_xy( 85, 56 )
		pdf.multi_cell( 16, 5, "Project", 1, 'L' )
		pdf.set_xy( 101, 56 )
		pdf.multi_cell( 50, 5, self.QuotationInfo[ 10 ], 1, 'L' )
		pdf.set_xy( 151, 56 )
		pdf.multi_cell( 18, 5, "Qta No.", 1, 'L' )
		pdf.set_xy( 169, 56 )
		pdf.multi_cell( 38, 5, "{:05d}".format( self.QuotationInfo[ 0 ] ), 1, 'L' )

		# pdf.set_x( 3 )
		pdf.set_xy( 3, 61 )
		pdf.multi_cell( 18, 5, "Tel No.", 1, 'L' )
		pdf.set_xy( 21, 61 )
		pdf.multi_cell( 64, 5, self.QuotationInfo[ 5 ], 1, 'L' )
		pdf.set_xy( 85, 61 )
		pdf.multi_cell( 16, 5, "Profile", 1, 'L' )
		pdf.set_xy( 101, 61 )
		pdf.multi_cell( 50, 5, self.QuotationInfo[ 8 ], 1, 'L' )
		pdf.set_xy( 151, 61 )
		pdf.multi_cell( 18, 5, "Ref No.", 1, 'L' )
		pdf.set_xy( 169, 61 )
		pdf.multi_cell( 38, 5, self.QuotationInfo[ 1 ], 1, 'L' )

		# pdf.set_x( 3 )
		pdf.set_xy( 3, 66 )
		pdf.multi_cell( 18, 5, "Email", 1, 'L' )
		pdf.set_xy( 21, 66 )
		pdf.multi_cell( 64, 5, self.QuotationInfo[ 6 ], 1, 'L' )
		pdf.set_xy( 85, 66 )
		pdf.multi_cell( 16, 5, "Finish", 1, 'L' )
		pdf.set_xy( 101, 66 )
		pdf.multi_cell( 50, 5, self.QuotationInfo[ 9 ], 1, 'L' )
		pdf.set_xy( 151, 66 )
		pdf.multi_cell( 18, 5, "Date", 1, 'L' )
		pdf.set_xy( 169, 66 )
		pdf.multi_cell( 38, 5, self.QuotationInfo[ 2 ].strftime( "%d-%m-%Y" ), 1, 'L' )
		# pdf.ln()

		# pdf.set_x( 3 )
		pdf.set_xy( 3, 71 )
		pdf.multi_cell( 18, 5, "Address", 1, 'L' )
		pdf.set_xy( 21, 71 )
		pdf.multi_cell( 64, 5, self.QuotationInfo[ 7 ], 1, 'L' )
		pdf.set_xy( 85, 71 )
		pdf.multi_cell( 16, 5, "Mesh", 1, 'L' )
		pdf.set_xy( 101, 71 )
		pdf.multi_cell( 50, 5, self.QuotationInfo[ 11 ], 1, 'L' )
		pdf.set_xy( 151, 71 )
		pdf.multi_cell( 18, 5, "Currency", 1, 'L' )
		pdf.set_xy( 169, 71 )
		pdf.multi_cell( 38, 5, self.QuotationInfo[ 3 ], 1, 'L' )

		# pdf.ln( 7 )
		pdf.set_x( 3 )
		pdf.set_font( 'Arial', 'b', 10 )
		pdf.set_xy( 3, 78 )
		pdf.multi_cell( 204, 6, "Material List", 1, 'C', True )
		# pdf.ln()
		pdf.set_xy( 3, 84 )
		pdf.multi_cell( 20, 5, "Code", 1, 'C' )
		pdf.set_xy( 23, 84 )
		pdf.multi_cell( 74, 5, "Name", 1, 'C' )
		pdf.set_xy( 97, 84 )
		pdf.multi_cell( 14, 5, "Unit", 1, 'C' )
		pdf.set_xy( 111, 84 )
		pdf.multi_cell( 18, 5, "Quontity", 1, 'C' )
		pdf.set_xy( 129, 84 )
		pdf.multi_cell( 20, 5, "Length", 1, 'C' )
		pdf.set_xy( 149, 84 )
		pdf.multi_cell( 20, 5, "Extra 10%", 1, 'C' )
		pdf.set_xy( 169, 84 )
		pdf.multi_cell( 18, 5, "PCS", 1, 'C' )
		pdf.set_xy( 187, 84 )
		pdf.multi_cell( 20, 5, "Weight", 1, 'C' )
		pdf.set_xy( 207, 84 )

		pdf.set_font( 'Arial', 'b', 9 )
		y = 84
		for code, mat in self.MaterialQty.items():
			print( mat )
			pcs = math.ceil( mat[ 5 ] )
			unit = mat[ 2 ].split( '/' )
			kg = float( unit[ 0 ] )
			mtr = float( unit[ 1 ] )
			weight = pcs * kg
			y += 5

			pdf.set_xy( 3, y )
			pdf.multi_cell( 20, 5, code, 1, 'C' )
			pdf.set_xy( 23, y )
			pdf.multi_cell( 74, 5, mat[ 0 ], 1, 'C' )
			pdf.set_xy( 97, y )
			pdf.multi_cell( 14, 5, mat[ 1 ], 1, 'C' )
			pdf.set_xy( 111, y )
			pdf.multi_cell( 18, 5, mat[ 2 ], 1, 'C' )
			pdf.set_xy( 129, y )
			pdf.multi_cell( 20, 5, "{:.2f}".format( mat[ 3 ] ), 1, 'C' )
			pdf.set_xy( 149, y )
			pdf.multi_cell( 20, 5, "{:.2f}".format( mat[ 4 ] ), 1, 'C' )
			pdf.set_xy( 169, y )
			pdf.multi_cell( 18, 5, str( pcs ), 1, 'C' )
			pdf.set_xy( 187, y )
			pdf.multi_cell( 20, 5, "{:.2f}".format( weight ), 1, 'C' )
			pdf.set_xy( 207, y )

		# pdf.ln( 7 )
		# pdf.set_x( 3 )
		pdf.set_font( 'Arial', 'b', 10 )
		pdf.set_xy( 3, y + 7 )

		pdf.multi_cell( 204, 6, "Accessory List", 1, 'C', True )
		pdf.ln()
		pdf.set_x( 3 )
		pdf.multi_cell( 20, 5, "Code", 1, 'C' )
		pdf.multi_cell( 74, 5, "Name", 1, 'C' )
		pdf.multi_cell( 14, 5, "Unit", 1, 'C' )
		pdf.multi_cell( 18, 5, "Quontity", 1, 'C' )
		pdf.multi_cell( 20, 5, "Length", 1, 'C' )
		pdf.multi_cell( 20, 5, "Extra 10%", 1, 'C' )
		pdf.multi_cell( 18, 5, "PCS", 1, 'C' )
		pdf.multi_cell( 20, 5, "Weight", 1, 'C' )
		pdf.set_font( 'Arial', 'b', 9 )

		for code, acc in self.AccessoryQty.items():
			pdf.ln()
			pdf.set_x( 3 )
			pdf.multi_cell( 20, 5, str( code ), 1, 'C' )
			pdf.multi_cell( 74, 5, acc[ 0 ], 1, 'C' )
			pdf.multi_cell( 14, 5, acc[ 1 ], 1, 'C' )
			pdf.multi_cell( 18, 5, "{:.2f}".format( acc[ 2 ] ), 1, 'C' )
			pdf.multi_cell( 20, 5, "-", 1, 'C' )
			pdf.multi_cell( 20, 5, "-", 1, 'C' )
			pdf.multi_cell( 18, 5, "{:.2f}".format( acc[ 3 ] ), 1, 'C' )
			pdf.multi_cell( 20, 5, "-", 1, 'C' )

		now = datetime.now().strftime( "%I%M%S" )
		fileName = "Quotations\\" + r"{}_{}_{}_MAList.pdf".format(
		    self.QuotationInfo[ 4 ], self.QuotationInfo[ 1 ], now
		    ).replace( '/', '-' )

		pdf.output( fileName, 'F' )

		os.startfile( fileName )


if __name__ == "__main__":
	DBHandler = sqlite3.connect(
	    "Data/GDAS.data", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
	    )
	p = PrintQuotation( DBHandler, 1 )
	# p.printQuotation( False, "abc" )
	p.printQuotationwithMaterials()
