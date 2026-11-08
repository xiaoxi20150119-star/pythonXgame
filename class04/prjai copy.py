######################載入套件/ import packages######################
import math
import os
import random
from array import array
import urllib.request
import pygame
import sys


class Particle:
    def __init__(self, x, y, vx, vy, color, life=24, size=3):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08
        self.life -= 1

    def draw(self, surface):
        alpha = max(0, self.life / self.max_life)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), max(1, int(self.size * alpha)))


######################物件類別/ object class######################
class Brick:
    def __init__(self, x, y, width, height, color, brick_type="normal", hp=1):
        '''
        初始化磚塊屬性/ initialize brick\n
        x,y:磚塊的左上角座標/ the top left corner of the brick\n
        width,height:磚塊的寬度與高度/ the width and height of the brick\n
        color:磚塊的顏色/ the color of the brick\n
        brick_type: 磚塊類型 / special brick type\n
        hp: 磚塊生命值 / hit points\n
        '''
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hit = False
        self.brick_type = brick_type
        self.hp = hp
        self.max_hp = hp
        self.pulse = 0

    def draw(self, display_area, now=0):
        if not self.hit:
            if self.brick_type == "bonus":
                pulse = 1 + math.sin(now * 0.01) * 0.25
                glow_rect = self.rect.inflate(int(10 * pulse), int(10 * pulse))
                glow_rect.center = self.rect.center
                pygame.draw.ellipse(display_area, (255, 220, 120), glow_rect)
                pygame.draw.rect(display_area, (255, 180, 40), self.rect.inflate(2, 2), border_radius=6)
                pygame.draw.rect(display_area, (120, 70, 0), self.rect, 2, border_radius=6)
                pygame.draw.polygon(
                    display_area,
                    (255, 255, 255),
                    [
                        (self.rect.centerx, self.rect.y + 4),
                        (self.rect.right - 6, self.rect.centery),
                        (self.rect.centerx, self.rect.bottom - 4),
                        (self.rect.x + 6, self.rect.centery),
                    ],
                )
                pygame.draw.circle(display_area, (255, 245, 180), self.rect.center, 3)
                return

            if self.brick_type == "boss":
                pulse = 1 + math.sin(now * 0.02) * 0.18
                glow = self.rect.inflate(int(18 * pulse), int(16 * pulse))
                glow.center = self.rect.center
                pygame.draw.ellipse(display_area, (255, 80, 80), glow)
                pygame.draw.rect(display_area, (255, 90, 90), self.rect, border_radius=10)
                pygame.draw.rect(display_area, (120, 0, 0), self.rect, 4, border_radius=10)
                hp_text = font.render(f"BOSS {self.hp}", True, (255, 255, 200))
                display_area.blit(hp_text, (self.rect.centerx - hp_text.get_width() // 2, self.rect.centery - 8))
                return

            pygame.draw.rect(display_area, self.color, self.rect)

            if self.brick_type == "explosive":
                pygame.draw.circle(display_area, (255, 255, 255), self.rect.center, 4)
                pygame.draw.line(
                    display_area,
                    (255, 255, 255),
                    (self.rect.x + 4, self.rect.centery),
                    (self.rect.right - 4, self.rect.centery),
                    2,
                )
            elif self.brick_type == "spawn":
                pygame.draw.rect(
                    display_area,
                    (255, 255, 255),
                    (self.rect.x + 5, self.rect.y + 5, self.rect.width - 10, self.rect.height - 10),
                    2,
                )
            elif self.brick_type == "boost":
                pygame.draw.line(
                    display_area,
                    (255, 255, 255),
                    (self.rect.centerx, self.rect.y + 4),
                    (self.rect.centerx, self.rect.bottom - 4),
                    2,
                )
                pygame.draw.line(
                    display_area,
                    (255, 255, 255),
                    (self.rect.x + 4, self.rect.centery),
                    (self.rect.right - 4, self.rect.centery),
                    2,
                )
            elif self.brick_type == "hard":
                pygame.draw.rect(
                    display_area,
                    (255, 255, 255),
                    (self.rect.x + 2, self.rect.y + 2, self.rect.width - 4, self.rect.height - 4),
                    2,
                )
                if self.hp > 1:
                    pygame.draw.line(
                        display_area,
                        (255, 255, 255),
                        (self.rect.x + 6, self.rect.y + 6),
                        (self.rect.right - 6, self.rect.bottom - 6),
                        1,
                    )


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
        pygame.draw.circle(display_area, self.color, (int(self.x), int(self.y)), self.radius)

    def move(self):
        if self.is_moving:
            self.x += self.speed_x
            self.y += self.speed_y

    def check_collision(self, bg_x, bg_y, bricks, pad):
        if self.x <= 0 or self.x + self.radius >= bg_x:
            self.speed_x = -self.speed_x

        if self.y - self.radius <= 0:
            self.speed_y = -self.speed_y

        if self.y + self.radius >= bg_y:
            self.is_moving = False
            return True

        if (
            self.y + self.radius >= pad.rect.y
            and self.y + self.radius <= pad.rect.y + pad.rect.height
            and self.x >= pad.rect.x
            and self.x <= pad.rect.x + pad.rect.width
        ):
            self.speed_y = -abs(self.speed_y)

        for brick in bricks:
            if brick.hit:
                continue

            dx = abs(self.x - (brick.rect.x + brick.rect.width / 2))
            dy = abs(self.y - (brick.rect.y + brick.rect.height / 2))

            if dx <= (self.radius + brick.rect.width / 2) and dy <= (self.radius + brick.rect.height / 2):
                if brick.hp > 1:
                    brick.hp -= 1
                    if self.x < brick.rect.x or self.x > brick.rect.x + brick.rect.width:
                        self.speed_x = -self.speed_x
                    else:
                        self.speed_y = -self.speed_y
                    return False

                brick.hit = True
                if brick.brick_type == "boss":
                    brick.hp -= 1
                    if brick.hp <= 0:
                        brick.hit = True
                        score += 1000
                        spawn_mega_explosion(brick.rect.centerx, brick.rect.centery, (255, 80, 80), 140)
                        score_popups.append({"x": brick.rect.centerx, "y": brick.rect.y - 20, "text": "+1000", "color": (255, 255, 150), "life": 40})
                        play_bonus_sound()
                        return False
                    spawn_mega_explosion(brick.rect.centerx, brick.rect.centery, (255, 120, 60), 40)
                    self.speed_x = -self.speed_x
                    self.speed_y = -abs(self.speed_y)
                    return False

                if brick.brick_type == "bonus":
                    rewards = ["life", "score", "wide", "score"]
                    grant_bonus_reward(random.choice(rewards))
                    spawn_bonus_effect(brick.rect.centerx, brick.rect.centery)
                else:
                    award_brick_score(brick)
                    maybe_spawn_bonus_box(bricks)
                    spawn_explosion(brick.rect.centerx, brick.rect.centery, brick.color, 22)

                if brick.brick_type == "explosive":
                    for target in bricks:
                        if not target.hit and target != brick:
                            target_x = abs(target.rect.centerx - brick.rect.centerx)
                            target_y = abs(target.rect.centery - brick.rect.centery)
                            if target_x <= 100 and target_y <= 50:
                                target.hit = True
                                award_brick_score(target, extra=15)
                                spawn_explosion(target.rect.centerx, target.rect.centery, target.color, 18)

                elif brick.brick_type == "spawn":
                    spawn_x = random.randint(70, bg_x - 120)
                    spawn_y = random.randint(60, 200)
                    new_brick = Brick(spawn_x, spawn_y, brick.rect.width, brick.rect.height, (0, 255, 255), "normal")

                    can_spawn = True
                    for existing in bricks:
                        if not existing.hit and new_brick.rect.colliderect(existing.rect):
                            can_spawn = False
                            break

                    if can_spawn:
                        bricks.append(new_brick)
                    if random.random() < 0.5:
                        grant_bonus_reward("life")

                elif brick.brick_type == "boost":
                    if self.speed_x > 0:
                        self.speed_x = min(self.speed_x + 2, 15)
                    else:
                        self.speed_x = max(self.speed_x - 2, -15)

                    if self.speed_y > 0:
                        self.speed_y = min(self.speed_y + 2, 15)
                    else:
                        self.speed_y = max(self.speed_y - 2, -15)

                if self.x < brick.rect.x or self.x > brick.rect.x + brick.rect.width:
                    self.speed_x = -self.speed_x
                else:
                    self.speed_y = -self.speed_y

                return False

        return False


######################定義函式區/ define functions######################

######################初始化設定/ initialize settings######################
pygame.init()
pygame.mixer.init()
FPS = pygame.time.Clock()
######################載入圖片/ load images######################


def make_beep(frequency=440, duration=0.08, volume=0.5):
    sample_rate = 22050
    total_samples = int(sample_rate * duration)
    samples = array('h')
    for i in range(total_samples):
        t = i / sample_rate
        value = math.sin(2 * math.pi * frequency * t) * 0.7 + math.sin(2 * math.pi * frequency * 2 * t) * 0.3
        samples.append(int(32767 * volume * value))
    return pygame.mixer.Sound(buffer=samples.tobytes())


MUSIC_CHANNEL = pygame.mixer.Channel(0)
EFFECT_CHANNEL = pygame.mixer.Channel(1)
MUSIC_NOTES = [220, 277, 330, 392, 330, 277, 247, 220]
MUSIC_INDEX = 0
MUSIC_TIMER = 0
particles = []
CONAN_STYLE = 0
CONAN_STYLE_LABELS = ["真像柯南", "漫畫感", "海報版"]
CONAN_BACKGROUND_URL = os.environ.get("CONAN_BACKGROUND_URL", "")
REMOTE_BG_IMAGE = None


def load_remote_background(url):
    global REMOTE_BG_IMAGE
    if not url:
        return None

    cache_dir = os.path.join(os.getcwd(), ".cache")
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = os.path.join(cache_dir, "conan_background.jpg")

    try:
        if not os.path.exists(cache_path):
            urllib.request.urlretrieve(url, cache_path)
        image = pygame.image.load(cache_path).convert()
        REMOTE_BG_IMAGE = pygame.transform.smoothscale(image, (bg_x, bg_y))
        return REMOTE_BG_IMAGE
    except Exception:
        return None


def play_sound(kind):
    try:
        if kind == "hit":
            sound = make_beep(660, 0.05, 0.22)
        elif kind == "lose":
            sound = make_beep(180, 0.20, 0.34)
        elif kind == "start":
            chime = [440, 554, 659]
            for idx, freq in enumerate(chime):
                tone = make_beep(freq, 0.06, 0.18)
                play_sound_effect(tone)
            return
        elif kind == "score":
            sound = make_beep(880, 0.04, 0.28)
        elif kind == "win":
            chord = [523, 659, 783]
            for freq in chord:
                tone = make_beep(freq, 0.12, 0.18)
                play_sound_effect(tone)
            return
        else:
            sound = make_beep(520, 0.05, 0.2)
        play_sound_effect(sound)
    except Exception:
        pass


def play_sound_effect(sound):
    try:
        EFFECT_CHANNEL.play(sound)
    except Exception:
        pass


def play_background_music():
    global MUSIC_INDEX
    try:
        note = MUSIC_NOTES[MUSIC_INDEX % len(MUSIC_NOTES)]
        sound = make_beep(note, 0.18, 0.08)
        if not MUSIC_CHANNEL.get_busy():
            MUSIC_CHANNEL.play(sound)
        else:
            MUSIC_CHANNEL.queue(sound)
        MUSIC_INDEX += 1
    except Exception:
        pass


def spawn_explosion(x, y, color, count=18, speed_min=1.5, speed_max=5.0, life_min=18, life_max=36, size_min=2, size_max=5):
    for _ in range(count):
        angle = random.random() * math.tau
        speed = random.uniform(speed_min, speed_max)
        particles.append(
            Particle(
                x,
                y,
                math.cos(angle) * speed,
                math.sin(angle) * speed - 0.5,
                color,
                life=random.randint(life_min, life_max),
                size=random.randint(size_min, size_max),
            )
        )


def spawn_bonus_effect(x, y):
    spawn_explosion(x, y, (255, 215, 0), count=48, speed_min=2.5, speed_max=8.0, life_min=28, life_max=55, size_min=3, size_max=8)
    spawn_explosion(x, y, (255, 120, 60), count=20, speed_min=1.2, speed_max=4.0, life_min=20, life_max=32, size_min=2, size_max=6)


def spawn_mega_explosion(x, y, color=(255, 80, 80), count=80):
    spawn_explosion(x, y, color, count=count, speed_min=2.0, speed_max=10.0, life_min=24, life_max=70, size_min=3, size_max=10)
    spawn_explosion(x, y, (255, 255, 120), count=count // 2, speed_min=1.0, speed_max=6.5, life_min=16, life_max=42, size_min=2, size_max=7)


def play_bonus_sound():
    try:
        pattern = [784, 988, 1174, 988, 1318]
        for idx, freq in enumerate(pattern):
            tone = make_beep(freq, 0.05, 0.16 if idx % 2 == 0 else 0.12)
            play_sound_effect(tone)
            pygame.time.delay(40)
    except Exception:
        pass


def draw_detective_scene(surface, beat=0, style_index=None):
    if REMOTE_BG_IMAGE is not None:
        surface.blit(REMOTE_BG_IMAGE, (0, 0))
        return

    if style_index is None:
        style_index = CONAN_STYLE

    style_index = max(0, min(2, style_index))
    scale = 1.0 + (style_index == 2) * 0.27
    outline_width = 2 if style_index == 0 else 4 if style_index == 1 else 5
    shirt_color = (26, 38, 78)
    jacket_color = (28, 56, 120) if style_index == 2 else (26, 38, 78)
    accent_color = (230, 35, 42)
    if style_index == 1:
        accent_color = (230, 70, 50)

    surface.fill((8, 10, 24))
    for i in range(0, 600, 22):
        pygame.draw.line(surface, (20, 28, 40), (0, i), (800, i), 1)

    for star_x in range(40, 760, 55):
        star_y = 40 + ((star_x * 7) % 120)
        pygame.draw.circle(surface, (255, 255, 200), (star_x, star_y), 2)

    moon_x = 650 + math.sin(beat * 0.02) * 8
    moon_y = 80 + math.cos(beat * 0.03) * 8
    pygame.draw.circle(surface, (255, 240, 180), (int(moon_x), int(moon_y)), int(26 * scale))
    pygame.draw.circle(surface, (100, 120, 160), (int(moon_x) + 8, int(moon_y) - 8), int(24 * scale))

    city_base = 420
    for i in range(0, bg_x + 50, 40):
        height = 80 + (i % 140)
        rect = pygame.Rect(i, city_base - height, 28, height)
        pygame.draw.rect(surface, (18, 24, 38), rect)
        pygame.draw.rect(surface, (60, 110, 170), rect, 1)

    detective_x = 610 + math.sin(beat * 0.01) * 12
    detective_y = 430 + math.cos(beat * 0.02) * 8
    if style_index == 2:
        detective_x += 20
        detective_y -= 18

    body_top = detective_y - 18
    head_radius = int(18 * scale)
    head_y = int(body_top - 18)
    body_w = int(36 * scale)
    body_h = int(34 * scale)
    torso_w = int(44 * scale)
    torso_h = int(52 * scale)

    # 頭部：短黑髮 + 圓眼鏡 + 年輕臉型
    pygame.draw.circle(surface, (244, 216, 185), (int(detective_x), head_y), head_radius)
    pygame.draw.arc(surface, (20, 20, 24), (int(detective_x) - 18, int(body_top - 42), 36, 18), 3.4, 6.2, outline_width)

    if style_index == 1:
        hair_color = (12, 12, 18)
        pygame.draw.polygon(surface, hair_color, [
            (int(detective_x) - 18, head_y),
            (int(detective_x) - 8, head_y - 18),
            (int(detective_x), head_y - 22),
            (int(detective_x) + 8, head_y - 18),
            (int(detective_x) + 18, head_y),
            (int(detective_x) + 14, head_y + 8),
            (int(detective_x) - 14, head_y + 8),
        ])
    else:
        hair_color = (24, 24, 30)
        pygame.draw.polygon(surface, hair_color, [
            (int(detective_x) - 18, head_y),
            (int(detective_x) - 6, head_y - 18),
            (int(detective_x) + 2, head_y - 30),
            (int(detective_x) + 12, head_y - 20),
            (int(detective_x) + 18, head_y),
            (int(detective_x) + 18, head_y + 8),
            (int(detective_x) - 18, head_y + 8),
        ])

    eye_y = int(body_top - 22)
    eye_half = int(6 * scale)
    eye_offset = int(7 * scale)
    pygame.draw.circle(surface, (40, 40, 42), (int(detective_x) - eye_offset, eye_y), eye_half, max(2, outline_width))
    pygame.draw.circle(surface, (40, 40, 42), (int(detective_x) + eye_offset, eye_y), eye_half, max(2, outline_width))
    pygame.draw.line(surface, (40, 40, 42), (int(detective_x) - 1, eye_y), (int(detective_x) + 1, eye_y), 2)
    pygame.draw.line(surface, (40, 40, 42), (int(detective_x) - 14, eye_y), (int(detective_x) - 18, eye_y), 2)
    pygame.draw.line(surface, (40, 40, 42), (int(detective_x) + 14, eye_y), (int(detective_x) + 18, eye_y), 2)

    pygame.draw.line(surface, (200, 130, 110), (int(detective_x), int(body_top - 16)), (int(detective_x), int(body_top - 10)), 2)
    pygame.draw.arc(surface, (200, 130, 110), (int(detective_x) - 5, int(body_top - 8), 10, 8), 0.2, 3.0, 2)

    # 上身：藍色外套、白襯衫、紅色領帶
    pygame.draw.rect(surface, jacket_color, (int(detective_x) - int((18 * scale)), int(body_top - 2), body_w, int(34 * scale)), border_radius=6)
    pygame.draw.rect(surface, (240, 240, 240), (int(detective_x) - int(10 * scale), int(body_top + 2), int(20 * scale), int(18 * scale)), border_radius=3)
    pygame.draw.polygon(surface, accent_color, [
        (int(detective_x) - int(4 * scale), int(body_top + 2)),
        (int(detective_x) + int(4 * scale), int(body_top + 2)),
        (int(detective_x) + int(12 * scale), int(body_top + int(18 * scale))),
        (int(detective_x), int(body_top + int(25 * scale))),
        (int(detective_x) - int(12 * scale), int(body_top + int(18 * scale))),
    ])

    # 手臂與腿
    pygame.draw.rect(surface, jacket_color, (int(detective_x) - int(20 * scale), int(body_top + int(28 * scale)), int(10 * scale), int(44 * scale)))
    pygame.draw.rect(surface, jacket_color, (int(detective_x) + int(10 * scale), int(body_top + int(28 * scale)), int(10 * scale), int(44 * scale)))
    pygame.draw.rect(surface, (20, 30, 42), (int(detective_x) - int(12 * scale), int(body_top + int(68 * scale)), int(12 * scale), int(52 * scale)))
    pygame.draw.rect(surface, (20, 30, 42), (int(detective_x) + int(2 * scale), int(body_top + int(68 * scale)), int(12 * scale), int(52 * scale)))

    # 鞋子
    pygame.draw.rect(surface, (18, 18, 20), (int(detective_x) - int(14 * scale), int(body_top + int(118 * scale)), int(18 * scale), int(8 * scale)))
    pygame.draw.rect(surface, (18, 18, 20), (int(detective_x) + int(4 * scale), int(body_top + int(118 * scale)), int(18 * scale), int(8 * scale)))

    if style_index == 1:
        pygame.draw.line(surface, (55, 70, 90), (int(detective_x) - int(12 * scale), int(body_top + int(18 * scale))), (int(detective_x) + int(12 * scale), int(body_top + int(18 * scale))), 4)
    else:
        pygame.draw.line(surface, (58, 86, 146), (int(detective_x) - int(6 * scale), int(body_top + int(2 * scale))), (int(detective_x) + int(6 * scale), int(body_top + int(2 * scale))), max(2, outline_width))

    if style_index == 2:
        highlight = pygame.Rect(int(detective_x) - 80, int(body_top) - 120, 160, 210)
        pygame.draw.rect(surface, (20, 20, 20), highlight, 2)
        pygame.draw.circle(surface, (255, 255, 255), (int(detective_x) - 42, int(body_top) - 16), 5)
        pygame.draw.circle(surface, (255, 255, 255), (int(detective_x) + 42, int(body_top) - 16), 5)


######################遊戲視窗設定/ game window settings######################
bg_x = 800
bg_y = 600
bg_width = (bg_x, bg_y)
pygame.display.set_caption("My Game")
screen = pygame.display.set_mode(bg_width)
game_surface = pygame.Surface((bg_x, bg_y))
shake_timer = 0
shake_power = 0
######################磚塊設定/ brick settings######################
bricks_w = 58
bricks_h = 16
bricks_gap = 2
score_popups = []
LEVELS = [
    {
        "rows": 4,
        "cols": 8,
        "start_x": 100,
        "start_y": 70,
        "ball_speed": 5,
        "pad_width": 58,
        "special": {
            (1, 1): ("explosive", 1),
            (5, 2): ("spawn", 1),
            (3, 3): ("boost", 1),
        },
    },
    {
        "rows": 5,
        "cols": 9,
        "start_x": 80,
        "start_y": 60,
        "ball_speed": 6,
        "pad_width": 54,
        "special": {
            (2, 1): ("explosive", 1),
            (6, 2): ("spawn", 1),
            (4, 3): ("boost", 1),
            (1, 4): ("hard", 2),
        },
    },
    {
        "rows": 6,
        "cols": 10,
        "start_x": 70,
        "start_y": 50,
        "ball_speed": 7,
        "pad_width": 50,
        "special": {
            (1, 1): ("explosive", 1),
            (7, 2): ("spawn", 1),
            (4, 3): ("boost", 1),
            (2, 4): ("hard", 2),
            (8, 4): ("hard", 2),
            (5, 5): ("explosive", 1),
        },
    },
    {
        "rows": 7,
        "cols": 11,
        "start_x": 55,
        "start_y": 40,
        "ball_speed": 8,
        "pad_width": 44,
        "special": {
            (1, 0): ("explosive", 1),
            (3, 1): ("boost", 1),
            (5, 2): ("spawn", 1),
            (8, 2): ("hard", 2),
            (2, 4): ("explosive", 1),
            (7, 4): ("boost", 1),
            (9, 5): ("spawn", 1),
            (4, 6): ("hard", 2),
            (6, 6): ("hard", 2),
        },
    },
    {
        "rows": 8,
        "cols": 12,
        "start_x": 40,
        "start_y": 35,
        "ball_speed": 9,
        "pad_width": 40,
        "special": {
            (1, 0): ("explosive", 1),
            (3, 0): ("boost", 1),
            (6, 1): ("spawn", 1),
            (9, 1): ("hard", 2),
            (2, 2): ("boost", 1),
            (5, 2): ("explosive", 1),
            (8, 3): ("spawn", 1),
            (10, 3): ("hard", 2),
            (1, 4): ("hard", 2),
            (4, 4): ("boost", 1),
            (7, 5): ("explosive", 1),
            (10, 5): ("spawn", 1),
            (3, 6): ("hard", 2),
            (8, 6): ("boost", 1),
            (6, 7): ("explosive", 1),
        },
    },
    {
        "rows": 9,
        "cols": 12,
        "start_x": 35,
        "start_y": 30,
        "ball_speed": 10,
        "pad_width": 38,
        "special": {
            (0, 0): ("boost", 1),
            (2, 1): ("explosive", 1),
            (5, 1): ("hard", 2),
            (8, 1): ("spawn", 1),
            (10, 2): ("boost", 1),
            (3, 3): ("explosive", 1),
            (6, 3): ("hard", 2),
            (9, 3): ("spawn", 1),
            (1, 5): ("boost", 1),
            (4, 5): ("hard", 2),
            (7, 5): ("explosive", 1),
            (10, 5): ("spawn", 1),
            (2, 7): ("hard", 2),
            (5, 7): ("boost", 1),
            (8, 7): ("explosive", 1),
            (11, 8): ("spawn", 1),
        },
    },
    {
        "rows": 10,
        "cols": 13,
        "start_x": 30,
        "start_y": 25,
        "ball_speed": 11,
        "pad_width": 36,
        "special": {
            (1, 0): ("boost", 1),
            (4, 0): ("explosive", 1),
            (7, 1): ("spawn", 1),
            (10, 1): ("hard", 2),
            (2, 2): ("hard", 2),
            (6, 2): ("boost", 1),
            (9, 2): ("explosive", 1),
            (12, 3): ("spawn", 1),
            (3, 4): ("boost", 1),
            (6, 4): ("hard", 2),
            (9, 4): ("explosive", 1),
            (1, 6): ("spawn", 1),
            (4, 6): ("boost", 1),
            (7, 6): ("hard", 2),
            (10, 6): ("explosive", 1),
            (2, 8): ("hard", 2),
            (5, 8): ("boost", 1),
            (8, 8): ("spawn", 1),
            (11, 8): ("explosive", 1),
        },
    },
    {
        "rows": 1,
        "cols": 1,
        "start_x": 350,
        "start_y": 120,
        "ball_speed": 12,
        "pad_width": 34,
        "boss": {"x": 330, "y": 90, "width": 140, "height": 42},
        "special": {
            (0, 0): ("boss", 8),
        },
    },
]


def build_stage(level_index):
    config = LEVELS[level_index]
    bricks = []

    if config.get("boss"):
        boss = config["boss"]
        boss_brick = Brick(boss["x"], boss["y"], boss["width"], boss["height"], (255, 90, 90), "boss", 8)
        bricks.append(boss_brick)
        return bricks

    for col in range(config["cols"]):
        for row in range(config["rows"]):
            x = col * (bricks_w + bricks_gap) + config["start_x"]
            y = row * (bricks_h + bricks_gap) + config["start_y"]
            brick_type_data = config["special"].get((col, row), ("normal", 1))
            brick_type = brick_type_data[0]
            hp = brick_type_data[1]
            color = (random.randint(50, 255), random.randint(0, 255), random.randint(0, 255))

            if brick_type == "explosive":
                color = (255, 100, 50)
            elif brick_type == "spawn":
                color = (50, 200, 255)
            elif brick_type == "boost":
                color = (255, 215, 0)
            elif brick_type == "hard":
                color = (150, 150, 150)

            brick = Brick(x, y, bricks_w, bricks_h, color, brick_type, hp)
            bricks.append(brick)
    return bricks


def award_brick_score(brick, extra=0):
    global score
    bonus_values = {
        "normal": 10,
        "explosive": 30,
        "spawn": 40,
        "boost": 50,
        "hard": 25,
        "bonus": 80,
    }
    score += bonus_values.get(brick.brick_type, 10) + extra
    if brick.brick_type in {"explosive", "spawn", "boost", "hard", "bonus", "boss"}:
        spawn_mega_explosion(brick.rect.centerx, brick.rect.centery, (255, 180, 80) if brick.brick_type == "boss" else (255, 120, 60))

    if not hasattr(brick, "popup_done") or not brick.popup_done:
        score_popups.append({
            "x": brick.rect.centerx,
            "y": brick.rect.y - 8,
            "text": f"+{bonus_values.get(brick.brick_type, 10) + extra}",
            "color": (255, 215, 0),
            "life": 28,
        })
        brick.popup_done = True


def maybe_spawn_bonus_box(bricks):
    if any(not brick.hit and brick.brick_type == "bonus" for brick in bricks):
        return
    if random.random() > 0.35:
        return

    for _ in range(200):
        x = random.randint(50, bg_x - 110)
        y = random.randint(70, 220)
        rect = pygame.Rect(x, y, bricks_w, bricks_h)
        if all(not rect.colliderect(existing.rect) for existing in bricks if not existing.hit):
            bricks.append(Brick(x, y, bricks_w, bricks_h, (255, 200, 80), "bonus", 1))
            return


def grant_bonus_reward(reward_kind):
    global score, lives
    rewards = {
        "life": ("+1 Life", 0, 1),
        "score": ("+200", 200, 0),
        "wide": ("Wide Pad", 150, 0),
    }
    label, points, life_gain = rewards.get(reward_kind, ("+120", 120, 0))
    score += points
    lives += life_gain
    score_popups.append({
        "x": pad.rect.centerx,
        "y": pad.rect.y - 16,
        "text": label,
        "color": (255, 243, 160),
        "life": 40,
    })
    play_bonus_sound()
    spawn_bonus_effect(pad.rect.centerx, pad.rect.y)

    if reward_kind == "wide":
        pad.rect.width = min(pad.rect.width + 12, 120)


######################顯示文字設定/ text display settings######################
font = pygame.font.Font(None, 32)
title_font = pygame.font.Font(None, 72)
ui_font = pygame.font.Font(None, 24)

######################底板設定/ paddle settings######################
pad = Brick(0, bg_y - 48, bricks_w, bricks_h, (255, 255, 255))
######################球設定/ ball settings######################
ball_radius = 10
ball_color = (255, 215, 0)
ball = Ball(pad.rect.x + pad.rect.width // 2, pad.rect.y - ball_radius, ball_radius, ball_color)
current_stage = 0
lives = 3
score = 0
leaderboard = []
game_state = "start"


def load_leaderboard():
    path = os.path.join(os.getcwd(), "breakout_leaderboard.txt")
    try:
        with open(path, "r", encoding="utf-8") as file:
            values = [int(line.strip()) for line in file if line.strip()]
            return sorted(values, reverse=True)[:5]
    except Exception:
        return [0, 0, 0]


def save_leaderboard(values):
    path = os.path.join(os.getcwd(), "breakout_leaderboard.txt")
    try:
        with open(path, "w", encoding="utf-8") as file:
            for value in values[:5]:
                file.write(f"{value}\n")
    except Exception:
        pass


def update_leaderboard(new_score):
    global leaderboard
    leaderboard = sorted(load_leaderboard() + [new_score], reverse=True)[:5]
    save_leaderboard(leaderboard)


def reset_game():
    global current_stage, lives, score, game_state, shake_timer, shake_power, leaderboard
    current_stage = 0
    lives = 3
    score = 0
    game_state = "start"
    shake_timer = 0
    shake_power = 0
    setup_stage(current_stage)
    leaderboard = load_leaderboard()


def setup_stage(stage_index):
    global bricks, current_stage, pad, ball
    current_stage = stage_index
    bricks = build_stage(stage_index)
    pad.rect.width = LEVELS[stage_index]["pad_width"]
    pad.rect.x = (bg_x - pad.rect.width) // 2
    ball.speed_x = LEVELS[stage_index]["ball_speed"]
    ball.speed_y = -LEVELS[stage_index]["ball_speed"]
    ball.is_moving = False
    ball.x = pad.rect.x + pad.rect.width // 2
    ball.y = pad.rect.y - ball_radius


leaderboard = load_leaderboard()
REMOTE_BG_IMAGE = load_remote_background(CONAN_BACKGROUND_URL)
setup_stage(current_stage)
######################遊戲結束設定/ game over settings######################

######################主程式/ main program######################
while True:
    FPS.tick(60)
    now = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                CONAN_STYLE = event.key - pygame.K_1
            if game_state == "start" and (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN):
                game_state = "playing"
                play_sound("start")
            elif game_state == "gameover" and (event.key == pygame.K_r or event.key == pygame.K_RETURN):
                reset_game()
                game_state = "playing"
                play_sound("start")
            elif game_state == "win" and (event.key == pygame.K_r or event.key == pygame.K_RETURN):
                reset_game()
                game_state = "start"
            elif game_state == "playing" and event.key == pygame.K_SPACE and not ball.is_moving:
                ball.is_moving = True

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "start":
                game_state = "playing"
                play_sound("start")
            elif game_state == "gameover":
                reset_game()
                game_state = "playing"
                play_sound("start")
            elif game_state == "win":
                reset_game()
                game_state = "start"
            elif not ball.is_moving:
                ball.is_moving = True

    if now - MUSIC_TIMER > 200 and game_state in {"playing", "start"}:
        play_background_music()
        MUSIC_TIMER = now

    if game_state == "playing":
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pad.rect.x = mouse_x - pad.rect.width // 2

        if pad.rect.x < 0:
            pad.rect.x = 0

        if pad.rect.x + pad.rect.width > bg_x:
            pad.rect.x = bg_x - pad.rect.width

        if not ball.is_moving:
            ball.x = pad.rect.x + pad.rect.width // 2
            ball.y = pad.rect.y - ball_radius
        else:
            ball.move()
            brick_hit = ball.check_collision(bg_x, bg_y, bricks, pad)
            if brick_hit:
                lives -= 1
                play_sound("lose")
                shake_timer = 12
                shake_power = 8
                if lives <= 0:
                    game_state = "gameover"
                    lives = 0
                    update_leaderboard(score)
                    leaderboard = load_leaderboard()
                else:
                    setup_stage(current_stage)

        if all(brick.hit for brick in bricks):
            stage_bonus = 100 + (current_stage + 1) * 25
            score += stage_bonus
            play_sound("score")
            current_stage += 1
            if current_stage >= len(LEVELS):
                update_leaderboard(score)
                leaderboard = load_leaderboard()
                game_state = "win"
                play_sound("win")
            else:
                setup_stage(current_stage)

        if shake_timer > 0:
            shake_timer -= 1

        game_surface.fill((0, 0, 0))
        draw_detective_scene(game_surface, now, CONAN_STYLE)
        for brick in bricks:
            brick.draw(game_surface, now)

        for particle in particles[:]:
            particle.update()
            particle.draw(game_surface)
            if particle.life <= 0:
                particles.remove(particle)

        for popup in score_popups[:]:
            popup["life"] -= 1
            popup["y"] -= 1.2
            if popup["life"] <= 0:
                score_popups.remove(popup)
                continue
            popup_surface = ui_font.render(popup["text"], True, popup["color"])
            game_surface.blit(popup_surface, (popup["x"] - popup_surface.get_width() // 2, int(popup["y"])))

        pad.draw(game_surface)
        ball.draw(game_surface)

        stage_text = ui_font.render(f"Stage: {current_stage + 1}", True, (255, 255, 255))
        score_text = ui_font.render(f"Score: {score}", True, (255, 255, 255))
        best_text = ui_font.render(f"Best: {max(leaderboard[0], score) if leaderboard else score}", True, (255, 215, 0))
        life_text = ui_font.render("Lives: " + "♥" * lives, True, (255, 80, 80))
        bonus_text = ui_font.render("Bonus: +special bricks", True, (255, 215, 0))

        shift_x = random.randint(-shake_power, shake_power) if shake_timer > 0 else 0
        shift_y = random.randint(-shake_power, shake_power) if shake_timer > 0 else 0

        screen.fill((0, 0, 0))
        screen.blit(game_surface, (shift_x, shift_y))
        screen.blit(stage_text, (20, 20))
        screen.blit(score_text, (20, 52))
        screen.blit(best_text, (20, 84))
        screen.blit(life_text, (20, 116))
        screen.blit(bonus_text, (20, 148))

        if shake_timer > 0:
            shake_power = max(0, shake_power - 1)

    elif game_state == "start":
        screen.fill((10, 12, 28))
        draw_detective_scene(screen, now, CONAN_STYLE)
        title_text = title_font.render("Breakout", True, (255, 255, 255))
        subtitle_text = ui_font.render("Click or press Space to start", True, (200, 200, 200))
        best_score_text = ui_font.render(f"Best Score: {leaderboard[0] if leaderboard else 0}", True, (255, 215, 0))
        style_text = ui_font.render(f"Style: {CONAN_STYLE_LABELS[CONAN_STYLE]} (1/2/3)", True, (180, 220, 255))

        panel_rect = pygame.Rect(150, 130, 500, 300)
        pygame.draw.rect(screen, (25, 30, 55), panel_rect, border_radius=18)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect, 2, border_radius=18)

        logo_y = 170 + math.sin(now * 0.005) * 8
        screen.blit(title_text, (bg_x // 2 - title_text.get_width() // 2, int(logo_y)))
        screen.blit(subtitle_text, (bg_x // 2 - subtitle_text.get_width() // 2, 260))
        screen.blit(best_score_text, (bg_x // 2 - best_score_text.get_width() // 2, 300))
        screen.blit(style_text, (bg_x // 2 - style_text.get_width() // 2, 330))

        leaderboard_title = ui_font.render("Top Scores", True, (160, 200, 255))
        screen.blit(leaderboard_title, (bg_x // 2 - leaderboard_title.get_width() // 2, 340))
        for idx, value in enumerate(leaderboard[:5], start=1):
            rank_text = ui_font.render(f"{idx}. {value}", True, (255, 255, 255))
            screen.blit(rank_text, (bg_x // 2 - rank_text.get_width() // 2, 370 + idx * 22))

    elif game_state == "gameover":
        screen.fill((25, 10, 15))
        draw_detective_scene(screen, now, CONAN_STYLE)
        game_over_text = title_font.render("Game Over", True, (255, 255, 255))
        final_score_text = ui_font.render(f"Final Score: {score}", True, (255, 255, 255))
        best_score_text = ui_font.render(f"Best Score: {leaderboard[0] if leaderboard else 0}", True, (255, 215, 0))
        restart_text = ui_font.render("Click or press R to restart", True, (200, 200, 200))

        screen.blit(game_over_text, (bg_x // 2 - game_over_text.get_width() // 2, 150))
        screen.blit(final_score_text, (bg_x // 2 - final_score_text.get_width() // 2, 250))
        screen.blit(best_score_text, (bg_x // 2 - best_score_text.get_width() // 2, 285))
        screen.blit(restart_text, (bg_x // 2 - restart_text.get_width() // 2, 360))

        leaderboard_title = ui_font.render("Top Scores", True, (160, 200, 255))
        screen.blit(leaderboard_title, (bg_x // 2 - leaderboard_title.get_width() // 2, 410))
        for idx, value in enumerate(leaderboard[:5], start=1):
            rank_text = ui_font.render(f"{idx}. {value}", True, (255, 255, 255))
            screen.blit(rank_text, (bg_x // 2 - rank_text.get_width() // 2, 440 + idx * 22))

    elif game_state == "win":
        screen.fill((8, 30, 18))
        draw_detective_scene(screen, now, CONAN_STYLE)
        win_text = title_font.render("You Win!", True, (255, 255, 255))
        final_score_text = ui_font.render(f"Final Score: {score}", True, (255, 255, 255))
        best_score_text = ui_font.render(f"Best Score: {leaderboard[0] if leaderboard else 0}", True, (255, 215, 0))
        restart_text = ui_font.render("Click or press R to play again", True, (200, 200, 200))

        screen.blit(win_text, (bg_x // 2 - win_text.get_width() // 2, 150))
        screen.blit(final_score_text, (bg_x // 2 - final_score_text.get_width() // 2, 250))
        screen.blit(best_score_text, (bg_x // 2 - best_score_text.get_width() // 2, 285))
        screen.blit(restart_text, (bg_x // 2 - restart_text.get_width() // 2, 360))

        leaderboard_title = ui_font.render("Top Scores", True, (160, 200, 255))
        screen.blit(leaderboard_title, (bg_x // 2 - leaderboard_title.get_width() // 2, 410))
        for idx, value in enumerate(leaderboard[:5], start=1):
            rank_text = ui_font.render(f"{idx}. {value}", True, (255, 255, 255))
            screen.blit(rank_text, (bg_x // 2 - rank_text.get_width() // 2, 440 + idx * 22))

    pygame.display.update()
