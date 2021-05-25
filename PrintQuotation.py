from fpdf import FPDF
from datetime import datetime
import sqlite3
import math
import os, subprocess

y = 0


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
		self.ln( 7 )
		globals()[ 'y' ] = self.y + 1
		# print( "called" )

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
		globals()[ 'y' ] = 0
		self.lastUsedSpace = 0
		if not os.path.exists( "Quotations" ):
			os.mkdir( "Quotations" )
		self.getData()

	def getData( self ):
		result = self.DBHandler.execute( """select * from currency""" ).fetchall()
		for cur in result:
			self.allCurrency[ cur[ 0 ] ] = float( cur[ 1 ] )

		self.Products = {}
		self.QuotationItems = {}
		self.QuotationInfo = []
		self.MaterialQty = {}
		self.AccessoryQty = {}
		self.GlassQty = {}

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

			if productId not in self.QuotationItems.keys():
				self.QuotationItems[ productId ] = {}

			self.QuotationItems[ productId ][ quoProductId ] = templist

	def getQuontity( self ):
		try:

			for productId, productGroup in self.QuotationItems.items():
				for quoProductId, product in productGroup.items():

					QuoPro = product[ 0 ]
					MaterialGroup = product[ 1 ]
					AccessoryGroup = product[ 2 ]

					matgroups = QuoPro[ 13 ]
					accgroups = QuoPro[ 14 ]

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
									    name, material[ 6 ], material[ 7 ], result, extra, pcs,
									    weight
									    ]

					for AGId, accessory_group in AccessoryGroup.items():

						if AGId in accgroups:
							for accessory in accessory_group:
								code = accessory[ 4 ]
								name = accessory[ 5 ]
								formula = accessory[ 10 ]
								unit = float( accessory[ 7 ] )
								result = float( eval( formula ) )
								pcs = result * unit
								# print( self.GlassQty )

								if code == "GD 0000/":
									# print( accessory )

									if QuoPro[ 21 ] in self.GlassQty.keys():
										self.GlassQty[ QuoPro[ 21 ] ][ 3 ] += pcs
									else:
										self.GlassQty[ QuoPro[ 21 ] ] = [
										    QuoPro[ 21 ], accessory[ 6 ], accessory[ 7 ], pcs
										    ]

								else:

									if code in self.AccessoryQty.keys():
										self.AccessoryQty[ code ][ 3 ] += pcs

									else:
										self.AccessoryQty[ code ] = [
										    name, accessory[ 6 ], accessory[ 7 ], pcs
										    ]
		except Exception as e:
			print( "getQuontity : ", e )

	def convertCurrency( self, src, des, value ):
		return ( ( self.allCurrency[ des ] * value ) / self.allCurrency[ src ] )

	def getRow( self, line=[], lineSpace=3 ):
		# print( line )
		res = []

		maxLines = 0

		lineHeight = 0
		y = 0
		for text, lineWidth in line:
			lineWidth = lineWidth - 2
			if text == "":
				text = "     "
			textWidth = self.pdf.get_string_width( text )
			totalLine = math.ceil( textWidth / lineWidth )
			# lineHeight = defaultLineHeight * totalLine
			if totalLine > maxLines:
				maxLines = totalLine
			# print( text, lineWidth, textWidth, totalLine, sep=" : " )

		# print( maxLines )

		for text, lineWidth in line:
			lineWidth = lineWidth - 2
			if text == "":
				text = "    "
			freeSpace = 0
			textWidth = self.pdf.get_string_width( text )
			usedLine = math.ceil( textWidth / lineWidth )
			# print( usedLine )
			if usedLine < maxLines:
				freeSpace = math.ceil( lineWidth * ( maxLines - 1 ) )
				spaceWidth = self.pdf.get_string_width( " " )
				# print( spaceWidth )
				pad = " " * math.floor( freeSpace / spaceWidth )
				text = text + "\n" + pad

			res.append( text )

		self.lastUsedSpace = maxLines * lineSpace
		return res

	def update_Y( self ):

		globals()[ 'y' ] += self.lastUsedSpace

	def printQuotation( self, sqm_flag=False, TC=None ):
		self.TC = TC
		# count = 1
		self.pdf = PDF()
		self.pdf.alias_nb_pages()
		self.pdf.add_page()
		self.pdf.c_margin = 1
		self.pdf.set_line_width( 0.5 )
		self.pdf.set_fill_color( 180, 199, 231 )

		self.pdf.set_font( 'Arial', 'bu', 10 )
		self.pdf.text( 4, 36, "Extrusion Factory" )
		self.pdf.text( 149, 36, "Sales Outlet / Fabrication Division" )

		self.pdf.set_font( 'Arial', 'b', 8 )
		self.pdf.text( 4, 40.5, "Block 295 (Model Farm)" )
		self.pdf.text( 119, 40.5, "Plot No-155-165,Near DFCU Bank, Sixth Street, Kampala, Uganda" )

		self.pdf.text( 4, 44, "Plot - 321,498-504,506, Kyaggwe,Mibiko,Njeru " )
		self.pdf.text( 131.3, 44, "Tel : + 256 757614545 E-Mail : info@gdasindustries.com" )

		self.pdf.text( 4, 47.5, "PO Box 1069, Jinja, Uganda" )
		self.pdf.text( 160.5, 47.5, "Wesite : www.gdasindustries.com" )

		# self.pdf.rect( 3, 49, 204, 7, "DF" )
		self.pdf.set_font( 'Arial', 'b', 16 )
		# self.pdf.text( 92, 54.5, "Quotation" )
		self.pdf.ln( 18 )
		globals()[ 'y' ] = self.pdf.y

		self.pdf.set_xy( 3, globals()[ 'y' ] )

		self.pdf.multi_cell( 204, 7, "Quotation", 1, 'C', True )
		globals()[ 'y' ] += 7

		self.pdf.set_font( 'Arial', 'b', 9 )
		self.pdf.set_line_width( 0.3 )

		row = self.getRow(
		    [
		        [ "Name", 18 ], [ self.QuotationInfo[ 4 ], 64 ], [ "Project", 16 ],
		        [ self.QuotationInfo[ 10 ], 50 ], [ "Qta No.", 18 ],
		        [ "{:05d}".format( self.QuotationInfo[ 0 ] ), 38 ]
		        ], 4
		    )

		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 4, row[ 0 ], 1, 'L' )
		self.pdf.set_xy( 21, globals()[ 'y' ] )
		self.pdf.multi_cell( 64, 4, row[ 1 ], 1, 'L' )
		self.pdf.set_xy( 85, globals()[ 'y' ] )
		self.pdf.multi_cell( 16, 4, row[ 2 ], 1, 'L' )
		self.pdf.set_xy( 101, globals()[ 'y' ] )
		self.pdf.multi_cell( 50, 4, row[ 3 ], 1, 'L' )
		self.pdf.set_xy( 151, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 4, row[ 4 ], 1, 'L' )
		self.pdf.set_xy( 169, globals()[ 'y' ] )
		self.pdf.multi_cell( 38, 4, row[ 5 ], 1, 'L' )

		self.update_Y()
		row = self.getRow(
		    [
		        [ "Tel No.", 18 ], [ self.QuotationInfo[ 5 ], 64 ], [ "Profile", 16 ],
		        [ self.QuotationInfo[ 8 ], 50 ], [ "Ref No.", 18 ], [ self.QuotationInfo[ 1 ], 38 ]
		        ], 4
		    )

		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 4, row[ 0 ], 1, 'L' )
		self.pdf.set_xy( 21, globals()[ 'y' ] )
		self.pdf.multi_cell( 64, 4, row[ 1 ], 1, 'L' )
		self.pdf.set_xy( 85, globals()[ 'y' ] )
		self.pdf.multi_cell( 16, 4, row[ 2 ], 1, 'L' )
		self.pdf.set_xy( 101, globals()[ 'y' ] )
		self.pdf.multi_cell( 50, 4, row[ 3 ], 1, 'L' )
		self.pdf.set_xy( 151, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 4, row[ 4 ], 1, 'L' )
		self.pdf.set_xy( 169, globals()[ 'y' ] )
		self.pdf.multi_cell( 38, 4, row[ 5 ], 1, 'L' )

		self.update_Y()
		row = self.getRow(
		    [
		        [ "Email", 18 ], [ self.QuotationInfo[ 6 ], 64 ], [ "Finish", 16 ],
		        [ self.QuotationInfo[ 9 ], 50 ], [ "Date", 18 ],
		        [ self.QuotationInfo[ 2 ].strftime( "%d-%m-%Y" ), 38 ]
		        ], 4
		    )

		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 4, row[ 0 ], 1, 'L' )
		self.pdf.set_xy( 21, globals()[ 'y' ] )
		self.pdf.multi_cell( 64, 4, row[ 1 ], 1, 'L' )
		self.pdf.set_xy( 85, globals()[ 'y' ] )
		self.pdf.multi_cell( 16, 4, row[ 2 ], 1, 'L' )
		self.pdf.set_xy( 101, globals()[ 'y' ] )
		self.pdf.multi_cell( 50, 4, row[ 3 ], 1, 'L' )
		self.pdf.set_xy( 151, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 4, row[ 4 ], 1, 'L' )
		self.pdf.set_xy( 169, globals()[ 'y' ] )
		self.pdf.multi_cell( 38, 4, row[ 5 ], 1, 'L' )
		self.update_Y()

		row = self.getRow(
		    [
		        [ "Address", 18 ], [ self.QuotationInfo[ 7 ], 64 ], [ "Mesh", 16 ],
		        [ self.QuotationInfo[ 11 ], 50 ], [ "Currency", 18 ],
		        [ self.QuotationInfo[ 3 ], 38 ]
		        ], 4
		    )

		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 4, row[ 0 ], 1, 'L' )
		self.pdf.set_xy( 21, globals()[ 'y' ] )
		self.pdf.multi_cell( 64, 4, row[ 1 ], 1, 'L' )
		self.pdf.set_xy( 85, globals()[ 'y' ] )
		self.pdf.multi_cell( 16, 4, row[ 2 ], 1, 'L' )
		self.pdf.set_xy( 101, globals()[ 'y' ] )
		self.pdf.multi_cell( 50, 4, row[ 3 ], 1, 'L' )
		self.pdf.set_xy( 151, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 4, row[ 4 ], 1, 'L' )
		self.pdf.set_xy( 169, globals()[ 'y' ] )
		self.pdf.multi_cell( 38, 4, row[ 5 ], 1, 'L' )

		self.update_Y()
		self.pdf.set_font( 'Arial', 'b', 9 )
		self.pdf.set_line_width( 0.3 )

		globals()[ 'y' ] += 2
		# self.pdf.ln()
		# self.pdf.set_xy( 3, globals()['y'] )
		if sqm_flag:
			self.pdf.set_xy( 3, globals()[ 'y' ] )
			self.pdf.multi_cell( 8, 5, "No.", 1, 'C', 1 )
			self.pdf.set_xy( 11, globals()[ 'y' ] )
			self.pdf.multi_cell( 68, 5, "Item Description", 1, 'C', 1 )
			self.pdf.set_xy( 79, globals()[ 'y' ] )
			self.pdf.multi_cell( 15, 5, "Width", 1, 'C', 1 )
			self.pdf.set_xy( 94, globals()[ 'y' ] )
			self.pdf.multi_cell( 15, 5, "Height", 1, 'C', 1 )
			self.pdf.set_xy( 109, globals()[ 'y' ] )
			self.pdf.multi_cell( 13, 5, "Sqm", 1, 'C', 1 )
			self.pdf.set_xy( 122, globals()[ 'y' ] )
			self.pdf.multi_cell( 11, 5, "Qty", 1, 'C', 1 )
			self.pdf.set_xy( 133, globals()[ 'y' ] )
			self.pdf.multi_cell( 13, 5, "T.Sqm", 1, 'C', 1 )
			self.pdf.set_xy( 146, globals()[ 'y' ] )
			self.pdf.multi_cell( 17, 5, "Sqm Rate", 1, 'C', 1 )
			self.pdf.set_xy( 163, globals()[ 'y' ] )
			self.pdf.multi_cell( 22, 5, "Unit Rate", 1, 'C', 1 )
			self.pdf.set_xy( 185, globals()[ 'y' ] )
			self.pdf.multi_cell( 22, 5, "Amount", 1, 'C', 1 )
		else:
			self.pdf.set_xy( 3, globals()[ 'y' ] )
			self.pdf.multi_cell( 10, 5, "No.", 1, 'C', 1 )
			self.pdf.set_xy( 13, globals()[ 'y' ] )
			self.pdf.multi_cell( 73, 5, "Item Description", 1, 'C', 1 )
			self.pdf.set_xy( 86, globals()[ 'y' ] )
			self.pdf.multi_cell( 15, 5, "Width", 1, 'C', 1 )
			self.pdf.set_xy( 101, globals()[ 'y' ] )
			self.pdf.multi_cell( 15, 5, "Height", 1, 'C', 1 )
			self.pdf.set_xy( 116, globals()[ 'y' ] )
			self.pdf.multi_cell( 13, 5, "Sqm", 1, 'C', 1 )
			self.pdf.set_xy( 129, globals()[ 'y' ] )
			self.pdf.multi_cell( 11, 5, "Qty", 1, 'C', 1 )
			self.pdf.set_xy( 140, globals()[ 'y' ] )
			self.pdf.multi_cell( 17, 5, "T. Sqm", 1, 'C', 1 )
			self.pdf.set_xy( 157, globals()[ 'y' ] )
			self.pdf.multi_cell( 25, 5, "Unit Rate", 1, 'C', 1 )
			self.pdf.set_xy( 182, globals()[ 'y' ] )
			self.pdf.multi_cell( 25, 5, "Amount", 1, 'C', 1 )

		globals()[ 'y' ] += 5

		total_sqm = 0
		total_qty = 0
		for productId, productGroup in self.QuotationItems.items():
			for quoProId, product in productGroup.items():
				product = product[ 0 ]
				total_qty += product[ 5 ]
				total_sqm += product[ 12 ]

		TL = 0
		for i in self.QuotationItems.values():
			TL += len( i )

		net_total = self.QuotationInfo[ 12 ]
		overhead = total_sqm * self.QuotationInfo[ 13 ]
		if self.QuotationInfo[ 3 ] != "USD":
			overhead = self.convertCurrency( "USD", self.QuotationInfo[ 3 ], overhead )
		transport = self.QuotationInfo[ 14 ]
		total = net_total + overhead + transport
		profit = ( float( self.QuotationInfo[ 15 ] ) / 100 ) * total
		div = ( overhead + transport + profit ) / TL

		# print( net_total, overhead, transport, total, profit, sep=" : " )

		self.pdf.set_font( 'Arial', 'b', 8 )
		no = 1

		for productId, productGroup in self.QuotationItems.items():
			for quoProId, product in productGroup.items():
				product = product[ 0 ]

				qty = product[ 5 ]
				tot_sqm = product[ 12 ]
				sqm = tot_sqm / qty

				groupLen = len( productGroup )
				netAmount = product[ 19 ] + ( div * groupLen )
				clientSqmRate = netAmount / product[ 18 ]
				ur = clientSqmRate * ( tot_sqm / qty )
				amount = clientSqmRate * tot_sqm

				if sqm_flag:
					row = self.getRow(
					    [
					        [ str( no ), 8 ],
					        [
					            "{} : {} : {}".format( product[ 1 ], product[ 21 ], product[ 23 ] ),
					            68
					            ], [ "{:.4f}".format( product[ 3 ] ), 15 ],
					        [ "{:.4f}".format( product[ 4 ] ), 15 ], [ "{:.2f}".format( sqm ), 13 ],
					        [ str( int( product[ 5 ] ) ), 11 ],
					        [ "{:.2f}".format( product[ 12 ] ), 13 ],
					        [ "{:,.2f}".format( clientSqmRate ), 17 ],
					        [ "{:,.2f}".format( ur ), 22 ], [ "{:,.2f}".format( amount ), 22 ]
					        ], 4
					    )
					self.pdf.set_xy( 3, globals()[ 'y' ] )
					self.pdf.multi_cell( 8, 4, row[ 0 ], 1, 'C' )
					self.pdf.set_xy( 11, globals()[ 'y' ] )
					self.pdf.multi_cell( 68, 4, row[ 1 ], 1, 'C' )
					self.pdf.set_xy( 79, globals()[ 'y' ] )
					self.pdf.multi_cell( 15, 4, row[ 2 ], 1, 'C' )
					self.pdf.set_xy( 94, globals()[ 'y' ] )
					self.pdf.multi_cell( 15, 4, row[ 3 ], 1, 'C' )
					self.pdf.set_xy( 109, globals()[ 'y' ] )
					self.pdf.multi_cell( 13, 4, row[ 4 ], 1, 'C' )
					self.pdf.set_xy( 122, globals()[ 'y' ] )
					self.pdf.multi_cell( 11, 4, row[ 5 ], 1, 'C' )
					self.pdf.set_xy( 133, globals()[ 'y' ] )
					self.pdf.multi_cell( 13, 4, row[ 6 ], 1, 'C' )
					self.pdf.set_xy( 146, globals()[ 'y' ] )
					self.pdf.multi_cell( 17, 4, row[ 7 ], 1, 'C' )
					self.pdf.set_xy( 163, globals()[ 'y' ] )
					self.pdf.multi_cell( 22, 4, row[ 8 ], 1, 'R' )
					self.pdf.set_xy( 185, globals()[ 'y' ] )
					self.pdf.multi_cell( 22, 4, row[ 9 ], 1, 'R' )
				else:
					row = self.getRow(
					    [
					        [ str( no ), 10 ],
					        [
					            "{} : {} : {}".format( product[ 1 ], product[ 21 ], product[ 23 ] ),
					            73
					            ], [ "{:.4f}".format( product[ 3 ] ), 15 ],
					        [ "{:.4f}".format( product[ 4 ] ), 15 ], [ "{:.2f}".format( sqm ), 13 ],
					        [ str( int( product[ 5 ] ) ), 11 ],
					        [ "{:.2f}".format( product[ 12 ] ), 17 ],
					        [ "{:,.2f}".format( ur ), 25 ], [ "{:,.2f}".format( amount ), 25 ]
					        ], 4
					    )
					self.pdf.set_xy( 3, globals()[ 'y' ] )
					self.pdf.multi_cell( 10, 4, row[ 0 ], 1, 'C' )
					self.pdf.set_xy( 13, globals()[ 'y' ] )
					self.pdf.multi_cell( 73, 4, row[ 1 ], 1, 'C' )
					self.pdf.set_xy( 86, globals()[ 'y' ] )
					self.pdf.multi_cell( 15, 4, row[ 2 ], 1, 'C' )
					self.pdf.set_xy( 101, globals()[ 'y' ] )
					self.pdf.multi_cell( 15, 4, row[ 3 ], 1, 'C' )
					self.pdf.set_xy( 116, globals()[ 'y' ] )
					self.pdf.multi_cell( 13, 4, row[ 4 ], 1, 'C' )
					self.pdf.set_xy( 129, globals()[ 'y' ] )
					self.pdf.multi_cell( 11, 4, row[ 5 ], 1, 'C' )
					self.pdf.set_xy( 140, globals()[ 'y' ] )
					self.pdf.multi_cell( 17, 4, row[ 6 ], 1, 'C' )
					self.pdf.set_xy( 157, globals()[ 'y' ] )
					self.pdf.multi_cell( 25, 4, row[ 7 ], 1, 'R' )
					self.pdf.set_xy( 182, globals()[ 'y' ] )
					self.pdf.multi_cell( 25, 4, row[ 8 ], 1, 'R' )

				# count += 1
				no += 1
				self.update_Y()

		# print( self.pdf.y )
		# print( globals()[ 'y' ] )

		while globals()[ 'y' ] < 200:

			self.pdf.set_xy( 3, globals()[ 'y' ] )
			self.pdf.multi_cell( 0, 4, "", 0, 'C' )

			globals()[ 'y' ] += 4

		# print( self.pdf.y )
		# self.pdf.ln()
		# globals()[ 'y' ] = self.pdf.y
		net_total = net_total + overhead + transport + profit
		self.pdf.set_font( 'Arial', 'B', 10 )
		if sqm_flag:
			self.pdf.set_xy( 3, globals()[ 'y' ] )
			self.pdf.multi_cell( 8, 5, "", 1, 'C' )
			self.pdf.set_xy( 11, globals()[ 'y' ] )
			self.pdf.multi_cell( 68, 5, "Total", 1, 'C' )
			self.pdf.set_xy( 79, globals()[ 'y' ] )
			self.pdf.multi_cell( 15, 5, "", 1, 'C' )
			self.pdf.set_xy( 94, globals()[ 'y' ] )
			self.pdf.multi_cell( 15, 5, "", 1, 'C' )
			self.pdf.set_xy( 109, globals()[ 'y' ] )
			self.pdf.multi_cell( 13, 5, "", 1, 'C' )
			self.pdf.set_xy( 122, globals()[ 'y' ] )
			self.pdf.multi_cell( 11, 5, "{:.2f}".format( total_qty ), 1, 'C' )
			self.pdf.set_xy( 133, globals()[ 'y' ] )
			self.pdf.multi_cell( 13, 5, "{:.2f}".format( total_sqm ), 1, 'C' )
			self.pdf.set_xy( 146, globals()[ 'y' ] )
			self.pdf.multi_cell( 17, 5, "", 1, 'C' )
			self.pdf.set_xy( 163, globals()[ 'y' ] )
			self.pdf.multi_cell( 22, 5, "", 1, 'R' )
			self.pdf.set_xy( 185, globals()[ 'y' ] )
			self.pdf.multi_cell( 22, 5, "", 1, 'R' )
		else:
			self.pdf.set_xy( 3, globals()[ 'y' ] )
			self.pdf.multi_cell( 10, 5, "", 1, 'C' )
			self.pdf.set_xy( 13, globals()[ 'y' ] )
			self.pdf.multi_cell( 73, 5, "Total", 1, 'C' )
			self.pdf.set_xy( 86, globals()[ 'y' ] )
			self.pdf.multi_cell( 15, 5, "", 1, 'C' )
			self.pdf.set_xy( 101, globals()[ 'y' ] )
			self.pdf.multi_cell( 15, 5, "", 1, 'C' )
			self.pdf.set_xy( 116, globals()[ 'y' ] )
			self.pdf.multi_cell( 13, 5, "", 1, 'C' )
			self.pdf.set_xy( 129, globals()[ 'y' ] )
			self.pdf.multi_cell( 11, 5, "{:.2f}".format( total_qty ), 1, 'C' )
			self.pdf.set_xy( 140, globals()[ 'y' ] )
			self.pdf.multi_cell( 17, 5, "{:.2f}".format( total_sqm ), 1, 'C' )
			self.pdf.set_xy( 157, globals()[ 'y' ] )
			self.pdf.multi_cell( 25, 5, "", 1, 'R' )
			self.pdf.set_xy( 182, globals()[ 'y' ] )
			self.pdf.multi_cell( 25, 5, "", 1, 'R' )
		globals()[ 'y' ] += 5

		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 147, 5, "Net Total", 1, 'R' )
		self.pdf.set_xy( 150, globals()[ 'y' ] )
		self.pdf.multi_cell( 17, 5, self.QuotationInfo[ 3 ], 1, 'C' )
		self.pdf.set_xy( 167, globals()[ 'y' ] )
		self.pdf.multi_cell( 40, 5, "{:,.2f}".format( net_total ), 1, 'R' )
		globals()[ 'y' ] += 5

		vat = ( self.QuotationInfo[ 16 ] / 100 ) * ( net_total )
		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 147, 5, "Vat " + str( self.QuotationInfo[ 16 ] ) + "%", 1, 'R' )
		self.pdf.set_xy( 150, globals()[ 'y' ] )
		self.pdf.multi_cell( 17, 5, self.QuotationInfo[ 3 ], 1, 'C' )
		self.pdf.set_xy( 167, globals()[ 'y' ] )
		self.pdf.multi_cell( 40, 5, "{:,.2f}".format( vat ), 1, 'R' )
		globals()[ 'y' ] += 5

		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 147, 5, "Grand Total", 1, 'R', True )
		self.pdf.set_xy( 150, globals()[ 'y' ] )
		self.pdf.multi_cell( 17, 5, self.QuotationInfo[ 3 ], 1, 'C', True )
		self.pdf.set_xy( 167, globals()[ 'y' ] )
		self.pdf.multi_cell( 40, 5, "{:,.2f}".format( math.ceil( net_total + vat ) ), 1, 'R', True )
		globals()[ 'y' ] += 5

		globals()[ 'y' ] += 2
		self.pdf.set_line_width( 0.3 )
		self.pdf.set_font( 'Arial', 'B', 9 )
		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 204, 5, "Terms & Conditions", 1, 'L', True )
		globals()[ 'y' ] += 5

		self.pdf.set_font( 'Arial', '', 7 )
		result = self.DBHandler.execute(
		    """select * from termsandconditions where name == ?""", ( self.TC, )
		    ).fetchone()
		i = 0
		for tc in result[ 1 : ]:

			row = self.getRow( [ [ str( i + 1 ), 5 ], [ tc, 199 ] ], 4 )
			self.pdf.set_xy( 3, globals()[ 'y' ] )
			self.pdf.multi_cell( 5, 4, row[ 0 ], 1, 'C' )
			self.pdf.set_xy( 8, globals()[ 'y' ] )
			self.pdf.multi_cell( 199, 4, row[ 1 ], 1, 'L' )
			self.update_Y()
			i += 1

		self.pdf.set_font( 'Arial', 'B', 9 )
		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 8, 5, "No.", 1, 'C', True )
		self.pdf.set_xy( 11, globals()[ 'y' ] )
		self.pdf.multi_cell( 56, 5, "BANK NAME", 1, 'C', True )
		self.pdf.set_xy( 67, globals()[ 'y' ] )
		self.pdf.multi_cell( 56, 5, "ACCOUNT NUMBER", 1, 'C', True )
		self.pdf.set_xy( 123, globals()[ 'y' ] )
		self.pdf.multi_cell( 28, 5, "SWIFT CODE", 1, 'C', True )
		self.pdf.set_xy( 151, globals()[ 'y' ] )
		self.pdf.multi_cell( 28, 5, "CURRENCY", 1, 'C', True )
		self.pdf.set_xy( 179, globals()[ 'y' ] )
		self.pdf.multi_cell( 28, 5, "BRANCH", 1, 'C', True )
		globals()[ 'y' ] += 5

		self.pdf.set_font( 'Arial', '', 8 )
		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 8, 4, "1", 1, 'C' )
		self.pdf.set_xy( 11, globals()[ 'y' ] )
		self.pdf.multi_cell( 56, 4, "BANK Of BARODA (U) LTD.", 1, 'C' )
		self.pdf.set_xy( 67, globals()[ 'y' ] )
		self.pdf.multi_cell( 56, 4, "95030400000152", 1, 'C' )
		self.pdf.set_xy( 123, globals()[ 'y' ] )
		self.pdf.multi_cell( 28, 4, "BARBUGKA", 1, 'C' )
		self.pdf.set_xy( 151, globals()[ 'y' ] )
		self.pdf.multi_cell( 28, 4, "UGX", 1, 'C' )
		self.pdf.set_xy( 179, globals()[ 'y' ] )
		self.pdf.multi_cell( 28, 4, "JINJA", 1, 'C' )
		globals()[ 'y' ] += 4

		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 8, 4, "2", 1, 'C' )
		self.pdf.set_xy( 11, globals()[ 'y' ] )
		self.pdf.multi_cell( 56, 4, "BANK Of BARODA (U) LTD.", 1, 'C' )
		self.pdf.set_xy( 67, globals()[ 'y' ] )
		self.pdf.multi_cell( 56, 4, "95030400000150", 1, 'C' )
		self.pdf.set_xy( 123, globals()[ 'y' ] )
		self.pdf.multi_cell( 28, 4, "BARBUGKA", 1, 'C' )
		self.pdf.set_xy( 151, globals()[ 'y' ] )
		self.pdf.multi_cell( 28, 4, "USD", 1, 'C' )
		self.pdf.set_xy( 179, globals()[ 'y' ] )
		self.pdf.multi_cell( 28, 4, "JINJA", 1, 'C' )
		globals()[ 'y' ] += 4

		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 8, 4, "3", 1, 'C' )
		self.pdf.set_xy( 11, globals()[ 'y' ] )
		self.pdf.multi_cell( 56, 4, "DFCU BANK", 1, 'C' )
		self.pdf.set_xy( 67, globals()[ 'y' ] )
		self.pdf.multi_cell( 56, 4, "02463657216211", 1, 'C' )
		self.pdf.set_xy( 123, globals()[ 'y' ] )
		self.pdf.multi_cell( 28, 4, "DFCUUGKA", 1, 'C' )
		self.pdf.set_xy( 151, globals()[ 'y' ] )
		self.pdf.multi_cell( 28, 4, "USD", 1, 'C' )
		self.pdf.set_xy( 179, globals()[ 'y' ] )
		self.pdf.multi_cell( 28, 4, "JINJA", 1, 'C' )
		globals()[ 'y' ] += 4

		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 8, 4, "4", 1, 'C' )
		self.pdf.set_xy( 11, globals()[ 'y' ] )
		self.pdf.multi_cell( 56, 4, "DFCU BANK", 1, 'C' )
		self.pdf.set_xy( 67, globals()[ 'y' ] )
		self.pdf.multi_cell( 56, 4, "01463657215799", 1, 'C' )
		self.pdf.set_xy( 123, globals()[ 'y' ] )
		self.pdf.multi_cell( 28, 4, "DFCUUGKA", 1, 'C' )
		self.pdf.set_xy( 151, globals()[ 'y' ] )
		self.pdf.multi_cell( 28, 4, "UGX", 1, 'C' )
		self.pdf.set_xy( 179, globals()[ 'y' ] )
		self.pdf.multi_cell( 28, 4, "JINJA", 1, 'C' )
		globals()[ 'y' ] += 4
		path = os.getcwd()
		now = datetime.now().strftime( "%I%M%S" )
		fileName = path + "/Quotations/" + r"{}_{}_{}.self.pdf".format(
		    self.QuotationInfo[ 4 ], self.QuotationInfo[ 1 ], now
		    ).replace( '/', '-' )

		self.pdf.output( fileName, 'F' )

		if os.name == "nt":
			os.startfile( fileName )
		elif os.name == "posix":
			subprocess.call( [ 'open', fileName ] )
			# os.system( "open {}".format( fileName ) )

	def printQuotationwithMaterials( self ):
		self.getQuontity()
		self.pdf = PDF()
		self.pdf.alias_nb_pages()
		self.pdf.add_page()
		self.pdf.set_line_width( 0.5 )
		self.pdf.set_fill_color( 180, 199, 231 )

		self.pdf.set_font( 'Arial', 'bu', 10 )
		self.pdf.text( 4, 36, "Extrusion Factory" )
		self.pdf.text( 149, 36, "Sales Outlet / Fabrication Division" )

		self.pdf.set_font( 'Arial', 'b', 8 )
		self.pdf.text( 4, 40.5, "Block 295 (Model Farm)" )
		self.pdf.text( 119, 40.5, "Plot No-155-165,Near DFCU Bank, Sixth Street, Kampala, Uganda" )

		self.pdf.text( 4, 44, "Plot - 321,498-504,506, Kyaggwe,Mibiko,Njeru " )
		self.pdf.text( 131.3, 44, "Tel : + 256 757614545 E-Mail : info@gdasindustries.com" )

		self.pdf.text( 4, 47.5, "PO Box 1069, Jinja, Uganda" )
		self.pdf.text( 160.5, 47.5, "Wesite : www.gdasindustries.com" )

		self.pdf.set_font( 'Arial', 'b', 16 )

		self.pdf.ln( 18 )
		globals()[ 'y' ] = self.pdf.y

		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 204, 7, "Used Materials and Accessories", 1, 'C', True )
		# self.lastUsedSpace = 7
		globals()[ 'y' ] += 7
		self.pdf.set_font( 'Arial', 'b', 9 )
		self.pdf.set_line_width( 0.3 )

		row = self.getRow(
		    [
		        [ "Name", 18 ], [ self.QuotationInfo[ 4 ], 64 ], [ "Project", 16 ],
		        [ self.QuotationInfo[ 10 ], 50 ], [ "Qta No.", 18 ],
		        [ "{:05d}".format( self.QuotationInfo[ 0 ] ), 38 ]
		        ], 4
		    )

		self.pdf.c_margin = 1

		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 4, row[ 0 ], 1, 'L' )
		self.pdf.set_xy( 21, globals()[ 'y' ] )
		self.pdf.multi_cell( 64, 4, row[ 1 ], 1, 'L' )
		self.pdf.set_xy( 85, globals()[ 'y' ] )
		self.pdf.multi_cell( 16, 4, row[ 2 ], 1, 'L' )
		self.pdf.set_xy( 101, globals()[ 'y' ] )
		self.pdf.multi_cell( 50, 4, row[ 3 ], 1, 'L' )
		self.pdf.set_xy( 151, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 4, row[ 4 ], 1, 'L' )
		self.pdf.set_xy( 169, globals()[ 'y' ] )
		self.pdf.multi_cell( 38, 4, row[ 5 ], 1, 'L' )

		self.update_Y()
		row = self.getRow(
		    [
		        [ "Tel No.", 18 ], [ self.QuotationInfo[ 5 ], 64 ], [ "Profile", 16 ],
		        [ self.QuotationInfo[ 8 ], 50 ], [ "Ref No.", 18 ], [ self.QuotationInfo[ 1 ], 38 ]
		        ], 4
		    )
		# self.pdf.set_x( 3 )
		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 4, row[ 0 ], 1, 'L' )
		self.pdf.set_xy( 21, globals()[ 'y' ] )
		self.pdf.multi_cell( 64, 4, row[ 1 ], 1, 'L' )
		self.pdf.set_xy( 85, globals()[ 'y' ] )
		self.pdf.multi_cell( 16, 4, row[ 2 ], 1, 'L' )
		self.pdf.set_xy( 101, globals()[ 'y' ] )
		self.pdf.multi_cell( 50, 4, row[ 3 ], 1, 'L' )
		self.pdf.set_xy( 151, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 4, row[ 4 ], 1, 'L' )
		self.pdf.set_xy( 169, globals()[ 'y' ] )
		self.pdf.multi_cell( 38, 4, row[ 5 ], 1, 'L' )

		self.update_Y()
		row = self.getRow(
		    [
		        [ "Email", 18 ], [ self.QuotationInfo[ 6 ], 64 ], [ "Finish", 16 ],
		        [ self.QuotationInfo[ 9 ], 50 ], [ "Date", 18 ],
		        [ self.QuotationInfo[ 2 ].strftime( "%d-%m-%Y" ), 38 ]
		        ], 4
		    )

		# self.pdf.set_x( 3 )
		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 4, row[ 0 ], 1, 'L' )
		self.pdf.set_xy( 21, globals()[ 'y' ] )
		self.pdf.multi_cell( 64, 4, row[ 1 ], 1, 'L' )
		self.pdf.set_xy( 85, globals()[ 'y' ] )
		self.pdf.multi_cell( 16, 4, row[ 2 ], 1, 'L' )
		self.pdf.set_xy( 101, globals()[ 'y' ] )
		self.pdf.multi_cell( 50, 4, row[ 3 ], 1, 'L' )
		self.pdf.set_xy( 151, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 4, row[ 4 ], 1, 'L' )
		self.pdf.set_xy( 169, globals()[ 'y' ] )
		self.pdf.multi_cell( 38, 4, row[ 5 ], 1, 'L' )
		# self.pdf.ln()
		self.update_Y()

		row = self.getRow(
		    [
		        [ "Address", 18 ], [ self.QuotationInfo[ 7 ], 64 ], [ "Mesh", 16 ],
		        [ self.QuotationInfo[ 11 ], 50 ], [ "Currency", 18 ],
		        [ self.QuotationInfo[ 3 ], 38 ]
		        ], 4
		    )
		# print( row )

		# self.pdf.set_x( 3 )
		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 4, row[ 0 ], 1, 'L' )
		self.pdf.set_xy( 21, globals()[ 'y' ] )
		self.pdf.multi_cell( 64, 4, row[ 1 ], 1, 'L' )
		self.pdf.set_xy( 85, globals()[ 'y' ] )
		self.pdf.multi_cell( 16, 4, row[ 2 ], 1, 'L' )
		self.pdf.set_xy( 101, globals()[ 'y' ] )
		self.pdf.multi_cell( 50, 4, row[ 3 ], 1, 'L' )
		self.pdf.set_xy( 151, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 4, row[ 4 ], 1, 'L' )
		self.pdf.set_xy( 169, globals()[ 'y' ] )
		self.pdf.multi_cell( 38, 4, row[ 5 ], 1, 'L' )

		self.update_Y()

		# self.pdf.ln( 7 )
		globals()[ 'y' ] += 3
		self.pdf.set_x( 3 )
		self.pdf.set_font( 'Arial', 'b', 10 )
		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 204, 6, "Material List", 1, 'C', True )
		globals()[ 'y' ] += 6

		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 20, 5, "Code", 1, 'C' )
		self.pdf.set_xy( 23, globals()[ 'y' ] )
		self.pdf.multi_cell( 74, 5, "Name", 1, 'C' )
		self.pdf.set_xy( 97, globals()[ 'y' ] )
		self.pdf.multi_cell( 14, 5, "Unit", 1, 'C' )
		self.pdf.set_xy( 111, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 5, "Quontity", 1, 'C' )
		self.pdf.set_xy( 129, globals()[ 'y' ] )
		self.pdf.multi_cell( 20, 5, "Length", 1, 'C' )
		self.pdf.set_xy( 149, globals()[ 'y' ] )
		self.pdf.multi_cell( 20, 5, "Extra 10%", 1, 'C' )
		self.pdf.set_xy( 169, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 5, "PCS", 1, 'C' )
		self.pdf.set_xy( 187, globals()[ 'y' ] )
		self.pdf.multi_cell( 20, 5, "Weight", 1, 'C' )
		self.pdf.set_xy( 207, globals()[ 'y' ] )
		globals()[ 'y' ] += 5

		self.pdf.set_font( 'Arial', 'b', 8 )
		# y = 84
		for code, mat in self.MaterialQty.items():
			# print( mat )
			pcs = math.ceil( mat[ 5 ] )
			unit = mat[ 2 ].split( '/' )
			kg = float( unit[ 0 ] )
			mtr = float( unit[ 1 ] )
			weight = pcs * kg
			# print( self.pdf.y )
			row = self.getRow(
			    [
			        [ code, 20 ], [ mat[ 0 ], 74 ], [ mat[ 1 ], 14 ], [ mat[ 2 ], 18 ],
			        [ "{:.2f}".format( mat[ 3 ] ), 20 ], [ "{:.2f}".format( mat[ 4 ] ), 20 ],
			        [ str( pcs ), 18 ], [ "{:.2f}".format( weight ), 20 ]
			        ], 4
			    )
			# print( row )
			self.pdf.set_xy( 3, globals()[ 'y' ] )
			self.pdf.multi_cell( 20, 4, row[ 0 ], 1, 'L' )
			self.pdf.set_xy( 23, globals()[ 'y' ] )
			self.pdf.multi_cell( 74, 4, row[ 1 ], 1, 'L' )
			self.pdf.set_xy( 97, globals()[ 'y' ] )
			self.pdf.multi_cell( 14, 4, row[ 2 ], 1, 'L' )
			self.pdf.set_xy( 111, globals()[ 'y' ] )
			self.pdf.multi_cell( 18, 4, row[ 3 ], 1, 'L' )
			self.pdf.set_xy( 129, globals()[ 'y' ] )
			self.pdf.multi_cell( 20, 4, row[ 4 ], 1, 'L' )
			self.pdf.set_xy( 149, globals()[ 'y' ] )
			self.pdf.multi_cell( 20, 4, row[ 5 ], 1, 'L' )
			self.pdf.set_xy( 169, globals()[ 'y' ] )
			self.pdf.multi_cell( 18, 4, row[ 6 ], 1, 'L' )
			self.pdf.set_xy( 187, globals()[ 'y' ] )
			self.pdf.multi_cell( 20, 4, row[ 7 ], 1, 'L' )
			# self.pdf.set_xy( 207, globals()['y'] )

			self.update_Y()

		# self.pdf.ln( 7 )
		# self.pdf.set_x( 3 )

		globals()[ 'y' ] += 3
		self.pdf.set_font( 'Arial', 'b', 10 )
		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 204, 6, "Accessory List", 1, 'C', True )
		globals()[ 'y' ] += 6

		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 20, 5, "Code", 1, 'C' )
		self.pdf.set_xy( 23, globals()[ 'y' ] )
		self.pdf.multi_cell( 74, 5, "Name", 1, 'C' )
		self.pdf.set_xy( 97, globals()[ 'y' ] )
		self.pdf.multi_cell( 14, 5, "Unit", 1, 'C' )
		self.pdf.set_xy( 111, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 5, "Quontity", 1, 'C' )
		self.pdf.set_xy( 129, globals()[ 'y' ] )
		self.pdf.multi_cell( 20, 5, "Length", 1, 'C' )
		self.pdf.set_xy( 149, globals()[ 'y' ] )
		self.pdf.multi_cell( 20, 5, "Extra 10%", 1, 'C' )
		self.pdf.set_xy( 169, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 5, "PCS", 1, 'C' )
		self.pdf.set_xy( 187, globals()[ 'y' ] )
		self.pdf.multi_cell( 20, 5, "Weight", 1, 'C' )

		globals()[ 'y' ] += 5
		self.pdf.set_font( 'Arial', 'b', 8 )

		for code, acc in self.AccessoryQty.items():

			row = self.getRow(
			    [
			        [ str( code ), 20 ], [ acc[ 0 ], 74 ], [ acc[ 1 ], 14 ],
			        [ "{:.2f}".format( acc[ 2 ] ), 18 ], [ "-", 20 ], [ "-", 20 ],
			        [ "{:.2f}".format( acc[ 3 ] ), 18 ], [ "-", 20 ]
			        ], 4
			    )
			# print( row )

			self.pdf.set_xy( 3, globals()[ 'y' ] )
			self.pdf.multi_cell( 20, 4, row[ 0 ], 1, 'C' )
			self.pdf.set_xy( 23, globals()[ 'y' ] )
			self.pdf.multi_cell( 74, 4, row[ 1 ], 1, 'C' )
			self.pdf.set_xy( 97, globals()[ 'y' ] )
			self.pdf.multi_cell( 14, 4, row[ 2 ], 1, 'C' )
			self.pdf.set_xy( 111, globals()[ 'y' ] )
			self.pdf.multi_cell( 18, 4, row[ 3 ], 1, 'C' )
			self.pdf.set_xy( 129, globals()[ 'y' ] )
			self.pdf.multi_cell( 20, 4, row[ 4 ], 1, 'C' )
			self.pdf.set_xy( 149, globals()[ 'y' ] )
			self.pdf.multi_cell( 20, 4, row[ 5 ], 1, 'C' )
			self.pdf.set_xy( 169, globals()[ 'y' ] )
			self.pdf.multi_cell( 18, 4, row[ 6 ], 1, 'C' )
			self.pdf.set_xy( 187, globals()[ 'y' ] )
			self.pdf.multi_cell( 20, 4, row[ 7 ], 1, 'C' )
			self.update_Y()

		globals()[ 'y' ] += 3
		self.pdf.set_font( 'Arial', 'b', 10 )
		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 204, 6, "Glass List", 1, 'C', True )
		globals()[ 'y' ] += 6

		self.pdf.set_xy( 3, globals()[ 'y' ] )
		self.pdf.multi_cell( 20, 5, "Code", 1, 'C' )
		self.pdf.set_xy( 23, globals()[ 'y' ] )
		self.pdf.multi_cell( 74, 5, "Name", 1, 'C' )
		self.pdf.set_xy( 97, globals()[ 'y' ] )
		self.pdf.multi_cell( 14, 5, "Unit", 1, 'C' )
		self.pdf.set_xy( 111, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 5, "Quontity", 1, 'C' )
		self.pdf.set_xy( 129, globals()[ 'y' ] )
		self.pdf.multi_cell( 20, 5, "Length", 1, 'C' )
		self.pdf.set_xy( 149, globals()[ 'y' ] )
		self.pdf.multi_cell( 20, 5, "Extra 10%", 1, 'C' )
		self.pdf.set_xy( 169, globals()[ 'y' ] )
		self.pdf.multi_cell( 18, 5, "PCS", 1, 'C' )
		self.pdf.set_xy( 187, globals()[ 'y' ] )
		self.pdf.multi_cell( 20, 5, "Weight", 1, 'C' )

		globals()[ 'y' ] += 5
		self.pdf.set_font( 'Arial', 'b', 8 )

		for code, acc in self.GlassQty.items():

			row = self.getRow(
			    [
			        [ "GD 0000/", 20 ], [ acc[ 0 ], 74 ], [ acc[ 1 ], 14 ],
			        [ "{:.2f}".format( acc[ 2 ] ), 18 ], [ "-", 20 ], [ "-", 20 ],
			        [ "{:.2f}".format( acc[ 3 ] ), 18 ], [ "-", 20 ]
			        ], 4
			    )
			# print( row )

			self.pdf.set_xy( 3, globals()[ 'y' ] )
			self.pdf.multi_cell( 20, 4, row[ 0 ], 1, 'C' )
			self.pdf.set_xy( 23, globals()[ 'y' ] )
			self.pdf.multi_cell( 74, 4, row[ 1 ], 1, 'C' )
			self.pdf.set_xy( 97, globals()[ 'y' ] )
			self.pdf.multi_cell( 14, 4, row[ 2 ], 1, 'C' )
			self.pdf.set_xy( 111, globals()[ 'y' ] )
			self.pdf.multi_cell( 18, 4, row[ 3 ], 1, 'C' )
			self.pdf.set_xy( 129, globals()[ 'y' ] )
			self.pdf.multi_cell( 20, 4, row[ 4 ], 1, 'C' )
			self.pdf.set_xy( 149, globals()[ 'y' ] )
			self.pdf.multi_cell( 20, 4, row[ 5 ], 1, 'C' )
			self.pdf.set_xy( 169, globals()[ 'y' ] )
			self.pdf.multi_cell( 18, 4, row[ 6 ], 1, 'C' )
			self.pdf.set_xy( 187, globals()[ 'y' ] )
			self.pdf.multi_cell( 20, 4, row[ 7 ], 1, 'C' )
			self.update_Y()
		now = datetime.now().strftime( "%I%M%S" )

		path = os.getcwd()
		fileName = path + "/Quotations/" + r"{}_{}_{}_MAList.self.pdf".format(
		    self.QuotationInfo[ 4 ], self.QuotationInfo[ 1 ], now
		    ).replace( '/', '-' )

		self.pdf.output( fileName, 'F' )

		if os.name == "nt":
			os.startfile( fileName )
		elif os.name == "posix":
			# os.system( "open {}".format( fileName ) )
			subprocess.call( [ 'open', fileName ] )


if __name__ == "__main__":
	DBHandler = sqlite3.connect(
	    "Data/GDAS.data", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
	    )
	p = PrintQuotation( DBHandler, 1 )
	# p.printQuotation( False, "TC1" )
	p.printQuotationwithMaterials()