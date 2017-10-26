''' CabbageBase Database Module '''

import psycopg2
from psycopg2 import sql
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
	
	def query(self, table):
		''' Returns all rows from the given table '''
		cur = self.cdb.cursor()
		cur.execute(sql.SQL('SELECT * from {};').format(sql.Identifier(table)))

		return cur

	def queryFilter(self, table, elem, val):
		''' Returns rows from the given table using the given filter '''
		cur = self.cdb.cursor()
		cur.execute(sql.SQL('SELECT * FROM {} WHERE {} = %s;').format(sql.Identifier(table), sql.Identifier(elem)), (val,))

		return cur
	
	def query2Filter(self, table, elem, val, elem2, val2):
		''' Returns rows from the given table using the given filters '''
		cur = self.cdb.cursor()
		cur.execute(sql.SQL('SELECT * FROM {} WHERE {} = %s AND {} = %s').format(sql.Identifier(table), sql.Identifier(elem), sql.Identifier(elem2)), (val,val2))

		return cur
	
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
