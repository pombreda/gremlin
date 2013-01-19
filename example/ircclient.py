import gc


class BaseModel(object):
    def get_layout(self):
        pass

class BaseArgModel(BaseModel):
    def __init__(self, argname, title, validator = None, default = NotImplemented):
        self.argname = argname
        self.title = title
        self.validator = validator
        self.default = default

class StrArgModel(BaseArgModel):
    def get_layout(self):
        return InputNode()

class PasswordArgModel(StrArgModel):
    pass
class IntArgModel(BaseArgModel):
    def __init__(self, argname, title, min_val = None, max_val = None, validator = None, default = NotImplemented):
        pass

class BasePropertyModel(BaseModel):
    pass
class ListPropertyModel(BasePropertyModel):
    pass

class _FuncModel(BaseModel):
    def __init__(self, func, args):
        self.func = func
        self.args = args
    def __get__(self, inst, cls):
        return self.func.__get__(inst, cls)

def FuncModel(*args, **kwargs):
    def deco(func):
        return _FuncModel(func, *args, **kwargs)
    return deco


class IRCClient(object):
    history = ListPropertyModel("Session")
    room_members = ListPropertyModel("Members")
    all_rooms = ListPropertyModel("Rooms")

    @FuncModel(
        StrArgModel("host", "Host", default = "chat.freenode.net"), 
        IntArgModel("port", "Port", default = 6667, min_val = 1, max_val = 65535), 
        StrArgModel("nickname", "Nickname"),
        PasswordArgModel("password", "Password", required = False),
    )
    def __init__(self, host, port, nickname, password):
        self.conn = irclib.Connection(host, port, nickname, password)
        self.history = []
        self.room_members = []
        self.all_rooms = []
        self.conn.on_message(self._on_message)
        self.conn.list_rooms(when_done = lambda rooms: self.all_rooms.extend(rooms))
        self.room_members.extend()
    
    def _on_message(self, msg):
        if msg.type == "join":
            self.room_members.append(msg.text)
        elif msg.type == "leave":
            self.room_members.remove(msg.text)
        else:
            self.history.append(msg.text)
    
    @FuncModel(StrArgModel("msg", "Message"), text = ">>")
    def send(self, msg):
        self.conn.send(msg)
    
    @room_members.on_select
    def begin_private_chat(self, membername):
        self.conn.join_member(membername)
    
    @all_rooms.on_select
    def join_room(self, roomname):
        self.conn.join(roomname)
        self.conn.list_members(roomname, 
            when_done = lambda members: self.room_members.extend(members))
    
    def get_layout(self):
        chat_area = (self.history
                     ------------ 
                     self.send.X(None, 30))
        info_area = (self.all_rooms
                     --------------
                     self.room_members).X(200, None)
        return chat_area | info_area

run(IRCClient)




