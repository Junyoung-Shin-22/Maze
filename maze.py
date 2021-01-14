import numpy as np
import cv2 as cv

black = np.array([0, 0, 0], dtype='uint8')
white = np.array([255, 255, 255], dtype='uint8')
red = np.array([0, 255, 0], dtype='uint8')
blue = np.array([255, 0, 0])


class Maze:

    def __init__(self, img, thickness=5):
        self.original_img = img
        self.thickness = thickness
        self.processed_img = np.zeros(img.shape[:2])
        self.result_img = self.original_img[::]

        self.width, self.height, _ = img.shape
        self.top, self.bottom, self.left, self.right = self.height, 0, self.width, 0
        self.preprocess()

        self.entrance = []
        self.solution = None

    # to black and white, find corners
    def preprocess(self):
        for i in range(self.height):
            for j in range(self.width):

                if sum(self.original_img[i][j]) / 3 > 200:
                    self.processed_img[i][j] = 255
                else:
                    self.processed_img[i][j] = 0

                    if i < self.top: self.top = i
                    if i > self.bottom: self.bottom = i
                    if j < self.left: self.left = j
                    if j > self.right: self.right = j

    def find_entrance(self):
        # 0:left, 1:right, 2:top, 3:bottom
        dp = [[] for _ in range(4)]

        # searching vertical sides
        for i in range(self.top, self.bottom):
            dp[0].append(1)  # white==1 black==0
            dp[1].append(1)

            # left side
            for j in range(self.left - self.thickness, self.left + self.thickness):
                if 0 <= j < self.width and (self.processed_img[i][j] == black).all():
                    dp[0][-1] = 0
                    break
            # right side
            for j in range(self.right - self.thickness, self.right + self.thickness):
                if 0 <= j < self.width and (self.processed_img[i][j] == black).all():
                    dp[1][-1] = 0
                    break

        # searching horizontal sides
        for j in range(self.left, self.right):
            dp[2].append(1)  # white==1 black==0
            dp[3].append(1)

            # top side
            for i in range(self.top - self.thickness, self.top + self.thickness):
                if 0 <= i < self.height and (self.processed_img[i][j] == black).all():
                    dp[2][-1] = 0
                    break
            # bottom side
            for i in range(self.bottom - self.thickness, self.bottom + self.thickness):
                if 0 <= i < self.height and (self.processed_img[i][j] == black).all():
                    dp[3][-1] = 0
                    break

        for d in dp:
            for i in range(1, len(d)):
                if d[i]: d[i] += d[i - 1]

        E = []

        for i in range(4):
            l = max(dp[i])
            a = dp[i].index(l)

            E.append((l, a, i))

        for _ in range(2):
            e = max(E)
            m, a, i = e

            if i == 0:
                x1, y1 = self.top + a - m + 1, self.left
                x2, y2 = self.top + a, self.left
            elif i == 1:
                x1, y1 = self.top + a - m + 1, self.right
                x2, y2 = self.top + a, self.right
            elif i == 2:
                x1, y1 = self.top, self.left + a - m + 1
                x2, y2 = self.top, self.left + a
            else:
                x1, y1 = self.bottom, self.left + a - m + 1
                x2, y2 = self.bottom, self.left + a

            self.entrance.append(((x1, y1), (x2, y2), i))
            E.remove(e)

    def solve(self):
        self.find_entrance()

        start = self.entrance[0][:2]
        end = self.entrance[1][:2]
        x_start = (start[0][0] + start[1][0])//2
        y_start = (start[0][1] + start[1][1])//2

        x_end = (end[0][0] + end[1][0]) // 2
        y_end = (end[0][1] + end[1][1]) // 2

        path = [(x_start, y_start), ]
        Queue = [path, ]
        visited = [[False] * self.width for _ in range(self.height)]
        visited[x_start][y_start] = True

        while Queue:
            path = Queue.pop(0)
            # print(path[-1])
            x, y = path[-1]

            if (x, y) == (x_end, y_end):
                self.solution = path
                return

            for i, j in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]:
                if self.top <= i <= self.bottom and self.left <= j <= self.right:
                    if visited[i][j] or self.processed_img[i][j] == 0: continue

                    visited[i][j] = True
                    Queue.append(path + [(i, j)])

    def draw_corners(self):
        cv.circle(self.result_img, (self.top, self.left), 5, (0, 0, 255))
        cv.circle(self.result_img, (self.bottom, self.right), 5, (0, 0, 255))

    def draw_entrance(self):
        if not self.entrance: return

        for p1, p2, _ in self.entrance:
            self.result_img[p1[0]][p1[1]] = blue
            self.result_img[p2[0]][p2[1]] = blue

    def draw_solution(self):
        if not self.solution:
            print('No solution available.')
            return

        for x, y in self.solution:
            self.result_img[x][y] = blue
