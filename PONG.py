import pygame, sys, random

class Block(pygame.sprite.Sprite):
    def __init__(self, path, x_pos, y_pos):
        super().__init__()
        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect(center=(x_pos, y_pos))

class Player(Block):
    def __init__(self, path, x_pos, y_pos, speed):
        super().__init__(path, x_pos, y_pos)
        self.speed = speed
        self.movement = 0

    def screen_constrain(self):
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= screen_height:
            self.rect.bottom = screen_height

    def update(self, ball_group, game_state):
        if not game_state.is_game_paused():
            self.rect.y += self.movement
            self.screen_constrain()

class Ball(Block):
    def __init__(self, path, x_pos, y_pos, speed_x, speed_y, paddles):
        super().__init__(path, x_pos, y_pos)
        self.speed_x = speed_x * random.choice((-1, 1))
        self.speed_y = speed_y * random.choice((-1, 1))
        self.paddles = paddles
        self.active = False
        self.score_time = 0

    def update(self, game_state):
        if not game_state.is_game_paused() and self.active:
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            self.collisions()
        elif not self.active:
            self.restart_counter()

    def collisions(self):
        if self.rect.top <= 0 or self.rect.bottom >= screen_height:
            pygame.mixer.Sound.play(plob_sound)
            self.speed_y *= -1

        if pygame.sprite.spritecollide(self, self.paddles, False):
            pygame.mixer.Sound.play(plob_sound)
            collision_paddle = pygame.sprite.spritecollide(self, self.paddles, False)[0].rect
            if abs(self.rect.right - collision_paddle.left) < 10 and self.speed_x > 0:
                self.speed_x *= -1
            if abs(self.rect.left - collision_paddle.right) < 10 and self.speed_x < 0:
                self.speed_x *= -1
            if abs(self.rect.top - collision_paddle.bottom) < 10 and self.speed_y < 0:
                self.rect.top = collision_paddle.bottom
                self.speed_y *= -1
            if abs(self.rect.bottom - collision_paddle.top) < 10 and self.speed_y > 0:
                self.rect.bottom = collision_paddle.top
                self.speed_y *= -1

    def reset_ball(self):
        self.active = False
        self.speed_x *= random.choice((-1, 1))
        self.speed_y *= random.choice((-1, 1))
        self.score_time = pygame.time.get_ticks()
        self.rect.center = (screen_width / 2, screen_height / 2)
        pygame.mixer.Sound.play(score_sound)

    def restart_counter(self):
        current_time = pygame.time.get_ticks()
        countdown_number = 3

        if current_time - self.score_time <= 700:
            countdown_number = 3
        if 700 < current_time - self.score_time <= 1400:
            countdown_number = 2
        if 1400 < current_time - self.score_time <= 2100:
            countdown_number = 1
        if current_time - self.score_time >= 2100:
            self.active = True

        time_counter = basic_font.render(str(countdown_number), True, accent_color)
        time_counter_rect = time_counter.get_rect(center=(screen_width / 2, screen_height / 2 + 50))
        time_counter_bg = pygame.Rect(time_counter_rect.topleft, (time_counter_rect.width + 20, time_counter_rect.height + 10))
        pygame.draw.rect(screen, bg_color, time_counter_bg)
        screen.blit(time_counter, time_counter_rect)

class Opponent(Block):
    def __init__(self, path, x_pos, y_pos, speed):
        super().__init__(path, x_pos, y_pos)
        self.speed = speed

    def update(self, ball_group, game_state):
        if not game_state.is_game_paused():
            ball = ball_group.sprites()[0]  # Access the first (and only) ball sprite in the group
            if self.rect.top < ball.rect.y:
                self.rect.y += self.speed
            if self.rect.bottom > ball.rect.y:
                self.rect.y -= self.speed
            self.constrain()

    def constrain(self):
        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= screen_height:
            self.rect.bottom = screen_height

class GameManager:
    def __init__(self, ball_group, paddle_group):
        self.player_score = 0
        self.opponent_score = 0
        self.ball_group = ball_group
        self.paddle_group = paddle_group

    def run_game(self, game_state):
        self.paddle_group.draw(screen)
        self.ball_group.draw(screen)
        self.paddle_group.update(self.ball_group, game_state)
        self.ball_group.update(game_state)
        self.reset_ball()
        self.draw_score()

    def reset_ball(self):
        ball = self.ball_group.sprites()[0]  # Access the first ball sprite
        if ball.rect.right >= screen_width:
            self.opponent_score += 1
            ball.reset_ball()
        if ball.rect.left <= 0:
            self.player_score += 1
            ball.reset_ball()

    def draw_score(self):
        player_score = basic_font.render(str(self.player_score), True, accent_color)
        opponent_score = basic_font.render(str(self.opponent_score), True, accent_color)
        player_score_rect = player_score.get_rect(midleft=(screen_width / 2 + 40, screen_height / 2))
        opponent_score_rect = opponent_score.get_rect(midright=(screen_width / 2 - 40, screen_height / 2))
        screen.blit(player_score, player_score_rect)
        screen.blit(opponent_score, opponent_score_rect)

# New code for the Start Menu
class StartMenu:
    def __init__(self):
        # Load the icon for the start button
        self.start_button_icon = pygame.image.load('start_icon.png')
        self.start_button_icon = pygame.transform.scale(self.start_button_icon, (200, 50))  # Adjust size
        self.start_button_rect = self.start_button_icon.get_rect(center=(screen_width / 2, screen_height / 2))  # Center it

    def draw(self, screen):
        # Draw the start button icon
        screen.blit(self.start_button_icon, self.start_button_rect)

    def handle_events(self, event, game_state):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button_rect.collidepoint(event.pos):
                game_state.change_to_game()  # Transition to the game state

# New Pause, Resume, and End Game Button
class PauseButton:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Load and create the pause button
        self.pause_icon = pygame.image.load('pause_icon.png')
        self.pause_icon = pygame.transform.scale(self.pause_icon, (50, 50))
        self.pause_button_rect = self.pause_icon.get_rect(topleft=(10, 10))
        
        # Load and create the resume button
        self.resume_icon = pygame.image.load('resume_icon.png')
        self.resume_icon = pygame.transform.scale(self.resume_icon, (200, 240))
        self.resume_button_rect = self.resume_icon.get_rect(center=(screen_width / 2, screen_height / 2 - 100))
        
        # Load and create the end game button
        self.end_icon = pygame.image.load('end_game_icon.png')
        self.end_icon = pygame.transform.scale(self.end_icon, (200, 100))
        self.end_button_rect = self.end_icon.get_rect(center=(screen_width / 2, screen_height / 2 + 100))
        
        self.hover_effects = {"pause": False, "resume": False, "end": False}
    
    def draw(self, screen, game_state):
        """Draw buttons based on the game state with hover effects."""
        if game_state.is_game_paused():
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))  # Semi-transparent overlay
            screen.blit(overlay, (0, 0))

            # Apply hover effect
            resume_icon = pygame.transform.scale(self.resume_icon, (220, 250)) if self.hover_effects["resume"] else self.resume_icon
            end_icon = pygame.transform.scale(self.end_icon, (220, 110)) if self.hover_effects["end"] else self.end_icon
            
            screen.blit(resume_icon, self.resume_button_rect.topleft)
            screen.blit(end_icon, self.end_button_rect.topleft)
        else:
            pause_icon = pygame.transform.scale(self.pause_icon, (55, 55)) if self.hover_effects["pause"] else self.pause_icon
            screen.blit(pause_icon, self.pause_button_rect.topleft)
    
    def handle_events(self, event, game_state):
        """Handle button click and hover events."""
        mouse_pos = pygame.mouse.get_pos()

        # Update hover effects
        self.hover_effects["pause"] = self.pause_button_rect.collidepoint(mouse_pos) and not game_state.is_game_paused()
        self.hover_effects["resume"] = self.resume_button_rect.collidepoint(mouse_pos) and game_state.is_game_paused()
        self.hover_effects["end"] = self.end_button_rect.collidepoint(mouse_pos) and game_state.is_game_paused()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.pause_button_rect.collidepoint(event.pos) and not game_state.is_game_paused():
                game_state.toggle_pause()
            elif self.resume_button_rect.collidepoint(event.pos) and game_state.is_game_paused():
                game_state.toggle_pause()
            elif self.end_button_rect.collidepoint(event.pos) and game_state.is_game_paused():
                pygame.quit()
                sys.exit()


class GameState:
    def __init__(self):
        self.state = "start_menu"  # Initially in the start menu
        self.is_paused = False

    def change_to_game(self):
        self.state = "game"  # Switch to the game

    def toggle_pause(self):
        self.is_paused = not self.is_paused  # Toggle pause state

    def get_state(self):
        return self.state

    def is_game_paused(self):
        return self.is_paused

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
clock = pygame.time.Clock()

screen_width = 1280
screen_height = 960
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Pong')

bg_color = pygame.Color('#2F373F')
accent_color = (27, 35, 43)
basic_font = pygame.font.Font('freesansbold.ttf', 32)
plob_sound = pygame.mixer.Sound("pong.ogg")
score_sound = pygame.mixer.Sound("score.ogg")
middle_strip = pygame.Rect(screen_width / 2 - 2, 0, 4, screen_height)

player_paddle = Player('player_paddle.png', screen_width - 20, screen_height / 2, 5)
opponent_paddle = Opponent('opponent_paddle.png', 20, screen_height / 2, 5)
paddle_group = pygame.sprite.Group()
paddle_group.add(player_paddle)
paddle_group.add(opponent_paddle)

ball = Ball('Ball.png', screen_width / 2, screen_height / 2, 4, 4, paddle_group)
ball_sprite = pygame.sprite.GroupSingle()
ball_sprite.add(ball)

game_manager = GameManager(ball_sprite, paddle_group)
start_menu = StartMenu()
pause_button = PauseButton(screen_width, screen_height)
game_state = GameState()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_state.get_state() == 'start_menu':
            start_menu.handle_events(event, game_state)
        elif game_state.get_state() == 'game':
            pause_button.handle_events(event, game_state)
            
            # Handle player movement from the old code
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player_paddle.movement -= player_paddle.speed
                if event.key == pygame.K_DOWN:
                    player_paddle.movement += player_paddle.speed
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    player_paddle.movement += player_paddle.speed
                if event.key == pygame.K_DOWN:
                    player_paddle.movement -= player_paddle.speed

    screen.fill(bg_color)

    if game_state.get_state() == 'start_menu':
        start_menu.draw(screen)  # Ensure the start menu is drawn
    elif game_state.get_state() == 'game':
        pygame.draw.rect(screen, accent_color, middle_strip)
        game_manager.run_game(game_state)
        pause_button.draw(screen, game_state)

    pygame.display.update()
    clock.tick(60)
