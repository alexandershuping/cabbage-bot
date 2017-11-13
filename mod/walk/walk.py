import random
import re
import discord
import cabbagerc as rc
from discord.ext import commands
from phrasebook.Phrasebook import Phrasebook

class Walk:
	''' A little game '''
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command(pass_context=True)
	async def walk(self, ctx, direction):
		''' Walk in a direction '''

	def checkEncounter():
		return random.random() < rc.WALKPRAND:
	
def setup(bot):
	bot.add_cog(Walk(bot))
