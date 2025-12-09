import pygame
import sys
import random

# initialize pygame
pygame.init()

# screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700

# high score for the session
GLOBAL_HIGH_SCORE = 0

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (204, 102, 0)

# create screen and game setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Pinball Machine")
clock = pygame.time.Clock()
FPS = 60

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 8
        self.vel_x = 0
        self.vel_y = 0
        self.gravity = 0.5
        self.active = True
    
    def update(self):
        # apply gravity
        self.vel_y += self.gravity
        
        # update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # bounce off walls
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vel_x = -self.vel_x * 0.5
        if self.x + self.radius > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.radius
            self.vel_x = -self.vel_x * 0.5
        
        # bounce off top
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vel_y = -self.vel_y * 0.5
        
        # ball falls off bottom (game over for that ball)
        if self.y > SCREEN_HEIGHT:
            self.active = False
    
    def draw(self, screen):
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y)), self.radius)

class Paddle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 110
        self.height = 12
        self.vel_x = 0
    
    def update(self):
        # update position with velocity
        self.x += self.vel_x
        
        # prevent paddle from leaving screen
        if self.x < 0:
            self.x = 0
        if self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
    
    def draw(self, screen):
        # draw the paddle
        pygame.draw.rect(screen, ORANGE, (self.x, self.y, self.width, self.height))

class Brick:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
    
    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, self.rect)

class BallGame:
    def __init__(self):
        self.score = 0
        self.game_over = False
        # place paddle centered horizontally using its width
        self.paddle = Paddle(SCREEN_WIDTH // 2 - 55, SCREEN_HEIGHT - 30)
        # put ball above paddle and launch upwards at start
        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40)
        self.ball.vel_y = -28
        self.bricks = []
        self.generate_random_bricks()
    
    def generate_single_brick(self):
        # generate a single brick at a random position without overlapping existing bricks
        brick_width = 40
        brick_height = 25
        upper_half_height = SCREEN_HEIGHT // 2
        
        # check for overlaps and retry as necessary
        max_attempts = 100
        for _ in range(max_attempts):
            x = random.randint(0, SCREEN_WIDTH - brick_width)
            y = random.randint(50, upper_half_height - brick_height)
            new_rect = pygame.Rect(x, y, brick_width, brick_height)
            
            overlap = False
            if hasattr(self, 'bricks'):
                for existing_brick in self.bricks:
                    if new_rect.colliderect(existing_brick.rect):
                        overlap = True
                        break
            
            if not overlap:
                return Brick(x, y, brick_width, brick_height)
        
        return None
    
    def generate_random_bricks(self):
        # generate 7 bricks at random positions in upper half of screen without overlapping
        for _ in range(7):
            brick = self.generate_single_brick()
            if brick:
                self.bricks.append(brick)
    
    
    def check_collisions(self):
        # handle paddle collisions and brick collisions
        paddle_rect = pygame.Rect(self.paddle.x, self.paddle.y, 
                                   self.paddle.width, self.paddle.height)
        
        if (self.ball.x > paddle_rect.left and 
            self.ball.x < paddle_rect.right and
            self.ball.y + self.ball.radius > paddle_rect.top and
            self.ball.y - self.ball.radius < paddle_rect.bottom):
            
            self.ball.vel_y = -abs(self.ball.vel_y) * 1.05
            self.ball.y = paddle_rect.top - self.ball.radius
            self.score += 5
            
            # add angle based on where ball hits on paddle
            paddle_center = paddle_rect.left + paddle_rect.width / 2
            distance_from_center = self.ball.x - paddle_center

            if abs(distance_from_center) <= 3:
                self.ball.vel_x = 0
            else:
                # angled bounce scales with paddle width so feel stays consistent
                divisor = paddle_rect.width / 2 - 5
                angle_factor = max(-1, min(1, distance_from_center / divisor))
                self.ball.vel_x = angle_factor * 9

            # add spin if paddle is moving
            self.ball.vel_x += self.paddle.vel_x * 0.3
        
        # check collision with bricks
        for brick in self.bricks[:]:
            if (self.ball.x > brick.rect.left - self.ball.radius and 
                self.ball.x < brick.rect.right + self.ball.radius and
                self.ball.y > brick.rect.top - self.ball.radius and 
                self.ball.y < brick.rect.bottom + self.ball.radius):
                
                # reverse both directions
                self.ball.vel_x = -self.ball.vel_x
                self.ball.vel_y = -self.ball.vel_y
                
                # dampen speed if hit from bottom edge
                if self.ball.y > brick.rect.bottom - 5:
                    speed = (self.ball.vel_x ** 2 + self.ball.vel_y ** 2) ** 0.5
                    if speed > 0:
                        self.ball.vel_x = (self.ball.vel_x / speed) * speed * 0.7
                        self.ball.vel_y = (self.ball.vel_y / speed) * speed * 0.6
                # boost speed if hit from top edge
                elif self.ball.y < brick.rect.top + 5:
                    self.ball.vel_x *= 1.4
                    self.ball.vel_y *= 1.4
                
                self.score += 100
                
                # remove brick and respawn a new one
                self.bricks.remove(brick)
                new_brick = self.generate_single_brick()
                if new_brick:
                    self.bricks.append(new_brick)
                break
    
    def update(self):
        # update game objects and check for game over
        if not self.game_over and self.ball.active:
            self.ball.update()
            self.paddle.update()
            self.check_collisions()
        elif not self.game_over and not self.ball.active:
            global GLOBAL_HIGH_SCORE
            if self.score > GLOBAL_HIGH_SCORE:
                GLOBAL_HIGH_SCORE = self.score
            self.game_over = True
    
    def draw(self):
        screen.fill(BLACK)
        
        # draw game objects
        self.ball.draw(screen)
        self.paddle.draw(screen)
        for brick in self.bricks:
            brick.draw(screen)
        
        # draw ui
        font = pygame.font.Font(None, 36)
        high_score_text = font.render(f"High Score: {GLOBAL_HIGH_SCORE}", True, WHITE)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(high_score_text, (10, 10))
        screen.blit(score_text, (10, 40))

        # draw game over screen
        if self.game_over:
            game_over_text = font.render("GAME OVER!", True, RED)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(game_over_text, game_over_rect)

            small_font = pygame.font.Font(None, 24)
            high_score_final = small_font.render(f"High Score: {GLOBAL_HIGH_SCORE}", True, WHITE)
            restart_text = small_font.render("Press R to restart", True, WHITE)
            high_score_rect = high_score_final.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
            screen.blit(high_score_final, high_score_rect)
            screen.blit(restart_text, restart_rect)

        pygame.display.flip()
    
    def handle_input(self):
        # poll user input events and move paddle or request restart/quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.paddle.vel_x = -12
                if event.key == pygame.K_RIGHT:
                    self.paddle.vel_x = 12
                if event.key == pygame.K_r and self.game_over:
                    return "restart"
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    self.paddle.vel_x = 0
        return True
    
    def run(self):
        # main loop to run the game. handle input, update, draw at fixed framerate
        running = True
        while running:
            result = self.handle_input()
            if result == False:
                running = False
            elif result == "restart":
                return True

            self.update()
            self.draw()
            clock.tick(FPS)
        return False

def main():
    restart = True
    while restart:
        game = BallGame()
        restart = game.run() # runs again if user wants to restart
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
