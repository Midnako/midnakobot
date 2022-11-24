import discord
from discord.ext import commands

# -----------------------------------------------------------------------------
# abomzo?
# -----------------------------------------------------------------------------
async def abomzo(ctx):
    if ((ctx.author.id == 643913946537132033) or (ctx.author.id == 268783208705818625)):
        return True
    




###############################################################################
################################# ADMIN COG ###################################
###############################################################################

class Admin(commands.Cog):

    def __init__(self,client):
        self.client = client

# -----------------------------------------------------------------------------
# on ready admin
# -----------------------------------------------------------------------------    
    @commands.Cog.listener()
    async def on_ready(self):
        print('loaded: admin')


# -----------------------------------------------------------------------------
# load, unload & reload
# -----------------------------------------------------------------------------
    @commands.command()
    @commands.check(abomzo)
    async def load(self,ctx,extension):
        self.client.load_extension(f'cogs.{extension}')
        await ctx.send(f'Loaded {extension} commands')


    @commands.command()
    @commands.check(abomzo)
    async def unload(self,ctx,extension):
        if extension == 'admin':
            await ctx.send(f'Cannot unload {extension} commands')
        else:
            self.client.unload_extension(f'cogs.{extension}')
            await ctx.send(f'Unloaded {extension} commands')


    @commands.command()
    @commands.check(abomzo)
    async def reload(self,ctx,extension):
        if ctx.author.id == 643913946537132033:
            self.client.unload_extension(f'cogs.{extension}')
            self.client.load_extension(f'cogs.{extension}')
            await ctx.send(f'Reloaded {extension} commands')
        else:
            await ctx.send('No eres Abomzo •︿•')





def setup(client):
    client.add_cog(Admin(client))