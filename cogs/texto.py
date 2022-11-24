# dependencies
import discord
import random
import os
from discord.ext import commands
# import warnings
import conectar


chans_def = 5
dic_insultos = {}
dic_chance ={}
dic_shhh = {}
acvdo = ["<@269679453112762378>", "acvdo", "acevedo","acvedo","asevedo","acepedo","acpedo","acpdo","acbdo","asebdo","acbedo","acebedo","asebedo","acbik"]
starter_resp = ["esa mierda nunca debio pasar señales...", "Acvdo d mrd", "esa caca infrahumana","embebidos","acvdo? >////<"]


# -----------------------------------------------------------------------------
# add_insulto
# -----------------------------------------------------------------------------
def add_insulto(guild_id,str_msg):
    conectar.cursor.execute(f"""insert into tab_insultos(id_general,insulto) values((select id from tab_general where sv_id = '{guild_id}'), (%s));""", (str_msg,))
    #conectar.cursor.execute(f"insert into contactos (nombre) values (%s)", (friend_name,))
    conectar.conexion.commit()

      
# -----------------------------------------------------------------------------
# del_insulto
# -----------------------------------------------------------------------------
def del_insulto(guild_id,ind):
    conectar.cursor.execute(f'DELETE FROM tab_insultos WHERE id = (SELECT id FROM tab_insultos LIMIT 1 OFFSET {ind}-1) and id_general = (select id from tab_general where sv_id = \'{guild_id}\');')
    conectar.conexion.commit()








###############################################################################
################################## TEXTO COG ##################################
###############################################################################

class Texto(commands.Cog):

    def __init__(self,client):
        self.client = client

# -----------------------------------------------------------------------------
# on ready texto
# -----------------------------------------------------------------------------    
    @commands.Cog.listener()
    async def on_ready(self):
        print('loaded: texto')


# -----------------------------------------------------------------------------
# ola
# -----------------------------------------------------------------------------
    @commands.command(description="q hago aqui?", brief="q hago aqui?")
    async def ola(self,ctx):
        guild_id = ctx.guild.id
        # update tab_general set f2 = 40000 where (sv_id = {guild_id}::text)
        #if (dic_shhh.get(guild_id,True)):
        conectar.cursor.execute(f"select * from tab_general where sv_id = '{guild_id}';")
        if (conectar.cursor.fetchone()[7]):
            await ctx.send("ola, estoy aki para insultar a acvdo cuando abomzo no este")


# -----------------------------------------------------------------------------
# kyc
# -----------------------------------------------------------------------------
    @commands.command(description="deshabilita respuestas para acvdo",brief="deshabilita respuestas para acvdo")
    async def kyc(self,ctx):
        guild_id = ctx.guild.id
        #dic_shhh[guild_id] = False
        conectar.cursor.execute(f'update tab_general set habla = false where (sv_id = {guild_id}::text)')
        conectar.conexion.commit()
        await ctx.send("oki :(")


# -----------------------------------------------------------------------------
# habla
# -----------------------------------------------------------------------------
    @commands.command(description="habilita respuestas para acvdo", brief="habilita respuestas para acvdo")
    async def habla(self,ctx):
        guild_id = ctx.guild.id
        # dic_shhh[guild_id] = True
        conectar.cursor.execute(f'update tab_general set habla = true where sv_id = {guild_id}::text')
        conectar.conexion.commit()
        await ctx.send("volví")
        # await client.change_presence(status=discord.Status.online)


# -----------------------------------------------------------------------------
# chance 0-10
# -----------------------------------------------------------------------------
    @commands.command(description="(1-10) cambia la chance d responder", brief = "(1-10) cambia la chance d responder")
    async def chance(self,ctx,*,chance):
        guild_id = ctx.guild.id
        if int(chance)>10:
            chans = 10
        elif int(chance)<0:
            chans = 0
        else:
            chans = int(chance)
        conectar.cursor.execute(f'update tab_general set chance = {chans} where (sv_id = {guild_id}::text)')
        conectar.conexion.commit()
        await ctx.send("Chance en " + str(chans))


# -----------------------------------------------------------------------------
# nuevo
# -----------------------------------------------------------------------------
    @commands.command(description="agrega una nueva respuesta posible", brief="agrega una nueva respuesta posible")
    async def nuevo(self,ctx,*,message):
        guild_id = ctx.guild.id
        add_insulto(guild_id,message)
        await ctx.send("lo tomaré en cuenta...")


# -----------------------------------------------------------------------------
# lista
# -----------------------------------------------------------------------------
    @commands.command(description="muestra la lista de respuestas agregadas", brief="muestra la lista de respuestas agregadas")
    async def lista(self,ctx):

        guild_id = ctx.guild.id

        conectar.cursor.execute(f"select insulto from tab_insultos join tab_general on id_general = tab_general.id where tab_general.sv_id = '{guild_id}';")
        tuplas_sv = conectar.cursor.fetchall()

        if len(tuplas_sv) == 0:
            await ctx.send("no hay nada :c, **n@k nuevo msg** para agregar")
        lista_bonita = "```md\n"
        for indice, mensaje in enumerate(tuplas_sv, 1):
            lista_bonita += f"{indice}. {mensaje[0]}\n"
        lista_bonita += "```"
        await ctx.send("**n@k olvida indice** para eliminar")
        await ctx.send(lista_bonita)


# -----------------------------------------------------------------------------
# olvida
# -----------------------------------------------------------------------------
    @commands.command(description="olvida alguna de las respuestas", brief="olvida alguna de las respuestas")
    async def olvida(self,ctx,*,index):
        guild_id=ctx.guild.id
        ind = index
        del_insulto(guild_id,ind)
        await ctx.send("...")


# -----------------------------------------------------------------------------
# msg event
# -----------------------------------------------------------------------------
    @commands.Cog.listener()
    async def on_message(self,message):

        guild_id = message.author.guild.id
        conectar.cursor.execute(f"select habla from tab_general where sv_id = '{guild_id}';")
        if (conectar.cursor.fetchone()[0]):   
            if message.author == self.client.user:
                return
            
            if (message.author.id in [643913946537132033,268783208705818625]) and any(word in message.content for word in ['<@371868954936737805>']):
                await message.channel.send('c piki')
            
            if any(word in (message.content).lower() for word in acvdo):
                a = random.randint(1,10)
                print(a)
                conectar.cursor.execute(f"select chance from tab_general where sv_id = '{guild_id}';")
                if (a<= conectar.cursor.fetchone()[0]):
                    conectar.cursor.execute(f"select insulto from tab_insultos join tab_general on id_general = tab_general.id where tab_general.sv_id = '{guild_id}';")
                    tuplas_sv = conectar.cursor.fetchall()
                    lista_sv = [tupla[0] for tupla in tuplas_sv]
                    await message.channel.send(random.choice(starter_resp+lista_sv))




def setup(client):
    client.add_cog(Texto(client))