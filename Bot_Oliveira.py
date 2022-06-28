from datetime import datetime
import requests
import discord
from discord.ext import commands, tasks

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

#Diz "Olá" e cita o usuario que usar o comando: !ajuda
@bot.command(name="ajuda")
async def send_hello(ctx):
    name = ctx.author.name
    
    response = f"Ola, {name} no que posso te ajudar!?"
    
    await ctx.send(response)
    
#a calculadora é usada com o comando: !calc
@bot.command(name="calc")
async def calculate_expression(ctx, *expression):
    expression = "".join(expression)
    response = eval(expression)
    
    
    await ctx.send("A resposta é: " + str(response))

#Calcula cripto moedas usando a API da biance com o comando: !binance   
@bot.command()
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
        
#Envia mensagem no privado do usuario que usar o comando: !segredo        
@bot.command(name="segredo")
async def secret(ctx):
    try:
        await ctx.author.send("Curta o canal da ByLearn!")
        
    #Caso ele não tenha habilitado o bot dara as instruções para que o usuario possa receber a mensagem
    except discord.errors.Forbidden:
        await ctx.send("Desculpe,não posso te contar um segredo,habilite Permitir mensagens diretas de membros do servidor (Opções > Privacidade e Segurança) ")

#Mostra O Dia/Mês/Ano e o Horario no chat Geral
@tasks.loop(hours=24)
async def current_time():
    now = datetime.now()   
    
    now = now. strftime("%d/%m/%Y ás %H:%M:%S")
    
    channel = bot.get_channel(976487221374881894)
    
    await channel.send("Data atual: " + now)
    
   

bot.run("OTkxMTM1MDEzMTkyMDc3Mzky.GWnrQN.ktbmsGmiI6a5GKBAz0IKrhjsp9kHyoIqz16rEE")