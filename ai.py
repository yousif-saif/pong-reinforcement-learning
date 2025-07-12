import pygame
# from game import AI_player, Ball, Game, Player, HEIGHT, WIDTH, main, PADDLE_HEIGHT, PADDLE_WIDTH
import random 
import pickle
import math
from game import *

ACTIONS = ["up", "down"]
# ACTIONS = ["up", "down", "stay"]

GAME_SPEED = 20
REPEAT_ACTION = 40
distance = lambda pt1, pt2: math.sqrt((pt2[0] - pt1[0])**2 + (pt2[1] - pt1[1])**2)


class Q_learning():
    def __init__(self, speed, epsilon=1.0, alpha=0.5, gamma=0.9):
        self.q = {}
        self.alpha = alpha
        self.gamma = gamma
        self.speed = speed
        
        self.epsilon = epsilon
        self.epsilon_decay = 0.995
        self.min_epsilon = 0.05
        
    
    def ensure_state_actions(self, state):
        for a in ACTIONS:
            self.q.setdefault((tuple(state), a), 0)

    def update(self, old_state, new_state, reward, action):
        self.ensure_state_actions(old_state)
        self.ensure_state_actions(new_state)
        
        old_q = self.get_q(old_state, action)
        future_rewards = self.best_future_reward(new_state)
        # print("future rewards: ", future_rewards)
        self.update_q(old_state, action, reward, old_q, future_rewards)
        
    
    def get_q(self, s, a):
        key = (tuple(s), a)
        
        if key in self.q:
            return self.q[key]

        else:
            return 0
    
    def update_q(self, s, a, reward, old_q, future_rewards):
        # print("action in update q: ", a)
        self.q[(tuple(s), a)] = old_q + self.alpha * (reward + self.gamma * future_rewards - old_q)
    
    def best_future_reward(self, s):
        q_values = []
        
        for action in ACTIONS:
            # key = (self.apply_action(s, action), action)
            key = (tuple(s), action)
            
            q_values.append(self.q[key] if key in self.q else 0)
        
        return max(q_values)

    def apply_action(self, s, a):
        new_state = list(s).copy()
        
        if a == "up":
            new_state[0] -= self.speed
            
        elif a == "down":
            new_state[0] += self.speed
        
        elif a == "stay":
            pass
        
        return tuple(new_state)

    
    def decay_epslion(self):
        if self.epsilon and self.epsilon > self.min_epsilon:
            self.epsilon *= self.epsilon_decay
    
    def choose_action(self, state):
        if self.epsilon and random.random() <= self.epsilon:
            return random.choice(ACTIONS)

        state = tuple(state)
        
        up_key = (state, "up")
        down_key = (state, "down")
                
        up_q = self.q[up_key] if up_key in self.q else 0
        down_q = self.q[down_key] if down_key in self.q else 0
        
        # stay_state = (state, "stay")
        
        # up_action = self.q[up_state] if up_state in self.q else 0
        # down_action = self.q[down_state] if down_state in self.q else 0
        # stay_action = self.q[stay_state] if stay_state in self.q else 0
        
        
        # Find the action with the highest Q-value
        # best_action = "up"  # default action
        # best_value = stay_action
        
        # if up_action > best_value:
        #     best_action = "up"
        #     best_value = up_action
            
        # if down_action > best_value:
        #     best_action = "down"
        #     best_value = down_action
        
        # sorted_actions = sorted(ACTIONS, key=lambda x: self.q[(state, x)] if (state, x) in self.q else 0)
        
        # print(sorted_actions[-1])
        # return sorted_actions[-1]
        
        # print(up_q)
        # print(down_q)
        
        if up_q > down_q:
            # print("up")
            return "up"

        elif down_q > up_q:
            # print("down")
            return "down"
        
        else:
            return random.choice(ACTIONS)

distance = lambda pt1, pt2: math.sqrt((pt2[0] - pt1[0])**2 + (pt2[1] - pt1[1])**2)
# center_point = lambda pt1, pt2: ((pt1[0] + pt2[0]) / 2, (pt1[1] + pt2[1]) / 2)
# center_point = lambda pt1: (pt1[0] + PADDLE_WIDTH, pt1[1] + PADDLE_HEIGHT // 2)
center_point = lambda pt1, pt2: ((pt1[0] + pt2[0]) / 2, (pt1[1] + pt2[1]) / 2)

def discretize(val, bin_size):
    return round(val / bin_size)

def create_state(p, opp, ball):
    sign = lambda val: 1 if val > 0 else -1
    return (
        discretize(p.y, 10),
        discretize(p.y - ball.y, 10),
        # discretize(distance(center_point((p.x, p.y)), (ball.x, ball.y)), 1),
        
        discretize(ball.x, 10),
        discretize(ball.y, 10),
        sign(ball.Vx),
        sign(ball.Vy),
        
    )


distance = lambda pt1, pt2: math.sqrt((pt2[0] - pt1[0])**2 + (pt2[1] - pt1[1])**2)


def get_hit_zone(paddle_rect, ball_y):
    paddle_top = paddle_rect.top
    paddle_bottom = paddle_rect.bottom
    paddle_height = paddle_rect.height
    
    one_third = paddle_height / 3

    if ball_y < paddle_top + one_third:
        return "top"
    elif ball_y < paddle_top + 2 * one_third:
        return "middle"
    else:
        return "bottom"


def train(n, draw=False):
    left_q = Q_learning(GAME_SPEED)
    right_q = Q_learning(GAME_SPEED)
    
    with open("left_paddle_new_change_state2.pkl", "rb") as f:
        left_q = pickle.load(f)
    
    with open("right_paddle_new_change_state2.pkl", "rb") as f:
        right_q = pickle.load(f)
    
    for i in range(n):
        print(f"Training AI on game No. {i}...")
        # screen = pygame.display.set_mode((WIDTH, HEIGHT))
        
        game = Game(GAME_SPEED, None)
        ball = game.ball
        dt = game.dt
        
        p1 = AI_player(GAME_SPEED * dt, None, 1, 30, HEIGHT // 2 - 100) # left paddle
        p2 = AI_player(GAME_SPEED * dt, None, 2, 930, HEIGHT // 2 - 100) # right paddle
        
    
        # p1.screen = screen
        # p2.screen = screen
        # ball.screen = screen
        
        
        while True:
            ball.check_collisions(p1.rect, p2.rect)
            ball.update(p1.rect, p2.rect, draw=False)
            
            state1 = create_state(p1, p2, ball)
            state2 = create_state(p2, p1, ball)
            # print("STATE: ", state1)
            
            old_p1_point = (p1.x, p1.y)
            old_p2_point = (p2.x, p2.y)
            
            
            action1 = left_q.choose_action(state1)
            action2 = right_q.choose_action(state2)
            
            p1.move(action1, REPEAT_ACTION)
            p2.move(action2, REPEAT_ACTION)

            ball.update(p1.rect, p2.rect, draw=False) # ADD FALSE HERE
            new_state1 = create_state(p1, p2, ball)
            new_state2 = create_state(p2, p1, ball)
            
            paddle_hit = ball.check_collisions(p1.rect, p2.rect)
            
            # Check for win
            if game.win() == 1:
                left_q.update(state1, new_state1, 2, action1)
                right_q.update(state2, new_state2, -2, action2)
                break
            
            elif game.win() == 2:
                left_q.update(state1, new_state1, -2, action1)
                right_q.update(state2, new_state2, 2, action2)
                break
            
            # Check for paddle hit
            # left paddle hit/miss
            
            if paddle_hit == 1:
                # if get_hit_zone(p1.rect, ball.y) in ["top", "bottom"]:
                #     # print("top/bottom")
                    
                #     left_q.update(state1, new_state1, 0.5, action1)
                
                # else:
                #     # print("middle")
                    
                left_q.update(state1, new_state1, 1, action1)
                
                
            if ball.did_hit_sides() == -1:
                left_q.update(state1, new_state1, -1, action1)
                right_q.update(state2, new_state2, 1, action2)
                
            
            if paddle_hit == 2:
                # if get_hit_zone(p2.rect, ball.y) in ["top", "bottom"]:
                    # print("top/bottom")
                #     right_q.update(state2, new_state2, 0.5, action2)
                
                # else:
                    # print("middle")
                right_q.update(state2, new_state2, 1, action2)
                    
            if ball.did_hit_sides() == 1:
                right_q.update(state2, new_state2, -1, action2)
                left_q.update(state1, new_state1, 1, action1)
                
            
            ball_point = (ball.x, ball.y)
            did_hit_left_paddle = False
            did_hit_right_paddle = False
            
            
            

            if ball.x <= WIDTH // 2 and not did_hit_left_paddle: # left paddle
                if paddle_hit == 1:
                    did_hit_left_paddle = True
            
                if did_hit_right_paddle:
                    did_hit_right_paddle = False
            
                new_center = center_point((p1.x, p1.y), ball_point)
                old_center = center_point(old_p1_point, ball_point)
                
                # new_center = center_point((p1.x, p1.y))
                # old_center = center_point(old_p1_point)
                
                if distance(new_center, ball_point) < distance(old_center, ball_point):
                    left_q.update(state1, new_state1, 0.2, action1)
                
                else:
                    left_q.update(state1, new_state1, -0.2, action1)
            
            
            if ball.x >= WIDTH // 2 and not did_hit_right_paddle: # right paddle
                if paddle_hit == 2:
                    did_hit_right_paddle = True
                    
                if did_hit_left_paddle:
                    did_hit_left_paddle = False
            
                
                new_center = center_point((p2.x, p2.y), ball_point)
                old_center = center_point(old_p2_point, ball_point)
                
                # new_center = center_point((p2.x, p2.y))
                # old_center = center_point(old_p2_point)
                
                if distance(new_center, ball_point) < distance(old_center, ball_point):
                    right_q.update(state2, new_state2, 0.2, action2)
                
                else:
                    right_q.update(state2, new_state2, -0.2, action2)
                    
                
            
            
            
            
            
            
            
            
            # pygame.display.set_caption("Pong AI")
            # pygame.display.flip()

            # screen.fill((0, 0, 0))
            
            
            # game.p1 = p1
            # game.p2 = p2
            p1.update(draw=False)
            p2.update(draw=False)
            
            # game.screen = screen
            game.update_all(draw=False)
            pygame.event.pump()
            
            # pygame.display.flip()
        
        # print(len(right_q.q), len(left_q.q))
            
        # main(p1, p2, ball, right_q, speed=GAME_SPEED)
        left_q.decay_epslion()
        right_q.decay_epslion()
        
        
    return left_q, right_q




if __name__ == "__main__":
    left, right = train(100)
    
    with open("left_paddle_new_change_state2.pkl", "wb") as f:
        pickle.dump(left, f)
        
    
    with open("right_paddle_new_change_state2.pkl", "wb") as f:
        pickle.dump(right, f)
        
        