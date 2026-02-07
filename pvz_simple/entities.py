# entities.py
"""
定义游戏中的主要实体：
- Plant（植物）
- Zombie（僵尸）
- Bullet（子弹）

全部继承自 pygame.sprite.Sprite，方便使用分组更新和碰撞检测。
"""

import pygame
from settings import (
    PLANT_MAX_HP,
    PLANT_FIRE_INTERVAL,
    ZOMBIE_MAX_HP,
    ZOMBIE_SPEED,
    BULLET_SPEED,
    BULLET_DAMAGE,
    BLUE,
    DARK_RED,
    YELLOW,
    BLACK,
    SCREEN_WIDTH,
)

class Plant(pygame.sprite.Sprite):
    """
    简化版向日射手：
    - 固定在某一格子
    - 每隔一段时间向右发射一颗子弹
    - 有血量，被僵尸碰撞时会掉血
    """

    def __init__(self, pos):
        """
        pos: 像素坐标 (x, y)，一般为格子中心位置
        """
        super().__init__()
        # 创建带透明度的surface，确保正确渲染
        self.image = pygame.Surface((50, 60), pygame.SRCALPHA)
        self.image.fill(BLUE)
        # 用一个小黑框表示"脸"
        pygame.draw.rect(self.image, BLACK, (10, 15, 30, 30), 2)
        # 画两个眼睛
        pygame.draw.circle(self.image, (255, 255, 0), (20, 25), 4)
        pygame.draw.circle(self.image, (255, 255, 0), (30, 25), 4)

        self.rect = self.image.get_rect(center=pos)

        # 植物血量
        self.max_hp = PLANT_MAX_HP
        self.hp = self.max_hp

        # 上次发射子弹的时间（毫秒）
        self.last_fire_time = 0

    def update(self, dt):
        """
        植物本身没有移动，只处理冷却时间等逻辑
        dt: 每帧经过的毫秒数（可用可不用，这里演示用）
        """
        pass  # 当前不需要做额外处理

    def can_fire(self, current_time):
        """
        判断现在是否可以发射子弹
        current_time: pygame.time.get_ticks() 获取的毫秒数
        """
        return current_time - self.last_fire_time >= PLANT_FIRE_INTERVAL

    def fire(self, bullet_group):
        """
        发射一颗子弹
        bullet_group: 子弹精灵组，用于统一管理
        """
        bullet = Bullet((self.rect.right, self.rect.centery))
        bullet_group.add(bullet)
        # 记录这次开火时间
        self.last_fire_time = pygame.time.get_ticks()

    def take_damage(self, amount):
        """
        植物被僵尸攻击时掉血
        """
        self.hp -= amount
        if self.hp <= 0:
            self.kill()  # 从精灵组中删除，等同于"死亡"

class Zombie(pygame.sprite.Sprite):
    """
    简单僵尸：
    - 从右往左缓慢移动
    - 与植物碰撞时会啃植物（简化为持续扣植物血）
    """

    def __init__(self, pos):
        """
        pos: 像素坐标 (x, y)，一般在屏幕右侧某行中心生成
        """
        super().__init__()
        # 创建带透明度的surface，确保正确渲染
        self.image = pygame.Surface((60, 80), pygame.SRCALPHA)
        self.image.fill(DARK_RED)
        # 绘制僵尸的简单外观
        pygame.draw.rect(self.image, BLACK, (15, 20, 30, 40), 2)
        # 画两个眼睛
        pygame.draw.circle(self.image, (255, 255, 255), (20, 30), 3)
        pygame.draw.circle(self.image, (255, 255, 255), (40, 30), 3)

        self.rect = self.image.get_rect(center=pos)
        self.max_hp = ZOMBIE_MAX_HP
        self.hp = self.max_hp
        self.speed = ZOMBIE_SPEED

        # 攻击相关（简单化：每帧只要碰上就扣一点血）
        self.attack_damage_per_second = 20   # 每秒对植物造成伤害
        self.attack_damage_per_frame = 0     # 根据 FPS 在外部计算或这里预设也行

    def update(self, dt):
        """
        僵尸每帧向左移动
        dt: 每帧毫秒，用于按时间缩放伤害（更合理）
        """
        # 水平向左移动
        self.rect.x -= self.speed

        # 记录本帧的伤害量（方便在主循环中对植物扣血）
        seconds = dt / 1000.0
        self.attack_damage_per_frame = self.attack_damage_per_second * seconds

        # 如果僵尸完全走出屏幕左侧，可以视为"突破防线"
        # 是否在主循环中检测并结束游戏由 main 控制

    def take_damage(self, amount):
        """
        僵尸被子弹命中时掉血
        """
        self.hp -= amount
        if self.hp <= 0:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    """
    子弹：
    - 从左往右直线飞行
    - 命中僵尸时造成伤害并销毁自己
    """

    def __init__(self, pos):
        """
        pos: 像素坐标 (x, y)，一般是植物的右侧中心
        """
        super().__init__()
        # 创建带透明度的surface，确保正确渲染
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        self.image.fill(YELLOW)
        # 画一个小圆点，更像子弹
        pygame.draw.circle(self.image, (255, 200, 0), (5, 5), 5)

        self.rect = self.image.get_rect(center=pos)
        self.speed = BULLET_SPEED
        self.damage = BULLET_DAMAGE

    def update(self, dt):
        """
        子弹每帧向右移动
        """
        self.rect.x += self.speed

        # 如果飞出屏幕右侧，自动销毁，避免占用内存
        if self.rect.left > SCREEN_WIDTH:
            self.kill()

