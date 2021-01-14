import cv2 as cv
import maze

fname = 'test/maze3.png'
img = cv.imread(fname)

mz = maze.Maze(img)
mz.solve()
mz.draw_solution()

cv.imwrite('test/maze3-result.png', mz.result_img)
