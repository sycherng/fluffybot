class Test_Channel:
    def __init__(self, id):
        self.id = id

class Test_Message:
    def __init__(self, author, content, channel):
        self.author = author
        self.content = content
        self.channel = channel

class Test_User:
    def __init__(self, id, name):
        self.id = id
        self.name = name

test_user = Test_User('999999999999999999', 'Meow-meow-tester#9999')
test_channel = Test_Channel('000000000000000000')
test_message = Test_Message(test_user, 'Meow meow test content!', test_channel)
