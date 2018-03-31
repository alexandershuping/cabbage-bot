import cabbagerc as rc
import psycopg2
from psycopg2 import sql
from sql.cabbagebase import CabbageBase
from datetime import datetime, timedelta

class FlagFramework:
	''' Functions for managing simple flags in the SQL database
	  ' Note that flags are not unique -- that is, it is possible to have
		' multiple flags with the same name but different values.
		'''


	def __init__(self):
		self.base = CabbageBase()
		self.tables = ['baseflags', 'boolflags', 'textflags', 'intflags', 'userflags']
		self.ttypes = [None,bool,str,int,int]


	def fset(self, flag, module, server=0):
		''' Sets a flag without a value '''
		cmd = 'INSERT INTO baseFlags (time, name, module, server) VALUES (%s,%s,%s,%s)'
		cur = self.base.getCursor()
		cur.execute(cmd, (datetime.now(), flag, module, int(server)))
		self.base.commit()
		cur.close()


	def bset(self, flag, module, server=0, value=True):
		''' Sets a flag with a boolean value '''
		cmd = 'INSERT INTO boolFlags (time, name, module, flag, server) VALUES (%s,%s,%s,%s,%s)'
		cur = self.base.getCursor()
		cur.execute(cmd, (datetime.now(), flag, module, value, int(server)))
		self.base.commit()
		cur.close()


	def tset(self, flag, module, server=0, value=''):
		''' Sets a flag with a plaintext value '''
		cmd = 'INSERT INTO textFlags (time, name, module, flag, server) VALUES (%s,%s,%s,%s,%s)'
		cur = self.base.getCursor()
		cur.execute(cmd, (datetime.now(), flag, module, value, int(server)))
		self.base.commit()
		cur.close()


	def iset(self, flag, module, server=0, value=0):
		''' Sets a flag with an integer value '''
		cmd = 'INSERT INTO intFlags (time, name, module, flag, server) VALUES (%s,%s,%s,%s,%s)'
		cur = self.base.getCursor()
		cur.execute(cmd, (datetime.now(), flag, module, value, int(server)))
		self.base.commit()
		cur.close()


	def uset(self, flag, module, server, value):
		''' Sets a flag with a discord user value '''
		cmd = 'INSERT INTO userFlags (time, name, module, flag, server) VALUES (%s,%s,%s,%s,%s)'
		cur = self.base.getCursor()
		cur.execute(cmd, (datetime.now(), flag, module, value, int(server)))
		self.base.commit()
		cur.close()


	def hasFlag(self, name, module, server=0):
		''' Checks if the given flag exists, regardless of type or value '''
		for table in self.tables:
			if self.base.isPresentIn('name', name, table, (('module',module),('server',int(server)))):
				return True

		return False


	def getFlag(self, name, module, server=0):
		''' Gets all present values for the given flag '''
		flags = []
		for table in self.tables:
			if table == 'baseflags':
				query = self.base.query(table, ('time','name','module','server'), (('name',name),('module',module),('server',int(server))))
				if query and len(query)>0:
					for que in query:
						flags.append({'timestamp':que[0],'name':que[1],'module':que[2],'flag':None,'server':que[3]})
			else:
				query = self.base.query(table, ('time','name','module','flag','server'), (('name',name),('module',module),('server',int(server))))
				if query and len(query)>0:
					for que in query:
						flags.append({'timestamp':que[0],'name':que[1],'module':que[2],'flag':que[3],'server':que[4]})
		if len(flags) > 0:
			return flags
		else:
			return None


	def delFlag(self, name, module, server=0, value=None):
		''' Removes a flag from the database.'''
		for dex,table in enumerate(self.tables):
			if value and type(value) != self.ttypes[dex]:
				''' This table can't possibly have the value. Skip it.'''
				continue
			cmd = 'DELETE FROM {} WHERE name = %s AND module = %s AND server = %s'
			if value and table != 'baseflags':
				cmd = cmd + ' AND flag = %s'
			cmd = cmd + ';'

			cur = self.base.getCursor()
			print('Removing flags with value ' + str(value) + ' from server id ' + str(server))
			if value and table != 'baseflags':
				cur.execute(sql.SQL(cmd).format(sql.Identifier(table)), (name, module, server, value));
			else:
				cur.execute(sql.SQL(cmd).format(sql.Identifier(table)), (name, module, server));		
		
		self.base.commit()
		cur.close()
