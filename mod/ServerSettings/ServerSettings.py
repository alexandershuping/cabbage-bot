import discord
import cabbagerc as rc
from discord.ext import commands
from phrasebook.Phrasebook import Phrasebook
from sql.cabbagebase import CabbageBase

class ServerSettings:
	''' Management of server settings '''
	def __init__(self, bot):
		self.bot = bot
	
	@commands.command(pass_context=True)
	async def set(self, ctx, state=None):
		
	
def setup(bot):
	bot.add_cog(Admin(bot))
