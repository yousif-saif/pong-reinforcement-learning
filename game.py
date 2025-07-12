import pygame
import math
import random
import time
import pickle

pygame.init()

background_color = (0, 0, 0)
WIDTH, HEIGHT = 1000, 800
PADDLE_WIDTH = 30
PADDLE_HEIGHT = 130
PADDLE_SPEED = 0.2
REPEAT_ACTION = 10


def discretize(val, bin_size):
    return round(val / bin_size)


def create_state(p, opp, ball):
    sign = lambda val: 1 if val > 0 else -1
    return (
        discretize(p.y, 10),
        discretize(p.y - ball.y, 10),
        discretize(ball.x, 10),
        discretize(ball.y, 10),
        sign(ball.Vx),
        sign(ball.Vy),
    )

def clamp(a, b, c):
    if a < b:   return b
    elif a > c: return c
    else:       return a


class Player():
    def __init__(self, speed, screen, player, x, y):
        self.speed = speed
        self.color = (255, 255, 255)
        self.x = x
        self.y = y
        self.screen = screen
        self.rect = pygame.Rect(self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.player = player
        
    def handle_key_press(self):
        key = pygame.key.get_pressed()
        
        if self.player == 1:
            if key[pygame.K_w]: self.y -= self.speed
            if key[pygame.K_s]: self.y += self.speed
                
            self.check_borders()
            if key[pygame.K_ESCAPE]:
                quit(0)
            
        elif self.player == 2:
            key = pygame.key.get_pressed()
            if key[pygame.K_UP]: self.y -= self.speed
            if key[pygame.K_DOWN]: self.y += self.speed
            self.check_borders()



    def update(self, draw=True):
        self.handle_key_press()
        # self.rect = pygame.Rect(self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT)    
        self.rect.update(self.x, self.y, PADDLE_WIDTH, PADDLE_HEIGHT)    
        
        
        if draw:
            self.draw()
    
    def draw(self):
        # pygame.draw.circle(screen, self.color, (self.x, self.y), 10, 10)
        pygame.draw.rect(self.screen, self.color, self.rect)
    
    def check_borders(self):
        if self.y >= HEIGHT - PADDLE_HEIGHT:
            self.y = HEIGHT - PADDLE_HEIGHT
            
        elif self.y <= 0:
            self.y = 0


class AI_player(Player):
    def move(self, action, repeat_action_n):
        for i in range(repeat_action_n):
            if action == "up":
                self.y -= self.speed

            elif action == "down":
                self.y += self.speed
                
            elif action == "stay":
                continue
            
            self.check_borders()


class Ball():
    def __init__(self, speed, screen):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.width = 10
        self.radis = 10

        self.screen = screen
        # physics
        directions = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
        self.direction = random.choice(directions)
        
        # Velocities
        self.Vx = speed * self.direction[0]
        self.Vy = speed * self.direction[1]
        
        self.is_start = True
        
    def move_ball(self):
        if self.is_start:
            directions = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
            self.direction = random.choice(directions)
            
            self.Vx *= self.direction[0]
            self.Vy *= self.direction[1]


        self.is_start = False
        self.x += self.Vx
        self.y += self.Vy

        
    def update(self, rect1, rect2, draw=True):
        self.move_ball()
        self.check_collisions(rect1, rect2)
        
        if draw:            
            self.draw(self.x, self.y)
        
    def check_collisions(self, rect1: pygame.Rect, rect2: pygame.Rect):
        ball_point = (self.x, self.y)
        
        is_there_collision_y = self.y <= 0 or self.y >= HEIGHT
        # is_there_collision_x = self.x <= -(self.radis * 2) or self.x >= WIDTH + self.radis * 2            

        if is_there_collision_y:
            self.Vy *= -1
        
        for rect in [rect1, rect2]:            
            near_x = clamp(self.x, rect.x, rect.x + PADDLE_WIDTH)
            near_y = clamp(self.y, rect.y, rect.y + PADDLE_HEIGHT)
            
            dist = self.distance(ball_point, (near_x, near_y))
            
            if dist <= self.radis:      
                if self.y <= rect.y or self.y >= rect.y + PADDLE_HEIGHT:
                    self.Vy *= -1
                    
                else:
                    self.Vx *= -1
                
                return 1 if rect == rect1 else 2
                
            
        # is_there_collision_y = self.y <= 0 or self.y >= HEIGHT
        # # is_there_collision_x = self.x <= -(self.radis * 2) or self.x >= WIDTH + self.radis * 2            

        # if is_there_collision_y:
        #     self.Vy *= -1
        
        # if is_there_collision_x:
        #     self.Vx *= -1
    
    def did_hit_sides(self):
        left_wall_collision = self.x <= -(self.radis * 2)
        right_wall_collision = self.x >= WIDTH + self.radis * 2
        
        # left wall collision: 1
        # right wall collision: -1
        if left_wall_collision: return -1
        if right_wall_collision: return 1
        
        # return False
    
    def re_render_ball_after_loss(self, draw=True):
        self.is_start = True
                
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        
        if draw:
            self.draw(self.x, self.y)
    
    def distance(self, pt1, pt2):
        return math.sqrt((pt2[0] - pt1[0])**2 + (pt2[1] - pt1[1])**2)
        
    def draw(self, x, y, color=(255, 255, 255)):
        pygame.draw.circle(self.screen, color, (x, y), self.radis, self.width)
    
class Game:
    def __init__(self, speed, screen, ai=None):
        self.dt = pygame.time.Clock().tick(60) / 1000 
        
        self.screen = screen
        
        self.p1 = Player(speed * self.dt, self.screen, 1, 30, HEIGHT // 2 - 100)
        self.p2 = Player(speed * self.dt, self.screen, 2, 930, HEIGHT // 2 - 100)
        self.ai = ai
        if self.ai:
            self.p2 = AI_player(speed * self.dt, self.screen, 2, 930, HEIGHT // 2 - 100)
        
        self.ball = Ball(speed * self.dt, self.screen)
        
        self.p1_points = 0
        self.p2_points = 0
        self.points_to_win = 5
        
        self.frames = 0
        
        pygame.font.init()
        self.font = pygame.font.Font(pygame.font.get_default_font(), 80)
        
    def draw_points(self):
        text = self.font.render(str(self.p1_points), True, (84, 84, 84))
        self.screen.blit(text, (WIDTH//2 - 250, HEIGHT//2 - 50))

        text = self.font.render(str(self.p2_points), True, (84, 84, 84))
        self.screen.blit(text, (WIDTH//2 + 250, HEIGHT//2 - 50))
    
    def update_points(self, draw=True):
        wall = self.ball.did_hit_sides()
        if wall == -1:
            self.p2_points += 1
            self.ball.re_render_ball_after_loss(draw)
            
        if wall == 1:
            self.p1_points += 1
            self.ball.re_render_ball_after_loss(draw)
            
        if draw:
            self.draw_points()
        
        
    def update_all(self, draw=True):
        self.ball.update(self.p1.rect, self.p2.rect, draw)
        self.update_points(draw)

        self.p1.update(draw)
        self.p2.update(draw)
        
        
        if self.ai:
            if type(self.p1) == AI_player:
                action1 = self.left_ai.choose_action(create_state(self.p1, self.p2, self.ball))
                self.p1.move(action1, 1)
            
                # for i in range(10):
                #     self.p1.move(action1)
            
            action2 = self.ai.choose_action(create_state(self.p2, self.p1, self.ball))
            # print(action2)
            self.p2.move(action2, REPEAT_ACTION)
                
                # for i in range(10):
                #     self.p2.move(action2)
                    
        self.frames += 1
        
        
    def win(self):
        if self.p1_points == self.points_to_win:
            return 1
        
        elif self.p2_points == self.points_to_win:
            return 2

        else:
            return 0


def main(p1=None, p2=None, ball=None, ai=None, speed=15):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
    pygame.display.set_caption("Pong AI")
    pygame.display.flip()
    
    game = Game(speed, screen, ai)
    
    if type(p1) == AI_player:
        game.p1 = p1 if p1 else game.p1
        game.p1.screen = screen
        
        with open("left_paddle_new_change_state2.pkl", "rb") as f:
            left_ai = pickle.load(f)
            game.left_ai = left_ai
        
        
    # game.p2 = p2 if p2 else game.p2
    # game.ball = ball if ball else game.ball

    # game.p2.screen = screen
    # game.ball.screen = screen
        
    running = True
    while game.win() == 0:
        screen.fill(background_color)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game.update_all()
        pygame.display.flip()

    print(f"PLAYER {game.win()} WON")
    
        
if __name__ == "__main__":
    main()