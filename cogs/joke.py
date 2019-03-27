from cogs.cog import Cog


class Joke(Cog):
    """Fetches jokes from the web"""

    def __init__(self, bot):
        super().__init__(bot, name='Joke', call_func=self.joke)
        self.URL = 'https://icanhazdadjoke.com'

    async def joke(self, message, tags):

        headers = {"Accept": "application/json"}
        params = {'User-Agent': 'google.com'}

        if 'plural' in tags:
            response = await self._fetch(url=self.URL, params=params, headers=headers)
            response2 = await self._fetch(url=self.URL, params=params, headers=headers)

            if not response or not response2:
                return self.Response(response="Whoops, something went wrong!",
                                     channel=message.channel)

            return self.Response(response=f"{response['joke']} \n\n {response2['joke']}", channel=message.channel)

        else:
            response = await self._fetch(url=self.URL, params=params, headers=headers)

            if not response:
                return self.Response(response="Whoops, something went wrong!",
                                     channel=message.channel)

            return self.Response(response=f"{response['joke']}", channel=message.channel)

