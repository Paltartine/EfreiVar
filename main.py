import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import aiohttp

load_dotenv()
token = os.environ['DISCORD_BOT_TOKEN']

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
    except Exception as e:
        print(e)


DOWNLOADS_DIR = "./downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

def clear_downloads(folder: str = "./downloads"):
    """Delete all files from download folder"""
    if not os.path.exists(folder):
        return

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"⚠️ Impossible de supprimer {file_path} : {e}")

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

@bot.tree.command(name='var', description='Renvoie les vidéos de tous les buts du match donné')
async def var(interaction: discord.Interaction, arg: str):
    matchUrl = f"https://api-front.lefive.fr/splf/v1/matches/{arg}/matchevents"
    matchUrl = f"https://api-front.lefive.fr/splf/v1/matches/5577299/matchevents"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(matchUrl) as response:
                await interaction.response.send_message("✅ Données récupérées")
                if 'application/json' in response.headers.get('content-type', ''):
                    data = await response.json()  # récupère le JSON en dict Python
                    print(data)
                    for goal in data:
                        name = goal.get("name", "Inconnu")
                        time = goal.get("time", "Non défini")
                        video_url = goal.get("videoUrl", None)

                        embed = discord.Embed(
                            title=f"Événement : {name}",
                            description=f"⏱️ Temps : {time}",
                            color=discord.Color.blue()
                        )

                        if video_url:
                            # Ajout du lien cliquable
                            embed.add_field(name="Vidéo", value=f"[Clique ici pour voir]({video_url})", inline=False)
                            print(video_url)

                        # Suivi avec l'embed
                        await interaction.followup.send(embed=embed)# si une vidéo existe, télécharge et upload sur Discord

                        filepath = await download_video(video_url, video_url.split("/")[-1])
                        await interaction.followup.send(file=discord.File(filepath))
                        return

                else:
                    raise Exception("Une erreur est survenur")
    except Exception as e:
        print(e)
        print("Fin du à une erreur")




bot.run(token)