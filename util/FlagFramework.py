import cabbagerc as rc
from sq.cabbagebase import CabbageBase
from datetime import datetime, timedelta

class FlagFramework:
	''' Functions for managing simple flags in the SQL database '''

	def __init__(self):
		self.base = CabbageBase
		self.tables = ['baseFlags', 'boolFlags', 'textFlags', 'intFlags', 'userFlags']
	
	def fset(self, flag, module):
		''' Sets a flag without a value '''
		cmd = 'INSERT INTO baseFlags (time, name, module) VALUES (%s,%s,%s)'
		cur = self.base.getCursor()
		cur.execute(cmd, (datetime.now(), flag, module))
		self.base.commit()
		cur.close()


	def bset(self, flag, module, value=True):
		''' Sets a flag with a boolean value '''
		cmd = 'INSERT INTO boolFlags (time, name, module, flag) VALUES (%s,%s,%s,%s)'
		cur = self.base.getCursor()
		cur.execute(cmd, (datetime.now(), flag, module, value))
		self.base.commit()
		cur.close()
	
	def tset(self, flag, module, value=''):
		''' Sets a flag with a plaintext value '''
		cmd = 'INSERT INTO textFlags (time, name, module, flag) VALUES (%s,%s,%s,%s)'
		cur = self.base.getCursor()
		cur.execute(cmd, (datetime.now(), flag, module, value))
		self.base.commit()
		cur.close()
	
	def iset(self, flag, module, value=0):
		''' Sets a flag with an integer value '''
		cmd = 'INSERT INTO intFlags (time, name, module, flag) VALUES (%s,%s,%s,%s)'
		cur = self.base.getCursor()
		cur.execute(cmd, (datetime.now(), flag, module, value))
		self.base.commit()
		cur.close()
	
	def uset(self, flag, module, value):
		''' Sets a flag with a discord user value '''
		cmd = 'INSERT INTO userFlags (time, name, module, flag) VALUES (%s,%s,%s,%s)'
		cur = self.base.getCursor()
		cur.execute(cmd, (datetime.now(), flag, module, value))
		self.base.commit()
		cur.close()
	
	def hasFlag(self, name, module):
		''' Checks if the given flag exists, regardless of type or value '''
		for table in self.tables:
			if self.base.isPresentIn('name', name, table, (('module',module),)):
				return True

		return False
	
	def getFlag(self, name, module):
		''' Gets the value of the given flag '''
		if self.base.isPresentIn('name', name, 'baseFlags', (('module',module),)):
			return True # Handle value-less base table
		for table in self.tables:
			if table == 'baseFlags':
				continue # Skip base table
			que = self.base.query(table, ('timestamp','name','module','flag'), (('name',name),('module',module)))
			if que and len(que)>0:
				return {'timestamp':que[0][0],'name':que[0][1],'module':que[0][2],'flag':que[0][3]}
				# TODO finish this method

