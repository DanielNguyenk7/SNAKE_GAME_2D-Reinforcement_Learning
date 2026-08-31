import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
from snake_game import SnakeGameCore, SnakeRenderer, UP, DOWN, LEFT, RIGHT

class SnakeEnv(gym.Env):
    """
    Gymnasium environment for the Snake game.
    """
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}

    def __init__(self, render_mode=None):
        super().__init__()
        self.game = SnakeGameCore()
        
        # Action space: 0: Straight, 1: Right, 2: Left
        self.action_space = spaces.Discrete(3)
        
        # Observation space: 11 boolean values
        # [danger_straight, danger_right, danger_left,
        #  dir_l, dir_r, dir_u, dir_d,
        #  food_l, food_r, food_u, food_d]
        self.observation_space = spaces.Box(low=0, high=1, shape=(11,), dtype=np.uint8)
        
        self.render_mode = render_mode
        self.window = None
        self.clock = None
        self.renderer = None
        
        self.episode_steps = 0
        self.max_steps = 2000 # Prevent infinite loops
        self.episodes = 0
        
        # For rendering text
        self.cumulative_reward = 0.0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.game.reset()
        self.episode_steps = 0
        self.cumulative_reward = 0.0
        self.episodes += 1
        
        obs = self._get_obs()
        info = {}
        
        if self.render_mode == "human":
            self.render()
            
        return obs, info

    def step(self, action):
        self.episode_steps += 1
        
        # Map relative action to absolute direction
        clock_wise = [UP, RIGHT, DOWN, LEFT]
        idx = clock_wise.index(self.game.direction)
        
        if action == 0:
            new_dir = clock_wise[idx] # straight
        elif action == 1:
            new_dir = clock_wise[(idx + 1) % 4] # right turn
        else: # action == 2
            new_dir = clock_wise[(idx - 1) % 4] # left turn
            
        old_score = self.game.score
        old_dist = self._get_distance_to_food()
        
        state, reward, done, info = self.game.step(new_dir)
        
        # Reward shaping
        if not done and reward == 0:
            new_dist = self._get_distance_to_food()
            if new_dist < old_dist:
                reward = 0.1
            else:
                reward = -0.1
                
        # Starvation timeout
        truncated = False
        if self.episode_steps >= self.max_steps:
            truncated = True
            done = True
            
        self.cumulative_reward += reward
        
        obs = self._get_obs()
        
        if self.render_mode == "human":
            self.render()
            
        return obs, reward, done, truncated, info

    def _get_distance_to_food(self):
        head = self.game.snake[0]
        food = self.game.food
        return abs(head[0] - food[0]) + abs(head[1] - food[1])

    def _get_obs(self):
        head = self.game.snake[0]
        
        clock_wise = [UP, RIGHT, DOWN, LEFT]
        idx = clock_wise.index(self.game.direction)
        
        dir_straight = clock_wise[idx]
        dir_right = clock_wise[(idx + 1) % 4]
        dir_left = clock_wise[(idx - 1) % 4]
        
        # Danger calculation
        def is_danger(d):
            pt = (head[0] + d[0], head[1] + d[1])
            if (pt[0] < 0 or pt[0] >= self.game.width or 
                pt[1] < 0 or pt[1] >= self.game.height):
                return True
            if pt in self.game.snake:
                return True
            return False
            
        danger_straight = is_danger(dir_straight)
        danger_right = is_danger(dir_right)
        danger_left = is_danger(dir_left)
        
        # Directions
        dir_l = self.game.direction == LEFT
        dir_r = self.game.direction == RIGHT
        dir_u = self.game.direction == UP
        dir_d = self.game.direction == DOWN
        
        # Food relative location
        food = self.game.food
        food_l = food[0] < head[0]
        food_r = food[0] > head[0]
        food_u = food[1] < head[1]
        food_d = food[1] > head[1]
        
        obs = [
            danger_straight, danger_right, danger_left,
            dir_l, dir_r, dir_u, dir_d,
            food_l, food_r, food_u, food_d
        ]
        
        return np.array(obs, dtype=np.uint8)

    def render(self):
        if self.render_mode is None:
            return
            
        if self.window is None:
            pygame.init()
            pygame.font.init()
            
            from snake_game import SCREEN_WIDTH, SCREEN_HEIGHT, SnakeRenderer
            
            if self.render_mode == "human":
                pygame.display.init()
                self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                pygame.display.set_caption("Snake RL Training")
            else: # rgb_array
                self.window = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                
            self.clock = pygame.time.Clock()
            w, h = self.window.get_size()
            self.renderer = SnakeRenderer(self.window, w, h)

        # Handle events for human mode to prevent unresponsiveness
        if self.render_mode == "human":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
                elif event.type == pygame.VIDEORESIZE:
                    self.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.renderer.resize(event.w, event.h)
                    
        self.renderer.draw_state(self.game.get_state(), episode=self.episodes, cumulative_reward=self.cumulative_reward)
        
        if self.render_mode == "human":
            pygame.display.flip()
            self.clock.tick(self.metadata["render_fps"])
            return None
        elif self.render_mode == "rgb_array":
            return np.transpose(np.array(pygame.surfarray.pixels3d(self.window)), axes=(1, 0, 2))

    def close(self):
        if self.window is not None:
            pygame.quit()
            self.window = None
            self.renderer = None
