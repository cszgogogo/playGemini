import cv2
import mediapipe as mp
import pygame
import random
import math
import colorsys

# --- 1. 参数设置 (基于你提供的"神之手"参数) ---
WIDTH, HEIGHT = 1000, 700
PARTICLE_COUNT = 800  # 粒子数量
TRAIL_FADE = 40  # 拖尾层透明度 (越小拖尾越长)

# === 物理核心参数 ===
ATTRACTION_STRENGTH = 1.5  # 强引力
SWIRL_STRENGTH = 0.3  # 强漩涡
FRICTION = 0.95  # 低阻力
MAX_SPEED = 40  # 允许高速飞行 (视觉拉伸需要高速度)
EXPLOSION_FORCE = 30  # 炸开力度
WALL_DAMPING = -0.7  # 撞墙反弹

# --- 2. 初始化 ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("God Hand Swirl: Final Fusion")
clock = pygame.time.Clock()

# 拖尾层
fade_surface = pygame.Surface((WIDTH, HEIGHT))
fade_surface.set_alpha(TRAIL_FADE)
fade_surface.fill((0, 0, 0))

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)


# --- 3. 形状生成逻辑 ---
def get_heart_points(count, scale=12):
    points = []
    for _ in range(count):
        t = random.uniform(0, 2 * math.pi)
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        points.append((WIDTH // 2 + x * scale, HEIGHT // 2 + y * scale))
    return points


def get_text_points(text, count):
    font = pygame.font.SysFont("Arial", 150, bold=True)
    surface = font.render(text, True, (255, 255, 255))
    w, h = surface.get_size()
    mask = pygame.mask.from_surface(surface)
    points = []
    while len(points) < count:
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        if mask.get_at((x, y)):
            points.append((WIDTH // 2 - w // 2 + x, HEIGHT // 2 - h // 2 + y))
    return points


# 预计算形状
SHAPE_HEART = get_heart_points(PARTICLE_COUNT)
SHAPE_TEXT = get_text_points("MAGIC", PARTICLE_COUNT)


# --- 4. 粒子系统 ---
class Particle:
    def __init__(self, index):
        self.reset()
        self.index = index

    def reset(self):
        self.x = random.randint(20, WIDTH - 20)
        self.y = random.randint(20, HEIGHT - 20)
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.hue = random.random()
        self.size = random.randint(1, 3)  # 稍微小一点，适合画线

    def apply_physics(self, mode, attractors, repulsors, target_pos=None):
        # === 模式 1 & 2: 形状吸附 ===
        if mode != 0 and target_pos:
            tx, ty = target_pos
            dx = tx - self.x
            dy = ty - self.y
            # 弹性吸附
            self.vx += dx * 0.08
            self.vy += dy * 0.08
            self.vx *= 0.85
            self.vy *= 0.85

            # 形状模式下，手部(无论握拳张开)都是干扰源
            all_hands = attractors + repulsors
            for (hx, hy) in all_hands:
                dist_sq = (hx - self.x) ** 2 + (hy - self.y) ** 2 + 1
                if dist_sq < 15000:  # 靠近才干扰
                    dist = math.sqrt(dist_sq)
                    force = 2000 / dist_sq
                    self.vx -= (hx - self.x) / dist * force
                    self.vy -= (hy - self.y) / dist * force

        # === 模式 0: 神之手物理 (基于你提供的代码逻辑) ===
        else:
            # A. 处理引力源 (握拳)
            if attractors:
                for (ax, ay) in attractors:
                    dx = ax - self.x
                    dy = ay - self.y
                    dist = math.hypot(dx, dy) + 0.1  # 防止除0

                    # --- 1. 强引力 (直接飞向手心) ---
                    # 你的原版逻辑：(dx / dist) * ATTRACTION_STRENGTH * 5
                    force_x = (dx / dist) * ATTRACTION_STRENGTH * 5
                    force_y = (dy / dist) * ATTRACTION_STRENGTH * 5

                    # --- 2. 强漩涡 (绕手心旋转) ---
                    # 你的原版逻辑：垂直向量 (-dy, dx)
                    swirl_x = -dy * SWIRL_STRENGTH * 0.2
                    swirl_y = dx * SWIRL_STRENGTH * 0.2

                    # 距离越近，旋转越快 (模拟角动量守恒)
                    if dist < 200:
                        swirl_x *= 1.5
                        swirl_y *= 1.5

                    # 极近距离保护：防止粒子无限聚集在一个点穿模
                    # 如果距离小于20，减少向心力，保留旋转力
                    if dist < 30:
                        force_x *= 0.1
                        force_y *= 0.1

                    self.vx += force_x + swirl_x
                    self.vy += force_y + swirl_y

            # B. 处理斥力源 (张手)
            for (rx, ry) in repulsors:
                dx = rx - self.x
                dy = ry - self.y
                dist_sq = dx * dx + dy * dy + 1
                if dist_sq < 40000:  # 200像素范围内有效
                    dist = math.sqrt(dist_sq)
                    force = 10000 / dist_sq  # 强力推开
                    self.vx -= (dx / dist) * force
                    self.vy -= (dy / dist) * force

            # C. 物理通用属性
            self.vx *= FRICTION
            self.vy *= FRICTION

            # 速度限制 (Visuals needed)
            speed = math.hypot(self.vx, self.vy)
            if speed > MAX_SPEED:
                scale = MAX_SPEED / speed
                self.vx *= scale
                self.vy *= scale

        # 更新位置
        self.x += self.vx
        self.y += self.vy

        # 边界反弹
        if self.x < self.size:
            self.x = self.size; self.vx *= WALL_DAMPING
        elif self.x > WIDTH - self.size:
            self.x = WIDTH - self.size; self.vx *= WALL_DAMPING
        if self.y < self.size:
            self.y = self.size; self.vy *= WALL_DAMPING
        elif self.y > HEIGHT - self.size:
            self.y = HEIGHT - self.size; self.vy *= WALL_DAMPING

    def draw(self, surface):
        speed = math.hypot(self.vx, self.vy)
        lightness = min(0.5 + speed * 0.03, 1.0)
        rgb = colorsys.hsv_to_rgb((self.hue + pygame.time.get_ticks() * 0.0005) % 1, 0.9, lightness)
        color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

        # === 视觉拉伸 (Warp Effect) ===
        # 只有速度够快才拉伸，这样静止时是圆点，飞起来是光线
        if speed > 3:
            start_pos = (self.x, self.y)
            # 尾巴长度取决于速度
            end_pos = (self.x - self.vx * 1.5, self.y - self.vy * 1.5)
            pygame.draw.line(surface, color, start_pos, end_pos, self.size)
        else:
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)


particles = [Particle(i) for i in range(PARTICLE_COUNT)]


# --- 5. 辅助函数 ---
def is_fist_robust(landmarks):
    wrist = landmarks.landmark[0]
    count = 0
    tips = [8, 12, 16, 20]
    pips = [5, 9, 13, 17]
    for i in range(4):
        tip = landmarks.landmark[tips[i]]
        pip = landmarks.landmark[pips[i]]
        # 1.1 倍阈值，让握拳判定更灵敏
        if math.hypot(tip.x - wrist.x, tip.y - wrist.y) < math.hypot(pip.x - wrist.x, pip.y - wrist.y) * 1.1:
            count += 1
    return count >= 3


def draw_lightning(surface, p1, p2):
    mid_x = (p1[0] + p2[0]) / 2 + random.randint(-20, 20)
    mid_y = (p1[1] + p2[1]) / 2 + random.randint(-20, 20)
    pygame.draw.line(surface, (150, 255, 255), p1, (mid_x, mid_y), 2)
    pygame.draw.line(surface, (150, 255, 255), (mid_x, mid_y), p2, 2)


# --- 6. 主程序 ---
cap = cv2.VideoCapture(0)
mode = 0  # 0=Free, 1=Heart, 2=Text

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_0: mode = 0
            if event.key == pygame.K_1: mode = 1
            if event.key == pygame.K_2: mode = 2
            if event.key == pygame.K_SPACE:
                for p in particles:
                    # 赋予随机爆炸速度
                    p.vx = random.uniform(-20, 20)
                    p.vy = random.uniform(-20, 20)

    success, image = cap.read()
    if not success: continue

    image = cv2.flip(image, 1)
    results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # 绘制拖尾背景
    screen.blit(fade_surface, (0, 0))

    # 数据收集
    attractors = []
    repulsors = []
    hand_locs = []

    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            cx = int(landmarks.landmark[9].x * WIDTH)
            cy = int(landmarks.landmark[9].y * HEIGHT)
            cx = max(30, min(WIDTH - 30, cx))
            cy = max(30, min(HEIGHT - 30, cy))

            hand_locs.append((cx, cy))
            grabbing = is_fist_robust(landmarks)

            # --- 模式 0: 神之手逻辑 ---
            if mode == 0:
                if grabbing:
                    attractors.append((cx, cy))
                    # 视觉: 红色黑洞核心
                    pygame.draw.circle(screen, (0, 0, 0), (cx, cy), 15)
                    pygame.draw.circle(screen, (255, 50, 50), (cx, cy), 18, 2)
                    # 引导线
                    pygame.draw.circle(screen, (100, 0, 0), (cx, cy), 120, 1)
                else:
                    repulsors.append((cx, cy))
                    # 视觉: 青色斥力场
                    pygame.draw.circle(screen, (0, 255, 255), (cx, cy), 20, 2)

            # --- 模式 1/2: 形状干扰 ---
            else:
                if grabbing:
                    attractors.append((cx, cy))
                    pygame.draw.circle(screen, (255, 100, 100), (cx, cy), 15)
                else:
                    repulsors.append((cx, cy))
                    pygame.draw.circle(screen, (200, 200, 200), (cx, cy), 15, 1)

    # 双手闪电
    if len(hand_locs) == 2:
        draw_lightning(screen, hand_locs[0], hand_locs[1])

    # 更新粒子
    target_pos_list = None
    if mode == 1:
        target_pos_list = SHAPE_HEART
    elif mode == 2:
        target_pos_list = SHAPE_TEXT

    for i, p in enumerate(particles):
        target = None
        if target_pos_list:
            target = target_pos_list[i % len(target_pos_list)]

        p.apply_physics(mode, attractors, repulsors, target)
        p.draw(screen)

    # UI 提示
    font = pygame.font.SysFont("Arial", 24)
    mode_text = "God Hand" if mode == 0 else "Heart" if mode == 1 else "Text"
    screen.blit(font.render(f"Mode (0-2): {mode_text}", True, (150, 150, 150)), (10, 10))

    pygame.display.flip()
    clock.tick(60)