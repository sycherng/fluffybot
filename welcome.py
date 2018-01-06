import discord, asyncio, random
import db, secrets
import user

async def respond(bot, message):
    #---messages that came in without prefix in front
    await submit_my_response(bot, message)


async def prefix_respond(bot, message):
    #---messages that came in with prefix in front (commands)
    await user_welcome(bot, message)
    await test_dw(bot, message)


class Welcome_Package:
    def __init__(self, referer, target, membertype, ign, ref_channel):
        self.referer = referer
        self.target = target
        self.membertype = membertype
        self.ign = ign
        self.ref_channel = ref_channel


welcome_dict = {} #dict {target_id -> Welcome Package
async def user_welcome(bot, message):
    #---call: user welcome <id> <membertype> <ign-first> <ign-last>
    if message.content.startswith('user welcome ') and message.channel.is_private == True:
        if db.rank_check(message.author.id, 'user welcome'):
            msg = message.content.split()[2:]
            referer = message.author
            target = discord.User(id=msg[0])
            membertype = msg[1]
            ign = msg[2]+ ' ' + msg[3]
            if membertype in ['social', 'raider', 'supplier']:
                if db.user_exists(target.id):
                    try: await bot.send_message(target, f'''Hello, **welcome to {secrets.group_name}**. I'd like to properly introduce you to our members with a "2 truths and a wish" minigame.\n\nPlease think of 2 statements that are true about yourself, and 1 statement you wish were true. Make sure they are statements you are comfortable with sharing with everyone!\n\nWhen you are ready to submit them, direct-message me with the command `{secrets.prefix}submit my response` to get started.''')
                    except: await bot.send_message(referer, "Error: User could not be contacted. Ensure they are in a shared server with me.")
                    else:
                        welcome_dict[target] = Welcome_Package(referer, target, membertype, ign, message.channel)
                        await bot.send_message(referer, """Welcome sequence initiated. Target will be asked for "2 truths and a wish" now. I will run it by you when they have supplied a response.""")
                else:
                    await bot.send_message(message.author, "Error: User does not exist in my database. Create user first.")
            else:
                await bot.send_message(message.author, "Error: Membertype must be social, raider, or supplier.")


welcome_queue = []
async def submit_my_response(bot, message):
    #---call: submit my response
    if message.content == ('submit my response')  and message.author in welcome_dict and message.channel.is_private == True:
        welcome_package = welcome_dict[message.author]
        welcome_dict.pop(welcome_package.target)
        #---take response
        welcome_package.submission, welcome_package.items = await take_response(bot, welcome_package.target)
        if await confirm_response(bot, welcome_package):
            if await approve_response(bot, welcome_package):
                welcome_queue.append(welcome_package)
                await deliver_welcome(bot)
            else:
                await bot.send_message(welcome_package.referer, f"The welcome sequence for user {welcome_package.ign} ({welcome_package.target.id}) has been aborted. Please speak to them personally and/or reinitiate as needed.")


async def take_response(bot, target):
    await bot.send_message(target, "Great! Let's start with the first true statement about yourself.")
    truth1 = await bot.wait_for_message(author=target)
    truth1 = truth1.content
    await bot.send_message(target, "What is the second true statement about yourself?")
    truth2 = await bot.wait_for_message(author=target)
    truth2 = truth2.content
    await bot.send_message(target, "What is the one statement you wish was true about yourself?")
    wish = await bot.wait_for_message(author=target)
    wish = wish.content
    submission = f"```Truth: {truth1}\nTruth: {truth2}\nWish: {wish}```"
    items = [truth1, truth2, wish]
    return submission, items


class Fake_channel:
    def __init__(self):
        self.is_private = True

class Fake_message:
    def __init__(self, author, content):
        self.author = author
        self.content = content
        self.channel = Fake_channel()


async def confirm_response(bot, welcome_package):
    submission = welcome_package.submission
    target = welcome_package.target
    await bot.send_message(target, f"These are the statements you've submitted:\n\n{submission}\n\nRespond with **S** to submit\nRespond with **R** to restart\nRespond with **Q** to quit and come back later")
    response = ''
    while response not in ['Q', 'q', 'R', 'r', 'S', 's']:
        response = await bot.wait_for_message(author=target)
        response = response.content
        if response in ['Q', 'q']:
            welcome_dict[target] = welcome_package
            await bot.send_message(target, "Okay, see you later.")
        elif response in ['R', 'r']:
            welcome_dict[target] = welcome_package
            fake_message = Fake_message(target, 'submit my response')
            await submit_my_response(bot, fake_message)
        elif response in ['S', 's']:
            await bot.send_message(target, "Your response was submitted. Thank you!")
            return True
        else:
            await bot.send_message(target, "Please respond with either Q, R, or S.")


async def approve_response(bot, welcome_package): 
    await bot.send_message(welcome_package.referer, f'''The user {welcome_package.ign}({welcome_package.target.id}) whom you signed up for a welcome sequence has submitted the following information for "2 truths and 1 wish":\n\n{welcome_package.submission}\n\n Respond with **A** or **a** to approve and any other response to abort the welcome sequence entirely.''')
    referer_response = await bot.wait_for_message(author=welcome_package.referer, channel=welcome_package.ref_channel)
    response = referer_response.content
    return response in ['a', 'A']

class Test_Dw:
    def __init__(self, target):
        self.items = ['meow', 'woof', 'grawr']
        self.membertype = 'social'
        self.ign = 'Meow Weow'
        self.target = target
        self.referer = target

async def test_dw(bot, message):
    if message.content == 'tdw':
        while welcome_queue:
            welcome_queue.pop()
        welcome_queue.append(Test_Dw(message.author))
        await deliver_welcome(bot)

wait = False
async def deliver_welcome(bot):
    while welcome_queue:
        if wait == False:
            wait == True
            welcome_package = welcome_queue.pop(0)
            welcome_package.winner = []
            arr = welcome_package.items
            wish = arr[2]
            random.shuffle(arr)
            answer = str(arr.index(wish) + 1)
            await bot.send_message(secrets.fcgeneral, f"""@everyone\t Please welcome our newest {welcome_package.membertype} member {welcome_package.ign} ({welcome_package.target})!\n\nHere are 2 facts about them and 1 thing they wish were true.\nThe first 5 members to correctly guess the "wish" will win 100 {secrets.currency_name} each.\n\n1) {arr[0]}\n2) {arr[1]}\n3) {arr[2]}""")
            winlist = welcome_package.winner
            while len(winlist) < 5:
                msg = await bot.wait_for_message(channel=secrets.fcgeneral, content=answer)
                if msg.author not in winlist:
                    winlist.append(msg.author.id)
            await bot.send_message(secrets.fcgeneral, f"""We have our winners! Thanks for your participation.""")
            for winner in winlist:
                await user.bot_alter_balance('+', 100, winner)
                try: await bot.send_message(discord.User(id=winner), f"Congrats! 100 {secrets.currency_name} have been deposited into your wallet. The correct answer was #{answer}: '{wish}'.")
                except: pass
            wait == False
