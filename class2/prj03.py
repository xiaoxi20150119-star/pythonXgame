######################載入套件/ import packages######################
import random
import pygame
import sys
######################物件類別/ object class######################
class Brick:
    def __init__(self, x, y, width, height, color):
        '''
        初始化磚塊屬性/ initialize brick\n
        x,y:磚塊的左上角座標/ the top left corner of the brick\n
        width,height:磚塊的寬度與高度/ the width and height of the brick\n
        color:磚塊的顏色/ the color of the brick\n
        '''
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hit = False

    def draw(self, display_area):
        if not self.hit:
            pygame.draw.rect(display_area, self.color, self.rect)

######################定義函式區/ define functions######################

######################初始化設定/ initialize settings######################
pygame.init()
######################載入圖片/ load images######################

######################遊戲視窗設定/ game window settings######################
bg_x = 800
bg_y = 600
bg_width = (bg_x, bg_y)
pygame.display.set_caption("My Game")
screen = pygame.display.set_mode(bg_width)
######################磚塊設定/ brick settings######################
brickA = Brick(0, 0, 50, 20, (255, 0, 0))
brickB = Brick(200, 100, 50, 50, (0, 0, 255))
bricks_row = 9
bricks_col = 11
bricks_w = 58
bricks_h = 16
bricks_gap = 2
bricks = []
for col in range(bricks_col):
    for row in range(bricks_row):
        x = col * (bricks_w+bricks_gap) + 70
        y = row * (bricks_h+bricks_gap) + 60
        color = (random.randint(50, 255), random.randint(0, 255), random.randint(0, 255))
        brick = Brick(x, y, bricks_w, bricks_h, color)
        bricks.append(brick)
######################顯示文字設定/ text display settings######################

######################底板設定/ paddle settings######################
pad = Brick(0,  bg_y-48, bricks_w, bricks_h, (255, 255, 255))
######################球設定/ ball settings######################

######################遊戲結束設定/ game over settings######################

######################主程式/ main program######################
while True:
    screen.fill((0, 0, 0))
    mouse_x, mouse_y = pygame.mouse.get_pos()
    pad.rect.x = mouse_x-pad.rect.width//2

    if pad.rect.x < 0:
        pad.rect.x = 0

    if pad.rect.x + pad.rect.width>bg_x:
        pad.rect.x = bg_x-pad.rect.width

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    for brick in bricks:
        brick.draw(screen)

    pad.draw(screen)
    pygame.display.update()