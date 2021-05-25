import string
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import hashlib
from urllib.request import urlopen
import os


class Validation:

	def sendKey( self, name ):

		self.res = ''.join(
		    random.choices( string.ascii_uppercase + string.ascii_lowercase + string.digits, k=24 )
		    )
		print( "The generated random string : " + str( self.res ) )
		self.name = name
		# if self.check_connection():
		try:

			fromaddr = "gdascostingsystem@gmail.com"

			toaddr = "kishanpatel31199@gmail.com"

			# instance of MIMEMultipart
			msg = MIMEMultipart()

			# storing the senders email address
			msg[ 'From' ] = fromaddr

			# storing the receivers email address
			msg[ 'To' ] = toaddr

			# storing the subject
			msg[ 'Subject' ] = "Key"

			# string to store the body of the mail
			body = self.name + " --> " + self.res

			# attach the body with the msg instance
			msg.attach( MIMEText( body, 'plain' ) )

			s = smtplib.SMTP( 'smtp.gmail.com', 587 )

			# start TLS for security
			s.starttls()

			# Authentication
			s.login( fromaddr, "Password" )

			# Converts the Multipart msg into a string
			text = msg.as_string()

			# sending the mail
			s.sendmail( fromaddr, toaddr, text )

			# terminating the session
			s.quit()
			return True
		except Exception as e:

			print( e )
			return str( e )

	# def check_connection( self ):
	# 	try:
	# 		urlopen( 'https://www.google.com', timeout=4 )
	# 		return True
	# 	except:
	# 		return False

	# def compare( self, license_key ):
	# 	temp = []
	# 	hash_key = hashlib.md5(
	# 	    hashlib.sha1(
	# 	        hashlib.sha256( hashlib.sha512( self.res.encode() ).hexdigest().encode()
	# 	                       ).hexdigest().encode()
	# 	        ).hexdigest().encode()
	# 	    ).hexdigest()
	# 	for i, j in zip( [ 0, 8, 16, 24 ], [ 8, 16, 24, 32 ] ):
	# 		temp.append( hash_key[ i : j ] )
	# 	key = '-'.join( temp )

	# 	if license_key == key:
	# 		return True
	# 	else:
	# 		False

	def compare( self, license_key ):
		if license_key == self.res:
			return True
		else:
			return False
