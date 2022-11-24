# dependencies
import discord
import librosa
import soundfile as sf
from gtts import gTTS
from discord import FFmpegPCMAudio
from discord.ext import commands
# import asyncio
import warnings
import conectar

freq_en = [24000,32500]
freq_es = [24000,34000]
lang_def = 'es'
tldd_def = 'com'

dic_voz = {}


# -----------------------------------------------------------------------------
# conv_tts
# -----------------------------------------------------------------------------
def conv_tts(message,guild_id):

    #conectar.cursor.execute(f"select lang,tld,f1,f2 from tab_general where sv_id = '{guild_id}';")
    #lang, tld,f1,f2 = conectar.cursor.fetchone()
    lang, tld,f1,f2 = dic_voz[guild_id]
    tts = gTTS(text=message, lang=lang, tld=tld, slow=False)
    tts.save("tts-{}.wav".format(guild_id))
    warnings.simplefilter("ignore", UserWarning)
    warnings.simplefilter("ignore", FutureWarning)
    y,sr = librosa.load("tts-{}.wav".format(guild_id), f1)
    sf.write("tts-{}.wav".format(guild_id), y, f2)


# -----------------------------------------------------------------------------
# tts_abreviado
# -----------------------------------------------------------------------------
async def tts_abreviado(self,message):
    if message.content.startswith("° "):

        if (message.author.voice):
            guild_id = message.channel.guild.id
            str_msg = message.content.split("° ",1)[1]
            try:
                channel =  message.author.voice.channel
                voice = await channel.connect()
                conv_tts(str_msg,str(guild_id))
                source = discord.FFmpegPCMAudio("tts-{}.wav".format(guild_id), before_options='-v 16')
                player = voice.play(source)
            except:
                guild = message.author.guild
                voice = discord.utils.get(self.client.voice_clients,guild=guild)
                if not voice.is_playing():
                    conv_tts(str_msg,str(guild_id))
                    source = discord.FFmpegPCMAudio("tts-{}.wav".format(guild_id), before_options='-v 16')
                    player = voice.play(source)                        
        else:
            await message.channel.send("donde? -.-")










###############################################################################
################################## VOZ COG ####################################
###############################################################################

class Voz(commands.Cog):

    def __init__(self,client):
        self.client = client

# -----------------------------------------------------------------------------
# on ready voz
# -----------------------------------------------------------------------------    
    @commands.Cog.listener()
    async def on_ready(self):
        print('loaded: voz')

        conectar.cursor.execute(f"select sv_id from tab_general;")
        guild_list = conectar.cursor.fetchall()
        for guild_id in guild_list:
            conectar.cursor.execute(f"select lang,tld,f1,f2 from tab_general where sv_id = '{guild_id[0]}';")
            dic_voz[guild_id[0]] = conectar.cursor.fetchone()




# -----------------------------------------------------------------------------
# lang (en,es)
# -----------------------------------------------------------------------------
    @commands.group(invoke_without_command=True, description="n@k lang (es/en), cambia el lenguaje de TTS", brief="cambia el lenguaje de TTS")
    async def lang(self,ctx):
        await ctx.send("Usa **n@k lang (es/en)** para cambiar entre TTS en español(es) y en inglés(en)")

    @lang.command(brief="TTS en inglés")
    async def en(self,ctx):
        await ctx.send("xd")
        guild_id = ctx.guild.id
        #dic_lang[ctx.guild.id] = ['en','com'] # ['en','co.in] #
        #dic_freq[ctx.guild.id] = freq_en
        conectar.cursor.execute(f'update tab_general set lang=\'en\',tld=\'com\',f1=24000,f2=32500 where (sv_id = {guild_id}::text)')
        conectar.conexion.commit()
        dic_voz[str(guild_id)] = ('en','com',24000,32500)


    @lang.command(brief="TTS en español")
    async def es(self,ctx):
        guild_id = ctx.guild.id
        await ctx.send("si iron man fuera ramirez")
        #dic_lang[ctx.guild.id] = ['es','com']
        #dic_freq[ctx.guild.id] = freq_es
        conectar.cursor.execute(f'update tab_general set lang=\'es\',tld=\'com\',f1=24000,f2=34000 where (sv_id = {guild_id}::text)')
        conectar.conexion.commit()
        dic_voz[str(guild_id)] = ('es','com',24000,34000)

# -----------------------------------------------------------------------------
# ven
# -----------------------------------------------------------------------------
    @commands.command(pass_context = True, description="hace q el bot se conecte al vc", brief="hace q el bot se conecte al vc")
    async def ven(self,ctx):
        guild_id = ctx.guild.id
        if (ctx.author.voice):
            channel =  ctx.message.author.voice.channel
            voice = await channel.connect()
            conv_tts("aló imbéciles",str(guild_id))
            source = discord.FFmpegPCMAudio("tts-{}.wav".format(guild_id), before_options='-v 16')
            player = voice.play(source)
        else:
            await ctx.send("donde? -.-")


# -----------------------------------------------------------------------------
# tts
# -----------------------------------------------------------------------------
    @commands.command(description="dice algo",brief="dice algo")
    async def tts(self,ctx,*,message):

        if (ctx.author.voice):
            guild_id = ctx.guild.id
            try:
                channel =  ctx.author.voice.channel
                voice = await channel.connect()
                conv_tts(message,str(guild_id))
                source = discord.FFmpegPCMAudio("tts-{}.wav".format(guild_id), before_options='-v 16')
                player = voice.play(source)
            except:
                voice = discord.utils.get(self.client.voice_clients,guild=ctx.guild)
                if not voice.is_playing():
                    conv_tts(message,str(guild_id))
                    source = discord.FFmpegPCMAudio("tts-{}.wav".format(guild_id), before_options='-v 16')
                    player = voice.play(source)

        else:
            await ctx.send("donde? -.-")


# -----------------------------------------------------------------------------
# tts abreviado
# -----------------------------------------------------------------------------  
    @commands.Cog.listener()
    async def on_message(self,message):
        await tts_abreviado(self,message)



# -----------------------------------------------------------------------------
# sh
# -----------------------------------------------------------------------------
    @commands.command(pass_context = True, description="se detiene si estaba diciendo algo", brief="se detiene si estaba diciendo algo")
    async def sh(self,ctx):
        voice = discord.utils.get(self.client.voice_clients,guild=ctx.guild)
        if voice.is_playing():
            voice.stop()
            await ctx.reply(':(')
        else:
            await ctx.reply("no estaba diciendo nada D:")


# -----------------------------------------------------------------------------
# shu
# -----------------------------------------------------------------------------
    @commands.command(pass_context = True, description="hace q el bot se vaya del vc", brief="hace q el bot se vaya del vc")
    async def shu(self,ctx):
        if (ctx.voice_client):
            await ctx.guild.voice_client.disconnect()
            await ctx.reply("D:")
        else:
            await ctx.reply("no jodas >_<")



def setup(client):
    client.add_cog(Voz(client))