'''
Objects for testing
'''

class Dupe_Channel:
    def __init__(self, id):
        self.id = id

class Dupe_Message:
    def __init__(self, author, content, channel):
        self.author = author
        self.content = content
        self.channel = channel

class Dupe_User:
    def __init__(self, id, name):
        self.id = id
        self.name = name

dupe_user = Dupe_User('999999999999999999', 'Meow-meow-tester#9999')
dupe_channel = Dupe_Channel('000000000000000000')
dupe_message = Dupe_Message(dupe_user, 'Meow meow test content!', dupe_channel)
