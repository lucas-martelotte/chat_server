from control import Control
import sys, os
import curses

#==============================================================#
#====================== Initializations =======================#
#==============================================================#

def initialize(stdscr):

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Creating the control and initializing it
    control = Control(stdscr)
    control.main_loop()

if __name__ == '__main__':
    curses.wrapper(initialize)