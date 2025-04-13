from tkinter import Tk, BOTH, Canvas
import time
import random
import sys

############### Window #####################
class Window:
    def __init__(self, height, width):
        self.__root = Tk()
        self.__root.title = "title"

        self.__canvas = Canvas(self.__root, bg = "black", height = height, width = width)
        self.__canvas.pack(fill = BOTH, expand = 1)

        self.__running = False
        self.__root.protocol("WM_DELETE_WINDOW", self.close)

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self):
        self.__running = True
        while self.__running == True:
            self.redraw()

    def close(self):
        self.__running = False

    def draw_line(self, line, fill_color):
        line.draw(self.__canvas, fill_color)

################# POINT ######################
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

################# LinE ################
class Line:
    def __init__(self, point_a, point_b):
        self.point_a = point_a
        self.point_b = point_b

    def draw(self, canvas, fill_color):
        canvas.create_line(self.point_a.x, self.point_a.y, 
                           self.point_b.x, self.point_b.y, 
                           fill = fill_color, width = 2)


########################### CELL ################
class Cell:
    def __init__(self, point_top_left, point_bottom_right, 
                 window = None, fill_color = "white", visited = False):
        # booleans True if wall exists, False if not
        self.left_wall_bool = True
        self.right_wall_bool = True
        self.top_wall_bool = True
        self.bottom_wall_bool = True
        # just going to use the top_left and bottom_right points.  can access the points x and y with .x and .y
        # x/y coordinates of topleft of cell and bottom right + access to window
        self._point_tl = point_top_left
        self._point_bl = Point(point_top_left.x, point_bottom_right.y)
        self._point_br = point_bottom_right
        self._point_tr = Point(point_bottom_right.x, point_top_left.y)
        self._center = Point(self._point_tl.x + ((self._point_tr.x - self._point_tl.x)/2), 
                             self._point_tr.y + (self._point_br.y - self._point_tr.y)/2)

        self.visited = visited
        self._fill_color = fill_color
        self._window = window

    def draw(self):
        #drawing lines using points of cell.  top_right
        if self.left_wall_bool:
            self._window.draw_line(Line(self._point_tl, self._point_bl), self._fill_color)
        if self.right_wall_bool:
            self._window.draw_line(Line(self._point_tr, self._point_br), self._fill_color)
        if self.top_wall_bool:
            self._window.draw_line(Line(self._point_tr, self._point_tl), self._fill_color)
        if self.bottom_wall_bool:
            self._window.draw_line(Line(self._point_br, self._point_bl), self._fill_color)

    # if undo is False draw line in red otherwise draw in gray
    def draw_move(self, to_cell, undo = False):
        color = "red"
        if undo:
            color = "gray"
        line = Line(self._center, to_cell._center)
        self._window.draw_line(line, color)


############################ Maze #############################
class Maze:
    def __init__(self, maze_x, maze_y, num_cols, num_rows,
                cell_size_x, cell_size_y, window = None, seed = None):
        self._x = maze_x
        self._y = maze_y
        self._num_rows = num_rows
        self._num_cols = num_cols
        self._cell_size_x = cell_size_x
        self._cell_size_y = cell_size_y
        self._window = window
        if seed != None:
            self._seed = random.seed(seed)
        else:
            self._seed = random.seed()

        self._cells = []

    def _create_cells(self):
        for x in range (0, self._num_cols):
            column = []
            for y in range (0, self._num_rows):
                cell_top_left = Point(((x * self._cell_size_x) + self._x), 
                                ((y * self._cell_size_y) + self._y))
                cell_bottom_right = Point((((x + 1) * self._cell_size_x) + self._x), 
                                          (((y + 1) * self._cell_size_y) + self._y))
                column.append(Cell(cell_top_left, cell_bottom_right, self._window))
            self._cells.append(column)
        self._break_entrance_and_exit()

    def _draw_cells(self):
        for column in range (0, self._num_cols):
            for cell in range (0, self._num_rows):
                self._break_walls_r(column, cell)
                self._cells[column][cell].draw()
                self._animate()

    #sleep
    def _animate(self, sleep_time = 0):
        self._window.redraw()
        time.sleep(sleep_time)

    def _reset_cells_visited(self):
        for column in self._cells:
            for cell in column:
                cell.visited = False

    def _break_entrance_and_exit(self):
        self._cells[0][0].top_wall_bool = False
        self._cells[self._num_cols - 1][self._num_rows - 1].bottom_wall_bool = False

    def _break_walls_r(self, column, cell):
        self._cells[column][cell].visited = True
        while True:
            to_visit = []
            if column + 1 < self._num_cols and self._cells[column + 1][cell].visited == False:
                to_visit.append("right")
            if column > 0 and self._cells[column - 1][cell].visited == False:
                to_visit.append("left")
            if cell + 1 < self._num_rows and self._cells[column][cell + 1].visited == False:
                to_visit.append("bottom")
            if cell > 0 and self._cells[column][cell - 1].visited == False:
                to_visit.append("top")
            
            if to_visit == []:
                return
            else:
                direction = random.randrange(0, len(to_visit))
                if to_visit[direction] == "right":
                    self._cells[column + 1][cell].left_wall_bool = False
                    self._cells[column][cell].right_wall_bool = False
                    self._break_walls_r((column + 1), cell)
                elif to_visit[direction] == "left":
                    self._cells[column - 1][cell].right_wall_bool = False
                    self._cells[column][cell].left_wall_bool = False
                    self._break_walls_r((column - 1), cell)
                elif to_visit[direction] == "bottom": 
                    self._cells[column][cell + 1].top_wall_bool = False
                    self._cells[column][cell].bottom_wall_bool = False
                    self._break_walls_r(column, (cell + 1))
                elif to_visit[direction] == "top":
                    self._cells[column][cell - 1].bottom_wall_bool = False
                    self._cells[column][cell].top_wall_bool = False
                    self._break_walls_r(column, (cell - 1))
                
    def solve(self):
        self._reset_cells_visited()
        self._solve_r(0, 0)

    def _solve_r(self, column, cell):
        self._animate(0.02)
        self._cells[column][cell].visited = True
        if column == self._num_cols - 1 and cell == self._num_rows - 1:
            print("You made it to the end!")
            return True

        to_visit = []
        if (column + 1 < self._num_cols and self._cells[column + 1][cell].visited == False
            and self._cells[column][cell].right_wall_bool == False):
            to_visit.append("right")
        if (column > 0 and self._cells[column - 1][cell].visited == False
            and self._cells[column][cell].left_wall_bool == False):
            to_visit.append("left")
        if (cell + 1 < self._num_rows and self._cells[column][cell + 1].visited == False
            and self._cells[column][cell].bottom_wall_bool == False):
            to_visit.append("bottom")
        if (cell > 0 and self._cells[column][cell - 1].visited == False
            and self._cells[column][cell].top_wall_bool == False):
            to_visit.append("top")
        
        if to_visit == []:
            return False

        for direction in to_visit:
            origin = self._cells[column][cell]
            if direction == "right":
                origin.draw_move(self._cells[column + 1][cell])
                if self._solve_r(column + 1, cell):
                    return True
                else:
                    origin.draw_move(self._cells[column + 1][cell], True)
            
            elif direction == "left":
                origin.draw_move(self._cells[column - 1][cell])
                if self._solve_r(column - 1, cell):
                    return True
                else:
                    origin.draw_move(self._cells[column - 1][cell], True)
            
            elif direction == "bottom":
                origin.draw_move(self._cells[column][cell + 1])
                if self._solve_r(column, cell + 1):
                    return True
                else:
                    origin.draw_move(self._cells[column][cell + 1], True)
            
            elif direction == "top":
                origin.draw_move(self._cells[column][cell - 1])
                if self._solve_r(column, cell - 1):
                    return True
                else:
                    origin.draw_move(self._cells[column][cell - 1], True)
        return False

############################# MAIN ##########################
def main():
    sys.setrecursionlimit(2000)
    num_cols = 80
    num_rows = 40
    cell_width = 30
    cell_height = 30
    win_height = 200 + (num_rows * cell_height)
    win_width = 200 + (num_cols * cell_width)
    win = Window(win_height, win_width)
    
    maze = Maze(100, 100, num_cols, num_rows, cell_width, cell_height, win)
    maze._create_cells()
    maze._draw_cells()

    maze.solve()
    win.wait_for_close()

main() 
