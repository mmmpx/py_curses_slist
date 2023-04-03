import curses as cs


def addstr_safe(w, s, *args, break_ch = '…'):
    _, mx = w.getmaxyx()
    if len(s) < mx:
        w.addstr(s, *args)
    else:
        w.addnstr(s, mx - 1, *args)
        w.insstr(s[-1] if len(s) == mx else break_ch, *args)


class CS_ListS:

    def __init__(self, win, lines = [], break_ch = '…', selected = 0):
        self.win = win
        self.lines = lines
        self.break_ch = break_ch
        self.selected = selected
        self.start_y = selected

    def _draw_line(self, y):
        my, mx = self.win.getmaxyx()
        color = cs.A_NORMAL if y != self.selected else cs.A_REVERSE

        self.win.move(y - self.start_y, 0)
        addstr_safe(self.win, ' ' * mx, color)
        self.win.move(y - self.start_y, 0)

        line = self.lines[y]
        addstr_safe(self.win, line, color, break_ch = self.break_ch)

    def _select(self, inc):
        prev_y = self.selected
        self.selected = (self.selected + inc) % len(self.lines)
        if self.selected == prev_y: return

        my, _ = self.win.getmaxyx()
        if self.selected >= self.start_y + my:
            self.start_y = self.selected - my + 1
            self.draw()
        elif self.selected <= self.start_y - 1:
            self.start_y = self.selected
            self.draw()
        else:
            self._draw_line(prev_y)
            self._draw_line(self.selected)

    def draw(self):
        my, _ = self.win.getmaxyx()
        for y, l in enumerate(self.lines[self.start_y:self.start_y + my]):
            self._draw_line(y + self.start_y)

    def select_top(self):
        self._select(-self.selected)

    def select_bottom(self):
        self._select(len(self.lines) - self.selected - 1)

    def select_down(self):
        self._select(1)

    def select_pg_down(self):
        self._select(self.win.getmaxyx()[0])

    def select_up(self):
        self._select(-1)

    def select_pg_up(self):
        self._select(-self.win.getmaxyx()[0])


def main(stdscr):
    cs.curs_set(0)
    cs.use_default_colors()
    lines = [f'{i} unusually long line which may or may not be wrapped' for i in range(300)]
    sl = CS_ListS(stdscr, lines = lines)
    sl.draw()
    while True:
        ch = stdscr.getch()
        if ch == cs.KEY_RESIZE: sl.draw()
        elif ch in ( ord('j'), cs.KEY_DOWN ): sl.select_down()
        elif ch == cs.KEY_NPAGE: sl.select_pg_down()
        elif ch in ( ord('k'), cs.KEY_UP   ): sl.select_up()
        elif ch == cs.KEY_PPAGE: sl.select_pg_up()
        elif ch == ord('g'): sl.select_top()
        elif ch == ord('G'): sl.select_bottom()


if __name__ == '__main__':
    cs.wrapper(main)

