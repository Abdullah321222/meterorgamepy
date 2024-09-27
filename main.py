import pygame, sys
from random import randint, uniform

def laser_update(laser_list, speed=500, dt=0):
    for rect in laser_list:
        rect.y -= speed * dt
        if rect.bottom < 0:
            laser_list.remove(rect)

def display_score():
    score_text = f"Score: {pygame.time.get_ticks() // 1000}"
    text_surf = font.render(score_text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 80))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, 'white', text_rect.inflate(30, 40), width=10, border_radius=5)

def laser_timer(can_shoot, shoot_time, duration=500):
    if not can_shoot:
        current_time = pygame.time.get_ticks()
        if current_time - shoot_time > duration:
            can_shoot = True
    return can_shoot

def meteor_update(meteor_list, speed=500, dt=0):
    for meteor_tuple in meteor_list:
        direction = meteor_tuple[1]
        meteor_rect = meteor_tuple[0]
        meteor_rect.center += direction * speed * dt
        if meteor_rect.top > WINDOW_HEIGHT:
            meteor_list.remove(meteor_tuple)

def display_game_over():
    game_over_text = font.render("Game Over! Press R to Restart or Q to Quit", True, (255, 0, 0))
    text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
    display_surface.blit(game_over_text, text_rect)

def restart_game():
    global ship_rect, laser_list, meteor_list, can_shoot, shoot_time
    ship_rect = ship_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
    laser_list = []
    meteor_list = []
    can_shoot = True
    shoot_time = None
    pygame.time.set_timer(meteor_timer, 500)  # Reset meteor timer

pygame.init()

WINDOW_WIDTH, WINDOW_HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Asteroid")


try:
    ship_surf = pygame.image.load('./ship.png').convert_alpha()
    laser_surf = pygame.image.load('./laser.png').convert_alpha()
    meteor_surf = pygame.image.load('./meteor.png')
    bg_surf = pygame.image.load('./background.png').convert()
    font = pygame.font.Font('./subatomic.ttf', 50)
    laser_sound = pygame.mixer.Sound('./laser.ogg')
    explosion_sound = pygame.mixer.Sound('./music1.wav')
    background_music = pygame.mixer.Sound('./music2.wav')
    background_music.play(loops=-1)
except pygame.error as e:
    print(f"Error loading assets: {e}")
    pygame.quit()
    sys.exit()

# Game variables
ship_rect = ship_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
laser_list = []
meteor_list = []
can_shoot = True
shoot_time = None
meteor_timer = pygame.USEREVENT + 1
pygame.time.set_timer(meteor_timer, 500)

# Main game loop
clock = pygame.time.Clock()
game_over = False

while True:
    dt = clock.tick(120) / 1000  # Frame-rate independent delta time

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over and can_shoot:
            # Create laser
            laser_rect = laser_surf.get_rect(midbottom=ship_rect.midtop)
            laser_list.append(laser_rect)

            # Start cooldown timer
            can_shoot = False
            shoot_time = pygame.time.get_ticks()
            laser_sound.play()

        if event.type == meteor_timer and not game_over:
            # Create new meteor
            rand_x_pos = randint(-100, WINDOW_WIDTH + 100)
            rand_y_pos = randint(-100, -50)
            meteor_rect = meteor_surf.get_rect(center=(rand_x_pos, rand_y_pos))
            direction = pygame.math.Vector2(uniform(-0.5, 0.5), 1)
            meteor_list.append((meteor_rect, direction))

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                restart_game()
                game_over = False
            elif event.key == pygame.K_q and game_over:
                pygame.quit()
                sys.exit()

    if not game_over:
        # Update game state
        laser_update(laser_list, speed=500, dt=dt)
        can_shoot = laser_timer(can_shoot, shoot_time, duration=400)
        meteor_update(meteor_list, speed=500, dt=dt)

        # Update ship position
        ship_rect.center = pygame.mouse.get_pos()

        # Check collisions
        for meteor_tuple in meteor_list:
            meteor_rect = meteor_tuple[0]
            if ship_rect.colliderect(meteor_rect):
                game_over = True
                pygame.time.set_timer(meteor_timer, 0)  # Stop meteor spawning
                break

        for laser_rect in laser_list:
            for meteor_tuple in meteor_list:
                if laser_rect.colliderect(meteor_tuple[0]):
                    meteor_list.remove(meteor_tuple)
                    laser_list.remove(laser_rect)
                    explosion_sound.play()

        # Draw everything
        display_surface.fill((200, 200, 200))
        display_surface.blit(bg_surf, (0, 0))
        display_score()

        for meteor_tuple in meteor_list:
            display_surface.blit(meteor_surf, meteor_tuple[0])
        for rect in laser_list:
            display_surface.blit(laser_surf, rect)
        display_surface.blit(ship_surf, ship_rect)

    if game_over:
        display_game_over()

    # Update the display
    pygame.display.update()
