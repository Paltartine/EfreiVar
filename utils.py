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