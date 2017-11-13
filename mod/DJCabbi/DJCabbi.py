import random
import re
import discord
import cabbagerc as rc
import sql.cabbagebase as cb
from discord.ext import commands
from phrasebook.Phrasebook import Phrasebook

class DJCabbi:
	''' Music Functionality '''
	voice = None

	def __init__(self, bot):
		self.bot = bot
		self.voice = None
	
	@commands.command(pass_context=True)
	async def join(self, ctx, chan : discord.Channel):
		''' Joins the specified voice channel '''
		self.voice = await self.bot.join_voice_channel(chan)
	
	@commands.command()
	async def skip(self):
		''' Skips the current song '''
		await self.bot.say('Skipping this song.')
		self.player.stop()
		await self.playFrom()
	
	@commands.command()
	async def stop(self):
		''' Stops the current song '''
		await self.bot.say('Stopping music player.')
		self.continueSongs = False
		self.player.stop()

	@commands.command(pass_context=True)
	async def play(self, ctx, *reqs):
		''' Play random songs matching the given query
		    Queries take the form 'play [title] [by <artist>] [from <album>]'
		'''
		request = self.parseCommandPhrase(reqs)
		print(str(request['ARTIST']))
		result = self.query(request['ARTIST'], request['ALBUM'], request['TITLE'])

		ackString = ''
		for res in result:
			ackString = ackString + '"' + res['TITLE'] + '" BY ' + res['ARTIST'] + '\n'

		if ackString and len(ackString) > 0:
			if len(ackString) > 1900:
				ackString = ackString[:1900] + '\n... and more.'
			await self.bot.say(str(len(result)) + ' results:\n' + ackString)
			self.continueSongs = True
			self.interruptPlay = False
			self.songList = result
			await self.playFrom()
		else:
			await self.bot.say('No results found.')

	async def playFrom(self):
		if not self.voice or not self.voice.is_connected():
			await self.bot.say('Not connected.')
			return
		if not self.continueSongs:
			await self.bot.say('Playback halted.')
			return
		choice = random.choice(self.songList)
		await self.bot.say('Playing ' + choice['TITLE'] + ' by ' + choice['ARTIST'])
		self.player = self.voice.create_ffmpeg_player(choice['DIR'], after=self.playFrom)
		self.player.start()

	def parseCommandPhrase(self, words):
		''' Parse a request into song, artist, album '''
		req = {'ARTIST':None,'ALBUM':None,'TITLE':None}
		working = ''
		mode = 'TITLE'
		for word in words:
			if word[0] == '~':
				# Word has been escaped (i.e. NOT a keyword)
				working.append(' ' + word[1:])
				continue
			if word.upper() == 'BY':
				# Note that working will have a leading space at this point.
				# It must be trimmed before the value is returned.
				req[mode] = working.strip()
				mode = 'ARTIST'
				working = ''
				continue
			if word.upper() == 'IN' or word.upper() == 'FROM':
				req[mode] = working.strip()
				mode = 'ALBUM'
				working = ''
				continue
			if word.upper() == 'NAME' or word.upper() == 'NAMED':
				req[mode] = working.strip()
				mode = 'TITLE'
				working = ''
				continue
			working = working + ' ' + word

		if len(working.strip()) != 0:
			req[mode] = working.strip()
		return req

	def query(self, artist=None, album=None, title=None):
		restrictions = ''
		fils = []
		if artist and len(artist) > 0:
			fils.append(('artist', artist.lower()))
		if album and len(album) > 0:
			fils.append(('album', album.lower()))
		if title and len(title) > 0:
			fils.append(('name', title.lower()))

		base = cb.CabbageBase()

		quRes = base.queryRegexFilter('songbook', fils)

		songs = []
		for res in quRes:
			if res:
				songs.append({ \
					'TITLE':res[0], \
					'ALBUM':res[1], \
					'ARTIST':res[2], \
					'DIR':res[3] \
				})

		return songs
	
def setup(bot):
	bot.add_cog(DJCabbi(bot))
