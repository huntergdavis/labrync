# message_box.py

import curses
import time

class MessageBox:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.active = False
        self.message = ""
        self.duration = 0
        self.start_time = 0

    def show(self, message, duration=1.0):
        self.message = message
        self.duration = duration
        self.start_time = time.time()
        self.active = True

    def update(self):
        if self.active:
            current_time = time.time()
            if current_time - self.start_time >= self.duration:
                self.active = False

    def render(self):
        if self.active:
            # Get screen size
            max_y, max_x = self.stdscr.getmaxyx()
            # Create a window for the message box
            width = len(self.message) + 4
            height = 5
            start_x = (max_x - width) // 2
            start_y = (max_y - height) // 2
            win = curses.newwin(height, width, start_y, start_x)
            win.bkgd(' ', curses.color_pair(0))
            win.erase()
            win.border()
            win.addstr(2, 2, self.message)
            win.refresh()
