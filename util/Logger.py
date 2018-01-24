import cabbagerc as rc
from sq.cabbagebase import CabbageBase
from datetime import datetime, timedelta

class Logger:
	''' Functions for writing log data to the SQL database '''

	def __init__(self):
		self.base = CabbageBase
	
	def log(self, message, module='Core'):
		''' Logs a message (with optional module id) to the database '''
		cmd = 'INSERT INTO log (time, message, module) VALUES (%s,%s,%s)'
		cur = self.base.getCursor()
		cur.execute(cmd, (datetime.now(), message, module))
		cur.commit()
		cur.close()
