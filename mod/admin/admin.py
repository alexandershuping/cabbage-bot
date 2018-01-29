import discord
import cabbagerc as rc
from discord.ext import commands
from phrasebook.Phrasebook import Phrasebook
from util.FlagFramework import FlagFramework
from util.AdminFramework import AdminFramework

class Admin:
	''' Administrative tasks for my own servers '''
	def __init__(self, bot):
		self.bot = bot
		self.flags = FlagFramework()
	
	async def on_member_join(self, member):
		server = member.server
		if server.id == rc.ADMIN_SERVER:
			role = discord.utils.get(member.server.roles, name=rc.ADD_ROLE)
			await self.bot.add_roles(member, role)
	
	@commands.command(pass_context=True)
	async def amIAdmin(self, ctx):
		admin = AdminFramework(ctx.message.server)
		if admin.check(ctx.message.author):
			await self.bot.say("Yes")
		else:
			await self.bot.say("No")

	@commands.command(pass_context=True, timeout=10)
	async def promote(self, ctx, user):
		p = Phrasebook(ctx, self.bot)
		admin = AdminFramework(ctx.message.server)
		if not admin.check(ctx.message.author):
			await self.bot.say(p.pickPhrase('admin', 'notauthorized'))
			return

		mem = ctx.message.server.get_member_named(user)
		if not mem:
			await self.bot.say(p.pickPhrase('admin', 'notfound', user))
		else:
			await self.bot.say(p.pickPhrase('admin', 'confirmpromote', \
				mem.name, mem.discriminator, mem.id)\
			)
			msg = await self.bot.wait_for_message(author=ctx.message.author)
			if msg and 'yes' in msg.content.lower() or 'confirm' in msg.content.lower():
				admin.promote(mem)
				await self.bot.say(p.pickPhrase('admin', 'promote', mem.mention))
			else:
				await self.bot.say(p.pickPhrase('admin', 'abort'))
	
	@commands.command(pass_context=True, timeout=10)
	async def demote(self, ctx, user):
		p = Phrasebook(ctx, self.bot)
		admin = AdminFramework(ctx.message.server)
		if not admin.check(ctx.message.author):
			await self.bot.say(p.pickPhrase('admin', 'notauthorized'))
			return

		mem = ctx.message.server.get_member_named(user)
		if not mem:
			await self.bot.say(p.pickPhrase('admin', 'notfound', user))
		else:
			await self.bot.say(p.pickPhrase('admin', 'confirmdemote', \
				mem.name, mem.discriminator, mem.id)\
			)
			msg = await self.bot.wait_for_message(author=ctx.message.author)
			if msg and 'yes' in msg.content.lower() or 'confirm' in msg.content.lower():
				admin.demote(mem)
				await self.bot.say(p.pickPhrase('admin', 'demote', mem.mention))
			else:
				await self.bot.say(p.pickPhrase('admin', 'abort'))
	
	@commands.command(pass_context=True)
	async def dumpUsers(self, ctx):
		s = 'Member list:\n```'
		for member in ctx.message.server.members:
			s = s + str(member) + '(id: ' + member.id + ') '
			if member.server_permissions == discord.Permissions.all():
				s = s + '[ADMIN]'
			s = s + '\n'
		s = s + '```'

		await self.bot.say(s)
			
	
def setup(bot):
	bot.add_cog(Admin(bot))
