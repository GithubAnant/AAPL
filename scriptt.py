from collections import defaultdict
import random
import cv2
import numpy as np
from queue import Queue


class SnakeGame:
    def __init__(self, h=600, w=810, game_speed=60):
        self.cell_size = 30
        self.h = h//self.cell_size*self.cell_size
        self.w = w//self.cell_size*self.cell_size
        self.game_speed = game_speed
        self.grid_color = (1., 1., 1.)  # white
        self.body_color = (0., 0., 0.)  # black
        self.head_color = (0.5, 0.5, 0.5)  # grey
        self.food_color = (0., 0., 1.)  # red
        self.img = np.ones((h, w, 3))*self.grid_color
        for y in range(0, self.h, self.cell_size):
            for x in range(0, self.w, self.cell_size):
                self.color_square((y, x), self.grid_color)
        self.body = Queue()
        self.initial_pos = (300//self.cell_size*self.cell_size,
                            60//self.cell_size*self.cell_size)
        self.head = self.initial_pos
        self.body.put(self.initial_pos)
        self.body.put(self.initial_pos)
        self.body.put(self.initial_pos)
        self.color_square(self.head, self.head_color)
        self.food_pos = self.generate_food()
        self.score = 0
        self.direction = ''
        self.game_over = False
        self.move_map = defaultdict(lambda: (0, 0))
        self.move_map.update({
            'left': (0, -self.cell_size),
            'right': (0, self.cell_size),
            'up': (-self.cell_size, 0),
            'down': (self.cell_size, 0)
        })


    def color_square(self, pos, color):
        y, x = pos
        self.img[y:y+self.cell_size, x:x+self.cell_size] = color

    def move(self):
        delta = self.move_map[self.direction]
        new_y, new_x = self.head[0]+delta[0], self.head[1]+delta[1]
        if new_y < 0:
            new_y = self.h - self.cell_size
        elif new_y >= self.h:
            new_y = 0
        elif new_x < 0:
            new_x = self.w - self.cell_size
        elif new_x >= self.w:
            new_x = 0
        if (self.img[new_y, new_x] == self.body_color).all():
            self.end_game()
        else:
            if (self.img[new_y, new_x] == self.grid_color).all():
                tail = self.body.get()
                self.color_square(tail, self.grid_color)
            elif (self.img[new_y, new_x] == self.food_color).all():
                self.score += 1
                self.food_pos = self.generate_food()
            self.body.put((new_y, new_x))
            self.color_square(self.head, self.body_color)
            self.head = (new_y, new_x)
            self.color_square(self.head, self.head_color)

    def end_game(self):
        self.game_over = True
        self.img[self.h//5:self.h*4//6, self.w//5:self.w*4//5] = (0.2, 0.2, 0.2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(self.img, 'Game over!', (self.w//3, self.h*2//7), font, 1.5, (1., 1., 1.), 4, 2)
        cv2.putText(self.img, 'Score:', (self.w*7//16, self.h * 3 // 8), font, 1.1, (1., 1., 1.), 1, 2)
        cv2.putText(self.img, str(self.score), (self.w * 7 // 16, self.h * 4//8), font, 2, (1., 1., 1.), 3, 2)
        cv2.putText(self.img, 'Press y to play again or n to quit', (self.w//4, self.h * 5 // 8), font, 0.75, (1., 1., 1.), 1, 2)

    def generate_food(self):
        y = random.randrange(self.h)//self.cell_size*self.cell_size
        x = random.randrange(self.w)//self.cell_size*self.cell_size
        while (self.img[y, x] != self.grid_color).any():
            y = random.randrange(self.h) // self.cell_size * self.cell_size
            x = random.randrange(self.w) // self.cell_size * self.cell_size
        self.color_square((y, x), self.food_color)
        return y, x

    def play(self):
        while True:
            self.__init__()
            while not self.game_over:
                cv2.imshow('Snake', self.img)
                k = cv2.waitKeyEx(self.game_speed)
                UP_KEY, LEFT_KEY, DOWN_KEY, RIGHT_KEY = 2490368, 2424832, 2621440, 2555904
                if k == UP_KEY and self.direction != 'down':
                    self.direction = 'up'
                elif k == LEFT_KEY and self.direction != 'right':
                    self.direction = 'left'
                elif k == DOWN_KEY and self.direction != 'up':
                    self.direction = 'down'
                elif k == RIGHT_KEY and self.direction != 'left':
                    self.direction = 'right'
                if self.direction:
                    self.move()
            choice = ''
            while choice not in ['y', 'n']:
                cv2.imshow('Snake', self.img)
                choice = chr(cv2.waitKey(0) & 0xFF)
            if choice == 'n':
                break
        cv2.destroyAllWindows()


snake_game = SnakeGame()
snake_game.play()