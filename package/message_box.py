# message_box.py

import curses
import time
import math

class MessageBox:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.active = False
        self.message = ""
        self.duration = 0
        self.start_time = 0
        self.jostle_angle = 0.0  # Initialize jostle_angle for smooth movement

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
            
            # Define message box dimensions
            width = len(self.message) + 4  # Padding of 2 on each side
            height = 5  # Fixed height
            
            # Define fixed text position (center of the screen)
            fixed_y = max_y // 2
            fixed_x = max_x // 2
            
            # Initialize jostle_angle if not already present
            if not hasattr(self, 'jostle_angle'):
                self.jostle_angle = 0.0  # Starting angle for jostling
            
            # Increment jostle_angle to create smooth movement
            self.jostle_angle += 0.05  # Adjust this value for speed of jostling
            
            # Calculate jostle offsets using sine and cosine for smooth, circular movement
            jostle_radius = 2  # Maximum offset in any direction
            jostle_x = int(math.sin(self.jostle_angle) * jostle_radius)
            jostle_y = int(math.cos(self.jostle_angle) * jostle_radius)
            
            # Calculate window start positions with jostle offsets
            start_y = fixed_y - (height // 2) + jostle_y
            start_x = fixed_x - (width // 2) + jostle_x
            
            # Ensure the window stays within the screen boundaries
            start_y = max(0, min(start_y, max_y - height))
            start_x = max(0, min(start_x, max_x - width))
            
            # Create a new window with the calculated positions
            win = curses.newwin(height, width, start_y, start_x)
            
            # Set the background color (using color pair 0 for default)
            win.bkgd(' ', curses.color_pair(0))
            
            # Clear the window content
            win.erase()
            
            # Draw the window border
            win.border()
            
            try:
                # Add the message text at a fixed position within the window
                # Position (2, 2) centers the text vertically and horizontally within the window
                win.addstr(2, 2, self.message)
            except curses.error:
                pass  # Ignore errors if the message is too long to fit
            
            # Refresh the window to display changes
            win.refresh()
