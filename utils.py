import os
from dotenv import load_dotenv

import discord

import aiohttp

load_dotenv()
token = os.environ['DISCORD_BOT_TOKEN']

DOWNLOADS_DIR = "./downloads"

def clear_downloads():
    """Delete all files from DOWNLOADS_DIR folder"""
    # ensure directory exists
    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)

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

async def get_recap_message(match_id):
    url = f"https://api-front.lefive.fr/splf/v1/matches/{match_id}/matchplayers"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if 'application/json' in response.headers.get('content-type', ''):
                    data = await response.json()  # récupère le JSON dans un dictionnaire
                    players_data = []
                    for player in data:
                        player_id = player.get('teamPlayer', {}).get('id', None)

                        # players 148 and 149 are private players
                        if player_id is not None and player_id != 148 and player_id != 149:
                            player_name = player.get('teamPlayer', {}).get('name', "Nom inconnu")
                            team_name = player.get('teamPlayer', {}).get('team', {}).get('name', "Nom d'équipe inconnu")
                            nb_goals = player.get('nbGoals', "Nombre de buts inconnu")
                            players_data.append({"player_name": player_name, "team_name": team_name, "nb_goals": nb_goals})

                    players_data_sorted = sorted(players_data, key=lambda p: p["team_name"])
                    current_team = ""
                    message = ""
                    for player in players_data_sorted:
                        new_team = player["team_name"]
                        if new_team != current_team:
                            current_team = new_team
                            if current_team != "":
                                message += "\n"
                            message += f"{new_team} :\n"
                        message += f"{player['player_name']} : {player['nb_goals']} {'buts' if player['nb_goals'] > 1 else 'but'}\n"
                    return message
                else:
                    raise Exception("Les données des joueurs sont introuvables")
    except Exception as e:
        raise Exception(f"Erreur : {e}")