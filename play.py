from game import *
from ai import *
import pickle
import pygame

GAME_SPEED = 20

if __name__ == "__main__":
    with open("right_paddle_new.pkl", "rb") as f:
        ai = pickle.load(f)
        ai.epsilon = False

        # print(len(ai.q))
        # screen = pygame.display.set_mode((WIDTH, HEIGHT))
        
                
        # p1 = AI_player(GAME_SPEED, None, 1, 30, HEIGHT // 2 - 100) # left paddle
        # p2 = AI_player(GAME_SPEED, None, 2, 930, HEIGHT // 2 - 100) # right paddle

        print(len(ai.q))
        main(None, None, None, ai, 15)