import discord
import random
game_channel = discord.Object(id = '312489882562068480')
empty_slot = ':black_medium_small_square:'
global gd #global dictionary
gd = {}
linebreak = '\n--------------------------------------------------'
'''
spawn 4 rooms in that 0, 1, 2, and 3
room1 = room[1]
room2 = room[2]
room3 = room[3]
'''
room = []
for i in range(4):
    room.append(list())

height = 6
width = 7

class Connect4:
    def __init__(self, bot, room_num, room_occupants):
        self.room_num = room_num
        self.participants = room_occupants
        spread = self.whogoesfirst(room_occupants) #no self needed if variable wont need to be available outside of initializing
        self.p1 = spread[0]
        self.p2 = spread[1]
        self.current_turn = self.p1 
        self.p1tile = ':small_orange_diamond:'
        self.p2tile = ':small_blue_diamond:'
        self.board = self.make_board()

    def whogoesfirst(self, room_occupants):
        rng = random.randrange(0, 2)
        p1 = room_occupants[rng]
        if p1 == room_occupants[0]:
                p2 = room_occupants[1]
        else:
                p2 = room_occupants[0]
        return (p1, p2)

    def make_board(self):
        height = 6
        width = 7
        board = []
        l0 = [empty_slot]*height  #equiv to for num in range (height):  \n  l0.append("0")
        for num in range(width):
                board.append(list(l0))
        return board

    async def print_board(self, bot):
        fmboard = []
        x = 0
        y = 5
        for n in range(6):
            for m in range(7):
                fmboard.append(self.board[x][y])
                x += 1
            x = 0
            fmboard.append("\n")
            y -= 1
        fmboard = "|".join(fmboard)
        fmboard = "|" + fmboard
        fmboard = fmboard + '|:regional_indicator_a:|:regional_indicator_b:|:regional_indicator_c:|:regional_indicator_d:|:regional_indicator_e:|:regional_indicator_f:|:regional_indicator_g:|' + linebreak
        await bot.send_message(game_channel, 'Room ' + self.room_num + '\n' + fmboard)

    def whose_turn(self):
        return self.current_turn
        
    def swap_turn(self):
        if self.whose_turn() == self.p1:
            self.current_turn = self.p2
        else:
            self.current_turn = self.p1

    async def placetile(self, bot, author, col, room_num):
        d1 = {}
        d1["A"] = self.board[0]
        d1["B"] = self.board[1]
        d1["C"] = self.board[2]
        d1["D"] = self.board[3]
        d1["E"] = self.board[4]
        d1["F"] = self.board[5]
        d1["G"] = self.board[6]
        d2 = {}
        d2["A"] = 0
        d2["B"] = 1
        d2["C"] = 2
        d2["D"] = 3
        d2["E"] = 4
        d2["F"] = 5
        d2["G"] = 6
        if self.whose_turn() == str(author):
            if str(author) == self.p1:
                tile = self.p1tile
            else:
                tile = self.p2tile
            if empty_slot not in d1[col]:
                await bot.send_message(game_channel, "Column " + col + " is full in room " + room_num + '.')
            else:
                emptysocket = d1[col].index(empty_slot)
                d1[col][emptysocket] = tile
                x = d2[col] #take column as a number
                y = emptysocket
                return (x, y, tile)
        else:
            await bot.send_message(author, "It isn't your turn yet in room " + room_num + '.')

    def hwin(self, t, x, y):
        counter = 0
        for i in range(width):
            if self.board[i][y] == t:
                counter +=1
                if counter == 4:
                    return True
            else:
                counter = 0    

    def vwin(self, t, x, y):
        counter = 0
        for i in range(height):
            if self.board[x][i] == t:
                counter +=1
                if counter == 4:
                    return True
            else:
                counter = 0

    def fwin(self, t, x, y):
        print(x,y)
        while x > 0 and y > 0:
            x -= 1
            y -= 1
        counter = ''
        print(x, y)
        while (x < width) and (y < height):
            counter += self.board[x][y]
            x += 1
            y += 1
        print(counter)
        if (t+t+t+t) in counter:
            print('4')
            return True

    def bwin(self, t, x, y):
        print(x,y)
        while (x < (width-1)) and (y > 0):
            x += 1
            y -= 1
        counter = ''
        print(x, y)
        while x >= 0 and y < height:
            counter += self.board[x][y]
            x -= 1
            y += 1
        print(counter)
        if (t+t+t+t) in counter:
            print('4')
            return True

    def anyvictor(self, tile, x, y):         #should return True or False after computations
        if self.hwin(tile, x, y) or self.vwin(tile, x, y) or self.fwin(tile, x, y) or self.bwin(tile, x, y):
            return True
        else:
            return False
    
async def respond(bot, message):
    if message.content.startswith('!c4join'): #c4join room 1
        await join_room(bot, message)
    if message.content.startswith('!c4add'): #c4add 1 G
        await placetile_manager(bot, message)

async def join_room(bot, message):
    msg = message.content
    msg = msg.split()
    valid_num = ['1', '2', '3']
    if (len(msg) ==3) and (msg[0] == '!c4join') and (msg[1] == 'room') and (msg[2] in valid_num):
            room_num = msg[2]
            room_occupants = (room[int(room_num)])
            if str(message.author) in room_occupants: #if requester is already in room
                await bot.send_message(message.author, 'You are already in Room ' + room_num + '.') #bot DMs and informs of same
            if str(message.author) not in room_occupants:
                if len(room_occupants) < 2:
                        room_occupants.append(str(message.author)) #join room
                        print(room_occupants)
                        await bot.send_message(message.channel, str(message.author) + ' has joined Room ' + room_num + '.')
                        if len(room_occupants) == 2:  #when a room is full, a game should start
                            #print("game started")
                            await start_game(bot, room_num, room_occupants)
                elif len(room_occupants) == 2:
                    await bot.send_message(message.channel, 'Room ' + room_num + ' is full.')
                    print(room_occupants)            
    else:
        await bot.send_message(message.author, ':dango: Format must be **!c4join room 1** between rooms 1-3')
        await bot.send_message(message.channel, 'Bad room join request from ' + str(message.author))        
    

async def start_game(bot, room_num, room_occupants):
    gd[room_num] = Connect4(bot, room_num, room_occupants)
    await bot.send_message(game_channel, 'Game in room ' + room_num + ' started between ' + gd[room_num].p1 + '(' + gd[room_num].p1tile + ') and ' + gd[room_num].p2 + '(' + gd[room_num].p2tile + ').' + linebreak)
    await bot.send_message(discord.Object(id = '226155730292572170'), 'A match of **Connect 4** between ' + gd[room_num].p1 + ' and ' + gd[room_num].p2 + ' has started in the bot-minigame channel.')
    await manager(bot, room_num)

async def manager(bot, room_num):
    await gd[room_num].print_board(bot)
    if gd[room_num].whose_turn() == gd[room_num].p1:
        tile = gd[room_num].p1tile
    else:
        tile = gd[room_num].p2tile
    #print('room_num:' + str(room_num))
    #print('gd.keys():' + str(gd.keys()))
    await bot.send_message(game_channel, gd[room_num].whose_turn() + '(' + tile + ')' + "'s turn in room " + room_num + '.' + linebreak)
    
async def placetile_manager(bot, message):
        msg = message.content.split() #message str -> msg list
        valid_num = ['1', '2', '3']
        valid_letter = ['A', 'B', 'C', 'D', 'E', 'F', 'G']     
        if (len(" ".join(msg)) == 10) and (msg[1] in valid_num) and (msg[2] in valid_letter):
            col = msg[2]
            room_num = msg[1]   
            if len(room[int(room_num)]) == 2:
                result = await gd[room_num].placetile(bot, message.author, col, room_num)
                if result:
                    anyvictor = gd[room_num].anyvictor(result[2], result[0], result[1])
                    if anyvictor:
                        await end_game(bot, room_num)
                    else:
                        gd[room_num].swap_turn()
                        await manager(bot, room_num)
            else:
                await bot.send_message(game_channel, "Badrequest: No game in session (Room " + room_num + ").")
        else:
            await bot.send_message(message.author, ':dango: Format must be **!c4select A** between A-G')      

async def end_game(bot, room_num):
    await gd[room_num].print_board(bot)
    victor = gd[room_num].whose_turn()
    await bot.send_message(game_channel, "**Victory!** :white_flower:\n" + victor + "\nwins in room " + room_num + '.' + linebreak)
    room[int(room_num)] = []
    gd[room_num] = None
