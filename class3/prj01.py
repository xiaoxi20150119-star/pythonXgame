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

class Ball:
    def __init__(self, x, y, radius, color):
        
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed_x = 5
        self.speed_y = -5
        self.is_moving = False
    def draw(self, display_area):
        '''
                初始化球屬性/ initialize ball\n
                x,y:球的中心座標/ the center of the ball\n
                radius:球的半徑/ the radius of the ball\n
                color:球的顏色/ the color of the ball\n
                '''
        pygame.draw.circle(display_area, self.color, (int(self.x), int(self.y)), self.radius)

    def move(self):
        if self.is_moving:
            self.x += self.speed_x
            self.y += self.speed_y

    def check_collision(self, bg_x, bg_y, bricks, pad):

        # Check window edge
        if self.x <= 0 or self.x + self.radius >= bg_x:
            self.speed_x = -self.speed_x

        if self.y - self.radius <= 0:
            self.speed_y = -self.speed_y

        if self.y + self.radius >= bg_y:
            self.is_moving = False

        if(
        self.y + self.radius >= pad.rect.y 
        and self.y + self.radius <= pad.rect.y + pad.rect.height
        and self.x >= pad.rect.x
        and self.x <= pad.rect.x + pad.rect.width
        ):
            self.speed_y = -abs(self.speed_y)

        for brick in bricks:
            if not brick.hit:
                dx = abs(abs(self.x) - abs(brick.rect.x + brick.rect.width / 2))
                dy = abs(abs(self.y) - abs(brick.rect.y + brick.rect.height / 2))

                if dx <= (self.radius + brick.rect.width / 2) and dy <= (self.radius + brick.rect.height / 2):
                    brick.hit = True
                    if self.x < brick.rect.x or self.x > brick.rect.x + brick.rect.width:
                        self.speed_x = -self.speed_x
                    else:
                        self.speed_y = -self.speed_y
######################定義函式區/ define functions######################

######################初始化設定/ initialize settings######################
pygame.init()
FPS = pygame.time.Clock()
######################載入圖片/ load images######################

######################遊戲視窗設定/ game window settings######################
bg_x = 800
bg_y = 600
bg_width = (bg_x, bg_y)
pygame.display.set_caption("My Game")
screen = pygame.display.set_mode(bg_width)
######################磚塊設定/ brick settings######################
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
ball_radius = 10
ball_color = (255, 215, 0)
ball = Ball(pad.rect.x + pad.rect.width // 2, pad.rect.y - ball_radius, ball_radius, ball_color)
######################遊戲結束設定/ game over settings######################

######################主程式/ main program######################
while True:
    FPS.tick(60)
    screen.fill((0, 0, 0))
    mouse_x, mouse_y = pygame.mouse.get_pos()
    pad.rect.x = mouse_x-pad.rect.width//2

    if pad.rect.x < 0:
        pad.rect.x = 0

    if pad.rect.x + pad.rect.width>bg_x:
        pad.rect.x = bg_x-pad.rect.width

    if not ball.is_moving:
        ball.x = pad.rect.x + pad.rect.width // 2
        ball.y = pad.rect.y - ball_radius
    else:
        ball.move()
        ball.check_collision(bg_x, bg_y, bricks, pad)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not ball.is_moving:
                ball.is_moving = True

    for brick in bricks:
        brick.draw(screen)

    pad.draw(screen)
    ball.draw(screen)
    pygame.display.update()


    