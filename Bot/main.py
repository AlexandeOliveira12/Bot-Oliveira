from datetime import datetime
import sys
import re
import requests
import random
import json

from decouple import config
import discord
from discord.app_commands import Command, Group, command
from discord.ext import commands, tasks
from discord.ext.commands.errors import MissingRequiredArgument, CommandNotFound



intents = discord.Intents.default()
intents.message_content = True  # Necessário para ler mensagens

bot = commands.Bot(command_prefix="/", intents=intents, help_command=None)
tree = bot.tree  # Objeto para registrar Slash Commands

# ------------------------------------------ BOT EVENTS ------------------------------------------ #

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
            color=0x00ff00
        )
        embed.set_thumbnail(url=bot.user.display_avatar.url)
        embed.set_footer(text="Status atualizado automaticamente.")
        await canal.send(embed=embed)

    await tree.sync()  # Sincroniza os Slash Commands com o Discord
    current_time.start()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Por favor, escreva o comando corretamente, digite !help para ver os comandos e suas funcionalidades!")
    elif isinstance(error, CommandNotFound):
        await ctx.send("Por favor, escreva o comando corretamente, digite !help para ver os comandos e suas funcionalidades!")
    else:
        raise error

# ------------------------------------------ BOT COMANDS ------------------------------------------ #

# Help
@tree.command(name="help", description="Mostra to       dos os comandos disponíveis")
async def help_slash(interaction: discord.Interaction):
    try:
        await interaction.response.defer()  # Defere a resposta, indicando que o bot está processando o comando
        
        embed = discord.Embed(title="📘 Lista de Comandos", color=0x00ff00)
        
        # Obtemos todos os comandos registrados de forma correta
        for command in bot.tree.get_commands():
            embed.add_field(name=f"/{command.name}", value=command.description or "Sem descrição", inline=False)
        
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Ocorreu um erro ao tentar listar os comandos: {e}")


# QAP
@tree.command(name="qap", description="Testa se o bot está online (Ping)")
async def qap_slash(interaction: discord.Interaction):
    await interaction.response.send_message("QAP Comando, Prossiga!!")

# Função para carregar dados do JSON
def load_steam_data():
    try:
        with open("steam_to_discord.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Função para salvar dados no JSON
def save_steam_data(data):
    with open("steam_to_discord.json", "w") as f:
        json.dump(data, f, indent=4)

# Comando Slash para vincular um Steam ID a um usuário do Discord
@bot.tree.command(name="linksteam", description="Vincula seu Steam ID ao seu usuário do Discord")
async def linksteam_slash(interaction: discord.Interaction, steam_id: str):
    await interaction.response.defer(ephemeral=True)  # Resposta visível apenas para o autor

    steam_data = load_steam_data()

    if steam_id in steam_data:
        await interaction.followup.send("🚫 Este Steam ID já está vinculado a outro usuário!")
    else:
        steam_data[steam_id] = str(interaction.user.id)
        save_steam_data(steam_data)
        await interaction.followup.send(f"✅ Steam ID `{steam_id}` foi vinculado ao seu usuário do Discord!")

# Comando Slash para exibir os jogos mais jogados (slash)
@bot.tree.command(name="timeplayed", description="Exibe os principais jogos da sua biblioteca por tempo jogado")
async def timeplayed_slash(interaction: discord.Interaction, steam_id: str):
    await interaction.response.defer()
    try:
        steam_data = load_steam_data()

        if steam_id not in steam_data:
            await interaction.followup.send("Este Steam ID não está vinculado a nenhum usuário do Discord.")
            return

        discord_user_id = steam_data[steam_id]
        discord_user = bot.get_user(int(discord_user_id))

        # Buscar dados da Steam
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

        if "response" in data and "games" in data["response"]:
            jogos = data["response"]["games"]

            ranking = [
                {
                    "nome": jogo["name"],
                    "horas": round(jogo["playtime_forever"] / 60, 2)
                }
                for jogo in jogos
                if jogo["playtime_forever"] > 0
            ]

            ranking.sort(key=lambda x: x["horas"], reverse=True)
            top10 = ranking[:10]

            embed = discord.Embed(
                title="🎮 Seus Jogos Mais Jogados 🎮",
                description=f"{discord_user.mention}, Aqui estão seus jogos mais jogados.",
                color=0x00FF00
            )

            total_hours = sum(j["horas"] for j in top10)
            embed.add_field(name="Total de Horas Jogadas", value=f"{total_hours} horas", inline=False)

            for i, jogo in enumerate(top10, start=1):
                embed.add_field(name=f"{i}. {jogo['nome']}", value=f"{jogo['horas']} horas", inline=True)

            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("Nenhum jogo encontrado ou perfil privado.")
    except Exception as e:
        await interaction.followup.send(f"⚠️ Erro ao buscar dados: {e}")

# Comando de reinício
@tree.command(name="restart", description="Reinicia o bot")
async def restart(interaction: discord.Interaction):
    # Verifica se o usuário tem permissões de administrador
    if interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Reiniciando o bot... 🚀")

        # Encerra o bot, o que fará a Railway reiniciar o container automaticamente
        sys.exit("Bot reiniciado!")  # Railway reiniciará automaticamente o container.

    else:
        await interaction.response.send_message("Você não tem permissão para reiniciar o bot.")


frases_motivacionais = [
    ("A persistência é o caminho do êxito.", "Charles Chaplin"),
    ("Só se pode alcançar um grande êxito quando nos mantemos fiéis a nós mesmos.", "Friedrich Nietzsche"),
    ("Tente mover o mundo – o primeiro passo será mover a si mesmo.", "Platão"),
    ("A vantagem de ter péssima memória é divertir-se muitas vezes com as mesmas coisas boas como se fosse a primeira vez.", "Friedrich Nietzsche"),
    ("O sucesso nasce do querer, da determinação e persistência em se chegar a um objetivo.", "José de Alencar"),
    ("A confiança é uma mulher ingrata, Que te beija e te abraça, te rouba e te mata.", "Racionais MC's"),
    ("De todos os animais selvagens, o homem jovem é o mais difícil de domar.", "Platão"),
    ("Deve-se temer a velhice, porque ela nunca vem só. Bengalas são provas de idade e não de prudência.", "Platão"),
    ("É mais fácil lidar com uma má consciência do que com uma má reputação.", "Friedrich Nietzsche"),
    ("O que me preocupa não é o grito dos maus. É o silêncio dos bons.", "Martin Luther King Jr."),
    ("Não espere por uma crise para descobrir o que é importante em sua vida.", "Platão"),
    ("A coragem é a primeira das qualidades humanas porque garante todas as outras.", "Aristóteles"),
    ("A maior glória em viver não está em nunca cair, mas em nos levantar cada vez que caímos.", "Nelson Mandela"),
    ("Quem olha para fora, sonha; quem olha para dentro, desperta.", "Carl Jung"),
    ("A mente que se abre a uma nova ideia jamais voltará ao seu tamanho original.", "Albert Einstein"),
    ("Nada é pequeno quando feito com amor.", "Cícero"),
    ("A felicidade não está em fazer o que se quer, mas em querer o que se faz.", "Jean-Paul Sartre"),
    ("Se queres ser feliz amanhã, tenta hoje mesmo.", "Liang Tzu"),
    ("É durante os momentos mais sombrios que devemos focar para ver a luz.", "Aristóteles"),
    ("A vida é 10% o que acontece com você e 90% como você reage a isso.", "Charles Swindoll")
]

emojis = [
    ("😁"),
    ("✌️"),
    ("🥶"),
    ("⛅"),
    ("🌹"),
    ("☀️"),
    ("💰"),
    ("🍎"),
    ("🖖"),
    ("🔥"),
    ("🎯"),
    ("🎉"),
    ("🤖"),
    ("🧠"),
    ("🚀"),
    ("🐍"),
    ("🛡️"),
    ("📚")
]

@tasks.loop(hours=24)
async def current_time():
    channel = bot.get_channel(1367650512492695572)

    frase, autor = random.choice(frases_motivacionais)
    emoji = random.choice(emojis)
    mensagem = f"{emoji} *\"{frase}\"* — **{autor}**"

    if channel:
        await channel.send(mensagem)

TOKEN = config("TOKEN")
bot.run(TOKEN)
