import time
import curses


def main(stdscr):
    states = [0, 0, 0, 0, 0, 0]

    # Curses config
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_YELLOW)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_MAGENTA)

    stdscr.nodelay(True)

    # Write the title
    stdscr.addstr(0, 0, "RIT FIRST ImagineRIT FMS Debug Screen")

    while True:
        # Read data from the file
        f = open("data/debug.dat", "r")
        for i, line in enumerate(f):
            if i <= 5:
                states[i] = int(line)
        f.close()

        # Put data on the screen
        for i, s in enumerate(states):
            stdscr.addstr(i + 2, 0, " [")
            stdscr.addstr("  " if s == 1 or s == 2 else "--", curses.color_pair(s + 1))
            stdscr.addstr("]")
            stdscr.addstr(" Robot " + str(i))

            if s == 1:
                stdscr.addstr("    (enabled)    ")
            elif s == 2:
                stdscr.addstr("    (disabled)   ")
            elif s == 3:
                stdscr.addstr("    (e-stop)     ")
            else:
                stdscr.addstr("    (error)      ")
        # Push to the screen
        stdscr.addstr("\n")
        stdscr.refresh()

        # Check for an escape
        if stdscr.getch() == ord('q'):
            break
        else:
            time.sleep(.5)


if __name__ == "__main__":
    curses.wrapper(main)
