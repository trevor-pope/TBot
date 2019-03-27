import asyncio

import json
import datetime

from .cog import Cog


class EmojiDict(dict):
    """ A dictionary of emote tallies, with a replaced __repr__ for better formatting on discord."""

    def __init__(self, old_dict):
        super().__init__(old_dict)
        self.OldDict = old_dict

    def __repr__(self):
        emojis = sorted(list(zip(self.keys(), self.values())), key=lambda x: x[1], reverse=True)

        return "\n".join(f"{str(emoji[0])} - {str(emoji[1])}" for emoji in emojis)

    def update(self, other):
        for key, val in other.items():
            if key in self:
                self[key] += val

            else:
                self[key] = val


class Emote(Cog):
    """Emote related command, for emoji census and tallies."""

    def __init__(self, bot):
        super().__init__(bot, name='Emote', call_func=self.emote_report,
                         routines=[self.emote_report ])

        from emoji import get_emoji_regexp
        import re

        self.unicode_pattern = get_emoji_regexp()
        self.custom_pattern = re.compile('<:.*?:.*?>')

        with open('cogs/util/data/emote_tally.json', 'r') as f:
            census = json.load(f)
            self.emote_tally = EmojiDict(census['emotes'])
            self.reaction_tally = EmojiDict(census['reactions'])
            self.tally_count = census['tally_count']

    async def emote_report(self, routine=False, **kwargs):

        await self.bot.wait_until_ready()

        if routine:
            print('Finished emote_report() empty task on startup.\n')
            await asyncio.sleep(60 * 60 * 24 * 7)

        while not self.bot.is_closed:
            now = datetime.datetime.now()

            if routine:
                self.tally_count += 1

            response = f"{'=' * 25}\n{' ' * 20}**Emoji Census**\n{' ' * 14}Tally #{self.tally_count}, " \
                       f"{now.strftime('%Y-%m-%d')}\n{'=' * 25}\n{' ' * 25} __Emotes__ \n"
            response += '\n' + repr(self.emote_tally)
            response += f"\n{'=' * 25}\n{' ' * 23} __Reactions__ \n"
            response += '\n' + repr(self.reaction_tally) + '\n'

            await self.record()

            if routine:
                await self.bot.send_message(destination=self.bot.default_channel, content=response)
                print("Finished automatic emote_report() task.\n")
                await asyncio.sleep(60 * 60 * 24 * 7)

            else:
                return self.Response(response=response)

    async def tally_message(self, message):
        custom_matches = self.custom_pattern.findall(message.content)
        unicode_matches = self.unicode_pattern.findall(message.content)
        matches = custom_matches + unicode_matches

        matches = {emote: matches.count(emote) for emote in set(matches)}

        if matches:
            self.emote_tally.update(matches)

    async def tally_reaction(self, reaction, add=True):
        reaction = reaction.emoji

        if type(reaction) != str:
            reaction = f"<:{reaction.name}:{reaction.id}>"

        if add:
            self.reaction_tally.update({reaction: 1})

        else:
            self.reaction_tally.update({reaction: -1})

    async def record(self):
        with open('cogs/util/data/emote_tally.json', 'w') as f:
            json.dump({'tally_count': self.tally_count,
                       'last_tally': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                       'emotes': self.emote_tally,
                       'reactions': self.reaction_tally}, f)




