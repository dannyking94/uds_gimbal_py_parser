import curses
from curses import wrapper

def main(stdscr):
    stdscr.clear()
    stdscr.addstr(10, 20, "Hi")
    stdscr.refresh()
    stdscr.getch() #wait for key input
    pass


if __name__ == '__main__':
    wrapper(main)
