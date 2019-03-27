import sys
import subprocess
import json
import random as rand


def install_reqs():
    interpreter = sys.executable
    
    if interpreter is None:
        print("Fatal error: cannot find Python interpreter.")
        sys.exit(1)
    
    print("Updating pip...")
    succ = subprocess.call([interpreter, '-m', 'pip', 'install', '--upgrade', 'pip'])
    
    if succ == 0:
        print("\nPip was successfully updated.\n")
    else:
        print("\nAn error occured while updating pip. This shouldn't be a big problem.\n")
    
    print("Downloading requirements")
    succ = subprocess.call([interpreter, '-m', 'pip', 'install', '--upgrade', '-r', 'requirements.txt'])
    
    if succ == 0:
        print("\nRequirements successfully installed.\n")
    else:
        print("An error occured while installing the requirements."
              "Double check that you installed everything correctly as per the instructions on the github and try again.")
        sys.exit(1)


def create_settings():
    print("By default, the trigger word is 'Hey Tbot, ' (space included)\n"
          "So, for example, you might say 'Hey Tbot, tell me a joke!'\n"
          "You can change this to be anything, such as '!Tbot ' or 'Yo Tbot! ' or simply '! '\n"
          "Leave it blank to use the default. You can make it case sensitive/insensitive later, "
          "and change the triggerword entirely as a bot command after setup.\n")
    
    confirm = 'N'
    while confirm in ['n', 'N']:
        wakeword = input("Please input a wakeword: ")
        if wakeword.strip() == '':
            wakeword = 'Hey Tbot, '
            
        case_sensitive = None
        while case_sensitive not in ['y', 'n', 'yes', 'no']:
            case_sensitive = input('Do you want this to be casesensitive? (Y/N): ').lower()
        
        if case_sensitive in ['y', 'yes']:
            case_sensitive = True
        else:
            case_sensitive = False
        
        print(f"Wakeword: '{wakeword}'\nCase Sensitive: {case_sensitive}")
        print(f"Do these commands look like what you want/are possible: \n")
        if case_sensitive:
            print(f"\t{wakeword}tell me a joke!")
            print(f"\t{wakeword}what rhymes with lizard?")
            print("\nThe following commands would not be valid: ")
            
            if wakeword.lower() != wakeword:
                print(f"\t{wakeword.lower()}tell me a joke!")
            if wakeword.title() != wakeword:
                print(f"\t{wakeword.title()}what rhymes with lizard?")
            if wakeword.upper() != wakeword:
                print(f"\t{wakeword.upper()}what's a synonym for cool?")
        else:
            print(f"\t{wakeword}what's up?")
            print(f"\t{wakeword.lower()}tell me a joke!")
            print(f"\t{''.join(rand.choice([char.upper(), char]) for char in wakeword.lower())}what rhymes with lizard?")
            print(f"\t{wakeword.upper()}what's a synonym for cool?")
        
        cont = None
        while cont not in ['y', 'n', 'yes', 'no']:
            cont = input("\nLook good? (Y/N): ").lower()
        confirm = cont
    
    print("TBot has several auto-task functions, which will automatically send messages in various intervals.\n"
          "For example, TBot has an emote report that will be sent every week and displays the popularity of "
          "various emotes.\nPlease input a channel ID to designate as the 'default channel' for TBot to post in "
          "(either for auto-tasks or for large posts.\n Input nothing and TBot will use the default channel on the "
          "server. To grab the channel ID, right click a channel in the discord client and click 'copy id.'")
    default_channel = "."
    while not default_channel.isdigit():
        default_channel = input("Please input a valid (numerical) channel id: ").strip()
        if default_channel == '':
            break

    token = None
    while token is None and token != '':
        token = input("\nAt the beginning of the setup instructions on github, you wrote down a token.\n"
                      "Please input that here: ")
    
    print("\nSaving all settings to cogs/util/data/settings.txt")
          
    with open('cogs/util/data/settings.txt', 'w') as f:
        settings = {'Wakeword': wakeword,
                    'CaseSensitive': case_sensitive,
                    'DefaultChannel': default_channel,
                    'Token': token}
        f.write(json.dumps(settings))


def fix_async():
    print('Fixing async issues in required libraries...\n')
    from inspect import getsourcefile
    import chardet

    path = getsourcefile(chardet)
    path = path[:path.rfind('\\chardet\\')] + '\\discord\\compat.py'
    print('Fixing discord/compat')
    with open(path, 'r') as f:
        lines = f.readlines()
        lines[31] = "    create_task = getattr(asyncio, 'async')\n"
    with open(path, 'w') as f:
        f.write(''.join(line for line in lines))

    path = path[:path.rfind('\\discord\\')] + '\\websockets\\compatibility.py'
    print('Fixing websockets/compatibility')
    with open(path, 'r') as f:
        lines = f.readlines()
        lines[8] = "    asyncio_ensure_future = getattr(asyncio, 'async')\n"
    with open(path, 'w') as f:
        f.write(''.join(line for line in lines))

    path = path[:path.rfind('\\websockets\\')] + '\\aiohttp\\helpers.py'
    print('Fixing aiohttp/helpers')
    with open(path, 'r') as f:
        lines = f.readlines()
        lines[24] = "    ensure_future = getattr(asyncio, 'async')\n"
    with open(path, 'w') as f:
        f.write(''.join(line for line in lines))
    print('\nFininished fixing compatibility.\n')


def main():
    interpreter = sys.executable
    
    if interpreter is None:
        print("Fatal Error: Cannot find Python interpreter")
        sys.exit(1)
    
    while True:
        try:
            succ = subprocess.call([interpreter, 'tbot.py'])

        except KeyboardInterrupt:
            succ = 0

        finally:
            break

    print(f"TBot has exited with exit code: {succ}.")
        

if __name__ == '__main__':
    print('======TBot Setup======\n' + '='*22, end='\n\n\n')
    print('Note, running this script will reset any current TBot settings. \n')
    cont = None
    while cont not in ['y', 'n', 'yes', 'no']:
        cont = input('Do you want to continue? (Y/N): ').lower()

    if cont in ['n', 'no']:
        sys.exit(0)

    if sys.version_info >= (3, 7):
        print(f"Your current Python version ({str(sys.version_info.major)}.{str(sys.version_info.minor)}) "
              f"is not fully compatible. TBot still uses the old version of discord.py which uses 3.6.\n"
              "This is okay, but you will have to make a few modifications to some of the required libraries "
              "for TBot to run. \nThis script can do this automatically, or you may create a virtual "
              "environment with an older Python version.", end='\n\n')
        edit = None
        while edit not in ['y', 'n', 'yes', 'no']:
            edit = input("Would you like to automatically edit the required libraries? (Y/N): ").lower()

        if edit in ['y', 'yes']:
            edit = True
        else:
            edit = False

    print('='*50 + '\n' + '='*50)

    print("Installing requirements...")
    install_reqs()
    input("Press any key to continue.")
    print('='*50 + '\n' + '='*50 + '\n')

    if edit:
        fix_async()
        input("Press any key to continue.")
        print('=' * 50 + '\n' + '=' * 50 + '\n')

    create_settings()
    input("Press any key to continue.")
    print('='*50 + '\n' + '='*50 + '\n')
    
    cont = None
    while cont not in ['y', 'n', 'yes', 'no']:
        cont = input("TBot setup has been complete. Would you like to launch the bot? (Y/N): ").lower()
    
    if cont in ['n', 'no']:
        print("You can launch TBot by typing into the command prompt 'python tbot.py'")
        sys.exit(0)
    
    else:
        print("Launching TBot!")
        main()
    
              

