######################Imports######################
import pygame
import sys
import random
######################定義函式區/ define functions######################
pygame.init()
FPS = pygame.time.Clock()
####################### Window settings######################
bg_x = 400
bg_y = 600
bg_size = (bg_x, bg_y)
pygame.display.set_caption("Doodle Jump")
screen = pygame.display.set_mode(bg_size)
#######################classes#####################
class Player:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = 5
        self.velocity_y = 0
        self.jump_power = -12
        self.gravity = 0.5
        self.on_platform = False
    def draw(self, display_area):
        '''繪製主角/ draw the player\ndisplay_area:繪製主角的目標視窗\n'''
        pygame.draw.rect(display_area, self.color, self.rect)

    def move(self, direction, bg_x):
        self.rect.x += direction * self.speed
        if self.rect.right < 0:
            self.rect.left = bg_x
        elif self.rect.left > bg_x:
            self.rect.right = 0

    def apply_gravity(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

    def check_platform_collision(self, platforms):
        if self.velocity_y > 0:
            check_points = max(1, int(abs(self.velocity_y) / 5))
            step_y = self.velocity_y / check_points
            for platform in platforms:
                for i in range(check_points):
                    test_rect = self.rect.copy()
                    test_rect.y += i * step_y
                    if (test_rect.bottom >= platform.rect.top 
                and test_rect.bottom <= platform.rect.bottom 
                and test_rect.right > platform.rect.left 
                and test_rect.left < platform.rect.right
                    ):
                        self.rect.bottom = platform.rect.top
                        self.velocity_y = self.jump_power
                        self.on_platform = True
                        return True
        return False
class Platform:
    '''繪製平台/ draw the platform\ndisplay_area:繪製平台的目標視窗\n'''
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
    def draw(self, display_area):
        pygame.draw.rect(display_area, self.color, self.rect)
######################player setup######################
player_w = 30
player_h = 30
player_x = (bg_x - player_w) //2
player_y = bg_y - player_h - 50
player=Player(player_x, player_y, player_w, player_h, (0, 0, 255))

#######################platform setup######################
platform_w = 60
platform_h = 10
platforms = []
platform_x = (bg_x - platform_w) //2
platform_y = bg_y - platform_h - 10
platform=Platform(platform_x, platform_y, platform_w, platform_h, (225, 225, 255))
platforms.append(platform)

platform_count = random.randint(8, 10) + 10
for i in range(platform_count):
    x = random.randint(0, bg_x - platform_w)
    y = (bg_y - 100)- (i * 60)
    platform=Platform(x, y, platform_w, platform_h, (225, 225, 255))
    platforms.append(platform)
########################custom functions######################
def update_camera():
    screen_middle = bg_y // 2

    if player.rect.y < screen_middle:
        camera_move = screen_middle - player.rect.y
        player.rect.y = screen_middle

        for platform in platforms:
            platform.rect.y += camera_move

        y_min = bg_y
        for platform in platforms:
            if platform.rect.y >bg_y:
                platforms.remove(platform)
            if platform.rect.y < y_min:
                y_min = platform.rect.top

        if len(platforms) < platform_count:
            x = random.randint(0, bg_x - platform_w)
            y = y_min - 60
            new_platform = Platform(x, y, platform_w, platform_h, (225, 225, 255))
            platforms.append(new_platform)
######################## main loop ######################
while True:
    FPS.tick(60)
    screen.fill((0, 0, 0))

    update_camera()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.move(-1, bg_x)
    player.apply_gravity()
    player.check_platform_collision(platforms)
    if keys[pygame.K_RIGHT]:
        player.move(1, bg_x)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    for platform in platforms:
        platform.draw(screen)        
    
    player.draw(screen)
    pygame.display.update()
  