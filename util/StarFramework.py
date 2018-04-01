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
	def __init__(self, server, bot):
		self.log = Logger()
		self.base = CabbageBase()
		self.flags = FlagFramework()
		self.server = server
		self.bot = bot
		self.sbChanid = None
		self.sbChannel = None
		self.thresh = None
		if self.flags.hasFlag('channel', 'star', self.server.id):
			self.sbChanid = self.flags.getFlag('channel', 'star', self.server.id)[0]['flag']
			self.sbChannel = self.server.get_channel(self.sbChanid)
		if self.flags.hasFlag('thresh', 'star', self.server.id):
			self.thresh = self.flags.getFlag('thresh', 'star', self.server.id)[0]['flag']



	def isWorking(self):
		''' Returns true if the server's starboard has been set up and is
				valid.
		'''
		return self.sbChannel and self.thresh and self.thresh > 0



	def reset(self, channel, thresh):
		''' Resets the starboard parameters to the provided ones. 
		'''
		self.sbChannel = channel
		if thresh > 0:
			self.thresh = thresh
		else:
			raise StarThresholdError
		self.log.log('Starboard for server ' + self.server.id + ' updated: parameters changed', 'star', 7)
		self._update()



	def _update(self):
		''' Updates the server flags and database entries for the starboard.
				Note that this does NOT check any messages for new stars or
				update starboard messages.
		'''
		if self.thresh <= 0:
			raise StarThresholdError
		self.flags.tset('channel', 'star', self.server.id, self.sbChannel.id)
		self.flags.iset('thresh', 'star', self.server.id, self.thresh)
		self.sbChanId = self.sbChannel.id



	def getStarboardMessage(self, chanid, messid):
		''' Return a StarMessage object for the provided message. 
		'''
		q = self.base.query('starboard', ('original_message_channel','starboard_message_messid'), (('server',int(self.server.id)),('original_message_channel',int(chanid)),('original_message_messid',int(messid))))
		if q and len(q) > 0:
			sm = StarMessage(self.server.id, q[0][0], messid, q[0][1])
		else:
			sm = StarMessage(self.server.id, chanid, messid)

		return sm


	
	def _determineAppropriateStarEmoji(self, numStars):
		''' Determines the appropriate star emoji
		'''
		if numStars < self.thresh:
			return '⚫'
		elif numStars < (1.5 * self.thresh):
			return '⭐'
		elif numStars < (2 * self.thresh):
			return '✴'
		elif numStars < (3 * self.thresh):
			return '🌠'
		else:
			return '🌌'



	async def _postOrUpdateStarboardMessage(self, msg, channel):
		''' Posts a message to the starboard, or (if it is already there)
				updates it to reflect changes in star totals.
		'''
		srv = self.bot.get_server(msg.server)
		cha = channel
		mes = await self.bot.get_message(cha, msg.messid)
		sbMessid = None

		if msg.starboardMessid:
			sbMessid = msg.starboardMessid
		else:
			# The message indicates that it is not yet on the starboard, but
			# check anyway.
			q = self.base.query('starboard', ('starboard_message_messid',), (('server',int(self.server.id)),('original_message_channel',int(self.sbChanid)),('original_message_messid',int(msg.messid))))
			if q and len(q) > 0:
				# It was actually on the starboard.
				sbMessid = q[0][0]

		newEmbed = msg.constructEmbed(mes)
		numStars = msg.getStars()
		header = '**' + self._determineAppropriateStarEmoji(numStars) + str(numStars) + '   ' + cha.mention + '**'

		if sbMessid:	
			sbMessage = await self.bot.get_message(self.sbChannel, sbMessid)
			await self.bot.edit_message(sbMessage, header, embed=newEmbed)
		else:
			newSbMes = await self.bot.send_message(self.sbChannel, header, embed=newEmbed)
			cmd = 'INSERT INTO starboard (server, starboard, starboard_message_messid, original_message_channel, original_message_messid, original_message_sent) VALUES (%s,%s,%s,%s,%s,%s)'
			cur = self.base.getCursor()
			cur.execute(cmd, (int(self.server.id), int(self.sbChanid), int(newSbMes.id), int(mes.channel.id), int(mes.id), mes.timestamp))
			self.base.commit()
			cur.close()





class StarMessage:
	''' Class representing a message with stars '''
	def __init__(self, server, chanid, messid, starboardMessid=None):
		self.base = CabbageBase()
		self.server = server
		self.chanid = chanid
		self.messid = messid 
		self.starboardMessid = starboardMessid



	def star(self, uid):
		''' Adds a star to a message, as long as it has not been starred by
				the same user before.
		'''
		if not self.hasStarred(uid):
			cur = self.base.getCursor()
			insertString = 'INSERT INTO stars (server,chanid,messid,starrer) VALUES (%s,%s,%s,%s);'
			cur.execute(insertString, (self.server, self.chanid, self.messid, uid))
			self.base.commit()
			cur.close()



	def unstar(self, uid):
		''' Removes a star from a message.
		'''
		if self.hasStarred(self, uid):
			cur = self.base.getCursor()
			delString = 'DELETE FROM ONLY stars WHERE server=%s AND chanid=%s AND messid=%s AND starrer=%s'
			cur.execute(delString, (self.server, self.chanid, self.messid, uid))
			self.base.commit()
			cur.close()



	def getStars(self):
		''' Returns the number of unique users who have starred the message.
		'''
		res = self.base.query('stars', ('server',), (('server', int(self.server)), ('messid', int(self.messid))))
		return len(res)



	def hasStarred(self, uid):
		''' Determines whether the provided user has previously starred the 
				message.
		'''
		res = self.base.query('stars', ('server',), (('server', int(self.server)), ('messid', int(self.messid)), ('starrer', int(uid))))
		return len(res) > 0



	def constructEmbed(self, messageObject):
		''' Constructs the embed object to be used in the starboard message.
		'''
		embed = discord.Embed(colour=discord.Colour(0x7f3e96), description=messageObject.content, timestamp=messageObject.timestamp)

		embed.set_author(name=messageObject.author.name, icon_url=messageObject.author.avatar_url)

		if messageObject.attachments and len(messageObject.attachments) > 0:
			attachment = messageObject.attachments[0]

			if attachment['filename'].lower().endswith(('gif', 'jpg', 'jpeg', 'png')):
				embed.set_image(url=attachment['url'])
			else:
				embed.add_field(name='Also attached',value=str(attachment['filename']))

		return embed
	


	async def updateStarboard(self, serverObject, channelObject, bot):
		''' Check if we're above the threshold value for the starboard. If so,
				ask to be posted.
		'''
		s = Starboard(serverObject, bot)
		if self.getStars() >= s.thresh:
			await s._postOrUpdateStarboardMessage(self, channelObject)
