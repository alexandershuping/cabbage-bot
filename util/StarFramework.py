import discord
import cabbagerc as rc
from discord.ext import commands
from util.FlagFramework import FlagFramework
from util.Logger import Logger
from sql.cabbagebase import CabbageBase
from datetime import datetime

class StarThresholdError:
	''' Thrown when a caller attempts to set the starboard threshold (the
	    number of stars required for the bot to post the message on the 
			starboard) to an invalid value.
	'''
	pass



class Starboard:
	''' Class representing a server's Starboard '''
	def __init__(self, server):
		self.flags = FlagFramework()
		self.server = server
		self.channel = self.flags.getFlag('channel', 'star', self.server)
		self.thresh = self.flags.getFlag('thresh', 'star', self.server)



	def isWorking(self):
		return self.channel and self.thresh and self.thresh > 0



	def reset(self, channel, thresh=None):
		self.channel = channel
		if thresh > 0:
			self.thresh = thresh
		else:
			raise StarThresholdError
		self.log.log('Starboard for server ' + self.server.id + ' updated: parameters changed', 'star', 7)
		self.update()



	def update(self):
		if self.thresh <= 0:
			raise StarThresholdError
		self.flags.tset('channel', 'star', self.server, self.channel)
		self.flags.iset('thresh', 'star', self.server, self.thresh)






class StarMessage:
	''' Class representing a message with stars '''
	def __init__(self, server, chanid, messid):
		self.base = CabbageBase()
		self.server = server
		self.chanid = chanid
		self.messid = messid 



	def star(self, uid):
	''' Adds a star to a message '''
		if not self.hasStarred(self, uid):
			cur = self.base.getCursor()
			insertString = 'INSERT INTO stars (server,chanid,messid,starrer) VALUES (%s,%s,%s,%s);'
			cur.execute(insertString, (self.server, self.chanid, self.messid, uid))
			self.base.commit()
			cur.close()



	def unstar(self, uid):
		if self.hasStarred(self, uid):
			cur = self.base.getCursor()
			delString = 'DELETE FROM ONLY stars WHERE server=%s AND chanid=%s AND messid=%s AND starrer=%s'
			cur.execute(delString, (self.server, self.chanid, self.messid, uid))
			self.base.commit()
			cur.close()



	def getStars(self):
		res = self.base.query('stars', ('server',), (('server', self.server), ('messid', self.messid)))
		return len(res)



	def hasStarred(self, uid):
		res = self.base.query('stars', ('server',), (('server', self.server), ('messid', self.messid), ('starrer', uid)))
		return len(res) > 0



	def constructEmbed(self, messageObject):
		embed = discord.Embed(colour=discord.Colour(0x7f3e96), description=messageObject.text, timestamp=messageObject.timestamp)

		embed.set_author(name=messageObject.author.name, icon_url=messageObject.author.avatar_url)

		return embed
