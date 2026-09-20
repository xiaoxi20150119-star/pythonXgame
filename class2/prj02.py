import pygame
######################匯入模組######################
import pygame
import sys

######################初始化######################
pygame.init() # 啟動pygame
width = 640 # 設定視窗寬度
height = 320 # 設定視窗高度
######################建立視窗及物件######################
# 設定建立視窗
screen = pygame.display.set_mode((width, height))
# 設定視窗標題
######################建立畫布######################
# 設定畫布
bg = pygame.Surface((width, height))
# 設定畫布為藍色
bg.fill((60, 60, 112))
pygame.display.set_caption("My Game")

######################繪製圓形######################
# 畫圓形, (畫布,顏色,圓心,半徑,線寬)
pygame.draw.circle(bg, (0, 0, 225), (200, 100), 30, 0)
pygame.draw.circle(bg, (0, 0, 225), (400, 100), 30, 0)
# 畫矩形, (畫布,顏色,[x,y],[寬,高],線寬)
pygame.draw.rect(bg, (0, 0, 225), [270, 130, 60, 40], 5)

# 畫橢圓, (畫布,顏色,[x,y],[寬,高],線寬)
pygame.draw.ellipse(bg, (225, 0, 0), [130, 160, 60, 35], 5)
pygame.draw.ellipse(bg, (225, 0, 0), [400, 160, 60, 35], 5)

# line, (畫布,顏色,[start],[end],線寬)
pygame.draw.line(bg, (225, 0, 225), [280, 220], [320, 220], 3)
######################循環偵測######################
ispen=False
while True:
    x,y = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # 如果按下[X]就退出
            sys.exit() # 離開遊戲

        if event.type == pygame.MOUSEBUTTONDOWN: # 如果按下鼠標左鍵
            print("click!") # 輸出滑鼠座標
            print("Mouse button down at:", x, y) # 輸出滑鼠座標
            ispen = not(ispen)
            print(f"ispen: {ispen}")

    if ispen :
        pygame.draw.circle(bg, (0, 0, 0), (x, y), 15, 0)


        # 繪製畫布與視窗
    screen.blit(bg, (0, 0))
        # 更新視窗
    pygame.display.update()
    