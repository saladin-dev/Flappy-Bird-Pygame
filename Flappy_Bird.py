import pygame
from sys import exit
import random

# -------------------- PLAYER SPRITE CLASS --------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        walk_1 = pygame.image.load('graphics/Player/Flappy_Bird_Bird_Frame_#1.png').convert_alpha()
        walk_2 = pygame.image.load('graphics/Player/Flappy_Bird_Bird_Frame_#2.png').convert_alpha()
        walk_1 = pygame.transform.rotozoom(walk_1, 0, .6)
        walk_2 = pygame.transform.rotozoom(walk_2, 0, .6)
        self.walk_frames = [walk_1, walk_2]
        self.index = 0
        self.jump_image = pygame.image.load('graphics/player/Flappy_Bird_Bird_Frame_#3.png').convert_alpha()
        self.jump_image = pygame.transform.rotozoom(self.jump_image, 0, .6)
        self.image = self.walk_frames[self.index]
        self.rect = self.image.get_rect(midbottom=(80, 450))
        self.gravity = 0
        self.jump_sound = pygame.mixer.Sound('audio/Flappy_Bird_Flight.mp3')
        self.jump_sound.set_volume(0.5)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.gravity = -10
            self.jump_sound.play()

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 600:
            self.rect.bottom = 600

    def animation_state(self):
        if self.gravity < 0:
            self.image = self.jump_image
        else:
            self.index += 0.1
            if self.index >= len(self.walk_frames):
                self.index = 0
            self.image = self.walk_frames[int(self.index)]

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation_state()

# -------------------- PIPE GENERATION --------------------
def Pipe_Genreation():
    random_y = random.randint(0, 300) # Limit max y so pipe always visible
    return random_y

# -------------------- OUTLINED TEXT HELPER FUNCTION --------------------
def render_outlined_text(font, message, text_col, outline_col, pos, outline_thickness=2):
    outline_surf = font.render(message, True, outline_col)
    text_surf = font.render(message, True, text_col)
    outline_rect = outline_surf.get_rect(center=pos)
    for dx in range(-outline_thickness, outline_thickness + 1):
        for dy in range(-outline_thickness, outline_thickness + 1):
            if dx != 0 or dy != 0:
                screen.blit(outline_surf, (outline_rect.x + dx, outline_rect.y + dy))
    screen.blit(text_surf, outline_rect)

# -------------------- HELPER FUNCTION --------------------
def display_score():
    current_time = int(pygame.time.get_ticks() / 1000) - start_time
    render_outlined_text(test_font, f"Score: {current_time}", (255,255,255), (0,0,0), (400, 50), outline_thickness=2)
    return current_time

# -------------------- PYGAME INITIALIZATION --------------------
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
test_font = pygame.font.Font("font/FlappyBirdRegular-9Pq0.ttf", 50)
pipe = pygame.image.load('graphics/green.png').convert_alpha()
pipe_flip = pygame.transform.rotate(pipe, 180)

# -------------------- GAME STATE --------------------
game_active = False
start_time = 0
score = 0

# Initial pipe position
pipe_x_pos = 800  # Start just off the right edge
pipe_y_pos = Pipe_Genreation()
pipe_gap = 10 - pipe_y_pos

# -------------------- PIPE RECT --------------------
pipe_rect = pipe.get_rect(topleft=(pipe_x_pos, pipe_y_pos))
pipe_flip_rect = pipe_flip.get_rect(topleft = (pipe_x_pos , pipe_gap))

# -------------------- SOUND SETUP --------------------
bg_music = [
    pygame.mixer.Sound("audio/Flappy_Bird_BGM_#1.mp3"),
    pygame.mixer.Sound("audio/Flappy_Bird_BGM_#2.mp3"),
    pygame.mixer.Sound("audio/Flappy_Bird_BGM_#3.mp3"),
    pygame.mixer.Sound("audio/Flappy_Bird_BGM_#4.mp3"),
    pygame.mixer.Sound("audio/Flappy_Bird_BGM_#5.mp3"),
    pygame.mixer.Sound("audio/Flappy_Bird_BGM_#6.mp3")
]
current_song = bg_music[0]
current_song.play(loops=-1)

# -------------------- SPRITE GROUPS --------------------
player = pygame.sprite.GroupSingle()
player.add(Player())

# -------------------- GRAPHICS --------------------
sky_surface = pygame.image.load("graphics/8-bit_Sky_Background.png").convert()
intro_bird_img = pygame.image.load("graphics/Player/Flappy_Bird_Bird_Frame_#1.png").convert_alpha()
intro_bird_img = pygame.transform.rotozoom(intro_bird_img, 0, 2.5)
intro_bird_rect = intro_bird_img.get_rect(center=(400, 200))

# -------------------- HITBOX TOGGLE --------------------
show_hitboxes = False

# -------------------- GAME LOOP --------------------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                show_hitboxes = not show_hitboxes  # Toggle hitboxes on/off

            if not game_active:
                if event.key == pygame.K_SPACE:
                    game_active = True
                    start_time = int(pygame.time.get_ticks() / 1000)

            if event.key == pygame.K_e:
                for sound in bg_music:
                    sound.stop()
                current_song = random.choice(bg_music)
                current_song.play(loops=-1)

    # -------------------- ACTIVE GAME --------------------
    if game_active:
        screen.blit(sky_surface, (0, 0))
        score = display_score()

        player.draw(screen)
        player.update()

        # Move pipe from right to left
        pipe_x_pos -= 4

        # Update rect positions
        pipe_rect.topleft = (pipe_x_pos, pipe_y_pos)
        pipe_flip_rect.topleft = (pipe_x_pos , pipe_gap)

        screen.blit(pipe, pipe_rect)
        screen.blit(pipe_flip, pipe_flip_rect)

        # Draw red rects only if toggled on
        if show_hitboxes:
            pygame.draw.rect(screen, (255, 0, 0), player.sprite.rect, 3)
            pygame.draw.rect(screen, (255, 0, 0), pipe_rect, 3)
            pygame.draw.rect(screen, (255, 0, 0), pipe_flip_rect, 3)

        # Reset pipe when off screen
        if pipe_x_pos < -300:
            pipe_x_pos = 800
            pipe_y_pos = Pipe_Genreation()
            pipe_rect.topleft = (pipe_x_pos, pipe_y_pos)

        if player.sprite.rect.colliderect(pipe_flip_rect) or player.sprite.rect.colliderect(pipe_rect):
            print("Player collided with pipe!")

    # -------------------- INACTIVE GAME (INTRO / GAME OVER) --------------------
    else:
        screen.fill((135, 206, 235))
        screen.blit(intro_bird_img, intro_bird_rect)
        render_outlined_text(test_font, "Flappy Bird", (255,255,255), (0,0,0), (400, 80), outline_thickness=3)

        if score == 0:
            render_outlined_text(test_font, "Press space to fly", (255,255,255), (0,0,0), (400, 330), outline_thickness=2)
            render_outlined_text(test_font, "Press E to change song", (255,255,255), (0,0,0), (400, 370), outline_thickness=2)
        else:
            render_outlined_text(test_font, f'Your score: {score}', (255,255,255), (0,0,0), (400, 330), outline_thickness=2)

    pygame.display.update()
    clock.tick(60)
