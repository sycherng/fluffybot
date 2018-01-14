import discord, asyncio, random
import async_db as db, secrets
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
    #jump - allow an alternate version "user welcome no game" that just sends a welcome message to the fc channel


    #---call: user welcome <id> <membertype> <ign-first> <ign-last>
    if message.content.startswith('user welcome ') and message.channel.is_private == True:
        if db.user_has_permission(message.author.id, 'user welcome'):
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
    '''|user|
    (Bot object, Message object) -> None

    Command: submit my response

    Checks: message author in welcome_dict and calling from private channel
    Action:
    '''
    command_opener = 'submit my response'
    #--- checks
    if not message.content == command_opener: return
    if not message.author in welcome_dict:
        await bot.send_message(message.author, secrets.low_rank_msg)
        return
    if not message.channel.is_private == True:
        await bot.send_message(message.author, 'This command must be called in a private message between bot and user (Direct Message).')
        return

    target = message.author
    #--- pop user's package from welcome_dict
    welcome_package = welcome_dict.pop(target)
    replies = await take_response(bot, welcome_package.target)
    if not replies:
        await bot.send_message(message.author, secrets.timeout_msg)
        return
    welcome_package.replies = replies
    welcome_package.submission = f"```Truth: {replies[0]}\nTruth: {replies[1]}\nWish: {replies[2]}```"

    if not await confirm_response(bot, welcome_package): return

    await approve_response(bot, welcome_package)


async def take_response(bot, target):
    '''|bot|
    (Bot object, discord.User object) -> (list of str)

    Invoker: submit_my_response() checks: user is target of welcome sequence
    Checks: None
    Action: -attempts to collect 2 truths and 1 wish from target user, if all 3 successfully collected
    returns a list containing a string for each response. If unsuccessful returns None.
    '''
    await bot.send_message(target, "Great! Let's start with the first true statement about yourself.")
    truth1 = await bot.wait_for_message(author=target, timeout = 30)
    if not truth1: return
    truth1 = truth1.content

    await bot.send_message(target, "What is the second true statement about yourself?")
    truth2 = await bot.wait_for_message(author=target, timeout = 30)
    if not truth2: return
    truth2 = truth2.content

    await bot.send_message(target, "What is the one statement you wish was true about yourself?")
    wish = await bot.wait_for_message(author=target)
    if not wish: return
    wish = wish.content

    return [truth1, truth2, wish]


class Placeholder_Channel:
    def __init__(self):
        self.is_private = True

class Placeholder_Message:
    def __init__(self, author, content):
        self.author = author
        self.content = content
        self.channel = Placeholder_Channel()


async def confirm_response(bot, welcome_package):
    '''|bot|
    (Bot object, Welcome_Package object) -> bool
    
    Evoker: submit_my_response()

    Action: 
    -shows user their responses to confirm whether they are happy with it.
    -if user asks to quit, puts user's package back in welcome_dict
    -if user asks to restart, calls submit_my_response() for them
    -if user asks to submit, returns True to evoker.
    -provides message confirming user's choice.
    '''
    submission = welcome_package.submission
    target = welcome_package.target
    await bot.send_message(target, f"These are the statements you've submitted:\n\n{submission}\n\nRespond with **S** to submit\nRespond with **R** to restart\nRespond with **Q** to quit and come back later")

    def check(msg):
        return (msg.content in ['Q', 'q', 'R', 'r', 'S', 's'])

    response = await bot.wait_for_message(author=target, check=check, timeout=30)
    if not response: 
        await bot.send_message(target, secrets.timeout_msg)
        return False
    response = response.content

    #if quitting, put target's package back in welcome_dict
    if response in ['Q', 'q']:
        welcome_dict[target] = welcome_package
        await bot.send_message(target, "Okay, see you later.")
        return False

    #if restarting, call submit_my_response for them
    elif response in ['R', 'r']:
        welcome_dict[target] = welcome_package
        placeholder_message = Placeholder_Message(target, 'submit my response')
        await submit_my_response(bot, placeholder_message)
        return False

    #if submitting, return True
    elif response in ['S', 's']:
        await bot.send_message(target, "Your response was submitted. Thank you!")
        return True


temp_ar_dict = {}
async def approve_response(bot, welcome_package):
    '''|bot|
    (Bot object, Welcome_Package Object) -> bool

    Evoker: submit_my_response()

    Action:
    -given a welcome package, seeks approval from referer regarding target's submission.
    ''' 
    wp = welcome_package
    records_list= await db.fetch(f"SELECT * FROM user_objects WHERE id = $1", wp.target.id) 
    target_nickname = records_list[0]['nickname']

    await bot.send_message(wp.referer, f"Dear admin:\n\nThe user {target_nickname} (id={wp.target.id}) you referred for a welcome message and minigame has submitted their response for the welcome minigame. This is a final screen for approval before the minigame goes forth. If you disapprove, the entire welcome package and their current submission will be cancelled. If this occurs, you will have to discuss with them personally to explain your decision. To approve the following submission reply 'approve', to disapprove reply 'disapprove'.\n\n{wp.submission}")

    def ar_check(msg):
        return msg.content in ['approve', 'disapprove']

    reply = await bot.wait_for_message(author=wp.referer, channel=wp.ref_channel, check = ar_check, timeout=30)

    if not reply:
        await bot.send_message(wp.referer, f"It seems you aren't there. Feel free to call me with `{secrets.prefix}approve welcome <target_id>` at a later time to approve.")
        temp_ar_dict[wp.target.id]
        return
    elif reply.content == 'disapprove':
        await bot.send_message(wp.referer, f"Welcome message, minigame, and user's submission for {target_nickname} cancelled.")
    else reply.content == 'approve':
        welcome_queue.append(wp)
        await deliver_welcome(bot)

async def belated_approve_response(bot, message):
    '''|user|

    Command: <prefix>approve welcome <target_id>

    Action: if target_id in temp approve response dict, allows belated approving of related welcome package.
    '''
    #jump allow append to temp queue if no reply in 30 seconds

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
            arr = welcome_package.replies
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
