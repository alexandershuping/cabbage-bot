import cabbagerc as rc
from sql.cabbagebase import CabbageBase
from datetime import datetime, timedelta

class Logger:
	''' Functions for writing log data to the SQL database 
	  ' Note on logging verbosity levels:
		'  1 -- critical program error/crash
		'  2 -- program error or warning
		'  3 -- extra-high-importance
		'  4 -- high-importance (e.g. admin promotion/demotion)
		'  5 -- standard importance
		'  6 -- low importance (new poll tracking messages)
		'  7 -- extra-low importance
	  '''

	def __init__(self):
		self.base = CabbageBase()
	
	def log(self, message, module='Core', verbosity=5):
		''' Logs a message (with optional module id) to the database '''
		cmd = 'INSERT INTO log (time, message, module, verbosity) VALUES (%s,%s,%s,%s)'
		cur = self.base.getCursor()
		cur.execute(cmd, (datetime.now(), message, module, verbosity))
		self.base.commit()
		cur.close()
