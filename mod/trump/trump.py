import random
import re
import discord
import requests
from lxml import etree
from discord.ext import commands
from phrasebook.Phrasebook import Phrasebook

class RollerParseException(Exception):
	pass

class Trump:
	''' Die Roller Module '''
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command(pass_context=True)
	async def trump(self, ctx, *target):
		''' Get presidential insight '''
		p = Phrasebook(ctx, self.bot)
		try:
			if(target):
				s = ''
				for t in target:
					s = s + t + ' '
				r = requests.get('https://api.whatdoestrumpthink.com/api/v1/quotes/personalized?q=' + s.rstrip())
			else:
				r = requests.get('https://api.whatdoestrumpthink.com/api/v1/quotes/random')
		except ConnectionError:
			await self.bot.say(p.pickPhrase('web', 'timeout', 'Presidential Quote', 'https://api.whatdoestrumpthink.com'))
			return
		await self.bot.say(p.pickPhrase('trump', 'trump', (r.json()['message']) + '\n\n  -- Donald J. Trump'))
		#await self.bot.delete_message(ctx.message)
	
	@commands.command(pass_context=True)
	async def dog(self, ctx):
		''' Get a dog '''
		p = Phrasebook(ctx, self.bot)
		try:
			r = requests.get('https://dog.ceo/api/breeds/image/random')
		except ConnectionError:
			await self.bot.say(p.pickPhrase('web', 'timeout', 'Dog Picture', 'https://dog.ceo/api'))
			return
		await self.bot.say(p.pickPhrase('trump', 'dog', r.json()['message']))

	@commands.command(pass_context=True)
	async def cat(self, ctx):
		''' Get a cat '''
		p = Phrasebook(ctx, self.bot)
		try:
			r = requests.get('http://thecatapi.com/api/images/get?format=xml')
		except ConnectionError:
			await self.bot.say(p.pickPhrase('web', 'timeout', 'Cat Picture', 'http://thecatapi.com'))
			return
		doc = etree.fromstring(r.text)
		source = doc.findtext('data/images/image/source_url')
		lnk = doc.findtext('data/images/image/url')
		await self.bot.say(p.pickPhrase('trump', 'cat', lnk, source))
	
def setup(bot):
	bot.add_cog(Trump(bot))
