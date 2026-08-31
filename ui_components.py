import pygame
import math

# Theme Palette (Coral Reef Catfish Theme)
THEME = {
    "bg.primary": (27, 111, 168),       # #1B6FA8 (Base gradient start)
    "panel.fill": (232, 93, 69),        # #E85D45 (Clamshell Coral tone)
    "panel.border": (255, 233, 214),    # #FFE9D6 (Shell edge)
    "panel.outline": (160, 60, 40),     # Darker clam shadow
    "header.fill": (242, 166, 60),      # #F2A63C
    "cta.primary": (30, 158, 110),      # #1E9E6E (Seafoam Green)
    "cta.border": (15, 110, 72),        # #0F6E48
    "danger": (232, 73, 47),            # #E8492F (Unchanged)
    "text.title.fill": (242, 217, 78),  # #F2D94E (Unchanged)
    "text.title.outline": (31, 61, 90), # #1F3D5A (Deep sea navy)
    "text.body": (255, 255, 255)        # #FFFFFF
}

def render_outlined_text(text, font, fill_color, outline_color, outline_width=3, shadow_offset=(3, 3)):
    """Renders text with a thick outline and drop shadow."""
    text_surf_fill = font.render(text, True, fill_color)
    text_surf_outline = font.render(text, True, outline_color)
    
    width = text_surf_fill.get_width() + outline_width * 2 + shadow_offset[0]
    height = text_surf_fill.get_height() + outline_width * 2 + shadow_offset[1]
    
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Draw drop shadow
    shadow = font.render(text, True, (20, 20, 20))
    surf.blit(shadow, (outline_width + shadow_offset[0], outline_width + shadow_offset[1]))
    
    # Draw outline (stroke)
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx == 0 and dy == 0:
                continue
            surf.blit(text_surf_outline, (outline_width + dx, outline_width + dy))
            
    # Draw fill
    surf.blit(text_surf_fill, (outline_width, outline_width))
    return surf

def draw_panel(screen, rect):
    """Draws a rounded, tactile panel with drop shadow."""
    # Drop shadow
    shadow_rect = rect.copy()
    shadow_rect.y += 8
    pygame.draw.rect(screen, (30, 40, 20, 100), shadow_rect, border_radius=24)
    
    # Outer Outline
    pygame.draw.rect(screen, THEME["panel.outline"], rect, border_radius=24)
    
    # Inner Rim
    inner_rect = rect.inflate(-6, -6)
    pygame.draw.rect(screen, THEME["panel.border"], inner_rect, border_radius=21)
    
    # Fill
    fill_rect = inner_rect.inflate(-6, -6)
    pygame.draw.rect(screen, THEME["panel.fill"], fill_rect, border_radius=18)
    
    # Slight top gradient/highlight simulate
    highlight_rect = pygame.Rect(fill_rect.x, fill_rect.y, fill_rect.width, fill_rect.height // 2)
    highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(highlight_surf, (255, 255, 255, 30), highlight_surf.get_rect(), border_top_left_radius=18, border_top_right_radius=18)
    screen.blit(highlight_surf, highlight_rect)

class CTAButton:
    def __init__(self, rect, text, font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.hovered = False
        self.pressed = False

    def draw(self, screen):
        draw_rect = self.rect.copy()
        
        # Scaling effect on hover/press
        if self.pressed:
            draw_rect = draw_rect.inflate(-4, -4)
        elif self.hovered:
            draw_rect = draw_rect.inflate(4, 4)
            
        color = THEME["cta.primary"]
        if self.hovered and not self.pressed:
            # Lighter on hover
            color = (min(255, color[0]+20), min(255, color[1]+20), min(255, color[2]+20))
            
        # Drop shadow
        if not self.pressed:
            shadow_rect = draw_rect.copy()
            shadow_rect.y += 4
            pygame.draw.rect(screen, (20, 40, 10), shadow_rect, border_radius=draw_rect.height//2)
            
        # Border
        pygame.draw.rect(screen, THEME["cta.border"], draw_rect, border_radius=draw_rect.height//2)
        
        # Fill
        fill_rect = draw_rect.inflate(-6, -6)
        pygame.draw.rect(screen, color, fill_rect, border_radius=fill_rect.height//2)
        
        # Glossy highlight
        if not self.pressed:
            hl_rect = pygame.Rect(fill_rect.x, fill_rect.y, fill_rect.width, fill_rect.height//3)
            hl_surf = pygame.Surface((hl_rect.width, hl_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(hl_surf, (255, 255, 255, 50), hl_surf.get_rect(), border_top_left_radius=fill_rect.height//2, border_top_right_radius=fill_rect.height//2)
            screen.blit(hl_surf, hl_rect)
            
        # Text
        text_surf = self.font.render(self.text, True, THEME["text.body"])
        
        # Subtle drop shadow for text
        text_shadow = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=draw_rect.center)
        screen.blit(text_shadow, (text_rect.x + 1, text_rect.y + 2))
        screen.blit(text_surf, text_rect)

    def update(self, mouse_pos, mouse_down):
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered and mouse_down:
            self.pressed = True
        elif not mouse_down:
            self.pressed = False
            
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.hovered:
                return True
        return False

class IconButton(CTAButton):
    def __init__(self, rect, icon_draw_func):
        # Pass empty string for text, we will draw an icon instead
        super().__init__(rect, "", None)
        self.icon_draw_func = icon_draw_func

    def draw(self, screen):
        draw_rect = self.rect.copy()
        
        # Scaling effect on hover/press
        if self.pressed:
            draw_rect = draw_rect.inflate(-4, -4)
        elif self.hovered:
            draw_rect = draw_rect.inflate(4, 4)
            
        color = THEME["cta.primary"]
        if self.hovered and not self.pressed:
            color = (min(255, color[0]+20), min(255, color[1]+20), min(255, color[2]+20))
            
        radius = draw_rect.width // 2

        # Drop shadow
        if not self.pressed:
            shadow_rect = draw_rect.copy()
            shadow_rect.y += 4
            pygame.draw.rect(screen, (20, 40, 30), shadow_rect, border_radius=radius)
            
        # Border
        pygame.draw.rect(screen, THEME["cta.border"], draw_rect, border_radius=radius)
        
        # Fill
        fill_rect = draw_rect.inflate(-6, -6)
        pygame.draw.rect(screen, color, fill_rect, border_radius=fill_rect.width//2)
        
        # Icon
        self.icon_draw_func(screen, draw_rect.center, draw_rect.width)
