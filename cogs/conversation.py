import random as rand
import json


from cogs.cog import Cog


class Conversation(Cog):
    """Generic Conversation Commands"""

    def __init__(self, bot):
        super().__init__(bot, name='Conversation', call_func=self.converse)

        with open("cogs/util/data/conversation_responses.json", 'r') as f:
            self.responses = json.load(f)

        self.conversations = {'casual': self.casual,
                              'whatsup': self.whatsup,
                              'rollcall': self.rollcall}

    async def converse(self, message, tags):
        if len(tags) > 1:
            return self.Response(response="This command for Conversation somehow has multiple tags, "
                                          "which is impossible. Fix it!",
                                 channel=message.channel)

        else:
            try:
                return await self.conversations[tags[0]](message)

            except KeyError:
                return self.Response(response="This command for Conversation somehow has a tag that doesn't exist. "
                                             "Fix it!",
                                     channel=message.channel)

            except Exception as e:
                print(str(e))

                return self.Response(response="Whoops, something went wrong!",
                                     channel=message.channel)

    async def casual(self, message):
        return self.Response(response=rand.choice(self.responses['casual']), channel=message.channel)

    async def whatsup(self, message):
        return self.Response(response=rand.choice(self.responses['whatsup']), channel=message.channel)

    async def rollcall(self, message):
        members = message.server.members

        offline = [member for member in members if str(member.status) != 'online']

        if len(offline) == 0:
            return self.Response(response=rand.choice(self.responses['rollcall']), channel=message.channel)

        elif len(offline) == len(members) - 1:
            return self.Response(response="It's feeling a little lonely in here...", channel=message.channel)

        else:
            response = ""
            for member in offline:
                try:
                    if member.nick == 'gary':
                        return self.Response(response="https://imgur.com/T6U7ayA", channel=message.channel)
                except:
                    if member.name.lower() == 'gary':
                        return self.Response(response="https://imgur.com/T6U7ayA", channel=message.channel)

                response += f"We miss you {str(member)[:-5]}! \n"

            return self.Response(response=response, channel=message.channel)