

import random

# Return a string that's a funny or quippy phrase that would happen when you run into a wall
def get_wall_message():
    messages = [
        "Well, that escalated quickly!",
        "Whoopsie daisy!",
        "That's a wall, not a door!",
        "Back off, buddy!",
        "You can't go that way.",
        "That's a brick wall!",
        "Watch where you're going!",
        "Oof! That was a solid hit.",
        "Oops! Didn't see that coming.",
        "Well, that was unexpected.",
        "Yikes! You're stuck.",
        "Oh no! Trapped by a wall.",
        "Guess that's a no-go.",
        "Nope! Can't pass.",
        "That's one stubborn wall.",
        "Heads up! Wall ahead.",
        "Whoa! That wall's not budging.",
        "Halt! There's no path here.",
        "My circuits! That's a wall.",
        "Zounds! A barrier appears.",
    ]
    return random.choice(messages)
