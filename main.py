import random
from collections import deque
from typing import List
import tkinter as tk

from config import *


class CityGrid:
    def __init__(self, N: int = None, M: int = None, blocks_percent: int = 30, city: List[List[int]] = None,
                 R: int = 2):
        if city is None:
            self.city = [[EMPTY for _ in range(M)] for __ in range(N)]

            blocks_count = M * N * blocks_percent // 100
            indices = set()
            while len(indices) < blocks_count:
                i = random.randint(0, N - 1)
                j = random.randint(0, M - 1)
                indices.add((i, j))
            for i, j in indices:
                self.city[i][j] = BLOCK
        else:
            self.city = [row.copy() for row in city]

        self.N = len(self.city)
        self.M = len(self.city[0])
        if R < 0:
            print("Неверный радиус")
            R = 3
        self.R = R

    def __get_neighbours(self, x: int, y: int, filter_: int = None):
        res = []
        for i in range(max(x - self.R, 0), min(x + self.R + 1, self.N)):
            for j in range(max(y - self.R, 0), min(y + self.R + 1, self.M)):
                if filter_ is None:
                    res.append((i, j, self.city[i][j]))
                else:
                    if self.city[i][j] == filter_:
                        res.append((i, j))
        return res

    def __check_coverage(self, x: int, y: int):
        if self.city[x][y] == BLOCK:
            return 0
        neighbours = self.__get_neighbours(x, y, filter_=EMPTY)
        return len(neighbours)

    def _get_all_towers(self):
        towers = []
        for i in range(self.N):
            for j in range(self.M):
                if self.city[i][j] == TOWER:
                    towers.append((i, j))
        return towers

    def _get_towers_adjacency_matrix(self):
        towers = self._get_all_towers()
        if not towers:
            print("There is no towers")
            return
        adjacency_matrix = [[0 for _ in range(len(towers))] for __ in range(len(towers))]
        for i, tower in enumerate(towers):
            towers_neighbours = self.__get_neighbours(*tower, filter_=TOWER)
            for neighbour in towers_neighbours:
                if tower != neighbour:
                    adjacency_matrix[i][towers.index(neighbour)] = 1
        return adjacency_matrix

    def add_tower(self, i: int, j: int):
        if not 0 <= i < self.N or not 0 <= j < self.M:
            print("Incorrect index")
            return
        if self.city[i][j] in (BLOCK, TOWER):
            print("It's not possible to place in this cell")
            return

        self.city[i][j] = TOWER

        neighbours = self.__get_neighbours(i, j, filter_=EMPTY)
        for neighbour in neighbours:
            self.city[neighbour[0]][neighbour[1]] = COVERAGE

    def add_effective_towers(self):
        empty_cells = [(i, j) for i in range(self.N) for j in range(self.M) if self.city[i][j] == EMPTY]
        covered_cells = []

        towers_count = 0
        while empty_cells:
            if towers_count == 0:
                best_tower = max(empty_cells, key=lambda coords: self.__check_coverage(*coords))
            else:
                best_tower = max(covered_cells, key=lambda coords: self.__check_coverage(*coords))

            self.add_tower(*best_tower)
            X, Y = best_tower
            neighbours = self.__get_neighbours(X, Y)
            for neighbour in neighbours:
                if neighbour[:-1] in empty_cells:
                    covered_cells.append(neighbour[:-1])
                    empty_cells.remove(neighbour[:-1])
            towers_count += 1
        print(f"{towers_count} towers were building.")

    def find_reliable_path(self, x1: int, y1: int, x2: int, y2: int):
        towers = self._get_all_towers()
        try:
            start = towers.index((x1, y1))
            end = towers.index((x2, y2))
        except ValueError:
            print("Incorrect coords")
            return
        adjacency_matrix = self._get_towers_adjacency_matrix()

        visited = set()
        queue = deque([(start, [start])])

        while queue:
            current, path = queue.popleft()

            if current == end:
                city = [row.copy() for row in self.city]
                for index in path:
                    tower_x, tower_y = towers[index]
                    city[tower_x][tower_y] = PATH
                self.show_grid(city=city)
                return path

            if current not in visited:
                visited.add(current)

                for neighbor, has_edge in enumerate(adjacency_matrix[current]):
                    if has_edge and neighbor not in visited:
                        queue.append((neighbor, path + [neighbor]))

        return None

    def show(self):
        print(*self.city, sep='\n')

    def show_grid(self, city: List[List[int]] = None):
        root = tk.Tk()
        root.geometry("400x400")
        frame = tk.Frame(root, width=400, height=400)
        frame.pack(expand=True, fill=tk.BOTH)  # .grid(row=0,column=0)
        canvas = tk.Canvas(frame, bg='#FFFFFF', width=300, height=300,
                           scrollregion=(0, 0, self.M * CELL_SIZE, self.N * CELL_SIZE))
        hbar = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        hbar.config(command=canvas.xview)
        vbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        vbar.config(command=canvas.yview)
        canvas.config(width=300, height=300)
        canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        if city is None:
            city = self.city

        for i in range(len(city)):
            for j in range(len(city[0])):
                x0, y0, x1, y1 = j * CELL_SIZE, i * CELL_SIZE, (j + 1) * CELL_SIZE, (
                        i + 1) * CELL_SIZE
                canvas.create_rectangle(x0, y0, x1, y1, fill=colors[city[i][j]], outline="black")

        root.mainloop()


if __name__ == '__main__':
    a = CityGrid(40, 50)
    a.show_grid()
    a.add_effective_towers()
    a.show_grid()
