import sys
import random
import json
import pygame, pygame_gui, pygame.transform
import moviepy.editor as mp
import threading


pygame.init()

# Screen Setup
MIN_SCREEN_WIDTH = 1000
MIN_SCREEN_HEIGHT = 500
screen = pygame.display.set_mode((MIN_SCREEN_WIDTH, MIN_SCREEN_HEIGHT))
pygame.display.set_caption("Geometry Crack")

# Create UI manager
ui_manager = pygame_gui.UIManager((MIN_SCREEN_WIDTH, MIN_SCREEN_HEIGHT))

# Title video
title_vid = mp.VideoFileClip("title_screen.mp4")

# Music
current_volume = 0.1
music = pygame.mixer.music.load('./Music/song1.mp3')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(current_volume)

# Sound effects
sound_volume = 0.1
fu_sound = pygame.mixer.Sound('./Sounds/f_u.mp3')
fu_sound.set_volume(1)
button_click = pygame.mixer.Sound('./Sounds/click.mp3')
death = pygame.mixer.Sound('./Sounds/death.mp3')
jump = pygame.mixer.Sound('./Sounds/boing.mp3')

# Game Constants
run = True
clock = pygame.time.Clock()

title_vid_width, title_vid_height = title_vid.size
title_vid_surface = pygame.Surface((title_vid_width, title_vid_height))

#vid
TARGET_WIDTH = MIN_SCREEN_WIDTH
TARGET_HEIGHT = MIN_SCREEN_HEIGHT

def update_video():
    global t, run
    while run:
        t += dt
        display_frame(t)
        pygame.time.wait(int(1000 / 30))

video_thread = threading.Thread(target=update_video)
video_thread.start()

def display_frame(t):
    if t >= title_vid.duration:
        t = t % title_vid.duration  # Loop the video
    frame = title_vid.get_frame(t)
    frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    scaled_surface = pygame.transform.scale(frame_surface, (TARGET_WIDTH, TARGET_HEIGHT))
    title_vid_surface.blit(scaled_surface, (0, 0))


# save and load volume
def save_volume(volume, slider_position):
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    data['volume'] = round(volume, 1)
    data['slider_position'] = round(slider_position, 1)

    with open('data.json', 'w') as f:
        json.dump(data, f)

def load_volume():
    try:
        with open('data.json', 'r') as f:
            return json.load(f).get('volume', 0.1)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0.1

# Load initial Volume
current_volume = load_volume()
pygame.mixer.music.set_volume(current_volume)
slider_position = int(current_volume * 10) # convert volume to slider position



# Score saving
def save_high_score(score):
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    data['high_score'] = score

    with open('data.json', 'w') as f:
        json.dump(data, f)

def load_high_score():
    try:
        with open('data.json', 'r') as f:
            return json.load(f).get('high_score', 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

def save_recent_score(score):
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}

    data['recent_score'] = score

    with open('data.json', 'w') as f:
        json.dump(data, f)

def load_recent_score():
    try:
        with open('data.json', 'r') as f:
            return json.load(f).get('recent_score', 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

# Player Configuration
normal_width = 40
normal_height = 40
duck_width = 40  # Width when ducking
duck_height = 10  # Height when ducking
player_size = (normal_width, normal_height)  # Default player size
player_x = 50
player_y = MIN_SCREEN_HEIGHT - normal_height  # Ground level
player_color = (255, 255, 255)  # White
player_velocity = 0
jump_force = -15
gravity = 1
is_ducking = False  # State to track ducking

# Ground Configuration
ground_height = 20
ground_width = MIN_SCREEN_WIDTH  # Set ground width to match screen width
ground_y = MIN_SCREEN_HEIGHT - ground_height
ground_color = (0, 0, 255)  # Blue

# Obstacle Configuration
OBSTACLE_WIDTH = 20
OBSTACLE_HEIGHT = 65
OBSTACLE_SPEED = 9
TRIGGERED_OBSTACLE_HEIGHT = 120
TRIGGERED_OBSTACLE_COLOR = (222, 0, 255)
DEFAULT_OBSTACLE_COLOR = (255, 0, 0)

# Obstacle Types
JUMP_OVER = 0
DUCK_UNDER = 1

# Define obstacle positions based on type
def set_obstacle_position(obstacle_type):
    if obstacle_type == JUMP_OVER:
        return ground_y - OBSTACLE_HEIGHT  # Ground level for "Jump Over"
    elif obstacle_type == DUCK_UNDER:
        return ground_y - OBSTACLE_HEIGHT  # Ground level at start, then moves up if triggered

# Animation Configuration
animation_speed = 3
animation_trigger_distance = 285  # Distance to trigger "Duck Under" animation
animation_target_y = ground_y - 380  # Final height for duck under

# Reset Function
def reset_game():
    global player_x, player_y, player_velocity, player_size, is_ducking, obstacles, score, recent_score
    player_x = 50
    player_y = MIN_SCREEN_HEIGHT - normal_height  # Ground level
    player_velocity = 0
    player_size = (normal_width, normal_height)  # Default size
    is_ducking = False  # Reset ducking state
    obstacles = []
    obstacle_type = random.choice([JUMP_OVER, DUCK_UNDER])
    obstacle_color = DEFAULT_OBSTACLE_COLOR
    new_obstacle = {
        "x": random.randint(MIN_SCREEN_WIDTH, MIN_SCREEN_WIDTH + 300),
        "type": obstacle_type,
        "y": set_obstacle_position(obstacle_type),
        "color": obstacle_color,
        "is_moving": False
    }
    obstacles.append(new_obstacle)
    recent_score = load_recent_score()

# Initialize Game
reset_game()

# Icon
Icon = pygame.image.load('./Images/icon.png')
pygame.display.set_icon(Icon)

# Load the overlay image
overlay_image = pygame.image.load('rührei.png')
overlay_image = pygame.transform.scale(overlay_image, (MIN_SCREEN_WIDTH, MIN_SCREEN_HEIGHT))

# Font Configuration
font = pygame.font.Font(None, 36)  # Choose font and size

# colour
black = (0, 0, 0)
white = (255, 255, 255)


# lgbtq+ Title
col_spd = 3
col_dir= [-1, 1, -1]
def_col = [50, 100, 255]

# Score Variables
score = 0
high_score = load_high_score()
recent_score = load_recent_score()

# Flag to track whether the overlay should be shown
show_overlay = False

# Setting Variables
grid_top_height = 162

# Game states
MAIN_MENU = 0
OPTIONS = 1
PLAYING = 2
PAUSED = 3
QUIT = 4



game_state = MAIN_MENU

# Title
def draw_text(text, size, col, x, y):
    font = "Ldfcomicsans-jj7l.ttf"
    font = pygame.font.Font(font, size)
    text_surface = font.render(text, True, col)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)

# lgbtq+ 
minimum = 20
maximum = 200

def col_change(color: list, direction: list) -> None:
    for i in range(3):
        color[i] += col_spd * direction[i]
        if color[i] >= maximum or color[i] <= minimum:
            direction[i] *= -1
        if color[i] >= maximum:
            color[i] = maximum
        elif color[i] <= minimum:
            color[i] = minimum

# Main Buttons
start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 190), (300, 50)),
                                            text='START',
                                            manager=ui_manager)


options_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 250), (300, 50)),
                                           text='OPTIONS',
                                           manager=ui_manager)

quit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 310), (300, 50)),
                                           text='QUIT',
                                           manager=ui_manager)

back_main_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((80, 30), (100, 50)),
                                           text='BACK',
                                           manager=ui_manager)
back_main_button.hide()

# Pause Buttons
higher_options_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 160), (300, 50)),
                                           text='OPTIONS',
                                           manager=ui_manager)
higher_options_button.hide()

back_game_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((80, 30), (100, 50)),
                                           text='BACK',
                                           manager=ui_manager)
back_game_button.hide()

resume_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 100), (300, 50)),
                                             text='RESUME',
                                             manager=ui_manager)
resume_button.hide()

menu_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 220), (300, 50)),
                                           text='BACK TO MENU',
                                           manager=ui_manager)
menu_button.hide()


# Volume Slider
volume_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((650, 150), (140, 20)),
                                                       start_value=current_volume * 10, value_range=(0, 10),
                                                       manager=ui_manager)
volume_slider.hide()



#Timer Variables
t = 0.0
dt = 1 / 30.0


# Main Game Loop
while run:
    time_delta = clock.tick(60) / 1000.0  # Convert milliseconds to seconds
    t += dt

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
             run = False
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == start_button or event.ui_element == quit_button or event.ui_element == options_button or event.ui_element == higher_options_button or event.ui_element == back_main_button or event.ui_element == back_game_button or event.ui_element == resume_button or event.ui_element == menu_button:
                    button_click.play()                
                if event.ui_element == start_button:
                    game_state = PLAYING
                    pygame.time.delay(500)
                    score = 0
                elif event.ui_element == options_button:
                    game_state = OPTIONS
                    volume_slider.show()
                    back_main_button.show()
                elif event.ui_element == higher_options_button:
                    game_state = OPTIONS
                    volume_slider.show()
                    back_game_button.show()                    
                elif event.ui_element == back_main_button:
                    game_state = MAIN_MENU
                    volume_slider.hide()
                    back_main_button.hide()
                elif event.ui_element == back_game_button:
                    game_state = PAUSED
                    volume_slider.hide()
                    back_game_button.hide()
                elif event.ui_element == resume_button:
                    game_state = PLAYING
                elif event.ui_element == quit_button:      
                    game_state = QUIT
                    pygame.time.delay(500)
                    run = False
                elif event.ui_element == menu_button:
                    game_state = MAIN_MENU
                     

                if game_state == PLAYING:
                    start_button.visible = False
                    options_button.visible = False
                    resume_button.visible = False
                    quit_button.visible = False
                    menu_button.visible = False
                    higher_options_button.visible = False
                    quit_button.visible = False

                elif game_state == PAUSED:
                    menu_button.visible = True
                    resume_button.visible = True
                    higher_options_button.visible = True

                elif game_state == MAIN_MENU:
                    resume_button.visible = False
                    menu_button.visible = False
                    higher_options_button.visible = False
                    start_button.visible = True
                    options_button.visible = True
                    quit_button.visible = True

                elif game_state == OPTIONS:
                    volume_slider.visible = True
                    menu_button.visible = False
                    resume_button.visible = False
                    higher_options_button.visible = False
                    start_button.visible = False
                    options_button.visible = False
                    quit_button.visible = False

            if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == volume_slider:
                    current_volume = event.value / 10.0
                    pygame.mixer.music.set_volume(current_volume)
                    save_volume(current_volume, event.value)
    
        ui_manager.process_events(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and game_state != MAIN_MENU and game_state != PAUSED and game_state != OPTIONS:
                game_state = PAUSED
                menu_button.show()
                resume_button.show()
                higher_options_button.show()

    # Update game state
    if game_state == PLAYING and game_state != PAUSED:
        # Handle player input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and not is_ducking and player_y >= ground_y - normal_height:
            player_velocity = jump_force
            jump.play()

        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            if player_y == ground_y - normal_height:
                is_ducking = True
                player_size = (duck_width, duck_height)
                player_y = ground_y - duck_height
        
        elif keys[pygame.K_p]:
            if keys[pygame.K_a]:
                player_x -= 8
            elif keys[pygame.K_d]:
                player_x += 8

        elif keys[pygame.K_m]:
            show_overlay = True
            pygame.mixer.Sound.play(fu_sound)
            pygame.mixer.Sound.set_volume(fu_sound, 1)
            
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_s or pygame.K_DOWN:
                is_ducking = False
                player_size = (normal_width, normal_height)
            elif event.key == pygame.K_m:
                show_overlay = False
            

        # Update score
        score += 1 
        # Definition of the minimum range
        minimum_range = [1500, 1800, 2000, 2500]

        # Gravity and player movement
        player_velocity += gravity
        player_y += player_velocity
        if player_y > ground_y - player_size[1]:  # Ground contact check
            player_y = ground_y - player_size[1]
            player_velocity = 0

        # Obstacle creation and update
        if len(obstacles) == 0 or MIN_SCREEN_WIDTH - obstacles[-1]["x"] >= random.choice(minimum_range):
            obstacle_type = random.choice([JUMP_OVER, DUCK_UNDER])
            obstacle_color = DEFAULT_OBSTACLE_COLOR
            new_obstacle = {
                "x": MIN_SCREEN_WIDTH,
                "type": obstacle_type,
                "y": set_obstacle_position(obstacle_type),
                "color": obstacle_color,
                "is_moving": False
            }
            obstacles.append(new_obstacle)

        # Move obstacles
        for obstacle in obstacles:
            obstacle["x"] -= OBSTACLE_SPEED
                    
            if obstacle["type"] == DUCK_UNDER and obstacle["x"] - player_x <= animation_trigger_distance:
                obstacle["is_moving"] = True  # Trigger animation for duck under
                obstacle["color"] = TRIGGERED_OBSTACLE_COLOR
                

            if obstacle["is_moving"] and obstacle["y"] > ground_y - animation_target_y:
                obstacle["y"] -= animation_speed

            # Collision detection
            player_rect = pygame.Rect(player_x, player_y, player_size[0], player_size[1])
            obstacle_rect = pygame.Rect(obstacle["x"], obstacle["y"], OBSTACLE_WIDTH, OBSTACLE_HEIGHT)

            if player_rect.colliderect(obstacle_rect):  # Collision check
                death.play()
                save_recent_score(score)
                recent_score = score  # Update recent_score before resetting
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
                score = 0
                reset_game()
                break

    # Draw everything
    screen.fill((black))
    volume_number = load_volume()

    # Title
    if game_state == MAIN_MENU:
        screen.fill((black))
        display_frame(t)
        screen.blit(title_vid_surface, (0, 1))
        draw_text("Geometry Crack", 130, def_col, MIN_SCREEN_WIDTH / 2, 100)
        col_change(def_col, col_dir)

    if game_state == OPTIONS:
        draw_text("Volume", 20, white, 614, grid_top_height)
        volume_int = int(volume_number * 10)
        draw_text(str([volume_int]), 20, white, 805, grid_top_height)

    ui_manager.update(time_delta)
    ui_manager.draw_ui(screen)

    if game_state == PLAYING:
        pygame.draw.rect(screen, ground_color, (0, ground_y, ground_width, ground_height))

        pygame.draw.rect(screen, player_color, (player_x, player_y, player_size[0], player_size[1]))

        for obstacle in obstacles:
            pygame.draw.rect(screen, obstacle["color"], (obstacle["x"], obstacle["y"], OBSTACLE_WIDTH, OBSTACLE_HEIGHT))

        if show_overlay:
            screen.blit(overlay_image, (0, 0))

        score_text = font.render(f"Score: {score}", True, (white))
        screen.blit(score_text, (10, 10))

        high_score_text = font.render(f"Highscore: {high_score}", True, (255, 230, 0))
        screen.blit(high_score_text, (10, 70))

        recent_score_text = font.render(f"Recent Score: {recent_score}", True, (white))
        screen.blit(recent_score_text, (10, 40))
        
    
    pygame.display.flip()
video_thread.join()
pygame.quit()
sys.exit()