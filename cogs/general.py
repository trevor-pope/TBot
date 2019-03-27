import json
import string
import cogs.cog as cog
import re
import logging
validChars = string.ascii_letters + string.digits + ' '


class General(cog.Cog):
    """General Commands, for creating/updating/deleting identifiers to pre-existing commands. """

    def __init__(self, bot):
        super().__init__(bot, name='General', call_func=self.general)

        self.commands = {'c_ident': self.create_identifier,
                         'u_ident': self.update_identifier,
                         'd_ident': self.delete_identifier,
                         'sleep'  : self.sleep,
                         'wakeup' : self.wakeup
                        }

        self.c_ident_pattern = re.compile("'(.+)' '(.+)' (\[(?:'.+'(?:, )?)*\])")
        self.u_ident_pattern = re.compile("'(.+)' '(.+)' '(.+)' (\[(?:'\w+'(?:, )?)*\])")
        self.d_ident_pattern = re.compile("'(.+)' '(.+)'")

    async def general(self, message, tags):
        try:
            return await self.commands[tags[0]](message)

        except Exception as e:
            print(str(e))
            return self.Response(response="Whoops, something went wrong!",
                                 channel=message.channel)

    async def sleep(self, message):
        await self.bot.sleep()
        return self.Response(response="On it! :sleeping:", channel=message.channel)

    async def wakeup(self, message):
        await self.bot.wakeup()
        return self.Response(response="Already?", channel=message.channel)

    async def create_identifier(self, message):
        match = self.c_ident_pattern.match(message.content.strip())

        if match:
            cmd, ident, tags = match.groups()
        else:
            return self.Response(response="I'm unable to parse your request. Try (with the quotes and brackets) \n"
                                          f"```{self.bot.wakeword} create identifier 'Command' 'identifier' ['tag1', 'tag2']```\n"
                                          "If there are no tags, just put empty brackets [].",
                                 channel=message.channel)

        cmd = self.check_command_exist(cmd)
        if not cmd:
            return self.Response(response=f"Command '{cmd}' does not exist. Try ```{self.bot.wakeword} what commands are there?```",
                                 channel=message.channel)

        if ident.lower().strip() in cmd.identifiers:
            return self.Response(response=f"Identifier '{ident}' already exists! ",
                                 channel=message.channel)

        if any(char not in validChars for char in ident) or ident.strip() == '':
            return self.Response(response=f"'{ident}' is not a valid identifier. "
                                          f"Try avoiding punctuation and special characters.",
                                 channel=message.channel)

        tags = re.findall('(\w+)', tags)
        for tag in tags:
            if tag not in cmd.tags + ('',):
                return self.Response(response=f"Tag '{tag}' does not currently exist for {cmd.name}. "
                                              f"See the current tags by doing ```{self.bot.wakeword} what commands are there?```",
                                     channel=message.channel)

        with open("cogs/util/data/identifiers.json", 'r+') as f:
            commands = json.load(f)
            f.seek(0)
            commands[cmd.name][ident.lower().strip()] = tags
            f.write(json.dumps(commands))
            f.truncate()

        await cmd.refresh_identifiers()
        return self.Response(response=f"Identifier sucesfully created! Test it out with \n ```{self.bot.wakeword} {ident}```",
                             channel=message.channel)

    async def update_identifier(self, message):
        match = self.u_ident_pattern.match(message.content.strip())

        if match:
            cmd, old_ident, new_ident, tags = match.groups()
        else:
            return self.Response(response="I'm unable to parse your request. Try (with the quotes and brackets) \n"
                                          f"```{self.bot.wakeword}, update identifier 'Command' 'old_identifier', 'new_identifier'"
                                          " ['tag1', 'tag2']```\n"
                                          "If there are no tags, just put empty brackets [].",
                                 channel=message.channel)

        cmd = self.check_command_exist(cmd)
        if not cmd:
            return self.Response(response=f"Command '{cmd}' does not exist. Try ```{self.bot.wakeword}, what commands are there?```",
                                 channel=message.channel)

        if old_ident.lower().strip() not in cmd.identifiers:
            return self.Response(response=f"Identifier '{old_ident}' doesn't exist. Try "
                                          f"```{self.bot.wakeword}, display all identifiers```",
                                 channel=message.channel)

        if any(char not in validChars for char in new_ident) or new_ident.strip() == '':
            return self.Response(response=f"'{new_ident}' is not a valid identifier. "
                                          f"Try avoiding punctuation and special characters.",
                                 channel=message.channel)

        tags = re.findall('(\w+)', tags)
        for tag in tags:
            if tag.lower() not in cmd.tags + ('',):
                return self.Response(response=f"Tag '{tag}' does not currently exist for {cmd.name}. ",
                                     channel=message.channel)

        with open("cogs/util/data/identifiers.json", 'r+') as f:
            commands = json.load(f)
            f.seek(0)
            del commands[cmd.name][old_ident.lower().strip()]
            commands[cmd.name][new_ident.lower().strip()] = [tag.lower() for tag in tags]
            f.write(json.dumps(commands))
            f.truncate()

        await cmd.refresh_identifiers()
        return self.Response(
            response=f"Identifier sucesfully updated! Test it out with \n ```{self.bot.wakeword}, {new_ident}```",
            channel=message.channel)

    async def delete_identifier(self, message):
        match = self.d_ident_pattern.match(message.content.strip())

        if match:
            cmd, ident = match.groups()
        else:
            return self.Response(response="I'm unable to parse your request. Try (with the quotes and brackets) \n"
                                          f"```{self.bot.wakeword}, delete identifier 'Command' 'identifier'```",
                                 channel=message.channel)

        cmd = self.check_command_exist(cmd)
        if not cmd:
            return self.Response(response=f"Command '{cmd}' does not exist. Try ```{self.bot.wakeword}, what commands are there?```",
                                 channel=message.channel)

        if ident.lower().strip() not in cmd.identifiers:
            return self.Response(response=f"Identifier '{ident}' doesn't exist. Try "
                                          f"```{self.bot.wakeword} display all identifiers```",
                                 channel=message.channel)

        with open("cogs/util/data/identifiers.json", 'r+') as f:
            commands = json.load(f)

            tags = commands[cmd.name][ident.lower().strip()]
            all_tags = cog.get_tags(commands[cmd.name])

            for tag in tags:
                if all_tags.count(tag) == 1:
                    f.seek(0)
                    f.write(json.dumps(commands))
                    f.truncate()

                    return self.Response(
                        response=f"Cannot delete '{ident}' because each tag must have at least one identifier to it.",
                        channel=message.channel)

                if len(commands[cmd.name]) == 1:
                    return self.Response(
                        response=f"Cannot delete '{ident}' because it is the last remaining identifier for {cmd.name}.",
                        channel=message.channel)

            else:
                del commands[cmd.name][ident.lower().strip()]
                f.seek(0)
                f.write(json.dumps(commands))
                f.truncate()

            await cmd.refresh_identifiers()
            return self.Response(
                response=f"Identifier successfully deleted!",
                channel=message.channel)

    def check_command_exist(self, command):
        for cog in self.bot.cogs:
            if cog.name == command.title():
                return cog

        else:
            return False
