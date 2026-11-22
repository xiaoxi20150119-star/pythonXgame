######################Imports######################
import pygame
import sys
import random
import os

os.chdir(sys.path[0])

####################### Global Variables ######################
score = 0
highest_score = 0
game_over = False
initial_player_y = 0
spring_chance = 0.2
special_spring_chance = 0.2
springs = []


####################### Functions #######################
def load_doodle_sprites():
    img_path = os.path.join("image", "src.png")
    source_image = pygame.image.load(img_path).convert_alpha()
    sprite_data = {
        "std_platform": (0, 0, 116, 30),
        "break_platform": (0, 145, 71, 35),
        "spring_normal": (376, 188, 71, 35),
        "player_left_jumping": os.path.join("image", "l.png"),
        "player_left_falling": os.path.join("image", "ls.png"),
        "player_right_jumping": os.path.join("image", "r.png"),
        "player_right_falling": os.path.join("image", "rs.png"),
    }
    sprites = {}
    for name, data in sprite_data.items():
        if name.startswith("player_"):
            try:
                sprites[name] = pygame.image.load(sprite_data[name]).convert_alpha()
            except Exception as e:
                print(f"Failed to load image: {name}:{e}")

        else:
            x, y, w, h = data
            sprites[name] = source_image.subsurface((x, y, w, h)).copy()
    return sprites


######################定義函式區/ define functions######################
pygame.init()
FPS = pygame.time.Clock()
####################### Window settings######################
bg_x = 400
bg_y = 600
bg_size = (bg_x, bg_y)
pygame.display.set_caption("Doodle Jump")
screen = pygame.display.set_mode(bg_size)

######################## Load sprites ######################
try:
    sprites = load_doodle_sprites()
    use_sprites = True
    print(f"Successfully translated {len(sprites)} sprite images,")
except Exception as e:
    print(f"Failed to load sprites: {e}")
    print(f"The game will use simple graphics.")
    sprites = None
    use_sprites = False


#######################classes#####################
class Player:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        color,
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = 5
        self.velocity_y = 0
        self.jump_power = -12
        self.gravity = 0.5
        self.on_platform = False

    def draw(self, display_area):
        """繪製主角/ draw the player\ndisplay_area:繪製主角的目標視窗\n"""
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

    def check_spring_collision(self, springs):
        if self.velocity_y > 0:
            check_points = max(1, int(abs(self.velocity_y) / 5))
            step_y = self.velocity_y / check_points

            for spring in springs:
                for i in range(check_points):
                    test_rect = self.rect.copy()
                    test_rect.y += i * step_y
                    if (
                        test_rect.bottom >= spring.rect.top
                        and test_rect.bottom <= spring.rect.bottom
                        and test_rect.right > spring.rect.left
                        and test_rect.left < spring.rect.right
                    ):

                        self.rect.bottom = spring.rect.top
                        self.velocity_y = self.jump_power
                        self.on_platform = True
                        return True
        return False

    def check_platform_collision(self, platforms):
        if self.velocity_y > 0:
            check_points = max(1, int(abs(self.velocity_y) / 5))
            step_y = self.velocity_y / check_points
            for platform in platforms:
                if platform.is_special and platform.is_touched:
                    continue
                for i in range(check_points):
                    test_rect = self.rect.copy()
                    test_rect.y += i * step_y
                    if (
                        test_rect.bottom >= platform.rect.top
                        and test_rect.bottom <= platform.rect.bottom
                        and test_rect.right > platform.rect.left
                        and test_rect.left < platform.rect.right
                    ):

                        if platform.is_special:
                            platform.is_touched = True

                        self.rect.bottom = platform.rect.top
                        self.velocity_y = self.jump_power
                        self.on_platform = True
                        return True
        return False


class Platform:
    """繪製平台/ draw the platform\ndisplay_area:繪製平台的目標視窗\n"""

    def __init__(self, x, y, width, height, color, is_special=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.is_special = is_special
        self.is_touched = False

    def draw(self, display_area):
        pygame.draw.rect(display_area, self.color, self.rect)
        if self.is_special and self.is_touched:
            return


class Spring:
    def __init__(self, x, y, width, height, color, is_special=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.is_special = is_special

    def draw(self, display_area):
        """繪製彈簧/ draw the spring\ndisplay_area:繪製彈簧的目標視窗\n"""
        pygame.draw.rect(display_area, self.color, self.rect)

    def move_with_platform(self, dy):
        self.rect.y += dy


######################player setup######################
player_w = 30
player_h = 30
player_x = (bg_x - player_w) // 2
player_y = bg_y - player_h - 50
player = Player(player_x, player_y, player_w, player_h, (0, 0, 255))

#######################platform setup######################
platform_w = 60
platform_h = 10
platforms = []
platform_x = (bg_x - platform_w) // 2
platform_y = bg_y - platform_h - 10
platform = Platform(platform_x, platform_y, platform_w, platform_h, (225, 225, 255))
platforms.append(platform)

platform_count = random.randint(8, 10) + 10
for i in range(platform_count):
    x = random.randint(0, bg_x - platform_w)
    y = (bg_y - 100) - (i * 60)
    platform = Platform(x, y, platform_w, platform_h, (225, 225, 255))
    platforms.append(platform)

########################Font setup######################
font = pygame.font.Font("../fonts/NotoSansTC-Regular.ttf", 24)


########################custom functions######################
def update_camera():
    screen_middle = bg_y // 2

    global score, initial_player_y

    if player.rect.y < screen_middle:
        camera_move = screen_middle - player.rect.y
        player.rect.y = screen_middle

        score += camera_move / 10

        for platform in platforms[:]:
            platform.rect.y += camera_move

        for spring in springs:
            spring.rect.y += camera_move

        y_min = bg_y
        for platform in platforms:
            if platform.rect.y > bg_y:
                platforms.remove(platform)
            if platform.rect.y < y_min:
                y_min = platform.rect.top

        if len(platforms) < platform_count:
            x = random.randint(0, bg_x - platform_w)
            y = y_min - 60
            if score > 100 and random.random() < spring_chance:
                platform = Platform(x, y, platform_w, platform_h, (225, 0, 0), True)
            else:
                platform = Platform(x, y, platform_w, platform_h, (225, 225, 255))
            platforms.append(platform)
        for spring in springs[:]:
            if spring.rect.y > bg_y:
                springs.remove(spring)


def reset_game():

    global score, game_over, initial_player_y, springs

    player.rect.x = (bg_x - player_w) // 2
    player.rect.y = bg_y - player_h - 50
    player.velocity_y = 0

    platforms.clear()
    springs.clear()

    platforms.clear()
    platform_x = (bg_x - platform_w) // 2
    platform_y = bg_y - platform_h - 10
    platform = Platform(platform_x, platform_y, platform_w, platform_h, (225, 225, 255))
    platforms.append(platform)

    if random.random() < spring_chance:
        spring_w = 20
        spring_h = 10
        spring_x = platform.rect.x + (platform_w - spring_w) // 2
        spring_y = platform.rect.y - spring_h
        spring = Spring(
            spring_x,
            spring_y,
            spring_w,
            spring_h,
            (255, 215, 0),
            is_special=random.random() < special_spring_chance,
        )
        springs.append(spring)

    for i in range(platform_count - 1):
        x = random.randint(0, bg_x - platform_w)
        y = (bg_y - 100) - (i * 60)
        platform = Platform(x, y, platform_w, platform_h, (225, 225, 255))
        platforms.append(platform)

        if random.random() < spring_chance:
            spring_w = 20
            spring_h = 10
            spring_x = platform.rect.x + (platform_w - spring_w) // 2
            spring_y = platform.rect.y - spring_h
            spring = Spring(
                spring_x,
                spring_y,
                spring_w,
                spring_h,
                (255, 215, 0),
                is_special=random.random() < special_spring_chance,
            )
            springs.append(spring)

    score = 0
    game_over = False
    initial_player_y = player.rect.y


######################## main loop ######################
while True:
    FPS.tick(60)
    screen.fill((0, 0, 0))
    if not game_over:
        update_camera()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(-1, bg_x)
        if keys[pygame.K_RIGHT]:
            player.move(1, bg_x)
        player.apply_gravity()
        if not player.check_spring_collision(springs):
            player.check_platform_collision(platforms)
        if player.rect.top > bg_y:
            game_over = True
            if score > highest_score:
                highest_score = score
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN and game_over:
            reset_game()
    for platform in platforms:
        platform.draw(screen)

    for spring in springs:
        spring.draw(screen)

    player.draw(screen)

    score_text = font.render(f"Score: {int(score)}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    if game_over:
        game_over_text = font.render(
            "Game Over! Press any key to restart.", True, (255, 255, 255)
        )
        highest_score_text = font.render(
            f"Highest Score: {int(highest_score)}", True, (255, 255, 155)
        )
        text_rect = game_over_text.get_rect(center=(bg_x // 2, bg_y // 2))
        score_rect = score_text.get_rect(center=(bg_x / 2, bg_y / 2 + 40))
        highest_score_rect = highest_score_text.get_rect(
            center=(bg_x / 2, bg_y / 2 + 80)
        )
        screen.blit(game_over_text, text_rect)
        screen.blit(highest_score_text, score_rect)
    pygame.display.update()
