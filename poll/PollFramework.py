import random
import sys
import re
from sql.cabbagebase import CabbageBase
from util.Logger import Logger
from datetime import datetime, timedelta
import cabbagerc as rc

class PollFramework:
	''' Backend tasks for polls '''
	def __init__(self, creator, server, name=None, description=None, openTime=None, closeTime=None, absoluteThreshold=None, percentThreshold=None, percentThresholdMinimum=None, thresholdTime=None, keepUpdated=True, pollid=None):
		self.log = Logger()
		self.base = CabbageBase()
		self.creator = creator
		self.server = server
		self.name = name
		self.description = description
		self.openTime = openTime
		self.closeTime = closeTime
		self.absoluteThreshold = absoluteThreshold
		self.percentThreshold = percentThreshold
		self.percentThresholdMinimum = percentThresholdMinimum
		self.thresholdTime = thresholdTime
		self.options = {'short':[], 'long':[], 'emoji':[]}
		self.keepUpdated = keepUpdated
		if pollid:
			self.pollid = pollid
		else:
			self.genPollid()
		self.update()
	
	@classmethod
	def fromSQL(cls, queryRow):
		log = Logger()
		log.log('Building pollid ' + str(queryRow[0]) + ' from SQL row', 'poll', 8)
		working = cls(queryRow[1], queryRow[2], queryRow[3], queryRow[4], queryRow[5], queryRow[6], queryRow[7], queryRow[8], queryRow[9], queryRow[10], keepUpdated=False, pollid=queryRow[0])
		opts = []
		for i in range(0,len(queryRow[11])):
			working.addOption(queryRow[11][i], queryRow[12][i], queryRow[13][i])
		working.setUpdate(True)
		print('Built pollid ' + str(queryRow[0]))
		return working

	
	def genPollid(self):
		#while True:
		propPollid = random.randint(-1*sys.maxsize, sys.maxsize)
		# This checks for the infinitesimal (1/(2*sys.maxsize+1) ~= 0) chance
		# of an id conflict. Uncomment if it ever becomes a problem. It shouldn't.
		#	if not self.base.isPresentIn('pollid', propPollid, 'polls'):
		#		break
		self.pollid = propPollid
		self.update()

	def setName(self,name):
		self.name = name
		self.update()
	
	def setDescription(self, desc):
		self.description = desc
		self.update()
	
	def setOpenTime(self, openTime):
		self.openTime = openTime
		self.update()
	
	def setCloseTime(self, closeTime):
		self.closeTime = closeTime
		self.update()
	
	def setAbsoluteThreshold(self, absThreshold):
		self.absoluteThreshold = absThreshold
		self.update()
	
	def setPercentThreshold(self, percThreshold):
		self.percentThreshold = percThreshold
		self.update()
	
	def setPercentThresholdMinimum(self, percThresholdMin):
		self.percentThresholdMinimum = percThresholdMin
		self.update()
	
	def setThresholdTime(self, threshTime):
		self.thresholdTime = threshTime
		self.update()
	
	def setUpdate(self, keepUp):
		self.keepUpdated = keepUp
	
	def addOption(self, shortOption, longOption, emojiOption=None):
		self.options['short'].append(shortOption)
		self.options['long'].append(longOption)
		if emojiOption:
			if re.match('<:.+:[0-9]+>', emojiOption):
				self.options['emoji'].append(emojiOption[-1:1])
			else:
				self.options['emoji'].append(emojiOption[0])
		else:
			self.options['emoji'].append(None)
		self.update()
	
	def addTrackingMessage(self, messid, chanid):
		''' Add a message to the list of tracked messages '''
		res = self.base.query('activemessages', filters=(('messid', int(messid)), ('chanid', int(chanid))))
		if res and len(res) > 0:
			# This message is already registered
			return False
		cmd = 'INSERT INTO activemessages (messid, chanid, pollid) VALUES (%s,%s,%s)'
		cur = self.base.getCursor()
		cur.execute(cmd, (int(messid), int(chanid), self.pollid))
		self.base.commit()
		cur.close()
		return True
	
	def delTrackingMessage(self, messid, chanid):
		''' Remove a message from the list of tracked messages '''
		res = self.base.query('activemessages', filters=(('messid', int(messid)), ('chanid', int(chanid))))
		if not res or len(res) == 0:
			# Message not found
			return False
		cmd = 'DELETE FROM ONLY activemessages WHERE messid = %s AND chanid = %s'
		cur = self.base.getCursor()
		cur.execute(cmd, (messid, chanid))
		self.base.commit()
		cur.close()
		return True
	
	def getTrackingMessages(self):
		''' Return all messages that are supposed to be updated '''
		res = self.base.query('activemessages', ('messid','chanid','pollid'))
		processed = []
		for result in res:
			# Convert to dict for convenience
			processed.append({'messid':result[0],'chanid':result[1],'pollid':result[2]})
		return processed
	
	def get(self):
		''' Return a dictionary containing all of the relevant poll parameters
		    (i.e. everything except votes and tracking messages)
		'''
		return {'creator':self.creator, 'server':self.server, 'name':self.name, 'description':self.description, 'pollid':self.pollid, 'openTime':self.openTime, 'closeTime':self.closeTime, 'absoluteThreshold':self.absoluteThreshold, 'percentThreshold':self.percentThreshold, 'percentThresholdMinimum':self.percentThresholdMinimum, 'thresholdTime':self.thresholdTime, 'options':self.options}

	def vote(self, user, shortOption):
		''' Registers a vote from a user by short option '''
		res = self.base.query('polls', ('shortoptions','opentime','closetime'), (('pollid', self.pollid),))

		curTime = datetime.now()
		if curTime - res[0][1] < timedelta(seconds=0) or curTime - res[0][2] > timedelta(seconds=0):
			return 2 # Poll is closed

		cmd = 'DELETE FROM ONLY votes WHERE voterid = %s AND pollid = %s;'
		cur = self.base.getCursor()
		cur.execute(cmd, (user, self.pollid))
		if shortOption not in res[0][0]:
			self.base.rollback()
			cur.close()
			return 1 # Invalid option
		
		cmd = 'INSERT INTO votes (voterid, pollid, voteTime, vote) VALUES (%s,%s,%s,%s)'
		cur.execute(cmd, (user, self.pollid, datetime.now(), shortOption))
		self.base.commit()
		cur.close()
		return 0 # OK
		
	def voteEmoji(self, user, emojiOption):
		''' Registers a votefrom a user by emoji option '''
		cmd = 'DELETE FROM ONLY votes WHERE voterid = %s AND pollid = %s;'
		cur = self.base.getCursor()
		cur.execute(cmd, (user, self.pollid))
		res = self.base.query('polls', ('shortoptions','emojioptions'), (('pollid', self.pollid),))
		shortEq = None
		for dex, shortOpt in enumerate(res[0][0]):
			if res[0][1][dex] == emojiOption:
				shortEq = shortOpt

		if not shortEq:
			# User voted with invalid emoji. Bad user.
			self.base.rollback()
			cur.close()
			return 1;
		
		return self.vote(user, shortEq)
	
	def getVoteDetails(self):
		''' Retrieves all votes from the SQL database '''
		return self.base.query('votes', ('voterid', 'pollid', 'votetime', 'vote'), (('pollid', self.pollid),))
	
	def getVoteTotals(self):
		''' Retrieves the total number of votes for each option '''
		counts = {};
		cur = self.base.getCursor()
		for option in self.options['short']:
			cur.execute('SELECT * FROM votes WHERE pollid = %s AND vote = %s', (self.pollid, option))
			counts[option] = cur.rowcount
		cur.close()
		return counts
	
	def update(self):
		''' Update the SQL database to reflect changes to the object '''
		if not self.keepUpdated:
			return # Update only functions if the object has keepUpdated set true
		self.log.log('Poll ID ' + str(self.pollid) + ' (' + self.name + ') updated.', 'poll', 7)
		cur = self.base.getCursor()
		table = 'polls'
		execString = '(creatorid, serverid, name, description, pollid, openTime, closeTime, absoluteThreshold, percentThreshold, percentThresholdMinimum, thresholdTime, shortOptions, longOptions, emojiOptions)'
		valString = '(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
		caveat = 'WHERE pollid=' + str(self.pollid)
		constructed = 'UPDATE ONLY ' + table + ' SET ' + execString + ' = ' + valString + caveat + ';'
		print(str(cur.mogrify( \
			constructed, \
				(self.creator, \
				self.server, \
				self.name, \
				self.description, \
				self.pollid, \
				self.openTime, \
				self.closeTime, \
				self.absoluteThreshold, \
				self.percentThreshold, \
				self.percentThresholdMinimum, \
				self.thresholdTime, \
				self.options['short'], \
				self.options['long'], \
				self.options['emoji'] \
				)\
			)))
		cur.execute( \
			constructed, \
				(self.creator, \
				self.server, \
				self.name, \
				self.description, \
				self.pollid, \
				self.openTime, \
				self.closeTime, \
				self.absoluteThreshold, \
				self.percentThreshold, \
				self.percentThresholdMinimum, \
				self.thresholdTime, \
				self.options['short'], \
				self.options['long'], \
				self.options['emoji'] \
				)\
			)

		if cur.statusmessage == 'UPDATE 0':
			# This is a new poll; insert it into the table
			constructed = 'INSERT INTO ' + table + execString + ' VALUES ' + valString + ';'
			cur.execute( \
				constructed, \
					(self.creator, \
					self.server, \
					self.name, \
					self.description, \
					self.pollid, \
					self.openTime, \
					self.closeTime, \
					self.absoluteThreshold, \
					self.percentThreshold, \
					self.percentThresholdMinimum, \
					self.thresholdTime, \
					self.options['short'], \
					self.options['long'], \
					self.options['emoji'] \
					)\
				)
			ms = 'Created new poll with pollid ' + str(self.pollid)
			rc.pinfo(ms)
			self.log.log(ms, 'poll', 6)
			self.base.commit()
		elif cur.statusmessage != 'UPDATE 1':
			errm = 'Rolling back UPDATE command for Poll object due to abnormal response -- check for multiple polls with the same pollid: ' + str(self.pollid) + ' (returned message: ' + str(cur.statusmessage) + ')'
			rc.perr(errm)
			self.log.log(errm, 'poll', 2)
			self.base.rollback()
		else:
			# Normal response; safe to commit
			self.base.commit()

		# Either way, release the database hold
		cur.close()
