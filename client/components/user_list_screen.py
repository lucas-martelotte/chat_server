import curses

class UserListScreen():

    STATE_OFFLINE = 0
    STATE_ONLINE = 1
    STATE_NEW_MESSAGE = 2

    def __init__(self, x, y, width, height, userlist = [], padding = 3):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.userlist = userlist
        self.padding = padding

    def set_user_list(self, userlist):
        self.userlist = userlist

    def render(self, stdscr, message_dict):
        for i in range(min(self.height, len(self.userlist))):
            username = self.userlist[i]

            n_messages = 0
            if username in message_dict:
                n_messages = message_dict[username].qsize()

            if n_messages > 0:
                stdscr.addstr(i+self.y, self.x, ' '*self.padding +\
                    str(self.userlist[i]) + ' (' + str(n_messages) + ')')
            else:
                stdscr.addstr(i+self.y, self.x, ' '*self.padding  + str(self.userlist[i]))
