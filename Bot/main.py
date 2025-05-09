from datetime import datetime
import re

from decouple import config
import requests

import discord
from discord.ext import commands
from discord.ext import commands, tasks
from discord.ext.commands.errors import MissingRequiredArgument, CommandNotFound 

import yt_dlp


intents = discord.Intents.default()
intents.message_content = True  # Necessário para ler mensagens

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

palavras_regex = re.compile(r"\b(merda|porra|caralho|bct|prr|krlh|puta|puto|fdp|filho da puta|desgraçado|bosta|vagabundo|vagabunda|arrombado|cuzão|cuzinha|buceta|babaca|otário|otaria|escroto|escrota|viado|veado|boiola|piranha|cacete|rola|pau no cu|pau|corno|corna|retardado|mongol|jumento|anta|imbecil|idiota|burro|burra)\b", re.IGNORECASE)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if palavras_regex.search(message.content):
        await message.channel.send(f"{message.author.mention}, evite linguagem ofensiva.")
        await message.delete()

    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f"Estou pronto! Estou conectado como {bot.user}")
    
    canal = bot.get_channel(1367650512492695572)
    if canal:
        embed = discord.Embed(
            title="🤖 Bot Oliveira Online!",
            description="O bot foi iniciado com sucesso e está pronto para uso!",
            color=0x00ff00  # Verde
        )
        embed.set_thumbnail(url=bot.user.display_avatar.url)
        embed.set_footer(text="Status atualizado automaticamente.")
        await canal.send(embed=embed)

    current_time.start()

@bot.event
async def on_reaction_add(reaction, user): 
    if reaction.emoji == "✅":
        role = user.guild.get_role(1354546382471561249)
        await user.add_roles(role)
    elif reaction.emoji == "👨‍💻":
        role = user.guild.get_role(976504255944994946)
        await user.add_roles(role)
             
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Por favor, escreva o comando corretamente, digite !help para ver os comandos e suas funcionalidades!")
    elif isinstance(error, CommandNotFound): 
        await ctx.send("Por favor, escreva o comando corretamente, digite !help para ver os comandos e suas funcionalidades!")    
    else:
        raise error   

@bot.command(help="Testa se o bot está online")
async def ping(ctx):
    await ctx.send("🏓 Pong!") 

@bot.command(name="help", help="Mostra todos os comandos disponíveis")
async def custom_help(ctx):
    embed = discord.Embed(title="📘 Lista de Comandos", color=0x00ff00)
    for command in bot.commands:
        embed.add_field(name=f"!{command.name}", value=command.help, inline=False)
    await ctx.send(embed=embed)

#!ajudaMusic
@bot.command(name="ajudaMusic", help=" Ajuda o usuario a achar os canais de musica")
async def send_hello(ctx):
    user_id = ctx.author.id
    canal = bot.get_channel(1196590744002109482)

    response = f"Ola, <@{user_id}> quer colocar uma musica? você pode coloca-la no canal {canal.mention}"
    
    await ctx.send(response)
    
@bot.command(name="TimePlayed", help="Exibe os principais jogos da sua biblioteca por TEMPO JOGADO")
async def calculate_timeplayed(ctx, STEAM_ID: str):
    try:
        API_KEY = config("API_KEY")

        url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
        params = {
            "key": API_KEY,
            "steamid": STEAM_ID,
            "include_appinfo": True,
            "include_played_free_games": True
        }

        response = requests.get(url, params=params)
        data = response.json()

        # Verifica se há jogos
        if "response" in data and "games" in data["response"]:
            jogos = data["response"]["games"]

            # Converte minutos para horas e organiza em lista
            ranking = [
                {
                    "nome": jogo["name"],
                    "horas": round(jogo["playtime_forever"] / 60, 2)
                }
                for jogo in jogos
                if jogo["playtime_forever"] > 0
            ]

            # Ordena do maior para o menor tempo
            ranking.sort(key=lambda x: x["horas"], reverse=True)
            top10 = ranking[:10]

            embed = discord.Embed(
                title="🎮 Seus jogos mais jogados!! 🎮",
                description="",
                color=0x00FF00
            )

            for i, jogo in enumerate(top10, start=1):
                    embed.description += f"{i}. **{jogo['nome']}** – `{jogo['horas']} horas`\n"

            await ctx.send(embed=embed)
        else:
            await ctx.send("Nenhum jogo encontrado ou perfil privado.")
    except Exception as e:
        await ctx.send(f"⚠️ Erro ao buscas dados: {e}")

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

@bot.command(help="Para que o Bot possa entrar no canal de musica")
async def entrar(ctx):
    if ctx.author.voice:
        canal = ctx.author.voice.channel
        await canal.connect()
        await ctx.send("Entrei no canal de voz!")
    else:
        await ctx.send("Você precisa estar em um canal de voz.")

@bot.command(help="Para que o Bot possa sair do canal de musica")
async def sair(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Saí do canal de voz.")
    else:
        await ctx.send("Não estou em nenhum canal de voz.")

@bot.command(help="Para adicionar uma musica ao canal, digite '!tocar link_da_musica' ")
async def tocar(ctx, *, url):
    await ctx.send("🔍 Buscando a música...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'default_search': 'auto',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except Exception:
            await ctx.send("❌ Não foi possível encontrar a música. Verifique o link.")
            return

        url_audio = info['url']
        titulo = info.get('title', 'Sem título')

    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("Você precisa estar em um canal de voz!")
            return

    ctx.voice_client.stop()
    source = await discord.FFmpegOpusAudio.from_probe(url_audio, method='fallback')
    ctx.voice_client.play(source)

    await ctx.send(f"🎶 Tocando agora: **{titulo}**")

@tasks.loop(hours=24)
async def current_time():
    now = datetime.now()   
    
    now = now. strftime("%d/%m/%Y ás %H:%M:%S")
    
    channel = bot.get_channel(1367650512492695572)
    
    await channel.send(f"**Bot Oliveira bateu seu ponto: {now}**")
TOKEN = config("TOKEN")
bot.run(TOKEN)