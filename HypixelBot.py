import discord
from discord.ext import commands
from javascript import require, On
import asyncio
from profanity_filter import ProfanityFilter
import os
mineflayer = require("mineflayer","latest")

############
CHANNEL_ID = 948935430731100230
############

pf = ProfanityFilter()
pf.censor_char = "#"

class MainApp(commands.Bot):
    def __init__(self, host, port, email, password, version, token):
        super().__init__(command_prefix="$", self_bot=False, activity=discord.Activity(type=discord.ActivityType.watching, name="Guild Chat"))
        self.host = host
        self.port = port
        self.email = email
        self.pswd = password
        self.version = version
        self.token = token
    
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

        @self.event
        async def on_message(message):
            await self.process_commands(message)
            if message.channel.id != ChannelID:
                return
            if message.author.name == self.user.name:
                return
            self.bot.chat(f"/gc {message.author.display_name} > {pf.censor(message.content)}")
        
        @On(self.bot, "chat")
        def handle(this, username, message, *args):
            self.splitmessage = message.split()

            if username == self.bot.username:
                return
            if username != "Guild":
                return
            if self.splitmessage[1] == self.bot.username:
                return

            if len(self.splitmessage) == 2:
                self.msg = f"**{username} > {message}**"
            else:
                if self.splitmessage[0] in ["[VIP]","[VIP+]","[MVP]","[MVP+]","[MVP++]"]:
                    self.msg = f"**{username} > {self.splitmessage[0]} {self.splitmessage[1]} {self.splitmessage[2]}** {message.split(' ', 3)[3]}"
                else:
                    self.msg = f"**{username} > {self.splitmessage[0]} {self.splitmessage[1]}** {message.split(' ', 2)[2]}"
            self.new_msg = True
        
        @self.command()
        async def say(ctx):
            if ctx.message.author.id == 320666320280616960:
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
    email = os.environ["EMAIL"]
    pswd = os.environ["PSWD"]
    token = os.environ["TOKEN"]
    App = MainApp(host="hypixel.net",port=25565,email=email,password=pswd,version="1.8.9",token=token)
    App.StartMinecraftClient()
    App.Listener(CHANNEL_ID)
    App.StartDiscordClient()

