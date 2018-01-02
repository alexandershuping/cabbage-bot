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
	
	def listTable(self, table):
		''' Returns all rows from the given table '''
		cur = self.cdb.cursor()
		cur.execute(sql.SQL('SELECT * from {};').format(sql.Identifier(table)))

		res = cur.fetchall()
		cur.close()
		return res

	def queryFilter(self, table, elem, val):
		''' Returns rows from the given table using the given filter '''
		cur = self.cdb.cursor()
		cur.execute(sql.SQL('SELECT * FROM {} WHERE {} = %s;').format(sql.Identifier(table), sql.Identifier(elem)), (val,))
		
		res = cur.fetchall()
		cur.close()
		return res
	
	def query2Filter(self, table, elem, val, elem2, val2):
		''' Returns rows from the given table using the given filters '''
		cur = self.cdb.cursor()
		cur.execute(sql.SQL('SELECT * FROM {} WHERE {} = %s AND {} = %s;').format(sql.Identifier(table), sql.Identifier(elem), sql.Identifier(elem2)), (val,val2))

		res = cur.fetchall()
		cur.close()
		return res
	
	def queryMultiFilter(self, table, *filters):
		''' Use the given filters, in the form (elem, value), to query '''
		cur = self.cdb.cursor()
		conSt = ''
		conLs = [sql.Identifier(table)]
		conEl = []
		nFilters = len(filters)
		for ftr in filters:
			if ftr:
				conSt = conSt + 'AND {} = %s '
				conLs.append(sql.Identifier(ftr[0]))
				conEl.append(ftr[1])

		conSt = 'SELECT * FROM {} WHERE ' + conSt[4:] + ';'
		print(conSt)
		print(str(conLs))
		print(str(conEl))

		cur.execute(sql.SQL(conSt).format(*conLs), conEl)

		res = cur.fetchall()
		cur.close()
		return res

	def queryRegexFilter(self, table, filters):
		''' Use the given filters, in the form (elem, value), to query '''
		cur = self.cdb.cursor()
		conSt = ''
		conLs = [sql.Identifier(table)]
		conEl = []
		nFilters = len(filters)
		for ftr in filters:
			if ftr:
				conSt = conSt + 'AND {} ~ E%s '
				conLs.append(sql.Identifier(ftr[0]))
				conEl.append(ftr[1])

		conSt = 'SELECT * FROM {} WHERE ' + conSt[4:] + ';'

		cur.execute(sql.SQL(conSt).format(*conLs), conEl)

		res = cur.fetchall()
		cur.close()
		return res
	
	def query(self, table, columns=None, filters=()):
		''' Use the given filters, in the form (elem, value), to query, and restrict the returned columns '''
		cur = self.cdb.cursor()
		conSt = ''
		conds = ''
		cols = ''
		conLs = []

		if not columns:
			cols = '  *'
		else:
			for col in columns:
				if col:
					cols = cols + ', {}'
					conLs.append(sql.Identifier(col))

		conEl = []
		conLs.append(sql.Identifier(table))
		nFilters = len(filters)
		for ftr in filters:
			if ftr:
				if type(ftr[1]) is str:
					conds = conds + 'AND {} ~ E%s '
					conEl.append(ftr[1])
				else:
					conds = conds + 'AND {} =%s '
					conEl.append(ftr[1])
				conLs.append(sql.Identifier(ftr[0]))

		conSt = 'SELECT ' + cols[2:] + ' FROM {}'
		if len(conEl) > 0:
			conSt = conSt + ' WHERE ' + conds[4:] + ';'
		else:
			conSt = conSt + ';'

		cur.execute(sql.SQL(conSt).format(*conLs), conEl)

		res = cur.fetchall()
		cur.close()
		return res

	
	def isPresentIn(self, column, checkValue, table, filters=()):
		res = self.query(table, (column,), filters)
		for result in res:
			if result[0] == checkValue:
				return True

		return False

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

