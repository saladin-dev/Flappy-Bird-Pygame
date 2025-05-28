import pygame
from sys import exit
import random

# -------------------- PLAYER SPRITE CLASS --------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Load and scale walking frames
        walk_1 = pygame.image.load('graphics/Player/Flappy_Bird_Bird_Frame_#1.png').convert_alpha()
        walk_2 = pygame.image.load('graphics/Player/Flappy_Bird_Bird_Frame_#2.png').convert_alpha()
        walk_1 = pygame.transform.rotozoom(walk_1, 0, .6)
        walk_2 = pygame.transform.rotozoom(walk_2, 0, .6)
        self.walk_frames = [walk_1, walk_2]
        self.index = 0

        # Load and scale jump image
        self.jump_image = pygame.image.load('graphics/player/Flappy_Bird_Bird_Frame_#3.png').convert_alpha()
        self.jump_image = pygame.transform.rotozoom(self.jump_image, 0, .6)

        # Set initial image and position
        self.image = self.walk_frames[self.index]
        self.rect = self.image.get_rect(midbottom=(80, 450))

        # Gravity
        self.gravity = 0

        # Jump sound
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

# -------------------- PIPE GENREATION --------------------
random_x = 0
random_y = 0
def Pipe_Genreation():
    random_x = random.randint(900, 0 )
    random_y = random.randint(0, 500)
    return random_x, random_y

# -------------------- OUTLINED TEXT HELPER FUNCTION --------------------
def render_outlined_text(font, message, text_col, outline_col, pos, outline_thickness=2):
    # I wrote this function to draw text with a black outline and white fill.
    outline_surf = font.render(message, True, outline_col)
    text_surf = font.render(message, True, text_col)
    outline_rect = outline_surf.get_rect(center=pos)
    # I blit the outline text in all directions around the main text
    for dx in range(-outline_thickness, outline_thickness + 1):
        for dy in range(-outline_thickness, outline_thickness + 1):
            if dx != 0 or dy != 0:
                screen.blit(outline_surf, (outline_rect.x + dx, outline_rect.y + dy))
    # I blit the main (white) text on top
    screen.blit(text_surf, outline_rect)

# -------------------- HELPER FUNCTION --------------------
def display_score():
    current_time = int(pygame.time.get_ticks() / 1000) - start_time
    # Instead of rendering with normal font, I use my outlined text function
    render_outlined_text(test_font, f"Score: {current_time}", (255,255,255), (0,0,0), (400, 50), outline_thickness=2)
    return current_time

# -------------------- PYGAME INITIALIZATION --------------------
pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
test_font = pygame.font.Font("font/FlappyBirdRegular-9Pq0.ttf", 50)
# Load the pipe image
pipe = pygame.image.load('graphics/green.png').convert_alpha()



# -------------------- GAME STATE --------------------
game_active = False
start_time = 0
score = 0

# -------------------- SOUND SETUP --------------------
import random

bg_music = [
    pygame.mixer.Sound("audio/Flappy_Bird_BGM_#1.mp3"),
    pygame.mixer.Sound("audio/Flappy_Bird_BGM_#2.mp3"),
    pygame.mixer.Sound("audio/Flappy_Bird_BGM_#3.mp3"),
    pygame.mixer.Sound("audio/Flappy_Bird_BGM_#4.mp3"),
    pygame.mixer.Sound("audio/Flappy_Bird_BGM_#5.mp3"),
    pygame.mixer.Sound("audio/Flappy_Bird_BGM_#6.mp3")
]

# Play the first song
current_song = bg_music[0]
current_song.play(loops=-1)
                

# -------------------- SPRITE GROUPS --------------------
player = pygame.sprite.GroupSingle()
player.add(Player())



# -------------------- GRAPHICS --------------------
sky_surface = pygame.image.load("graphics/8-bit_Sky_Background.png").convert()

# For the intro/game over, I use the player frame instead of player_stand, and scale it up
intro_bird_img = pygame.image.load("graphics/Player/Flappy_Bird_Bird_Frame_#1.png").convert_alpha()
intro_bird_img = pygame.transform.rotozoom(intro_bird_img, 0, 2.5)  # I scale it bigger
intro_bird_rect = intro_bird_img.get_rect(center=(400, 200))

# -------------------- GAME LOOP --------------------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if not game_active:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_active = True
                start_time = int(pygame.time.get_ticks() / 1000)

                        # Music switching with E
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
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
        screen.blit(pipe, (random_x, random_y))


    # -------------------- INACTIVE GAME (INTRO / GAME OVER) --------------------
    else:
        # I set the background color to yellow for intro/score screen
        screen.fill((135, 206, 235))  # Softer pastel yellow background
  

        # I use the larger bird frame as the stand-in
        screen.blit(intro_bird_img, intro_bird_rect)

        # Outlined title, message, and score text
        render_outlined_text(test_font, "Flappy Bird", (255,255,255), (0,0,0), (400, 80), outline_thickness=3)

        if score == 0:
            render_outlined_text(test_font, "Press space to fly", (255,255,255), (0,0,0), (400, 330), outline_thickness=2)
            render_outlined_text(test_font, "Press E to change song", (255,255,255), (0,0,0), (400, 370), outline_thickness=2)
        else:
            render_outlined_text(test_font, f'Your score: {score}', (255,255,255), (0,0,0), (400, 330), outline_thickness=2)

    pygame.display.update()
    clock.tick(60)
