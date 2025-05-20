import pygame
import sys
import random
import os

# Initialize Pygame
pygame.init() # Keep this at the very top

# --- Game Constants ---
SCREEN_WIDTH = 400  # Your requested window width
SCREEN_HEIGHT = 600 # Your requested window height
FPS = 60
GRAVITY = 0.25
BIRD_JUMP_STRENGTH = -7  # How much the bird jumps (negative Y is up)
PIPE_SPEED = 3
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # milliseconds between new pipe spawns

# Target sizes for scaled images
TARGET_BIRD_SIZE = (48, 34) # Scaled bird size (adjust if needed)
TARGET_PIPE_WIDTH = 52 # Scaled pipe width (adjust if needed)
TARGET_FLOOR_WIDTH = SCREEN_WIDTH # Floor width matches screen width

# --- Game States ---
GAME_STATE_START = 'start'
GAME_STATE_PLAYING = 'playing'
GAME_STATE_GAME_OVER = 'game_over'

# --- Asset Paths ---
# Assumes the script is inside the 'Code' folder, and 'graphics', 'audio', 'font' are subdirs of 'Code'
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
GRAPHICS_PATH = os.path.join(BASE_PATH, 'graphics')
PLAYER_GRAPHICS_PATH = os.path.join(GRAPHICS_PATH, 'Player')
AUDIO_PATH = os.path.join(BASE_PATH, 'audio')
FONT_PATH = os.path.join(BASE_PATH, 'font')

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird Clone')
clock = pygame.time.Clock()

# --- Helper Functions for Asset Loading ---
def load_image(path, alpha=True):
    """Loads and converts an image from the specified path."""
    full_path = path
    try:
        image = pygame.image.load(full_path)
        if image is None: 
             print(f"Warning: pygame.image.load returned None for {full_path}")
             return None 

        if alpha:
            image = image.convert_alpha() # For images with transparency (Bird, Pipes)
        else:
            image = image.convert() # For fully opaque images (Background, Floor)
            
        print(f"Successfully loaded image: {full_path}, Original Size: {image.get_size()}, Alpha: {alpha}") 
        return image
    except pygame.error as e:
        print(f"Critical Error loading image {full_path}: {e}") 
        pygame.quit() 
        sys.exit()
    except FileNotFoundError:
        print(f"Critical Error: Image file not found: {full_path}")
        print(f"Ensure '{os.path.basename(full_path)}' is in '{os.path.dirname(full_path)}'")
        pygame.quit()
        sys.exit()

def load_sound(path):
    """Loads a sound file."""
    full_path = path
    try:
        # Initialize mixer safely - required for sounds and music
        if not pygame.mixer.get_init(): 
             pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
             print("Info: pygame.mixer initialized in load_sound.")

        sound = pygame.mixer.Sound(full_path)
        print(f"Successfully loaded sound: {full_path}") 
        return sound
    except pygame.error as e:
        print(f"Error loading sound {full_path}: {e}") 
        return None # Return None on non-critical sound load failure
    except FileNotFoundError:
        print(f"Error: Sound file not found: {full_path}") 
        return None

def load_font(path, size):
    """Loads a font file."""
    full_path = path
    try:
        font = pygame.font.Font(full_path, size)
        print(f"Successfully loaded font: {full_path}, Size: {size}") 
        return font
    except pygame.error as e:
        print(f"Critical Error loading font {full_path}: {e}")
        pygame.quit() 
        sys.exit()
    except FileNotFoundError:
        print(f"Critical Error: Font file not found: {full_path}")
        print(f"Ensure '{os.path.basename(full_path)}' is in '{os.path.dirname(full_path)}'")
        pygame.quit()
        sys.exit()

# --- Load & Scale Assets ---

# Background - Load *without* alpha, scale to screen size
bg_surface_orig = load_image(os.path.join(GRAPHICS_PATH, '8-bit_Sky_Background.png'), alpha=False) 
bg_surface = None 
if bg_surface_orig:
     try:
         bg_surface = pygame.transform.scale(bg_surface_orig, (SCREEN_WIDTH, SCREEN_HEIGHT))
         print(f"Scaled background to: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
     except pygame.error as e:
          print(f"Error scaling background image: {e}")

# Floor - Load *without* alpha, scale width to screen width, preserve aspect ratio
floor_surface_orig = load_image(os.path.join(GRAPHICS_PATH, '8-bit_Ground_Surface.png'), alpha=False)
floor_surface = None 
# Default fallback position and height in case floor asset fails
FLOOR_Y_POS = SCREEN_HEIGHT - 100 
floor_height = 100 
if floor_surface_orig:
     try:
         original_w, original_h = floor_surface_orig.get_size()
         if original_w > 0: 
             # Calculate proportional height based on target width
             scaled_h = int(original_h * (TARGET_FLOOR_WIDTH / original_w))
             
             # Prevent floor from being ridiculously tall or too short
             if scaled_h > SCREEN_HEIGHT / 3: 
                 scaled_h = int(SCREEN_HEIGHT / 3)
                 print(f"Warning: Scaled floor height capped at {scaled_h}.")
             elif scaled_h == 0: # Ensure minimum height if original is flat
                  scaled_h = 20 
                  print("Warning: Scaled floor height was 0, set to minimum 20.")

             floor_surface = pygame.transform.scale(floor_surface_orig, (TARGET_FLOOR_WIDTH, scaled_h))
             floor_height = scaled_h # Store actual scaled height
             FLOOR_Y_POS = SCREEN_HEIGHT - floor_height # Calculate position based on scaled height
             print(f"Scaled floor to: {TARGET_FLOOR_WIDTH}x{floor_height}, Calculated FLOOR_Y_POS: {FLOOR_Y_POS}")
         except (ValueError, pygame.error) as e: 
             print(f"Error scaling floor image: {e}")
             print("Warning: Using estimated FLOOR_Y_POS/height due to floor asset loading/scaling failure.")


# Bird Animation Frames - Load *with* alpha, SCALE each frame
bird_frame_paths = [
    os.path.join(PLAYER_GRAPHICS_PATH, 'Flappy_Bird_Bird_Frame_#1.png'),
    os.path.join(PLAYER_GRAPHICS_PATH, 'Flappy_Bird_Bird_Frame_#2.png'),
    os.path.join(PLAYER_GRAPHICS_PATH, 'Flappy_Bird_Bird_Frame_#3.png')
]

loaded_bird_frames = [load_image(p) for p in bird_frame_paths] 

bird_frames = [] 
for frame in loaded_bird_frames:
    if frame: 
        try:
            # SCALE THE IMAGE HERE
            scaled_frame = pygame.transform.scale(frame, TARGET_BIRD_SIZE)
            bird_frames.append(scaled_frame)
            # print(f"Scaled a bird frame to: {TARGET_BIRD_SIZE}") # Muted, can be spammy
        except pygame.error as e:
             print(f"Error scaling bird frame: {e}")
             bird_frames.append(None) # Append None if scaling fails
    else:
         bird_frames.append(None) # Append None if loading failed


# Pipe Surface (Using 'green.png') - Load *with* alpha, SCALE IT
pipe_surface_orig = load_image(os.path.join(GRAPHICS_PATH, 'green.png'), alpha=True)
pipe_surface = None # We will use this as the base surface for pipes
if pipe_surface_orig:
    try:
        original_w, original_h = pipe_surface_orig.get_size()
        if original_w > 0: 
             # Scale pipe based on TARGET_PIPE_WIDTH, height doesn't matter here as we scale it for drawing
             # based on the size of the rects, but let's keep the proportional calculation for a base
             scaled_h = int(original_h * (TARGET_PIPE_WIDTH / original_w))
             pipe_surface = pygame.transform.scale(pipe_surface_orig, (TARGET_PIPE_WIDTH, scaled_h)) # Scale to a base size
             print(f"Scaled pipe base surface to: {TARGET_PIPE_WIDTH}x{scaled_h}")
        else:
            print("Warning: Original pipe image has zero width, cannot scale.")
    except (ValueError, pygame.error) as e:
        print(f"Error scaling pipe image: {e}")


# --- Font ---
game_font = load_font(os.path.join(FONT_PATH, 'Pixeltype.ttf'), 48) # Keeping base code font size


# --- Sounds ---
sound_flap = load_sound(os.path.join(AUDIO_PATH, 'Flappy_Bird_Flight.mp3'))
sound_death = load_sound(os.path.join(AUDIO_PATH, 'Flappy_Bird_Death.mp3'))
sound_score_point = load_sound(os.path.join(AUDIO_PATH, 'Flappy_Bird_Point_Score.mp3'))

# Background Music
bgm_path = os.path.join(AUDIO_PATH, 'Flappy_Bird_BGM_#1.mp3')
bgm_loaded = False
if os.path.exists(bgm_path):
    try:
        pygame.mixer.music.load(bgm_path) 
        pygame.mixer.music.set_volume(0.15)
        bgm_loaded = True
        print(f"Successfully loaded BGM: {bgm_path}")
    except pygame.error as e:
         print(f"Error loading BGM {bgm_path}: {e}")
else:
    print(f"Warning: Background music file not found at {bgm_path}")


# --- Game Timer Events ---
SPAWNPIPE_EVENT = pygame.USEREVENT 
BIRDFLAP_EVENT = pygame.USEREVENT + 1 # Custom event for bird animation


# --- Bird Class (Adapted) ---
class Bird:
    def __init__(self, frames, initial_pos):
        # Check if frames are valid *after* loading/scaling
        if not frames or not all(isinstance(f, pygame.Surface) for f in frames):
             print("Critical Error: Bird frames list is invalid or empty for Bird init.")
             # Create dummy surface to avoid errors later
             self.image = pygame.Surface(TARGET_BIRD_SIZE, pygame.SRCALPHA) 
             self.image.fill((255,0,0, 100)) # Semi-transparent red square fallback
             self.rect = self.image.get_rect(center=initial_pos)
             self.frames = [self.image] # Use dummy frame
             return 

        self.frames = frames # List of animation surfaces (already scaled)
        self.animation_index = 0
        self.image = self.frames[self.animation_index] # Current active surface
        self.rect = self.image.get_rect(center=initial_pos) # Collision rectangle
        self.velocity = 0 # Vertical speed
        self.angle = 0 # For rotation

        # Start the bird animation timer here if bird was successfully created
        pygame.time.set_timer(BIRDFLAP_EVENT, 150) # 150 ms per frame

    def jump(self):
        self.velocity = BIRD_JUMP_STRENGTH # Use the negative JUMP_SPEED constant

    def update(self):
        self.velocity += GRAVITY
        self.rect.centery += int(self.velocity) # Update position based on velocity
        
        # Update rotation based on velocity
        self.angle = max(-70, min(30, -self.velocity * 4))

    def animate(self):
        """Advances the animation frame."""
        self.animation_index = (self.animation_index + 1) % len(self.frames)
        self.image = self.frames[self.animation_index]

    def draw(self, surface):
        # Use rotozoom for smooth rotation
        if self.image is None: return # Don't draw if image is invalid

        rotated_bird = pygame.transform.rotozoom(self.image, self.angle, 1)
        # Get the rect of the rotated image and center it on the original bird_rect
        rotated_rect = rotated_bird.get_rect(center = self.rect.center)
        
        surface.blit(rotated_bird, rotated_rect) # Draw using the calculated rect

# --- Pipe Management (Using Rects) ---
# We'll manage pipes as a list of tuples containing rects and a scored flag

# Note: This function now returns a tuple of rects and a flag, not a Pipe instance
def create_pipes(pipe_surface, screen_w, screen_h, floor_y_pos, gap_size):
    """Creates a pair of pipe rects (top and bottom) with a random gap position."""
    if pipe_surface is None: 
         print("Warning: Cannot create pipes, pipe_surface is None.")
         return None 

    # Calculate the available height for the gap (between roof and floor)
    available_height = screen_h - floor_y_pos
    
    # Define vertical range for the gap center, ensuring pipes don't spawn too close to roof/floor edges
    min_gap_center_y = gap_size // 2 + 60 
    max_gap_center_y = floor_y_pos - gap_size // 2 - 60 # Gap center must be above the floor top
    
    # Ensure the range is valid; if not, center the gap in the available space
    if min_gap_center_y >= max_gap_center_y: 
        # Fallback: if the gap is too big or screen is too small, center the gap above the floor
        # print(f"Warning: Pipe gap range invalid. Min: {min_gap_center_y}, Max: {max_gap_center_y}. Centering gap.") # Mute spam
        gap_center_y = floor_y_pos - available_height // 2 
        # Ensure it's still within basic screen bounds if floor is high
        gap_center_y = max(gap_center_y, gap_size // 2 + 20)
        gap_center_y = min(gap_center_y, screen_h - gap_size // 2 - 20)
    else:
        gap_center_y = random.randint(min_gap_center_y, max_gap_center_y)

    # Calculate top and bottom pipe y positions based on the gap center
    top_pipe_bottom_y = gap_center_y - gap_size // 2
    bottom_pipe_top_y = gap_center_y + gap_size // 2

    # Create the pipe rects, using the scaled pipe surface's width
    pipe_width = pipe_surface.get_width()
    top_pipe_rect = pygame.Rect(SCREEN_WIDTH + 60, 0, pipe_width, top_pipe_bottom_y) # Top pipe extends from top to bottom_y
    bottom_pipe_rect = pygame.Rect(SCREEN_WIDTH + 60, bottom_pipe_top_y, pipe_width, SCREEN_HEIGHT - bottom_pipe_top_y - (SCREEN_HEIGHT - floor_y_pos)) # Bottom pipe from top_y to floor top

    return top_pipe_rect, bottom_pipe_rect, False # Return rects and a 'scored' flag (False initially)

def move_pipe_rects(pipes, speed):
    """Moves pipes to the left and returns a new list of on-screen pipes."""
    new_pipes = []
    for pipe_pair in pipes:
        if pipe_pair is not None:
            top_rect, bottom_rect, scored = pipe_pair
            top_rect.centerx -= speed
            bottom_rect.centerx -= speed
            # Keep pipes until they are completely off screen to the left (e.g., 20 pixels margin)
            if top_rect.right > -20: 
                new_pipes.append(pipe_pair)
    return new_pipes

def draw_pipe_surfaces(surface, pipes, pipe_surface_orig):
    """Draws all pipes using the original scaled pipe surface."""
    if pipe_surface_orig is None:
        return 

    # Create a flipped version of the original scaled pipe surface for the top pipe
    flipped_pipe_surface_orig = pygame.transform.flip(pipe_surface_orig, False, True)

    for pipe_pair in pipes:
        if pipe_pair is not None:
             top_rect, bottom_rect, _ = pipe_pair
             
             # Scale the original pipe surface to the height of the current top pipe rect
             try:
                scaled_top_pipe_surface = pygame.transform.scale(flipped_pipe_surface_orig, (top_rect.width, top_rect.height))
                surface.blit(scaled_top_pipe_surface, top_rect)
             except pygame.error as e:
                 print(f"Warning: Error scaling top pipe surface for drawing: {e}")


             # Scale the original pipe surface to the height of the current bottom pipe rect for drawing
             try:
                scaled_bottom_pipe_surface = pygame.transform.scale(pipe_surface_orig, (bottom_rect.width, bottom_rect.height))
                surface.blit(scaled_bottom_pipe_surface, bottom_rect)
             except pygame.error as e:
                print(f"Warning: Error scaling bottom pipe surface for drawing: {e}")


def check_collisions(bird_rect, pipes, screen_h, floor_y_pos):
    """Checks for collisions between the bird rect and pipes, screen boundaries, or floor."""
    # Check collisions with each pipe pair
    for pipe_pair in pipes:
        if pipe_pair is not None:
             top_rect, bottom_rect, _ = pipe_pair
             # Use the colliderect method of the bird's rect with each pipe rect
             if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                 return True # Collision detected

    # Check collision with the top screen boundary or the floor's top edge
    if bird_rect.top <= 0 or bird_rect.bottom >= floor_y_pos:
        return True # Collision detected
        
    return False # No collision detected


def update_high_score(current_score, high_score_val):
    """Updates high score if the current score is higher."""
    return max(current_score, high_score_val)

def manage_scoring(bird_rect, pipes, current_score, score_snd):
    """Checks if the bird has passed a pipe that hasn't been scored yet and updates score."""
    new_score = current_score
    updated_pipes = [] # Build a new list of pipes with updated 'scored' flags
    scored_this_frame = False # Flag to ensure score sound only plays once per frame

    for pipe_pair in pipes:
        if pipe_pair is not None:
            top_rect, bottom_rect, scored_flag = pipe_pair
            # Score when the pipe's right edge passes the bird's center x AND hasn't been scored
            # Added check that pipe is reasonably on screen to prevent scoring before pipes are visible
            if not scored_flag and bottom_rect.right < bird_rect.centerx and bottom_rect.right > 0: 
                if score_snd and not scored_this_frame: 
                    score_snd.play() 
                    scored_this_frame = True 
                new_score += 1 
                updated_pipes.append((top_rect, bottom_rect, True)) # Mark as scored
            else:
                updated_pipes.append(pipe_pair)
            
    return new_score, updated_pipes 

# --- Drawing Functions ---

def draw_background(surface, bg_surf):
    """Draws the background image or fallback color."""
    if bg_surf:
        surface.blit(bg_surf, (0, 0))
    else:
         surface.fill((135, 206, 235)) # Sky blue fallback


def draw_floor(surface, floor_surf, x_pos, y_pos):
    """Draws the scrolling floor."""
    if floor_surf is None:
        return
    # Draw two copies side-by-side for scrolling
    surface.blit(floor_surf, (x_pos, y_pos))
    surface.blit(floor_surf, (x_pos + floor_surf.get_width(), y_pos))

def display_score(surface, font, score):
    """Renders and displays the current score."""
    if font is None: return 
    score_surf = font.render(f'{score}', True, (255, 255, 255)) # White text
    score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, 50))
    surface.blit(score_surf, score_rect)

def display_game_over(surface, font, score, high_score):
    """Renders and displays the game over screen."""
    if font is None: return 

    # Use a semi-transparent overlay to make text stand out
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180)) # Black with 180 alpha (0-255)
    surface.blit(overlay, (0, 0))

    game_over_surf = font.render('Game Over!', True, (255, 0, 0)) # Red color
    game_over_rect = game_over_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    surface.blit(game_over_surf, game_over_rect)
    
    score_text = font.render(f'Score: {score}', True, (255, 255, 255))
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    surface.blit(score_text, score_rect)
    
    high_score_text = font.render(f'Best: {high_score}', True, (255, 255, 255))
    high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
    surface.blit(high_score_text, high_score_rect)
    
    prompt_text = font.render('Press SPACE or CLICK to Play!', True, (255, 255, 255))
    prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH // 2, WINDOW_HEIGHT * 2 // 3))
    surface.blit(prompt_text, prompt_rect)


def display_start_screen(surface, font, bird_surface):
    """Renders and displays the initial start screen."""
    if font is None: return
    
    # Display bird image with a slight bobbing effect on the start screen
    if bird_surface is not None: 
        bob_offset_y = int(5 * pygame.math.Vector2(0,1).rotate(pygame.time.get_ticks()*0.05).y) 
        temp_bird_start_pos = (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2 + bob_offset_y)
        temp_bird_start_rect = bird_surface.get_rect(center=temp_bird_start_pos) 
        surface.blit(bird_surface, temp_bird_start_rect) 

    # Title Text
    title_surf = font.render("Flappy Bird", True, (255,215,0)) # Gold color
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    surface.blit(title_surf, title_rect)

    # Start Message Text
    start_msg_surf = font.render("Press SPACE or CLICK to Start", True, (255, 255, 255))
    start_msg_rect = start_msg_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)) 
    surface.blit(start_msg_surf, start_msg_rect)


# --- Main Game Function ---
def main():
    # --- Game State Variables ---
    game_state = GAME_STATE_START # Start in the initial screen state
    current_score = 0
    high_score = 0 

    # Initialize floor_x_pos BEFORE the main loop
    floor_x_pos = 0 

    # Create the Bird sprite AFTER loading and scaling frames
    bird_sprite = Bird(bird_frames, (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2)) 
    # Bird animation timer is started within Bird.__init__

    # List to store pipe rect tuples (top_rect, bottom_rect, scored_flag)
    pipes = [] 

    # --- Timers ---
    # SPAWNPIPE_EVENT timer is set/unset based on game state


    # --- Game Loop ---
    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle space bar or mouse click
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print(f"Space pressed in state: {game_state}") 
                    if game_state == GAME_STATE_START:
                        # Ensure essential assets (bird, floor) loaded before starting
                        if bird_sprite and floor_surface: 
                            print("Starting game...") 
                            game_state = GAME_STATE_PLAYING
                            # --- Reset game state for the first game ---
                            pipes = [] # Clear any existing pipes
                            bird_sprite.rect.center = (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2) # Reset bird position
                            bird_sprite.velocity = 0 
                            current_score = 0 
                            floor_x_pos = 0 # Reset floor position
                            bird_sprite.jump() # Apply initial jump
                            if sound_flap: sound_flap.play() 
                            # Start pipe timer only if pipe and floor surfaces loaded
                            if pipe_surface and floor_surface:
                                pygame.time.set_timer(SPAWNPIPE_EVENT, PIPE_FREQUENCY) 
                            if bgm_loaded:
                                pygame.mixer.music.play(-1) # Start BGM
                        else:
                             print("Cannot start game, essential assets not loaded.")


                    elif game_state == GAME_STATE_PLAYING:
                        if bird_sprite: # Only flap if bird sprite exists
                            bird_sprite.jump() 
                            if sound_flap: sound_flap.play()

                    elif game_state == GAME_STATE_GAME_OVER:
                        if bird_sprite and floor_surface: 
                            print("Restarting game...") 
                            game_state = GAME_STATE_PLAYING
                            # --- Reset game state for restart ---
                            pipes = [] # Clear existing pipes
                            bird_sprite.rect.center = (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2) # Reset bird position
                            bird_sprite.velocity = 0 
                            current_score = 0 
                            floor_x_pos = 0 # Reset floor position
                            # Apply initial jump (optional, depends on design)
                            # bird_sprite.jump()
                            # if sound_flap: sound_flap.play() 
                            # Restart pipe timer only if pipe and floor surfaces loaded
                            if pipe_surface and floor_surface:
                                pygame.time.set_timer(SPAWNPIPE_EVENT, PIPE_FREQUENCY) 
                            if bgm_loaded:
                                 pygame.mixer.music.play(-1) # Restart BGM
                        else:
                            print("Cannot restart game, essential assets not loaded.")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                 print(f"Mouse clicked in state: {game_state}")
                 if game_state == GAME_STATE_START:
                     if bird_sprite and floor_surface: 
                            print("Starting game...") 
                            game_state = GAME_STATE_PLAYING
                            # --- Reset game state for the first game ---
                            pipes = [] 
                            bird_sprite.rect.center = (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2) 
                            bird_sprite.velocity = 0 
                            current_score = 0 
                            floor_x_pos = 0 
                            bird_sprite.jump() 
                            if sound_flap: sound_flap.play() 
                            if pipe_surface and floor_surface:
                                pygame.time.set_timer(SPAWNPIPE_EVENT, PIPE_FREQUENCY) 
                            if bgm_loaded:
                                 pygame.mixer.music.play(-1)
                     else:
                          print("Cannot start game, essential assets not loaded.")

                 elif game_state == GAME_STATE_PLAYING:
                     if bird_sprite: 
                            bird_sprite.jump() 
                            if sound_flap: sound_flap.play()

                 elif game_state == GAME_STATE_GAME_OVER:
                     if bird_sprite and floor_surface: 
                            print("Restarting game...") 
                            game_state = GAME_STATE_PLAYING
                            # --- Reset game state for restart ---
                            pipes = [] 
                            bird_sprite.rect.center = (SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2) 
                            bird_sprite.velocity = 0 
                            current_score = 0 
                            floor_x_pos = 0 
                            if pipe_surface and floor_surface:
                                pygame.time.set_timer(SPAWNPIPE_EVENT, PIPE_FREQUENCY) 
                            if bgm_loaded:
                                 pygame.mixer.music.play(-1)
                     else:
                         print("Cannot restart game, essential assets not loaded.")


            # Handle pipe spawning timer 
            if event.type == SPAWNPIPE_EVENT and game_state == GAME_STATE_PLAYING:
                 if pipe_surface and floor_surface: # Ensure required assets loaded
                      # Pass FLOOR_Y_POS to create_pipes
                      new_pipe_pair = create_pipes(pipe_surface, SCREEN_WIDTH, SCREEN_HEIGHT, FLOOR_Y_POS, PIPE_GAP) 
                      if new_pipe_pair:
                          pipes.append(new_pipe_pair)
                 else:
                     print("Warning: Skipping pipe spawning due to missing pipe or floor asset.")
            
            # Bird animation timer event 
            if bird_sprite and event.type == BIRDFLAP_EVENT: 
                 bird_sprite.animate()


        # --- Game Logic and Drawing based on State ---

        # Draw background (if loaded), otherwise fallback
        draw_background(screen, bg_surface)

        # Draw Pipes (before floor so floor is in front)
        if pipe_surface: # Only attempt to draw pipes if the asset loaded
            draw_pipe_surfaces(screen, pipes, pipe_surface) # Pass the original scaled pipe_surface

        # Draw floor
        # Update scrolling position only if game is playing
        if game_state == GAME_STATE_PLAYING: 
             if floor_surface:
                 floor_x_pos -= PIPE_SPEED
                 # Reset floor position if it scrolls completely off-screen
                 if floor_x_pos <= -floor_surface.get_width(): 
                     floor_x_pos = 0
        
        draw_floor(screen, floor_surface, floor_x_pos, FLOOR_Y_POS)


        if game_state == GAME_STATE_START:
            # Draw start screen elements
            display_start_screen(screen, game_font, bird_sprite.image if bird_sprite else None)

        elif game_state == GAME_STATE_PLAYING:
            # Update Bird (only if bird sprite exists)
            if bird_sprite:
                bird_sprite.update() 

                # Check bird collision
                collided = False
                # Check boundary collision (ensure floor loaded for height check)
                # Use the calculated FLOOR_Y_POS for the boundary check
                if floor_surface and check_collisions(bird_sprite.rect, pipes, SCREEN_HEIGHT, FLOOR_Y_POS): 
                    print(f"Collision detected! Bird bottom: {bird_sprite.rect.bottom}, Floor top: {FLOOR_Y_POS}") 
                    collided = True

                if collided:
                    game_state = GAME_STATE_GAME_OVER 
                    if sound_death: sound_death.play() 
                    if bgm_loaded: pygame.mixer.music.stop() 
                    high_score = update_high_score(current_score, high_score) 
                    pygame.time.set_timer(SPAWNPIPE_EVENT, 0) # Stop pipe spawning


                # Manage Scoring (only if game is still playing and bird/pipe assets loaded)
                if game_state == GAME_STATE_PLAYING and bird_sprite and pipe_surface: 
                     current_score, pipes = manage_scoring(bird_sprite.rect, pipes, current_score, sound_score_point) # pipes list might be modified here
                
                # Draw Bird
                bird_sprite.draw(screen)

                # Display Score
                display_score(screen, game_font, current_score)

        elif game_state == GAME_STATE_GAME_OVER:
            # Draw the bird at its last position (if sprite exists)
            if bird_sprite:
                 # Optionally stop bird movement/rotation logic on game over
                 # For simplicity, we draw the *last* frame/rotation here
                 bird_sprite.draw(screen) 

            # Display Game Over screen elements
            display_game_over(screen, game_font, current_score, high_score)

        # --- Update Display and Cap FPS ---
        pygame.display.flip() # Update the full screen
        clock.tick(FPS) # Limit frame rate


    # --- Game Quit ---
    pygame.quit()
    sys.exit()

# --- Run the game ---
if __name__ == "__main__":
    # Ensure essential asset paths exist before trying to run
    if not os.path.exists(GRAPHICS_PATH) or not os.path.exists(PLAYER_GRAPHICS_PATH) or not os.path.exists(AUDIO_PATH) or not os.path.exists(FONT_PATH):
        print("Error: One or more asset folders not found.")
        print(f"Checked paths: {GRAPHICS_PATH}, {PLAYER_GRAPHICS_PATH}, {AUDIO_PATH}, {FONT_PATH}")
        print("Please ensure your folders are structured correctly within the 'Code' directory.")
        sys.exit()

    main()