from collections import namedtuple
import json
import aiohttp


class Cog:
    """Generic cog object for TBot that houses several related commands"""
    def __init__(self, bot, name, call_func, routines=None):
        self.bot = bot
        self.name = name
        self.identifiers = get_identifiers(name)
        self.tags = tuple(set(get_tags(self.identifiers)))

        self.Response = namedtuple('Response', 'channel response embed',
                                   defaults=(self.bot.default_channel, None, None))
        self.call_func = call_func
        self.routines = routines
        self._start_routines()

    async def call(self, message, tags):
        """Generic method to call a Cog, which passes the necessary info to each Cog's specified call_func to do the
            actual work"""
        print(f"Calling {self.call_func.__name__} task.")
        response = await self.call_func(message=message, tags=tags)
        await self._respond(channel=response.channel, response=response.response, embed=response.embed)

    async def _respond(self, channel, response, embed):
        await self.bot.send_message(destination=channel, content=response, embed=embed)
        print(f"Finished {self.call_func.__name__} task.\n")

    def _start_routines(self):
        if self.routines:
            for routine in self.routines:
                self.bot.loop.create_task(routine(routine=True))

    async def _fetch(self, url, params=None, headers=None):
        """Generic API fetcher method"""
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url, params=params, headers=headers) as r:
                if r.status != 200:
                    print(f"API call from {self.call_func} went wrong, got: \n{r}\n{await r.json()}")
                    return False

                res = await r.json()
                return res

    async def refresh_identifiers(self):
        """Re-reads the identifiers.json to update newly added/updated idents"""
        print(f'{self.name} is refreshing idents.')
        self.identifiers = get_identifiers(self.name)


def get_all_identifiers():
    with open("util/data/identifiers.json", 'r') as f:
        return json.load(f)


def get_identifiers(command):
    with open("cogs/util/data/identifiers.json", 'r') as f:
        return json.load(f)[command]


def get_tags(identifiers):
    return [tag for taglist in identifiers.values() for tag in taglist]
