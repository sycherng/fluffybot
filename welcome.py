import db, secrets, asyncio, discord, random

async def respond(bot, message):
    await user_welcome(bot, message)
    await submit_my_response(bot, message)

welcome_list = {} #dict {target_id -> Welcome Package

class Welcome_Package:
    def __init__(self, referer, target, membertype, ign):
        self.referer = referer
        self.target = target
        self.membertype = membertype
        self.ign = ign

async def user_welcome(bot, message):
    #---call: user welcome <id> <membertype> <ign-first> <ign-last>
    if message.content.startswith('user welcome '):
        if db.rank_check(message.author.id, 'user welcome'):
            msg = message.content.split()[2:]
            target = msg[0]
            membertype = msg[1]
            ign = msg[2]+msg[3]
            if membertype in ['social', 'raider', 'supplier']:
                if db.user_exists(target):
                    try: await bot.send_message(discord.User(id = target), f'''Hello, welcome to {secrets.group_name}. I'd like to properly introduce you to our members with a "2 truths and a wish" minigame. Please think of 2 statements that are true about yourself, and 1 statement you wish were true. Make sure they are statements you are comfortable with sharing with everyone! When you are ready to submit them, direct-message me with the command `{secrets.prefix}submit my response` to get started.''')
                    except: await bot.send_message(message.author, "Error: User could not be contacted. Ensure they are in a shared server with me.")
                    bundle = (message.author, membertype, ign, [])
                    welcome_list[target] = bundle
                else:
                    await bot.send_message(message.author, "Error: User does not exist in my database. Create user first.")
            else:
                await bot.send_message(message.author, "Error: Membertype must be social, raider, or supplier.")

async def submit_my_response(bot, message):
    #---call: submit my response
    if message.content == ('submit my response') and message.author.id in welcome_list and message.channel.is_private == True:
        bundle = welcome_list[message.author.id]
        target = message.author
        welcome_list.pop(target)
        #---take response
        submission = await take_response(target)
        target_approval = await confirm_response(target, submission, bundle)
        #unpack bundle
        referer, membertype, ign, winner_list = bundle
 
               await bot.send_message(referer, f'''The user {message.author.id} whom you signed up for a welcome sequence has submitted the following information for "2 truths and 1 wish":\n{submission}\n Respond with **A** or **a** to approve and any other response to abort the welcome sequence.''')
                referer_response = bot.wait_for_message(author=referer)
                if referer_response in ['a', 'A']:
                    mixed = random.shuffle([truth1, truth2, wish])
                    await bot.send_message(secrets.fcgeneral, f"""@everyone\t Please welcome our newest {bundle[1]} member {bundle[2]} ({message.author})! Here are 2 facts about them and 1 thing they wish were true. The first 5 members to correctly guess the "wish" will win 100 {secrets.currency_name} each.""")
            else:
                await bot.send_message(message.author, "Please respond with **S**, **R**, or **Q**.")

async def take_response(target):
    await bot.send_message(target, "Great! Let's start with the first true statement about yourself.")
    truth1 = await bot.wait_for_message(author=message.author)
    await bot.send_message(target, "What is the second true statement about yourself?")
    truth2 = await bot.wait_for_message(author=message.author)
    await bot.send_message(message.author, "What is the one statement you wish was true about yourself?")
    wish = await bot.wait_for_message(author=message.author)
    submission = f"```Truth: {truth1}\nTruth: {truth2}\nWish: {wish}```"
    return submission

async def confirm_response(target, submission):
    await bot.send_message(target, f"These are the statements you've submitted:\n\n{submission}\n\n Respond with **S** to submit\nRespond with **R** to restart\nRespond with **Q** to quit and come back later with the `=submit my response` command")
    response = ''
    while response not in ['Q', 'q', 'R', 'r', 'S', 's']:
        response = await bot.wait_for_message(author=target)
        if response in ['Q', 'q']:
            welcome_list[message.author.id] = bundle
            await bot.send_message(message.author, "Okay, see you later.")
        elif response in ['R', 'r']:
            await submit_my_response(bot, message)
        elif response in ['S', 's']:
            await bot.send_message(message.author, "Your response was submitted. Thank you!")

async def approve_response():
async def send_welcome():
async def claim_prize():
