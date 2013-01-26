from irc.api import IRCClient
from models import ClassModel, FuncModel, StrArgModel, IntArgModel, PasswordArgModel


@ClassModel
class IRCClient(object):
    @FuncModel(
        server = StrArgModel("Server"),
        port = IntArgModel("Port"),
        nickname = StrArgModel("Nickname"),
        password = PasswordArgModel("Password", required = False),
    )
    def __init__(self, server, nickname, password, port = 6667):
        self.conn = None #IRCClient(server, port, nickname, password = password)


def run_model(model):
    pass

def main():
    inst = run_model(IRCClient)
    run_model(inst)


if __name__ == "__main__":
    main()

























