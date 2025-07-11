import pygame
from game import AI_player, Ball, Game, Player, HEIGHT, WIDTH, main, PADDLE_HEIGHT, PADDLE_WIDTH
import random 
import pickle
import math

ACTIONS = ["up", "down"]
PADDLE_SPEED = 40
distance = lambda pt1, pt2: math.sqrt((pt2[0] - pt1[0])**2 + (pt2[1] - pt1[1])**2)


class Q_learning():
    def __init__(self, speed, epsilon=0.1, alpha=0.2, gamma=0.9):
        self.q = {}
        self.alpha = alpha
        self.epsilon = epsilon
        self.gamma = gamma
        self.speed = speed

    def update(self, old_state, new_state, reward, action):
        old_q = self.get_q(old_state, action)
        future_rewards = self.best_future_reward(new_state)
        self.update_q(new_state, action, reward, old_q, future_rewards)
    
    def get_q(self, s, a):
        key = (tuple(s), a)
        
        if key in self.q:
            return self.q[key]

        else:
            return 0
    
    def update_q(self, s, a, reward, old_q, future_rewards):
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
        
        return tuple(new_state)

    
    def choose_action(self, state):
        # print("STATE: ", state)
        # print(epsilon, random.choices([1, 0], [self.epsilon, 1 - self.epsilon])[0] == 1, self.q)
        # print(epsilon and random.choices([1, 0], [self.epsilon, 1 - self.epsilon])[0] == 1 or self.q == {})
        
        if random.random() < self.epsilon:
            return random.choice(ACTIONS)
        
        
        state = tuple(state)
        
        up_state = (state, "up")
        down_state = (state, "down")
        
        up_action = self.q[up_state] if up_state in self.q else 0
        down_action = self.q[down_state] if down_state in self.q else 0
        
        if up_action > down_action:
            return "up"
        
        elif up_action < down_action:
            return "down"
        
        else:
            return random.choice(ACTIONS)
    



def calc_dist(player, ball):
    return distance((player.x, player.y), (ball.x, ball.y))


def discretize_state(player, opponent, ball):
    sign = lambda val: 1 if val > 0 else -1
    
    state = [
        round(player.y - ball.y) // 20,
        # round(opponent.y),
        # round(calc_dist(player, ball)),
        # round(ball.x),
        # round(ball.y),
        sign(ball.Vx),
        sign(ball.Vy)
    ]
    
    return state


def train(n):
    # ai = None
    # with open("fix_because_the_other_one_is_courpted.pkl", "rb") as f:
    #     ai = pickle.load(f)
    #     ai.speed = PADDLE_SPEED * game.dt
        
    # with open("left_paddle.pkl", "rb") as f:
    #     left_paddle = pickle.load(f)
    
    # with open("right_paddle.pkl", "rb") as f:
    #     right_paddle = pickle.load(f)
    
    
    for i in range(n):
        game = Game(PADDLE_SPEED, None)
        ball = game.ball
    
        
        left_paddle = Q_learning(PADDLE_SPEED * game.dt)
        right_paddle = Q_learning(PADDLE_SPEED * game.dt)
        
        # with open("left_paddle.pkl", "rb") as f:
        #     left_paddle = pickle.load(f)
    
        # with open("right_paddle.pkl", "rb") as f:
        #     right_paddle = pickle.load(f)
            
        ai_player1 = AI_player(PADDLE_SPEED * game.dt, None, 1, 30, HEIGHT // 2 - 100)
        ai_player2 = AI_player(PADDLE_SPEED * game.dt, None, 2, 930, HEIGHT // 2 - 100)

        print(f"Training on game No. {i}...")
        last = {
            0: { "state": None, "action": None, "dist": calc_dist(ai_player1, ball) },
            1: { "state": None, "action": None, "dist": calc_dist(ai_player2, ball) }
            
        }

        while True:
            state1 = discretize_state(ai_player1, ai_player2, ball)
            state2 = discretize_state(ai_player2, ai_player1, ball)
            
            action1 = left_paddle.choose_action(state1)
            action2 = right_paddle.choose_action(state2)
            
            
            last[0] = {"state": state1, "action": action1, "dist": calc_dist(ai_player1, ball)}
            last[1] = {"state": state2, "action": action2, "dist": calc_dist(ai_player2, ball)}
            
            ai_player1.move(action1)            
            ai_player2.move(action2)
            ball.update(ai_player1.rect, ai_player2.rect, draw=False)
                
            new_state1 = discretize_state(ai_player1, ai_player2, ball)
            new_state2 = discretize_state(ai_player2, ai_player1, ball)
            
            
            def give_reward(p, reward):
                if p == 1 and reward > 0:
                    if reward >= 0:
                        left_paddle.update(last[0]["state"], new_state1, reward, last[0]["action"])
                        
                    else:
                        left_paddle.update(state1, new_state1, reward, action1)
                    
                if p == 2:
                    if reward >= 0:
                        right_paddle.update(last[1]["state"], new_state2, reward, last[1]["action"])
                        
                    else:
                        right_paddle.update(state2, new_state2, reward, action2)
                    
            
                
            paddle_hit = ball.check_collisions(ai_player1.rect, ai_player2.rect)            

            if calc_dist(ai_player1, ball) < last[0]["dist"]:
                give_reward(1, 0.5)
            

            if calc_dist(ai_player2, ball) < last[1]["dist"]:
                give_reward(2, 0.5)
                

            if paddle_hit == 1:
                give_reward(1, 1)
                
            if paddle_hit == 2:
                give_reward(2, 1)
            
            if ball.did_hit_sides() == -1:
                give_reward(1, -0.5)
                give_reward(2, 0.5)
                
            else:
                give_reward(1, 0.5)
                give_reward(2, -0.5)


            if game.win() == 1:
                give_reward(1, 1)
                break
            
            elif game.win() == 2:
                give_reward(2, 1)
                break                


    main(ai_player1, ai_player2, right_paddle, speed=PADDLE_SPEED)
    return left_paddle, right_paddle




if __name__ == "__main__":
    # ai = train(100)
    left_paddle, right_paddle = train(3)
    # 300 games


    # with open("pong_ai.pkl", "wb") as f:
    #     pickle.dump(ai, f)


    with open("left_paddle.pkl", "wb") as f:
        pickle.dump(left_paddle, f)
        
    with open("right_paddle.pkl", "wb") as f:
        pickle.dump(right_paddle, f)

