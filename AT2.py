import pygame
import random
import sys
import json
import os


pygame.init()


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE


BLACK = (0, 0, 0)
GREEN = (0, 255, 65)
RED = (255, 68, 68)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
DARK_GREEN = (0, 128, 32)

INITIAL_SPEED = 8
SPEED_INCREMENT = 0.5
MAX_SPEED = 20
FPS = 60

class Food:
    
    def __init__(self):
        self.position = self.generate_position()
        self.color = RED
    
    def generate_position(self):
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        return (x, y)
    
    def draw(self, screen):
        rect = pygame.Rect(
            self.position[0] * GRID_SIZE,
            self.position[1] * GRID_SIZE,
            GRID_SIZE,
            GRID_SIZE
        )
        pygame.draw.rect(screen, self.color, rect)
        pygame.draw.rect(screen, WHITE, rect, 2)

class Snake:
    
    
    def __init__(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)  
        self.grow_pending = False
        self.color = GREEN
        self.head_color = YELLOW
    
    def move(self):
        
        head_x, head_y = self.positions[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)
        
        
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or 
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            return False
        
        
        if new_head in self.positions:
            return False
        
        self.positions.insert(0, new_head)
        
        if self.grow_pending:
            self.grow_pending = False
        else:
            self.positions.pop()
        
        return True
    
    def change_direction(self, new_direction):
        
        if (new_direction[0] * -1, new_direction[1] * -1) != self.direction:
            self.direction = new_direction
    
    def grow(self):
        
        self.grow_pending = True
    
    def draw(self, screen):
        
        for i, position in enumerate(self.positions):
            rect = pygame.Rect(
                position[0] * GRID_SIZE,
                position[1] * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE
            )
            
            
            if i == 0:
                pygame.draw.rect(screen, self.head_color, rect)
                pygame.draw.rect(screen, WHITE, rect, 2)
            else:
                pygame.draw.rect(screen, self.color, rect)
                pygame.draw.rect(screen, DARK_GREEN, rect, 1)

class Game:
    
    
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Retro Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
        
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.high_score = self.load_high_score()
        self.speed = INITIAL_SPEED
        self.game_over = False
        self.paused = False
        
        
        self.respawn_food()
    
    def load_high_score(self):
        """Load high score from file"""
        try:
            if os.path.exists('high_score.json'):
                with open('high_score.json', 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except:
            pass
        return 0
    
    def save_high_score(self):
        
        try:
            with open('high_score.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass
    
    def respawn_food(self):
        
        while self.food.position in self.snake.positions:
            self.food.position = self.food.generate_position()
    
    def handle_events(self):
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.restart_game()
                    elif event.key == pygame.K_ESCAPE:
                        return False
                else:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.snake.change_direction((0, -1))
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.snake.change_direction((0, 1))
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.snake.change_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.snake.change_direction((1, 0))
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_ESCAPE:
                        return False
        
        return True
    
    def update(self):
        
        if self.game_over or self.paused:
            return
        
        if not self.snake.move():
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            return
        
        
        if self.snake.positions[0] == self.food.position:
            self.snake.grow()
            self.score += 10
            self.respawn_food()
            
            if self.speed < MAX_SPEED:
                self.speed += SPEED_INCREMENT
    
    def draw(self):
        
        self.screen.fill(BLACK)
        
        
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        
        
        self.draw_ui()
        
        if self.game_over:
            self.draw_game_over()
        elif self.paused:
            self.draw_pause_screen()
        
        pygame.display.flip()
    
    def draw_ui(self):
        
        
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        
        high_score_text = self.font.render(f"High Score: {self.high_score}", True, WHITE)
        self.screen.blit(high_score_text, (10, 50))
        
        
        speed_text = self.font.render(f"Speed: {self.speed:.1f}", True, WHITE)
        self.screen.blit(speed_text, (WINDOW_WIDTH - 150, 10))
        
        
        length_text = self.font.render(f"Length: {len(self.snake.positions)}", True, WHITE)
        self.screen.blit(length_text, (WINDOW_WIDTH - 150, 50))
    
    def draw_game_over(self):
        
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.big_font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        self.screen.blit(game_over_text, text_rect)
        
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(score_text, score_rect)
        
        if self.score == self.high_score and self.score > 0:
            new_high_text = self.font.render("NEW HIGH SCORE!", True, YELLOW)
            high_rect = new_high_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 10))
            self.screen.blit(new_high_text, high_rect)
        
        restart_text = self.font.render("Press SPACE to restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
        
        quit_text = self.font.render("Press ESC to quit", True, WHITE)
        quit_rect = quit_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 90))
        self.screen.blit(quit_text, quit_rect)
    
    def draw_pause_screen(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.big_font.render("PAUSED", True, YELLOW)
        text_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(pause_text, text_rect)
        
        continue_text = self.font.render("Press SPACE to continue", True, WHITE)
        continue_rect = continue_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(continue_text, continue_rect)
    
    def restart_game(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.speed = INITIAL_SPEED
        self.game_over = False
        self.paused = False
        self.respawn_food()
    
    def run(self):
        print("🐍 Retro Snake Game Started!")
        print("Controls:")
        print("  Arrow Keys or WASD - Move")
        print("  SPACE - Pause/Unpause")
        print("  ESC - Quit")
        print("\nGood luck!")
        
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.speed)
        
        pygame.quit()
        sys.exit()

def main():
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()