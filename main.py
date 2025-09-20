import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

import aiohttp

load_dotenv()
token = os.environ['DISCORD_BOT_TOKEN']

DOWNLOADS_DIR = "./downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
    except Exception as e:
        print(e)


def clear_downloads():
    """Delete all files from DOWNLOADS_DIR folder"""
    if not os.path.exists(DOWNLOADS_DIR):
        return

    for filename in os.listdir(DOWNLOADS_DIR):
        file_path = os.path.join(DOWNLOADS_DIR, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Impossible de supprimer {file_path} : {e}")

async def download_video(url: str, filename: str) -> str:
    """Download video from URL and return his local path"""
    filepath = os.path.join(DOWNLOADS_DIR, filename)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(filepath, "wb") as f:
                    f.write(await resp.read())
                return filepath
            else:
                raise Exception(f"Échec du téléchargement (status {resp.status})")

def get_time_from_seconds(seconds: int) -> str:
    minutes = seconds // 60
    sec = seconds % 60
    return f"{minutes:02}:{sec:02}"

def get_color_from_action(action):
    if action.find("Team A") != -1:
        return discord.Color.blue()
    elif action.find("Team B") != -1:
        return discord.Color.green()
    else:
        return discord.Color.orange()


@bot.tree.command(name='var', description='Renvoie les vidéos de tous les buts du match donné')
async def var(interaction: discord.Interaction, arg: str):
    match_url = f"https://api-front.lefive.fr/splf/v1/matches/{arg}/matchevents"

    await interaction.response.send_message(f"Récupération des résultats du match {arg} en cours...")

    try:
        clear_downloads()
        async with aiohttp.ClientSession() as session:
            async with session.get(match_url) as response:
                if 'application/json' in response.headers.get('content-type', ''):
                    data = await response.json()  # récupère le JSON dans un dictionnaire
                    for goal in data:
                        name = goal.get("name", "Inconnu")
                        time = goal.get("time", "Inconnu")
                        video_url = goal.get("videoUrl", None)

                        embed = discord.Embed(
                            title=f"{name}",
                            description=f"⏱️ Temps : {get_time_from_seconds(time)}",
                            color=get_color_from_action(name)
                        )

                        # Ajout du lien cliquable
                        embed.add_field(name="Vidéo", value=f"[Clique ici pour voir l'action]({video_url})", inline=False)

                        filepath = await download_video(video_url, video_url.split("/")[-1])

                        await interaction.followup.send(
                            file=discord.File(filepath),
                            embed=embed
                        )
                else:
                    raise Exception("Le match est introuvable")
    except Exception as e:
        print(e)
        await interaction.followup.send("Une erreur est survenue, interruption de la commande !")

bot.run(token)