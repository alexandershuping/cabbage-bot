import discord
import cabbagerc as rc
from discord.ext import commands
from phrasebook.Phrasebook import Phrasebook

class Admin:
	''' Administrative tasks for my own servers '''
	def __init__(self, bot):
		self.bot = bot
	
	async def on_member_join(self, member):
		server = member.server
		if server.id == rc.ADMIN_SERVER:
			role = discord.utils.get(member.server.roles, name=rc.ADD_ROLE)
			await self.bot.add_roles(member, role)
	
def setup(bot):
	bot.add_cog(Admin(bot))
