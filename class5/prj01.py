######################Imports######################
import pygame
import sys
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
    
    def draw(self, display_area):
        '''繪製主角/ draw the player\ndisplay_area:繪製主角的目標視窗\n'''
        pygame.draw.rect(display_area, self.color, self.rect)

    def move(self, direction, bg_x):
        self.rect.x += direction * self.speed
        if self.rect.right < 0:
            self.rect.left = bg_x
        elif self.rect.left > bg_x:
            self.rect.right = 0
######################player setup######################
player_w = 30
player_h = 30
player_x = (bg_x - player_w) //2
player_y = bg_y - player_h - 50
player=Player(player_x, player_y, player_w, player_h, (0, 0, 255))
####################### main loop ######################
while True:
    FPS.tick(60)
    screen.fill((0, 0, 0))
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.move(-1, bg_x)
    if keys[pygame.K_RIGHT]:
        player.move(1, bg_x)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    player.draw(screen)
    pygame.display.update()