import discord, asyncio, datetime
import secrets

async def prefix_respond(bot, message):
    await bgtask_test(bot, message)
    await schedule_event(bot, message)
    await background_task_clock(bot, message)

async def respond(bot, message):
    pass

async def bgtask_test(bot, message):
    if message.content == 'bgtask_test':
        await bot.wait_until_ready()
        counter = 0
        channel = secrets.testingroom
        while not bot.is_closed:
            counter += 1
            await bot.send_message(channel, counter)
            await asyncio.sleep(5)

class Reminder:
    def __init__(self, trigger_time, who):
        self.trigger_time = trigger_time #--datetime object
        self.who = who #discord user object or list of discord user object

remind_dict = {hour: [] for hour in range(24)}

async def is_within(trigger_time, number_of_minutes, reference_time=datetime.datetime.now()):
    delta = datetime.timedelta(minutes = number_of_minutes)
    then = reference_time + delta
    return reference_time <= trigger_time and trigger_time < then  

async def schedule_event(bot, message):
    #-- call: schedule event year month day hour minute
    if message.content.startswith('schedule event'):
        msg = message.content.split()[2:]
        year = int(msg[0])
        month = int(msg[1])
        day = int(msg[2])
        hour = int(msg[3])
        minute = int(msg[4])
        trigger_time = datetime.datetime(year, month, day, hour, minute)
        print(trigger_time.hour, trigger_time.minute)
        reminder = Reminder(trigger_time, message.author)
        hour_list = remind_dict[hour]
        hour_list.append(reminder)
        await bot.send_message(message.author, f'Reminder set for {hour}:{minute}')

async def background_task_clock(bot, message):
    if message.content == 'start clock':
        await bot.wait_until_ready()
        while not bot.is_closed:
            print(f'bt clock')
            if remind_dict:
                print(True)
                now = datetime.datetime.now()
                print(now.hour)
                hour_list = remind_dict[now.hour]
                if hour_list:
                    print(True)
                    for reminder in hour_list:
                        if await is_within(reminder.trigger_time, 1, now): #set 1 minutes for testing
                            await bot.send_message(reminder.who, 'Your reminder was triggered!')
                else:
                    print(False)
            else:
                print(False)
            await asyncio.sleep(5)
