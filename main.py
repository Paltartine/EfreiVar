import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

import aiohttp

from utils import clear_downloads, download_video, get_time_from_seconds, get_color_from_action, get_recap_message

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
                        print("action : " + name + " extraite")
                else:
                    raise Exception("Le match est introuvable")

        embed_recap = discord.Embed(
            title=f"Fin de l'extraction des actions du match, récap des buts :",
            description=await get_recap_message(arg),
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed_recap)
        print("Fin de l'extraction")
    except Exception as e:
        print(e)
        await interaction.followup.send("Une erreur est survenue, interruption de la commande !")

bot.run(token)