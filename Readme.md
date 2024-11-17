Welcome to labrync (like labrynth + ncurses)

A simple console screensaver to explore mazes in your terminal

Based on and extended from the command line C fps from 
onelonecoder
https://github.com/OneLoneCoder/CommandLineFPS


1. Maps are randomly generated
2. Maps can be auto-solved (screensaver mode, if you will) by passing -a to labrync.py
3. Colors are supported 
4. Player entering 'X' exit will regenerate the map and start fresh in top left corner
5. Breadcrumbs (or .. reverse breadcrumbs?  Crumpled grass?) To show where you've been.
6. Fog of War (or not) for additional challenge  

Usage: python labrync.py [options]

Options:


  -a : Auto-play the game

  -f : Show FPS

  -w : Disable fog of war

  -h : Display this help message   q : Quit the game (while playing)

