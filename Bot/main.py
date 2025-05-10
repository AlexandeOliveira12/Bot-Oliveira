from datetime import datetime
import re

from decouple import config
import requests

import discord
from discord.app_commands import Command, Group, command  # Importações necessárias para Slash Commands
from discord.ext import commands, tasks
from discord.ext.commands.errors import MissingRequiredArgument, CommandNotFound

import yt_dlp

intents = discord.Intents.default()
intents.message_content = True  # Necessário para ler mensagens

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
tree = bot.tree # Objeto para registrar Slash Commands

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

    await tree.sync() # Sincroniza os Slash Commands com o Discord
    current_time.start()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Por favor, escreva o comando corretamente, digite !help para ver os comandos e suas funcionalidades!")
    elif isinstance(error, CommandNotFound):
        await ctx.send("Por favor, escreva o comando corretamente, digite !help para ver os comandos e suas funcionalidades!")
    else:
        raise error

# Convertendo o comando QAP para Slash Command
@tree.command(name="qap", description="Testa se o bot está online")
async def qap_slash(interaction: discord.Interaction):
    await interaction.response.send_message("QAP Comando, Prossiga!!")

# Convertendo o comando help para Slash Command
@tree.command(name="ajuda", description="Mostra todos os comandos disponíveis")
async def ajuda_slash(interaction: discord.Interaction):
    embed = discord.Embed(title="📘 Lista de Comandos", color=0x00ff00)
    for command in bot.commands:
        embed.add_field(name=f"!{command.name}", value=command.help, inline=False)
    await interaction.response.send_message(embed=embed)

# Convertendo o comando TimePlayed para Slash Command
@tree.command(name="timeplayed", description="Exibe os principais jogos da sua biblioteca por TEMPO JOGADO")
async def timeplayed_slash(interaction: discord.Interaction, steam_id: str):
    await interaction.response.defer() # Indica ao Discord que o bot precisa de mais tempo para responder
    try:
        API_KEY = config("API_KEY")

        url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
        params = {
            "key": API_KEY,
            "steamid": steam_id,
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
                title=f"🎮 Esses são seus jogos mais jogados!! 🎮",
                description="Aqui estão os jogos com o maior tempo de jogo.",
                color=0x00FF00
            )

            # Adiciona o total de horas jogadas ao embed
            total_hours = sum([jogo['horas'] for jogo in top10])
            embed.add_field(name="Total de Horas Jogadas", value=f"{total_hours} horas", inline=False)

            # Adiciona os jogos mais jogados
            for i, jogo in enumerate(top10, start=1):
                embed.add_field(name=f"{i}. {jogo['nome']}", value=f"{jogo['horas']} horas", inline=True)

            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("Nenhum jogo encontrado ou perfil privado.")
    except Exception as e:
        await interaction.followup.send(f"⚠️ Erro ao buscas dados: {e}")

# Convertendo o comando entrar para Slash Command
@tree.command(name="entrar", description="Para que o Bot possa entrar no canal de musica")
async def entrar_slash(interaction: discord.Interaction):
    if interaction.user.voice and interaction.user.voice.channel:
        canal = interaction.user.voice.channel
        try:
            await canal.connect()
            await interaction.response.send_message("Entrei no canal de voz!")
        except discord.ClientException:
            await interaction.response.send_message("Já estou conectado a um canal de voz.")
        except discord.opus.OpusNotLoaded:
            await interaction.response.send_message("Não foi possível conectar ao canal de voz. Certifique-se de que o Opus esteja instalado.")
    else:
        await interaction.response.send_message("Você precisa estar em um canal de voz.")

# Convertendo o comando sair para Slash Command
@tree.command(name="sair", description="Para que o Bot possa sair do canal de musica")
async def sair_slash(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Saí do canal de voz.")
    else:
        await interaction.response.send_message("Não estou em nenhum canal de voz.")

# Convertendo o comando tocar para Slash Command
@tree.command(name="tocar", description="Para adicionar uma musica ao canal")
async def tocar_slash(interaction: discord.Interaction, url: str):
    await interaction.response.defer() # Indica ao Discord que o bot precisa de mais tempo para responder

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
            await interaction.followup.send("❌ Não foi possível encontrar a música. Verifique o link.")
            return

        url_audio = info['url']
        titulo = info.get('title', 'Sem título')

    if not interaction.guild.voice_client:
        if interaction.user.voice and interaction.user.voice.channel:
            try:
                await interaction.user.voice.channel.connect()
            except discord.ClientException:
                await interaction.followup.send("Já estou conectado a um canal de voz.")
                return
            except discord.opus.OpusNotLoaded:
                await interaction.followup.send("Não foi possível conectar ao canal de voz. Certifique-se de que o Opus esteja instalado.")
                return
        else:
            await interaction.followup.send("Você precisa estar em um canal de voz!")
            return

    if interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.stop()

    try:
        source = await discord.FFmpegOpusAudio.from_probe(url_audio, method='fallback')
        interaction.guild.voice_client.play(source)
        await interaction.followup.send(f"🎶 Tocando agora: **{titulo}**")
    except Exception as e:
        await interaction.followup.send(f"⚠️ Erro ao tocar a música: {e}")

@tasks.loop(hours=24)
async def current_time():

    channel = bot.get_channel(1367650512492695572)

    await channel.send("")

TOKEN = config("TOKEN")
bot.run(TOKEN)