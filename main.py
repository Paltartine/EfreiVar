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

                else:
                    raise Exception("Une erreur est survenur")
    except Exception as e:
        print(e)
        print("Fin du à une erreur")




bot.run(token)