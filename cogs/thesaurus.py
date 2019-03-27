from cogs.cog import Cog

import random as rand
from string import ascii_letters


class Thesaurus(Cog):
    """Fetches synonyms/antonyms from the web"""

    def __init__(self, bot):
        super().__init__(bot, name='Thesaurus', call_func=self.thesaurus)
        self.URL = 'http://thesaurus.altervista.org/thesaurus/v1'
        self.api_key = 'y2Ae37Jp7skYZ130KPtP'

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

    async def thesaurus(self, message, tags, **kwargs):

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

        params = {
            'key': self.api_key,
            'word': word,
            'output': 'json',
            'language': 'en_US'
        }

        response = await self._fetch(url=self.URL, params=params)

        if not response:
            return self.Response(response="Whoops, something went wrong with the Thesaurus API!",
                                 channel=message.channel)

        else:
            synonyms = []
            x = 0
            while len(synonyms) < 7 and x < len(response['response']):
                words = response['response'][x]['list']['synonyms'].split('|')

                if 'antonym' in tags:
                    synonyms += [i.split(" (")[0] for i in words if "antonym" in i]

                else:
                    synonyms += [i.split(" (")[0] for i in words if "antonym" not in i]
                                 #and "related term" not in i]

                x += 1

            if not synonyms:
                return self.Response(response=f"No {'antonyms' if 'antonyms' in tags else 'synonyms'} found, "
                                              f"womp womp",
                                     channel=message.channel)

            longest = max(synonyms, key=lambda x: len(x))

            if 'singular' in tags or not tags:
                synonym = rand.choice(synonyms)
                response = rand.choice(self.response_singular).format(synonym)

                return self.Response(response=response, channel=message.channel)

            else:
                if len(synonyms) == 2:
                    synonyms = rand.sample(synonyms, 2)
                    response = rand.choice(self.response_plural_2).format(*synonyms)

                    return self.Response(response=response, channel=message.channel)

                else:
                    synonyms = rand.sample(synonyms, 3)
                    if longest not in synonyms and rand.choice([1,2,3,4,5,6]) >= 2:
                        synonyms[0] = longest

                    response = rand.choice(self.response_plural_3).format(*synonyms)

                    return self.Response(response=response, channel=message.channel)

