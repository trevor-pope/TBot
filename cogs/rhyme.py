from cogs.cog import Cog

import random as rand
from string import ascii_letters


class Rhyme(Cog):
    """Fetches rhymes from the web"""

    def __init__(self, bot):
        super().__init__(bot, name='Rhyme', call_func=self.rhyme)
        self.URL = "https://api.datamuse.com/words"

        self.response_singular = ["How about {}?",
                                  "Maybe use {}?",
                                  "Okay, here you go: {}"]

        self.response_plural_2 = ["How about {} or {}?",
                                  "Maybe try {} or {}?",
                                  "Sure! {} and {}."]

        self.response_plural_3 = ["Coming right up! {}, {}, {}.",
                                  "Here are some: {}, {}, {}.",
                                  "What about these: {}, {}, {}?",
                                  "Okay, here you go: {}, {}, {}."]

    async def rhyme(self, message, tags):

        try:
            word = ''.join(list(filter(lambda x: x in ascii_letters, message.content.strip().split(" ")[0])))

        except Exception as e:
            print(str(e))
            return self.Response(response="Whoops, something went wrong!",
                                 channel=message.channel)

        if not word:
            return self.Response(response="It appears you didn't input a valid word. "
                                          "Try something without special characters or emotes please!",
                                 channel=message.channel)

        params = {'rel_rhy': word}
        response = await self._fetch(url=self.URL, params=params)

        if not response:
            return self.Response(response="Whoops, something went wrong!",
                                 channel=message.channel)

        else:
            rhymes = [rhyme['word'] for rhyme in response if " " not in rhyme['word']]

            if not rhymes:
                return self.Response(response="No rhymes found, womp womp",
                                     channel=message.channel)

            else:
                if 'singular' in tags or not tags:
                    rhyme = rand.choice(rhymes)
                    response = rand.choice(self.response_singular).format(rhyme)

                    return self.Response(response=response, channel=message.channel)

                else:
                    if len(rhymes) == 2:
                        rhymes = tuple(rand.sample(rhymes, 2))
                        response = rand.choice(self.response_plural_2).format(*rhymes)

                        return self.Response(response=response, channel=message.channel)

                    else:
                        rhymes = tuple(rand.sample(rhymes, 3))
                        response = rand.choice(self.response_plural_3).format(*rhymes)

                        return self.Response(response=response, channel=message.channel)

