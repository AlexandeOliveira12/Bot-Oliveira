from datetime import datetime
import sys
import re
import requests
import random
import json
import os
import asyncio

from decouple import config
from discord import app_commands
import discord
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

    # Canal de status
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

    # 🔧 Modo de desenvolvimento (True = sync só em servidor de testes)
    MODO_DEV = True
    SERVIDOR_DE_TESTE = 1195507908075597844

    try:
        if MODO_DEV:
            synced = await bot.tree.sync(guild=discord.Object(id=SERVIDOR_DE_TESTE))
            print(f"✅ {len(synced)} comando(s) sincronizado(s) no servidor de testes.")
        else:
            synced = await bot.tree.sync()
            print(f"🌍 {len(synced)} comando(s) sincronizado(s) globalmente.")
    except Exception as e:
        print(f"❌ Erro ao sincronizar comandos: {e}")

    # Inicia tarefas de background
    current_time.start()

# ------------------------------------------ ERROR HANDLER ------------------------------------------ #

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("Por favor, escreva o comando corretamente, digite !help para ver os comandos e suas funcionalidades!")
    elif isinstance(error, CommandNotFound):
        await ctx.send("Por favor, escreva o comando corretamente, digite !help para ver os comandos e suas funcionalidades!")
    else:
        raise error

# ------------------------------------------ BOT COMMANDS ------------------------------------------ #

# Help
@tree.command(name="help", description="Mostra todos os comandos disponíveis")
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

STEAM_FILE = "steam_ids.json"
steam_data_path = STEAM_FILE

def load_steam_data():
    if not os.path.exists(STEAM_FILE):
        return {}
    with open(STEAM_FILE, "r") as f:
        return json.load(f)
    
def salvar_steam_data(caminho, dados):
    with open(caminho, "w") as f:
        json.dump(dados, f, indent=4)

class Steam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="linksteam", description="Vincule seu Steam ID ao seu Discord.")
    @app_commands.describe(steam_id="Seu Steam ID numérico")
    async def linksteam(self, interaction: discord.Interaction, steam_id: str):
        steam_data = load_steam_data()
        user_id = str(interaction.user.id)

        if steam_id in steam_data.values():
            await interaction.response.send_message("❌ Esse SteamID já está vinculado a outro usuário.", ephemeral=True)
            return

        if user_id in steam_data:
            await interaction.response.send_message(
                f"❌ Você já vinculou a Steam `{steam_data[user_id]}`.\nEntre em contato com um administrador para alterar.",
                ephemeral=True
            )
            return

        steam_data[user_id] = steam_id
        salvar_steam_data(steam_data_path, steam_data)

        await interaction.response.send_message(f"✅ SteamID `{steam_id}` vinculado com sucesso!", ephemeral=True)

    @app_commands.command(name="versteamid", description="Veja o Steam ID que você vinculou.")
    async def versteamid(self, interaction: discord.Interaction):
        steam_data = load_steam_data()
        user_id = str(interaction.user.id)

        if user_id in steam_data:
            steam_id = steam_data[user_id]
            await interaction.response.send_message(f"🔗 Seu SteamID vinculado é: `{steam_id}`", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Você ainda não vinculou nenhum SteamID.", ephemeral=True)
    
    @app_commands.command(name="resetsteam", description="Desvincula seu Steam ID do Discord.")
    async def desvincularsteam(self, interaction: discord.Interaction):
        steam_data = load_steam_data()
        user_id = str(interaction.user.id)

        if user_id not in steam_data:
            await interaction.response.send_message("❌ Você não possui nenhum SteamID vinculado.", ephemeral=True)
            return

        steam_id_removido = steam_data.pop(user_id)
        salvar_steam_data(steam_data_path, steam_data)

        await interaction.response.send_message(f"✅ SteamID `{steam_id_removido}` foi desvinculado com sucesso.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Steam(bot))


# Comando Slash para exibir os jogos mais jogados (slash)
@tree.command(name="timeplayed", description="Exibe os principais jogos da sua biblioteca por tempo jogado")
async def timeplayed_slash(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        steam_data = load_steam_data()

        # Recuperar Steam ID do usuário (corrigido para buscar steam_id pelo user_id)
        user_id = str(interaction.user.id)
        steam_id = steam_data.get(user_id)

        if not steam_id:
            await interaction.followup.send("Você não vinculou seu Steam ID ainda. Use o comando `/linksteam`.")
            return

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

            # Filtrar e calcular o tempo total de horas jogadas
            ranking = [
                {
                    "nome": jogo["name"],
                    "horas": round(jogo["playtime_forever"] / 60, 2)  # Convertendo minutos para horas
                }
                for jogo in jogos
                if jogo["playtime_forever"] > 0  # Somente jogos com tempo jogado
            ]

            # Ordenar os jogos por horas jogadas em ordem decrescente
            ranking.sort(key=lambda x: x["horas"], reverse=True)

            # Pegando os 10 jogos mais jogados
            top10 = ranking[:10]

            # Calculando o total de horas jogadas
            total_hours = sum(jogo["horas"] for jogo in top10)

            # Criando a resposta com os jogos
            embed = discord.Embed(
                title="🎮 Seus Jogos Mais Jogados 🎮",
                description=f"{interaction.user.mention}, Aqui estão seus jogos mais jogados na Steam.",
                color=0x00FF00
            )

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
    if interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Reiniciando o bot... 🚀")
        await asyncio.sleep(2)
        sys.exit("Bot reiniciado!")
    else:
        await interaction.response.send_message("Você não tem permissão para reiniciar o bot.") 

frases_motivacionais = [
    ("A persistência é o caminho do êxito.", "Charles Chaplin"),
    ("Só se pode alcançar um grande êxito quando nos mantemos fiéis a nós mesmos.", "Friedrich Nietzsche"),
    ("Tente e falhe, mas nunca falhe em tentar.", "Jared Kushner"),
    ("Não espere por uma crise para descobrir o que é importante em sua vida.", "Platão"),
    ("Você não é derrotado quando perde, você é derrotado quando desiste.", "Paulo Coelho"),
    ("O sucesso é ir de fracasso em fracasso sem perder o entusiasmo.", "Winston Churchill"),
]

@tree.command(name="motivacao", description="Envia uma frase motivacional")
async def motivacao_slash(interaction: discord.Interaction):
    frase, autor = random.choice(frases_motivacionais)
    await interaction.response.send_message(f'"{frase}"\n- {autor}')

@tasks.loop()
async def current_time():
    canal = bot.get_channel(1372582358523449484)
    if canal:
        await canal.send(f"⏰ O pai ta On!")

# ------------------------------------------ INÍCIO ------------------------------------------ #

async def main():
    async with bot:
        await setup(bot)
        await bot.start(config("TOKEN"))
        
asyncio.run(main())