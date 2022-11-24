# dependencies
import discord
import os
from discord.ext import commands, tasks
import warnings
import asyncio
import pandas as pd
import datetime
import conectar

# horario_activado = False
siguiente = {}
horario_corriendo = {}
all_classes ={}

def conv_dia_str(num):
    switcher = {0:'lunes',1:'martes',2:'miercoles',3:'jueves',4:'viernes',5:'sabado',6:'domingo'}
    return switcher[num]

def conv_mes_str(num):
    switcher = {1: "enero",2: "febrero",3: "marzo",4: "abril",5: "mayo",6: "junio",7: "julio",8: "agosto",9: "septiembre",10: "octubre",11: "noviembre",12: "diciembre"}
    return switcher[num]

def conv_fecha(mes,dia):
    if len(mes) == 1:
        mes = f'0{mes}'
    if len(dia) == 1:
        dia = f'0{dia}'
    return f'{dia}/{mes}'

def conv_tiempo(seconds):
    m,s = divmod(round(seconds),60)
    h,m = divmod(m,60)
    if h==0:
        h = ''
    else:
        h = f'{h}h '
    if m==0:
        m = ''
    else:
        m = f"{m}'"
    return (f"{h}{m}")


# -----------------------------------------------------------------------------
# get array of all classes
# -----------------------------------------------------------------------------
def get_all_classes(classes: pd.DataFrame, user_id: str):
    if len(all_classes.get(user_id,[])) != 0:
        return
    else:
        all_classes[user_id] = []
        for _, initial, interval, name, link, end in classes.to_records():
            initial_dt = datetime.datetime.utcfromtimestamp(initial.tolist() / 1e9)
            initial_dt -= datetime.timedelta(minutes=5)
            end_dt = datetime.datetime.utcfromtimestamp(end.tolist() / 1e9)
            interval_int = float(interval)
            while initial_dt < end_dt:
                all_classes[user_id].append((initial_dt, interval_int, name, link))
                initial_dt += datetime.timedelta(days=interval_int)
        all_classes[user_id].sort(key=lambda x: x[0])
        return


# -----------------------------------------------------------------------------
# schedule only immediate next reminder per user
# -----------------------------------------------------------------------------
async def por_favor_funciona(self, user_id):
    classes = pd.read_excel(f'horario-{user_id}.xlsx')
    get_all_classes(classes,user_id)
    now = datetime.datetime.utcnow() - datetime.timedelta(hours=5)

    for time, _, name, link in all_classes[user_id]:
        if time < now: 
            continue
        seconds = (time - now).total_seconds()
        siguiente[user_id] = (time, name, link)
        print(f" - @{user_id}: sgte recordatorio en {seconds}")
        break
    
    conectar.cursor.execute(f"select channel_id from tab_recordatorios where user_id = '{user_id}';")
    lista_canales = conectar.cursor.fetchall()

    for channel_id in lista_canales:
        await self.client.get_channel(int(channel_id[0])).send(f'<@{user_id}> sgte recordatorio en {conv_tiempo(seconds)}')

    await asyncio.sleep(seconds)

    # Actualizar lista canales tras esperar
    conectar.cursor.execute(f"select channel_id from tab_recordatorios where user_id = '{user_id}';")
    lista_canales = conectar.cursor.fetchall()

    if len(lista_canales) != 0:
        for channel_id in lista_canales:
            print(f" - @{user_id}: se envió un recordatorio en {channel_id[0]}")
            await self.client.get_channel(int(channel_id[0])).send(f'<@{user_id}> tienes **{name}** en 5\', {link}')
    else:
        print(f" - @{user_id}: se cumplió el tiempo pero no habían canales con recordatorios activados")
        return
    




# -----------------------------------------------------------------------------
# task recordatorios por usuario en varios canales
# -----------------------------------------------------------------------------
async def task_recordatorio(self, user_id):
    print(f' - @{user_id}: se lanzó task de recordatorios')
    # asignar activado valor inicial
    conectar.cursor.execute(f"select channel_id from tab_recordatorios where user_id = '{user_id}';")
    lista_canales = conectar.cursor.fetchall()

    if len(lista_canales) != 0:
        while len(lista_canales) != 0:
            if horario_corriendo.get(user_id,False):
                print(f' - @{user_id}: timer de recordatorio ya está corriendo')
                break
            else:    
                horario_corriendo[user_id] = True
                print(f' - @{user_id}: timer de recordatorio está corriendo')
                await por_favor_funciona(self,user_id)
                horario_corriendo[user_id] = False       
                print(f' - @{user_id}: timer de recordatorio ya no esta corriendo')
            
            await asyncio.sleep(1)
            # actualizar activado para siguiente iteracion del while
            conectar.cursor.execute(f"select channel_id from tab_recordatorios where user_id = '{user_id}';")
            lista_canales = conectar.cursor.fetchall()
            
    if len(lista_canales) == 0:
        print(f" - @{user_id}: no hay canales con recordatorios activados")
















class Horario(commands.Cog):

    def __init__(self,client):
        self.client = client
# -----------------------------------------------------------------------------
# on ready horario
# -----------------------------------------------------------------------------    
    @commands.Cog.listener()
    async def on_ready(self):
        print('loaded: horario')
        await asyncio.sleep(1)
        conectar.cursor.execute(f"select distinct user_id from tab_recordatorios;")
        userids = conectar.cursor.fetchall()
        await asyncio.gather(*(task_recordatorio(self,user_id[0]) for user_id in userids))
        # await task_recordatorio(self)

        print(' - ya salí de task_recordatorio')





# -----------------------------------------------------------------------------
# horario
# -----------------------------------------------------------------------------
    @commands.command()
    async def horario(self,ctx):
        if (ctx.author.id == 268783208705818625)or(ctx.author.id == 643913946537132033):
            await ctx.send('https://cdn.discordapp.com/attachments/701638301383393331/961702402107510865/af145180-d3a4-4412-b003-e62e9807017d.png')
        else:
            await ctx.send("no eres abomzo")


# -----------------------------------------------------------------------------
# qtoca
# -----------------------------------------------------------------------------
    @commands.command()
    async def qtoca(self,ctx):
        user_id = str(ctx.author.id)
        try:
            classes = pd.read_excel(f'horario-{user_id}.xlsx')
        except:
            await ctx.reply(f'no conozco tu horario >.<')
            print(f' - @{user_id}: no se encontró archivo de horario')
            return
        sig = siguiente[str(ctx.author.id)][0] + datetime.timedelta(minutes=5)
        name = siguiente[str(ctx.author.id)][1]
        dia_sem = sig.weekday()
        fecha = conv_fecha(str(sig.month), str(sig.day))
        hora = sig.strftime("%H:%M")
        ahora = datetime.datetime.utcnow() - datetime.timedelta(hours=5)
        delta = (sig - ahora).total_seconds()
        await ctx.reply(f"Tienes **{name}** en **{conv_tiempo(delta)}** el {conv_dia_str(dia_sem)} {fecha} a las {hora}")
        print(f' - @{user_id}: se informó del siguiente recordatorio')


# -----------------------------------------------------------------------------
# recordatorios
# -----------------------------------------------------------------------------
    @commands.group(invoke_without_command=True, brief="Grupo de comandos para recordatorios (solo funciona si tienes un archivo)")
    async def recs(self,ctx):
        await ctx.send("Usa **n@k recs (activa/desactiva/canales)**")
        return

    @recs.command(brief="Activar recordatorios en canal")
    async def activa(self,ctx):
        channel_id = str(ctx.channel.id)
        user_id = str(ctx.author.id)
        try:
            classes = pd.read_excel(f'horario-{user_id}.xlsx')
        except:
            await ctx.reply(f'no conozco tu horario >.<')
            print(f' - @{user_id}: no se encontró archivo de horario')
            return
        conectar.cursor.execute(f"select channel_id from tab_recordatorios where (user_id = '{user_id}' and channel_id = '{channel_id}');")
        result = conectar.cursor.fetchone()
        if result != None:
            await ctx.reply(f'ya te estaba avisando por acá -.-')
        else:
            conectar.cursor.execute(f"insert into tab_recordatorios (user_id,channel_id) values ('{user_id}','{channel_id}')")
            conectar.conexion.commit() 
            await ctx.reply(f'ok, te enviaré recordatorios en este canal :thumbsup:')
            print(f' - <@{user_id}>: se activaron recordatorios en {channel_id}')
            await task_recordatorio(self,str(user_id))
        return

    @recs.command(brief="Desactivar recordatorios en canal")
    async def desactiva(self,ctx):
        channel_id = str(ctx.channel.id)
        user_id = str(ctx.author.id)
        conectar.cursor.execute(f"delete from tab_recordatorios where (user_id = '{user_id}' and channel_id = '{channel_id}');")
        conectar.conexion.commit()
        await ctx.reply(f'ya no te enviaré recordatorios en este canal :white_check_mark:')
        print(f' - <@{user_id}>: se desactivaron recordatorios en {channel_id}')
        return

    @recs.command(brief="muestra los canales en los q tienes recordatorios")
    async def canales(self,ctx):
        await ctx.reply("en progreso...")
        return
    






def setup(client):
    client.add_cog(Horario(client))