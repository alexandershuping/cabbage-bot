''' CabbageBase Database Module '''

import psycopg2
import cabbagerc as rc

class CabbageBase:
	cdb = 0
	opened = False

	def __init__(self):
		''' Gets the database ready for queries '''
		self.cdb = psycopg2.connect(dbname=rc.DBNAME, user=rc.DBUSERNAME, password=rc.DBPASSWORD, host=rc.DBHOST, port=rc.DBPORT)
		self.opened = True

	def getCursor(self):
		''' Returns a cursor for performing database functions '''
		if not self.opened:
			return False

		return self.cdb.cursor()
	
	def commit(self):
		''' Commits a transaction '''
		if not self.opened:
			return False

		self.cdb.commit()
		return True
	
	def rollback(self):
		''' Rolls back a transaction '''
		if not self.opened:
			return False
		
		self.cdb.rollback()
		return True
	
	def close(self):
		''' Closes the connection '''

		if self.opened:
			self.cdb.close()
			self.opened = False
