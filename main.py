# dependencies
import discord
# import random
#import requests
#import json
import os
# import librosa
# import soundfile as sf
# from gtts import gTTS
# from discord import FFmpegPCMAudio
from discord.ext import commands, tasks
# import warnings
import asyncio
# import ejemplodb as pija
import conectar







TOKEN = os.environ['DJS_TOKEN']


intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = ['<@967136791310270555> ', 'n@k '], intents = intents, case_insensitive = True)



# -----------------------------------------------------------------------------
# load cogs
# -----------------------------------------------------------------------------
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}') # cuts last 3 characters











###############################################################################
################################## EVENTOS ####################################
###############################################################################

# -----------------------------------------------------------------------------
# rdy
# -----------------------------------------------------------------------------
@client.event
async def on_ready():
    print('Logged in as {0.user} :D'.format(client))


# -----------------------------------------------------------------------------
# on guild join
# -----------------------------------------------------------------------------
@client.event
async def on_guild_join(guild):
    guild_id = guild.id
    print(type(guild_id))
    conectar.cursor.execute(f"insert into tab_general (sv_id) values ({guild_id})")
    conectar.conexion.commit()


# -----------------------------------------------------------------------------
# msg event
# -----------------------------------------------------------------------------
@client.event
async def on_message(message):
    await client.process_commands(message)


# -----------------------------------------------------------------------------
# Exit if alone
# -----------------------------------------------------------------------------
GUILD_VC_TIMER = {}
# this event runs when user leave / join / defen / mute 
@client.event
async def on_voice_state_update(member, before, after):
    # if event is triggered by the bot? return
    if member.id == client.user.id:
        return

    if before.channel != None:
        voice = discord.utils.get(client.voice_clients , channel__guild__id = before.channel.guild.id)

        if voice == None:
            return

        if voice.channel.id != before.channel.id:
            return

        if len(voice.channel.members) <= 1:
            GUILD_VC_TIMER[before.channel.guild.id] = 0
            while True:
                print("At", str(before.channel.guild) ,": Time" , str(GUILD_VC_TIMER[before.channel.guild.id]) , "Total Members" , str(len(voice.channel.members)))
                await asyncio.sleep(10)
                GUILD_VC_TIMER[before.channel.guild.id] += 10
                if len(voice.channel.members) >= 2 or not voice.is_connected():
                    break
                if GUILD_VC_TIMER[before.channel.guild.id] >= 60:
                    await voice.disconnect()
                    print("At", str(before.channel.guild) ,": Time 60 Disconnected from VC")
                    return





try:
    client.run(TOKEN)
finally:
    conectar.cursor.close()
    conectar.conexion.close()























