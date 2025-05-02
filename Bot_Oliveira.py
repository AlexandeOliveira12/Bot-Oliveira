from datetime import datetime
from turtle import title
import certifi

import requests
import discord
from decouple import config

from discord.ext import commands, tasks
from discord.ext.commands.errors import MissingRequiredArgument, CommandNotFound 
from keep_alive import keep_alive

keep_alive()

intents = discord.Intents.default()
intents.message_content = True  # Necessário para ler mensagens

bot = commands.Bot(command_prefix="!", intents=intents)

#Displays in the Terminal that the Bot is Online
@bot.event
async def on_ready():
    print(f"Estou pronto! Estou conectado como {bot.user}")
    current_time.start() 

#Warns and deletes messages that contain the following words: "Palavrão"
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if "palavrão" in message.content:
        await message.channel.send(f"Por favor, {message.author.name}, não ofenda os demais úsuarios!")
        
        await message.delete()
        
    await bot.process_commands(message) 
    
#Bot charges from the reaction the user puts on the message
@bot.event
async def on_reaction_add(reaction, user): 
    if reaction.emoji == "✅":
        role = user.guild.get_role(1354546382471561249)
        await user.add_roles(role)
    elif reaction.emoji == "👨‍💻":
        role = user.guild.get_role(976504255944994946)
        await user.add_roles(role)

#Warning if the user writes a wrong command              
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Por favor, escreva o comando corretamente, digite !help para ver os comandos e suas funcionalidades!")
    elif isinstance(error, CommandNotFound): 
        await ctx.send("Por favor, escreva o comando corretamente, digite !help para ver os comandos e suas funcionalidades!")    
    else:
        raise error    


#!ajudaMusic
@bot.command(name="ajudaMusic", help=" Ajuda o usuario a achar os canais de musica (Não requer argumentos)")
async def send_hello(ctx):
    user_id = ctx.author.id
    canal = bot.get_channel(1196590744002109482)

    response = f"Ola, <@{user_id}> quer colocar uma musica? você pode coloca-la no canal {canal.mention}"
    
    await ctx.send(response)
    
#!calc
@bot.command(name="calc", help="Calcula uma expressão.Argumentos:Expressão")
async def calculate_expression(ctx, *expression):
    expression = "".join(expression)
    response = eval(expression)
    
    await ctx.send("A resposta é: " + str(response))

#Cota diferentes preços de Moedas
@bot.command(name="preco", help="Consulta o valor de uma moeda em relação a outra. Ex: !preco BTC BRL")
async def cotar_moeda(ctx, moeda: str, base: str):
    try:
        simbolo = f"{moeda.upper()}{base.upper()}"
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={simbolo}"
        response = requests.get(url)
        data = response.json()
        
        if "price" in data:
            preco = float(data["price"])
            
            embed = discord.Embed(
                title=f"💰 Cotação: {moeda.upper()}/{base.upper()}",
                description=f"O preço atual é **{preco:,.2f} {base.upper()}**",
                color=0x00FF00
            )
            embed.set_footer(text="Fonte: Binance", icon_url="https://cryptologos.cc/logos/binance-coin-bnb-logo.png")
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Par **{moeda}/{base}** não encontrado na Binance.")
    except Exception as e:
        await ctx.send("⚠️ Ocorreu um erro ao buscar o preço.")
        print(e)

# Envia uma foto aleatória no chat com dimensão de 1920x1080 usando o comando: !foto
@bot.command(name="foto", help="Envia uma foto aleatória no chat (Não requer argumentos)")
async def get_random_image(ctx):
    url_image = "https://picsum.photos/1920/1080"
    
    embed = discord.Embed(
        title = "Resultado da busca de imagem",
        description = "Ps: A busca será totalmente aleátoria",
        color = 0x0000FF,
    )

    largura = "1920"
    altura = "1080"

    embed.set_author(name=bot.user.name, icon_url=bot.user.display_avatar.url)
    
    embed.set_footer(text="Feito por " + bot.user.name, icon_url=bot.user.display_avatar.url)
    
    embed.add_field(name="API", value="API utilizada: https://picsum.photos/")
    embed.add_field(name="Parâmetros", value=f"{largura} x {altura}")
    
    embed.set_image(url=url_image)
    
    await ctx.send(embed=embed)

@tasks.loop(hours=24)
async def current_time():
    now = datetime.now()   
    
    now = now. strftime("%d/%m/%Y ás %H:%M:%S")
    
    channel = bot.get_channel(1367650512492695572)
    
    await channel.send(f"**Bot Oliveira bateu seu ponto: {now}**")
    
#Token for bot activation
TOKEN = config("TOKEN")   
bot.run(TOKEN)

