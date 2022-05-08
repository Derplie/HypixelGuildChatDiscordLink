import discord
from discord.ext import commands
from javascript import require, On
import asyncio
import os
import requests
import json
from dotenv import load_dotenv
import random
import string

load_dotenv()
mineflayer = require("mineflayer","latest")

############
CHANNEL_ID = 948935430731100230
############

class MainApp(commands.Bot):
    def __init__(self, host, port, email, password, version, token, key, antisnipe_key=""):
        super().__init__(command_prefix="$", self_bot=False, activity=discord.Activity(type=discord.ActivityType.watching, name="Guild Chat"))
        self.host = host
        self.port = port
        self.email = email
        self.pswd = password
        self.version = version
        self.token = token
        self.api_key = key
        self.antisnipe_key = antisnipe_key
    
    def StartDiscordClient(self):
        self.run(self.token)
    def StartMinecraftClient(self):
        self.bot = mineflayer.createBot({
            "host": self.host,
            "port": self.port,
            "username": self.email,
            "password": self.pswd,
            "version": self.version,
            "auth": "microsoft"
        })
    

    def Listener(self, ChannelID):
        self.msg = ""
        self.new_msg = False
        self.online_players = list()

        @self.command()
        async def online(ctx):
            await ctx.send("**Online Players: **" + ", ".join(self.online_players))
            return

        @self.event
        async def on_message(message):
            if message.channel.id != ChannelID:
                return
            await self.process_commands(message)
            if message.content.startswith("$"):
                return
            if message.author.name == self.user.name:
                return
            self.bot.chat(f"/gc {message.author.display_name} > {message.content}")
        
        @On(self.bot, "chat")
        def handle(this, username, message, *args):
            self.splitmessage = message.split()

            if username == self.bot.username:
                return
            if username != "Guild":
                if self.splitmessage[0] == "+bw":
                    if len(self.splitmessage) < 2:
                        self.bot.chat(f"/r Please use +bw USERNAME | {''.join(random.choices(string.ascii_lowercase + string.digits, k=15))}")
                        return
                    self.target_username = self.splitmessage[1]
                    self.mojang_response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{self.target_username}")
                    if int(self.mojang_response.status_code) in [404, 204]:
                        self.bot.chat(f"/r That username isn't valid. | {''.join(random.choices(string.ascii_lowercase + string.digits, k=15))}")
                        return
                    try: 
                        self.target_uuid = self.mojang_response.json()["id"]
                    except:
                        self.bot.chat(f"/r That username isn't valid. | {''.join(random.choices(string.ascii_lowercase + string.digits, k=15))}")
                        return
                    self.hypixel_response = requests.get(f"https://api.slothpixel.me/api/players/{self.target_uuid}?key={self.api_key}").json()
                    if "error" in self.hypixel_response:
                        self.bot.chat(f"/r Error: {self.hypixel_response['error']} | {''.join(random.choices(string.ascii_lowercase + string.digits, k=15))}")
                        return
                    if not "stats" in self.hypixel_response:
                        self.bot.chat(f"/r That player hasn't joined Hypixel before. | {''.join(random.choices(string.ascii_lowercase + string.digits, k=15))}")
                        return
                    self.bedwars_stats = self.hypixel_response["stats"]["BedWars"]
                    if self.antisnipe_key != "":
                        self.antisnipe_response = requests.get(f'http://api.antisniper.net/winstreak?key={self.antisnipe_key}&uuid={self.target_uuid}').json()
                        if self.antisnipe_response["success"] == False or self.antisnipe_response["player"] == None:
                            self.target_winstreak = self.bedwars_stats["winstreak"]
                        else:
                            self.target_winstreak = self.antisnipe_response["player"]["data"]["overall_winstreak"]
                    else:
                        self.target_winstreak = self.bedwars_stats["winstreak"]
                    self.bot.chat(f"/r [{self.bedwars_stats['level']}✫] {self.mojang_response.json()['name']} | FKDR: {self.bedwars_stats['final_k_d']} | WINSTREAK: {self.target_winstreak} | FINALS: {self.bedwars_stats['final_kills']} | {''.join(random.choices(string.ascii_lowercase + string.digits, k=15))}")
                    return
                else:
                    return
            if self.splitmessage[1] == self.bot.username:
                return

            if len(self.splitmessage) == 2:
                self.msg = f"**{username} > {message}**"
                if self.splitmessage[1] == "joined.":
                    if self.splitmessage[0] not in self.online_players:
                        self.online_players.append(self.splitmessage[0])
                if self.splitmessage[1] == "left.":
                    while self.splitmessage[0] in self.online_players:
                        self.online_players.remove(self.splitmessage[0])
            else:
                if self.splitmessage[0] in ["[VIP]","[VIP+]","[MVP]","[MVP+]","[MVP++]"]:
                    self.msg = f"**{username} > {self.splitmessage[0]} {self.splitmessage[1]} {self.splitmessage[2]}** {message.split(' ', 3)[3]}"
                else:
                    self.msg = f"**{username} > {self.splitmessage[0]} {self.splitmessage[1]}** {message.split(' ', 2)[2]}"
            self.new_msg = True
        
        @self.command()
        async def say(ctx):
            if ctx.message.author.id in [320666320280616960, 636626595066413066]:
                self.bot.chat(ctx.message.content.split(' ', 1)[1])
                await ctx.send("Sent")
            else:
                await ctx.send("no perms + L + ratio + bozo")

        async def timer():
            await self.wait_until_ready()
            ch = self.get_channel(ChannelID)

            while True:
                if self.new_msg == True:
                    await ch.send(self.msg)
                    self.new_msg = False
                await asyncio.sleep(0.05)

        self.loop.create_task(coro=timer())
        
if __name__ == "__main__":
    email = os.getenv("EMAIL")
    pswd = os.getenv("PSWD")
    token = os.getenv("TOKEN")
    key = os.getenv("KEY")
    antisnipe_key = os.getenv("ANTISNIPE_KEY")
    App = MainApp(host="hypixel.net",port=25565,email=email,password=pswd,version="1.8.9",token=token,key=key,antisnipe_key=antisnipe_key)
    App.StartMinecraftClient()
    App.Listener(CHANNEL_ID)
    App.StartDiscordClient()
