"""
MIT License

Copyright (c) 2019 Trevor Pope

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import discord
import asyncio
import random as rand
import sys
import json
from collections import namedtuple

"""
                        TBot by Trevor
                https://github.com/trevor-pope/

Feel free to modify, upgrade, and use my bot on your own servers.

    TBot's modular design is inspired by Red from TwentySix 
        https://github.com/Cog-Creators/Red-DiscordBot
      and R.Danny from Rapptz, the creator of discord.py
             https://github.com/Rapptz/RoboDanny/

"""

class TBot(discord.Client):
    def __init__(self, default_channel, wakeword, case_sensitive):
        super().__init__()

        self.default_channel = discord.Object(id=default_channel)
        self.case_sensitive = case_sensitive
        self.wakeword = wakeword
        self.games = []
        self.is_awake = True
        self.cogs = load_cogs(self)

    async def on_ready(self):
        print(f"Logged in as \n {self.user.name} \n {self.user.id} \n------")
        if self.games:
            await self.change_presence(game=discord.Game(name=rand.choice(self.games)))

        try:
            await self.send_message(content="I'm alive!", destination=self.default_channel)

        except discord.DiscordException:
            print("The current default_channel ID is incorrect or does not exist on this server. Switching to the "
                  "default channel on the server!")

            self.default_channel = list(self.servers)[0].default_channel
            if self.default_channel is None:
                self.default_channel = list(list(self.servers)[0].channels)[0]

            await self.send_message(content="I'm alive!", destination=self.default_channel)

    async def on_message(self, message):
        if message.author.bot:
            return

        if ((self.case_sensitive is False and message.content.lower().startswith(self.wakeword.lower()))
                or (self.case_sensitive is True and message.content.startswith(self.wakeword))) and self.is_awake:
            request = message.content[len(self.wakeword):]
            found = False

            for cog in self.cogs:
                for identifier, tags in cog.identifiers.items():  # More efficient command recognition coming soon :/
                    if request.lower().strip().startswith(identifier):
                        found = True
                        await self.send_typing(message.channel)
                        message.content = request[len(identifier):]

                        await cog.call(message=message, tags=tags)
                        break

                if found:
                    break

            else:
                await self.send_message(message.channel, f"I do not understand that command:\n```{request}```")

        elif any(message.content.lower() == self.wakeword + f'{i}' for i in
                 ["wakeup", "wake up", "get up", "stop sleeping"]) and not self.is_awake:
            await self.wakeup(message.channel)

        elif message.content.lower() == "!shutdown" or message.content.lower() == "!s":  # Emergency breaks
            await self._shutdown(message.channel)

        await self.cogs.Emote.tally_message(message)

    async def on_reaction_add(self, reaction, user):
        await self.cogs.Emote.tally_reaction(reaction)

        if reaction.count >= len(reaction.message.server.members)/2 and rand.randint(0, 3) >= 2:
            await self.add_reaction(reaction.message, reaction.emoji)

    async def on_reaction_remove(self, reaction, user):
        await self.cogs.Emote.tally_reaction(reaction, add=False)

    async def sleep(self):
        await self.change_presence(game=rand.choice(self.games) if self.games else None, status=discord.Status.idle)
        self.is_awake = False

    async def wakeup(self, channel):
        await self.change_presence(game=rand.choice(self.games) if self.games else None, status=discord.Status.online)
        self.is_awake = True
        await self.send_message(channel, "Already? _yawn_ ")

    async def _shutdown(self, channel):
        await self.send_message(channel, "Shutting down...")
        await self.cogs.Emote.record()
        await self.close()


def load_cogs(bot, cogs=[]):
    """Loads a list of cogs, as well as the default cogs, onto the bot as a namedtuple"""
    default_cogs = ['general', 'emote', 'rhyme', 'thesaurus', 'joke', 'conversation']
    loaded = []

    import importlib as imp 
    for cog in default_cogs + cogs:
        try:
            print(f'Loading {cog.title()}...')
            module = imp.import_module("cogs." + cog)
            loaded.append(getattr(module, cog.title())(bot))
            print('Loaded.\n')

        except ModuleNotFoundError as e:
            print(e)
            print(f'Cannot find cog {cog.title()}\n')
            print('Exiting.')
            sys.exit(-1)

    Cogs = namedtuple('Cogs', ' '.join(i.title() for i in default_cogs + cogs))
    loaded = Cogs(*loaded)

    return loaded


def load_settings():
    """Loads settings from settings.txt"""
    print("Loading cogs/util/data/settings.txt\n")
    try:
        with open('cogs/util/data/settings.txt') as f:
            settings = json.load(f)

            try:
                token = settings['Token']
                if token == '':
                    raise KeyError
                else:
                    print("Token found.\n")
            except KeyError:
                print('Could not find "Token" in settings.txt\nTBot cannot run without a proper token, double check'
                      'that you ran initial_setup.py')
                sys.exit(1)

            try:
                wakeword = settings['Wakeword']
                if wakeword == '':
                    raise KeyError
                else:
                    print(f"Using '{wakeword}' as wakeword.")
            except KeyError:
                print('Could not find "Trigger" in settings.txt\nDouble check that you ran initial_setup.py')
                print('We will use the default, "Hey Tbot, "')

            try:
                case_sensitive = settings['CaseSensitive']
                if type(case_sensitive) != bool:
                    raise KeyError
                else:
                    print(f"Wakeword case sensitivity is set to {case_sensitive}")
            except KeyError:
                print('Could not find "CaseSensitive" in settings.txt, or is invalid.\n'
                      'We will use the default, False')
                case_sensitive = False

            try:
                default_channel = settings['DefaultChannel']
                if not default_channel.isdigit():
                    raise KeyError
                else:
                    print(f"Default Channel os set to {default_channel}")
            except KeyError:
                print('Could not find "DefaultChannel" in settings.txt, or is invalid\n"'
                      'We will use the default channel that is on the server.')
                default_channel = None

            return token, wakeword, case_sensitive, default_channel

    except FileNotFoundError:
        print("Could not find settings.txt in cogs/util/data folder. Make sure you properly installed from the github.")
        sys.exit(1)


def main(token, wakeword, case_sensitive, default_channel):
    bot = TBot(wakeword=wakeword, case_sensitive=case_sensitive, default_channel=default_channel)

    try:
        bot.run(token)
    except KeyboardInterrupt:
        sys.exit(0)

    except discord.errors.LoginFailure:
        print("The token provided is invalid. Double check you followed the instructions on github correctly.")
        sys.exit(1)


if __name__ == '__main__':
    print('\n\n=~=~=~TBot v1.0.0~=~=~=\n' + '=' * 23, end='\n\n\n')
    token, wakeword, case_sensitive, default_channel = load_settings()
    main(token, wakeword, case_sensitive, default_channel)
