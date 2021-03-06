from datetime import datetime
from turtle import title

import requests
import discord
from decouple import config

from discord.ext import commands, tasks
from discord.ext.commands.errors import MissingRequiredArgument, CommandNotFound 


bot = commands.Bot("!")

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
        role = user.guild.get_role(976506535167524874)
        await user.add_roles(role)
    elif reaction.emoji == "👨‍💻":
        role = user.guild.get_role(976504255944994946)
        await user.add_roles(role)

#Warning if the user writes a wrong command              
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Por favor,escreva o comando corretamente,digite !help para ver os comandos e suas funcionalidades!")
    elif isinstance(error, CommandNotFound): 
        await ctx.send("Por favor,escreva o comando corretamente,digite !help para ver os comandos e suas funcionalidades!")    
    else:
        raise error    


#Say "Hello" and quote the user who uses the command: !help
@bot.command(name="ajuda", help="Ajuda o usuario a achar as informações sobre o servidor (Não requer argumentos)")
async def send_hello(ctx):
    name = ctx.author.name
    
    response = f"Ola, {name} esta perdido?você podera encontrar mais informações sobre o servidor no chat #❗丨informações!"
    
    await ctx.send(response)
    
#The calculator is used with the command: !calc
@bot.command(name="calc", help="Calcula uma expressão.Argumentos:Expressão")
async def calculate_expression(ctx, *expression):
    expression = "".join(expression)
    response = eval(expression)
    
    await ctx.send("A resposta é: " + str(response))

#Calculate cryptocurrencies using biance API with command: !binance  
@bot.command(help="Verifica o valor  de um par na Binance. Argumentos:Moeda, Base")
async def binance(ctx, coin, base):
    try:
        response = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={coin.upper()}{base.upper()}")
        
        data = response.json()
        price = data.get("price")
        
        if price:
            await ctx.send(f"O valor do par {coin}/{base} é {price}")
        else:
            await ctx.send(f"O par {coin}/{base} é inválido")

    #If the link is wrong or has a problem, it will display the following message:
    except Exception as error:
        await ctx.send("Ops...Deu algum erro")
        print(error)
        
#Send a private message to the user who uses the command: !segredo        
@bot.command(name="segredo", help="envia uma foto no privado (Não requer argumentos)")
async def secret(ctx):
    try:
        await ctx.author.send("Fico feliz que chegou até aqui!se não se importar ajude o criador deste bot seguindo-o no instagram @xande.code")
        
    #If he has not enabled the bot, he will give instructions so that the user can receive the message
    except discord.errors.Forbidden:
        await ctx.send("Desculpe,não posso te contar um segredo,habilite Permitir mensagens diretas de membros do servidor (Opções > Privacidade e Segurança) ")

#Send a random photo using the lorem picsum API using the command: !foto
@bot.command(name="foto", help="Envia uma foto aleatória no chat (Não requer argumentos)")
async def get_random_image(ctx):
    url_image = "https://picsum.photos/1920/1080"
    
    embed = discord.Embed(
        title = "Resultado da busca de imagem",
        description = "Ps:A busca a totalmente aleátoria",
        color = 0x0000FF,
    )

    embed.set_author(name=bot.user.name, icon_url=bot.user.avatar_url)
    
    embed.set_footer(text="Feito por " + bot.user.name, icon_url=bot.user.avatar_url)
    
    embed.add_field(name="API", value="Usamos a API do https://picsum.photos/")
    embed.add_field(name="parâmetros", value="{Largura}/{altura}")
    
    embed.add_field(name="exemplo", value=url_image, inline=False)
    
    embed.set_image(url=url_image)
    
    await ctx.send(embed=embed)
  
#Shows Day/Month/Year and Time in General chat
@tasks.loop(hours=24)
async def current_time():
    now = datetime.now()   
    
    now = now. strftime("%d/%m/%Y ás %H:%M:%S")
    
    channel = bot.get_channel(976487221374881894)
    
    await channel.send("Data atual: " + now)
    
#Token for bot activation
TOKEN = config("TOKEN")   
bot.run(TOKEN)

