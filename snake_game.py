import pygame
import random
import math
import sys
from ui_components import THEME, render_outlined_text, draw_panel, CTAButton, IconButton

# --- Constants & Config ---
DEFAULT_GRID_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 15
# Default initial screen size
SCREEN_WIDTH = GRID_WIDTH * DEFAULT_GRID_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * DEFAULT_GRID_SIZE

FPS_HUMAN = 10
FPS_AI = 60

# Colors (Keep some core ones for game elements, use THEME for UI)
COLOR_SNAKE_HEAD = (97, 175, 239)
COLOR_SNAKE_BODY = (152, 195, 121)
COLOR_FOOD = (224, 108, 117)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class SnakeGameCore:
    def __init__(self, width=GRID_WIDTH, height=GRID_HEIGHT):
        self.width = width
        self.height = height
        self.reset()

    def reset(self):
        self.snake = [(self.width // 2, self.height // 2), 
                      (self.width // 2 - 1, self.height // 2),
                      (self.width // 2 - 2, self.height // 2)]
        self.direction = RIGHT
        self.is_golden_food = False
        self.food = self._spawn_food()
        self.score = 0
        self.game_over = False
        self.steps = 0
        return self.get_state()

    def _spawn_food(self):
        self.is_golden_food = random.random() < 0.15  # 15% chance for golden poop
        while True:
            food = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
            if food not in self.snake:
                return food

    def step(self, action=None):
        if self.game_over:
            return self.get_state(), 0, True, {}

        self.steps += 1
        reward = 0

        if action is not None:
            if (action[0] * -1, action[1] * -1) != self.direction:
                self.direction = action

        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        if (new_head[0] < 0 or new_head[0] >= self.width or
            new_head[1] < 0 or new_head[1] >= self.height):
            self.game_over = True
            return self.get_state(), -10, True, {"reason": "wall"}

        if new_head in self.snake:
            self.game_over = True
            return self.get_state(), -10, True, {"reason": "self"}

        self.snake.insert(0, new_head)

        if new_head == self.food:
            pts = 30 if self.is_golden_food else 10
            self.score += pts
            reward = pts
            self.food = self._spawn_food()
        else:
            self.snake.pop()

        return self.get_state(), reward, self.game_over, {}

    def get_state(self):
        return {
            "snake": self.snake.copy(),
            "food": self.food,
            "is_golden_food": getattr(self, 'is_golden_food', False),
            "direction": self.direction,
            "score": self.score,
            "game_over": self.game_over,
            "width": self.width,
            "height": self.height
        }

class SnakeRenderer:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.resize(width, height)
        self.wobble_offset = 0

    def resize(self, width, height):
        self.screen_width = width
        self.screen_height = height
        cell_w = self.screen_width // GRID_WIDTH
        cell_h = self.screen_height // GRID_HEIGHT
        self.cell_size = min(cell_w, cell_h)
        self.offset_x = (self.screen_width - (GRID_WIDTH * self.cell_size)) // 2
        self.offset_y = (self.screen_height - (GRID_HEIGHT * self.cell_size)) // 2
        
        self.ui_font = pygame.font.SysFont("comicsansms", max(16, self.cell_size))
        self.title_font = pygame.font.SysFont("comicsansms", max(30, int(self.cell_size * 1.5)), bold=True)

    def draw_state(self, state, episode=None, cumulative_reward=None):
        self.screen.fill((0, 0, 0))
        self.wobble_offset += 0.1
        
        # 1. Background Gradient (Deep cyan to bright reef blue)
        play_area = pygame.Rect(self.offset_x, self.offset_y, GRID_WIDTH * self.cell_size, GRID_HEIGHT * self.cell_size)
        
        # Vertical gradient
        for y in range(play_area.height):
            lerp_val = y / play_area.height
            r = int(27 * (1 - lerp_val) + 127 * lerp_val)
            g = int(111 * (1 - lerp_val) + 216 * lerp_val)
            b = int(168 * (1 - lerp_val) + 224 * lerp_val)
            pygame.draw.line(self.screen, (r, g, b), (play_area.left, play_area.top + y), (play_area.right, play_area.top + y))
            
        # Draw sand floor
        sand_rect = pygame.Rect(play_area.left, play_area.bottom - self.cell_size, play_area.width, self.cell_size)
        pygame.draw.rect(self.screen, (222, 204, 158), sand_rect)
        
        # Draw Bubbles
        for i in range(15):
            bx = play_area.left + ((i * 47) % play_area.width)
            by = play_area.top + ((play_area.height - int(self.wobble_offset * 10 * (i%3 + 1))) % play_area.height)
            pygame.draw.circle(self.screen, (255, 255, 255, 100), (bx, by), (i%3) + 2, 1)

        # 2. Draw Food (Poop Emoji)
        self._draw_poop(state["food"], state.get("is_golden_food", False))

        # 3. Draw Catfish
        self._draw_catfish(state["snake"], state["direction"])

        # 4. HUD (Score only, player-facing)
        score_surf = render_outlined_text(f"Score: {state['score']}", self.ui_font, THEME["text.title.fill"], THEME["text.title.outline"])
        self.screen.blit(score_surf, (self.offset_x + 10, self.offset_y + 10))

        if episode is not None:
            ep_surf = render_outlined_text(f"Ep: {episode}", self.ui_font, THEME["text.title.fill"], THEME["text.title.outline"])
            self.screen.blit(ep_surf, (self.screen_width - 120, self.offset_y + 10))
        if cumulative_reward is not None:
            rew_surf = render_outlined_text(f"Reward: {cumulative_reward:.1f}", self.ui_font, THEME["text.title.fill"], THEME["text.title.outline"])
            self.screen.blit(rew_surf, (self.screen_width - 160, self.offset_y + 40))

    def _draw_poop(self, food_pos, is_golden):
        fx = self.offset_x + food_pos[0] * self.cell_size + self.cell_size // 2
        fy = self.offset_y + food_pos[1] * self.cell_size + self.cell_size // 2
        
        bounce = math.sin(self.wobble_offset * 3) * 3
        fy += bounce

        color = (255, 215, 0) if is_golden else (139, 69, 19)
        highlight = (255, 255, 200) if is_golden else (180, 110, 50)
        
        sz = self.cell_size * 0.45
        # Draw 3 overlapping ellipses for the swirl
        pygame.draw.ellipse(self.screen, color, (fx - sz, fy - sz*0.2, sz*2, sz*1.2))
        pygame.draw.ellipse(self.screen, highlight, (fx - sz, fy - sz*0.2, sz*2, sz*0.3)) # Gloss band
        
        pygame.draw.ellipse(self.screen, color, (fx - sz*0.7, fy - sz*0.7, sz*1.4, sz))
        pygame.draw.ellipse(self.screen, highlight, (fx - sz*0.7, fy - sz*0.7, sz*1.4, sz*0.2)) # Gloss band
        
        pygame.draw.ellipse(self.screen, color, (fx - sz*0.4, fy - sz*1.1, sz*0.8, sz*0.8))
        
        # Eyes
        pygame.draw.circle(self.screen, (255,255,255), (int(fx - sz*0.3), int(fy - sz*0.2)), int(sz*0.3))
        pygame.draw.circle(self.screen, (255,255,255), (int(fx + sz*0.3), int(fy - sz*0.2)), int(sz*0.3))
        pygame.draw.circle(self.screen, (0,0,0), (int(fx - sz*0.3), int(fy - sz*0.2)), int(sz*0.1))
        pygame.draw.circle(self.screen, (0,0,0), (int(fx + sz*0.3), int(fy - sz*0.2)), int(sz*0.1))
        
        # Smile (closed eye style)
        pygame.draw.arc(self.screen, (0,0,0), (fx - sz*0.4, fy, sz*0.8, sz*0.4), math.pi, 0, 2)
        
        if is_golden:
            # Starburst rays
            for i in range(4):
                ang = self.wobble_offset + i * math.pi/2
                rx = fx + math.cos(ang) * sz * 1.5
                ry = fy + math.sin(ang) * sz * 1.5
                pygame.draw.line(self.screen, (255, 255, 200), (fx, fy), (rx, ry), 2)

    def _draw_catfish(self, snake, direction):
        if not snake: return
        
        swim_offset = math.sin(self.wobble_offset * 4) * (self.cell_size * 0.15)
        dir_x, dir_y = direction
        
        # Draw tail
        tail = snake[-1]
        tx = self.offset_x + tail[0] * self.cell_size + self.cell_size//2
        ty = self.offset_y + tail[1] * self.cell_size + self.cell_size//2
        if len(snake) > 1:
            ptail = snake[-2]
            tdx, tdy = tail[0] - ptail[0], tail[1] - ptail[1]
        else:
            tdx, tdy = -dir_x, -dir_y
            
        tail_poly = [
            (tx, ty),
            (tx + tdx * self.cell_size + tdy * self.cell_size * 0.5, ty + tdy * self.cell_size - tdx * self.cell_size * 0.5),
            (tx + tdx * self.cell_size - tdy * self.cell_size * 0.5, ty + tdy * self.cell_size + tdx * self.cell_size * 0.5)
        ]
        pygame.draw.polygon(self.screen, (20, 150, 150), tail_poly)

        # Calculate body segments points
        points = []
        radii = []
        for i in range(len(snake)):
            segment = snake[i]
            sx = self.offset_x + segment[0] * self.cell_size + self.cell_size//2
            sy = self.offset_y + segment[1] * self.cell_size + self.cell_size//2
            
            if i > 0:
                if i % 2 == 0:
                    sx += int(tdy * swim_offset)
                    sy += int(tdx * swim_offset)
                else:
                    sx -= int(tdy * swim_offset)
                    sy -= int(tdx * swim_offset)
                    
            points.append((sx, sy))
            radii.append(int(self.cell_size * 0.45 * (1 - (i / len(snake)) * 0.3)))
            
        # Draw smooth connecting lines for the body
        if len(points) > 1:
            pygame.draw.lines(self.screen, (30, 170, 170), False, points, int(self.cell_size * 0.75))
            
        # Draw the circles on top to round out the segments and add the belly
        for i in range(len(points)-1, 0, -1):
            sx, sy = points[i]
            radius = radii[i]
            pygame.draw.circle(self.screen, (30, 170, 170), (sx, sy), radius)
            pygame.draw.circle(self.screen, (200, 240, 240), (sx, sy), int(radius*0.6))
            
        # Draw Head
        head = snake[0]
        hx = self.offset_x + head[0] * self.cell_size + self.cell_size//2
        hy = self.offset_y + head[1] * self.cell_size + self.cell_size//2
        
        # Pectoral fins (flapping)
        flap = math.sin(self.wobble_offset * 10) * self.cell_size * 0.3
        fin_color = (20, 150, 150)
        pygame.draw.ellipse(self.screen, fin_color, (hx - self.cell_size*0.6, hy - self.cell_size*0.2 + flap, self.cell_size*1.2, self.cell_size*0.4))
        
        pygame.draw.circle(self.screen, (40, 190, 190), (hx, hy), int(self.cell_size * 0.55))
        pygame.draw.circle(self.screen, (200, 240, 240), (hx, hy), int(self.cell_size * 0.35))
        
        # Googly Eyes
        eye_r = self.cell_size // 4
        ex1 = hx + dir_x * eye_r + (-dir_y * eye_r * 1.5)
        ey1 = hy + dir_y * eye_r + (dir_x * eye_r * 1.5)
        ex2 = hx + dir_x * eye_r - (-dir_y * eye_r * 1.5)
        ey2 = hy + dir_y * eye_r - (dir_x * eye_r * 1.5)
        
        pygame.draw.circle(self.screen, (255,255,255), (int(ex1), int(ey1)), eye_r)
        pygame.draw.circle(self.screen, (255,255,255), (int(ex2), int(ey2)), eye_r)
        pygame.draw.circle(self.screen, (0,0,0), (int(ex1 + dir_x*2), int(ey1 + dir_y*2)), eye_r//2)
        pygame.draw.circle(self.screen, (0,0,0), (int(ex2 + dir_x*2), int(ey2 + dir_y*2)), eye_r//2)
        
        # Whiskers (Barbels)
        wx1 = hx + dir_x * self.cell_size * 0.5 + (-dir_y * self.cell_size * 0.3)
        wy1 = hy + dir_y * self.cell_size * 0.5 + (dir_x * self.cell_size * 0.3)
        wx2 = hx + dir_x * self.cell_size * 0.5 - (-dir_y * self.cell_size * 0.3)
        wy2 = hy + dir_y * self.cell_size * 0.5 - (dir_x * self.cell_size * 0.3)
        
        # Trail backwards
        pygame.draw.line(self.screen, (40, 40, 40), (wx1, wy1), (wx1 - dir_x * self.cell_size - dir_y * swim_offset, wy1 - dir_y * self.cell_size - dir_x * swim_offset), 2)
        pygame.draw.line(self.screen, (40, 40, 40), (wx2, wy2), (wx2 - dir_x * self.cell_size + dir_y * swim_offset, wy2 - dir_y * self.cell_size + dir_x * swim_offset), 2)

def generate_sound(sound_type, volume=0.5):
    try:
        import numpy as np
        sample_rate = 44100
        
        if sound_type == 'eat':
            duration = 0.15
            n_samples = int(duration * sample_rate)
            t = np.linspace(0, duration, n_samples, False)
            # Plop: sweep from 200 to 600 Hz
            freqs = np.linspace(200, 600, n_samples)
            wave = np.sin(2 * np.pi * freqs * t)
            # Envelope
            env = np.exp(-10 * t)
            wave *= env
            
        elif sound_type == 'die':
            duration = 0.5
            n_samples = int(duration * sample_rate)
            t = np.linspace(0, duration, n_samples, False)
            # Glug: sweep down with AM modulation (bubbling)
            freqs = np.linspace(300, 50, n_samples)
            am = 0.5 * (1 + np.sin(2 * np.pi * 15 * t))
            wave = np.sin(2 * np.pi * freqs * t) * am
            env = np.exp(-4 * t)
            wave *= env
            
        elif sound_type == 'click':
            duration = 0.05
            n_samples = int(duration * sample_rate)
            t = np.linspace(0, duration, n_samples, False)
            wave = np.sin(2 * np.pi * 800 * t)
            env = np.exp(-30 * t)
            wave *= env
            
        else:
            return None

        buf = np.zeros((n_samples, 2), dtype=np.int16)
        max_sample = 2**(16 - 1) - 1
        val = (wave * volume * max_sample).astype(np.int16)
        buf[:, 0] = val
        buf[:, 1] = val
        
        return pygame.sndarray.make_sound(buf)
    except Exception:
        return None

def main_menu(screen):
    clock = pygame.time.Clock()
    bg_offset = 0

    while True:
        w, h = screen.get_size()
        ui_font = pygame.font.SysFont("comicsansms", max(16, h // 20))
        title_font = pygame.font.SysFont("comicsansms", max(30, h // 10), bold=True)
        
        btn_w = min(300, int(w * 0.6))
        btn_h = max(40, int(h * 0.1))
        
        # Panel Rect
        panel_w = btn_w + 60
        panel_h = btn_h * 3 + 60
        panel_rect = pygame.Rect(w//2 - panel_w//2, h//2 - panel_h//2, panel_w, panel_h)
        
        # Buttons
        btn_human_rect = pygame.Rect(w//2 - btn_w//2, panel_rect.y + 40, btn_w, btn_h)
        btn_ai_rect = pygame.Rect(w//2 - btn_w//2, btn_human_rect.bottom + 20, btn_w, btn_h)
        
        btn_human = CTAButton(btn_human_rect, "Play (Human)", ui_font)
        btn_ai = CTAButton(btn_ai_rect, "Watch AI", ui_font)
        
        # Draw Background
        screen.fill(THEME["bg.primary"])
        bg_offset += 0.5
        for i in range(-50, w, 40):
            for j in range(-50, h, 40):
                pygame.draw.circle(screen, (50, 55, 65, 50), (int(i + (bg_offset%40)), int(j + (bg_offset%40))), 3)

        # Draw Title
        title_y = panel_rect.y - 60 + math.sin(bg_offset * 0.1) * 5
        title_surf = render_outlined_text("SNAKE RL", title_font, THEME["text.title.fill"], THEME["text.title.outline"])
        t_rect = title_surf.get_rect(center=(w // 2, int(title_y)))
        screen.blit(title_surf, t_rect)
        
        # Draw Panel
        draw_panel(screen, panel_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]
        
        btn_human.update(mouse_pos, mouse_down)
        btn_ai.update(mouse_pos, mouse_down)
        
        btn_human.draw(screen)
        btn_ai.draw(screen)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if btn_human.is_clicked(event):
                return "HUMAN", screen
            if btn_ai.is_clicked(event):
                return "AI", screen
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                    return "HUMAN", screen
                elif event.key == pygame.K_2 or event.key == pygame.K_KP2:
                    return "AI", screen
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        clock.tick(60)

def draw_overlay_menu(screen, title_text, btn_text):
    """Draws a pause or game over modal"""
    w, h = screen.get_size()
    ui_font = pygame.font.SysFont("comicsansms", max(16, h // 20))
    title_font = pygame.font.SysFont("comicsansms", max(24, h // 15), bold=True)
    
    panel_w = min(400, int(w * 0.8))
    panel_h = 200
    panel_rect = pygame.Rect(w//2 - panel_w//2, h//2 - panel_h//2, panel_w, panel_h)
    
    # Semi-transparent overlay
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    screen.blit(overlay, (0, 0))
    
    draw_panel(screen, panel_rect)
    
    # Header
    title_surf = render_outlined_text(title_text, title_font, THEME["text.title.fill"], THEME["text.title.outline"])
    t_rect = title_surf.get_rect(center=(w // 2, panel_rect.y + 30))
    screen.blit(title_surf, t_rect)
    
    # CTA Button
    btn_w = 200
    btn_h = 50
    btn_rect = pygame.Rect(w//2 - btn_w//2, panel_rect.bottom - 70, btn_w, btn_h)
    btn = CTAButton(btn_rect, btn_text, ui_font)
    
    return btn

def draw_pause_icon(screen, center, size):
    w = size * 0.12
    h = size * 0.4
    cx, cy = center
    pygame.draw.rect(screen, (255,255,255), (cx - w*1.5, cy - h/2, w, h))
    pygame.draw.rect(screen, (255,255,255), (cx + w*0.5, cy - h/2, w, h))

def play_human(screen):
    clock = pygame.time.Clock()
    eat_sound = generate_sound('eat', 0.4)
    die_sound = generate_sound('die', 0.5)
    click_sound = generate_sound('click', 0.3)
    
    core = SnakeGameCore()
    w, h = screen.get_size()
    renderer = SnakeRenderer(screen, w, h)
    
    btn_pause = IconButton(pygame.Rect(w - 60, 20, 40, 40), draw_pause_icon)
    
    running = True
    paused = False
    
    while running:
        w, h = screen.get_size()
        renderer.resize(w, h)
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return screen
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                renderer.resize(event.w, event.h)
            
            if event.type == pygame.KEYDOWN:
                if core.game_over:
                    if event.key == pygame.K_r:
                        core.reset()
                    elif event.key == pygame.K_ESCAPE:
                        return screen
                else:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        core.step(UP)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        core.step(DOWN)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        core.step(LEFT)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        core.step(RIGHT)
                    elif event.key == pygame.K_p:
                        paused = not paused
                    elif event.key == pygame.K_ESCAPE:
                        return screen
                        
        if not paused and not core.game_over:
            state, reward, done, info = core.step()
            if reward > 0 and eat_sound:
                eat_sound.play()
            if done and die_sound:
                die_sound.play()
                
        renderer.draw_state(core.get_state())
        
        # Draw and update pause button
        if not core.game_over:
            btn_pause.rect.topleft = (w - 60, 20)
            btn_pause.update(mouse_pos, mouse_down)
            btn_pause.draw(screen)
            for event in events:
                if btn_pause.is_clicked(event):
                    if click_sound: click_sound.play()
                    paused = not paused
        
        # UI Overlays
        if core.game_over:
            btn = draw_overlay_menu(screen, "Oh Shell!", "Swim Again")
            btn.update(mouse_pos, mouse_down)
            btn.draw(screen)
            for event in events:
                if btn.is_clicked(event):
                    if click_sound: click_sound.play()
                    core.reset()
        elif paused:
            btn = draw_overlay_menu(screen, "PAUSED", "Resume (P)")
            btn.update(mouse_pos, mouse_down)
            btn.draw(screen)
            for event in events:
                if btn.is_clicked(event):
                    if click_sound: click_sound.play()
                    paused = False
            
        pygame.display.flip()
        clock.tick(FPS_HUMAN)
        
    return screen

def play_ai(screen):
    import os
    print("Launching AI visualization...")
    try:
        from stable_baselines3 import PPO
        from snake_env import SnakeEnv
        
        if not os.path.exists("models/snake_model_final.zip"):
            print("Model 'models/snake_model_final.zip' not found.")
            return screen
            
        model = PPO.load("models/snake_model_final.zip")
        env = SnakeEnv(render_mode="human")
        
        obs, info = env.reset()
        done = False
        while not done:
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, done, truncated, info = env.step(action)
            env.render()
            if done or truncated:
                pygame.time.wait(1000)
                obs, info = env.reset()
                done = False
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        env.close()
                        return screen
    except ImportError:
        print("Required libraries for AI not found.")
    except Exception as e:
        print(f"Error running AI: {e}")
    return screen

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    # Initialize resizable screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Snake RL - Signature UI")
    
    while True:
        mode, screen = main_menu(screen)
        if mode == "HUMAN":
            screen = play_human(screen)
        elif mode == "AI":
            screen = play_ai(screen)
