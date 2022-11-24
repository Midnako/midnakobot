import discord
from discord.ext import commands



###############################################################################
################################# PING COG ###################################
###############################################################################

class Ping(commands.Cog):

    def __init__(self,client):
        self.client = client

# -----------------------------------------------------------------------------
# on ready ping
# -----------------------------------------------------------------------------    
    @commands.Cog.listener()
    async def on_ready(self):
        print('loaded: ping')
    

# -----------------------------------------------------------------------------
# ping
# -----------------------------------------------------------------------------
    @commands.command()
    async def ping(self,ctx):
        await ctx.send("pong")


def setup(client):
    client.add_cog(Ping(client))
