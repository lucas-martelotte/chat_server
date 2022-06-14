class StringBuffer():
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.lines = ['' for i in range(height)]

    def clear(self):
        self.lines = ['' for i in range(self.height)]

    def append(self, line):
        parts = []
        for i in range(0, len(line), self.width-1):
            parts.append(line[i:min(i+self.width-1,len(line))])

        for part in parts:
            del self.lines[0]
            self.lines.append(part)

    def render(self, stdscr):
        for i in range(self.y, self.height, 1):
            stdscr.addstr(i, self.x, self.lines[i])
