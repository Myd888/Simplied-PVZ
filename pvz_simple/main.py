# main.py
"""
简化版植物大战僵尸
功能：
1. 创建游戏窗口并绘制网格
2. 鼠标点击网格种植植物（不考虑阳光消耗）
3. 定时生成僵尸，从右往左移动
4. 植物自动向右发射子弹
5. 子弹与僵尸碰撞、僵尸与植物碰撞的处理
6. 血量系统 + 简单的"突破防线则游戏结束"
"""

import sys
import random
import pygame

from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    GRID_ROWS,
    GRID_COLS,
    ZOMBIE_SPAWN_INTERVAL,
    WHITE,
    BLACK,
)
from grid import Grid
from entities import Plant, Zombie

def main():
    pygame.init()
    pygame.display.set_caption("简化版 植物大战僵尸 - Pygame Demo")

    # 创建窗口
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # 创建网格对象
    grid = Grid()

    # 精灵组：
    plants = pygame.sprite.Group()   # 所有植物
    zombies = pygame.sprite.Group()  # 所有僵尸
    bullets = pygame.sprite.Group()  # 所有子弹

    # 用一个二维数组记录每个格子是否已经有植物（防止重复种植）
    # None 表示该格子为空；否则存储 Plant 对象
    plant_grid = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

    # 僵尸生成计时器
    last_zombie_spawn_time = pygame.time.get_ticks()

    # 游戏结束标志
    game_over = False
    font = pygame.font.SysFont(None, 32)

    # 主循环
    running = True
    while running:
        # 计算 dt：本帧经过的毫秒数
        dt = clock.tick(FPS)

        # 1. 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # 鼠标点击种植植物
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 左键点击
                if not game_over:
                    mouse_pos = pygame.mouse.get_pos()
                    cell_indices = grid.get_cell_indices_from_pos(mouse_pos)
                    if cell_indices is not None:
                        row, col = cell_indices
                        # 如果当前格子没有植物，则种一棵
                        if plant_grid[row][col] is None:
                            cell_center = grid.get_cell_center(row, col)
                            new_plant = Plant(cell_center)
                            plants.add(new_plant)
                            plant_grid[row][col] = new_plant

        # 2. 游戏逻辑更新（若已游戏结束，则不再更新实体，只显示结束文字）
        if not game_over:
            current_time = pygame.time.get_ticks()

            # 2.1 生成僵尸（根据时间间隔）
            if current_time - last_zombie_spawn_time >= ZOMBIE_SPAWN_INTERVAL:
                last_zombie_spawn_time = current_time
                # 随机选择一行
                spawn_row = random.randint(0, GRID_ROWS - 1)
                # 僵尸从屏幕右侧外一点点生成
                spawn_x = SCREEN_WIDTH + 30
                # 找到这行中任意一个格子，取其 y 中心即可
                spawn_y = grid.cells[spawn_row][0].centery
                new_zombie = Zombie((spawn_x, spawn_y))
                zombies.add(new_zombie)

            # 2.2 更新植物、僵尸、子弹
            plants.update(dt)
            zombies.update(dt)
            bullets.update(dt)

            # 2.3 植物自动开火（当前行有僵尸则开火）
            for plant in plants:
                # 判断该植物所在行是否有僵尸（简单通过 y 坐标近似比较）
                row_has_zombie = any(
                    abs(zombie.rect.centery - plant.rect.centery) < 10
                    for zombie in zombies
                )
                if row_has_zombie and plant.can_fire(current_time):
                    plant.fire(bullets)

            # 2.4 子弹与僵尸碰撞检测
            # groupcollide 返回一个字典：{bullet: [zombies...]}
            collisions = pygame.sprite.groupcollide(
                bullets, zombies, True, False  # True: 碰撞后删除子弹；False: 先不删僵尸
            )
            for bullet, hit_zombies in collisions.items():
                for zombie in hit_zombies:
                    zombie.take_damage(bullet.damage)

            # 2.5 僵尸与植物碰撞检测
            # 这里不使用 groupcollide，直接遍历简单处理
            for zombie in zombies:
                # 如果僵尸到达屏幕左侧（突破防线），判定游戏结束
                if zombie.rect.left <= 0:
                    game_over = True
                    break

                # 僵尸与所有植物的碰撞检测
                for plant in plants:
                    if zombie.rect.colliderect(plant.rect):
                        # 僵尸在这一帧对植物造成伤害
                        plant.take_damage(zombie.attack_damage_per_frame)

            # 2.6 维护 plant_grid：如果植物死亡，则清理对应格子
            for row in range(len(plant_grid)):
                for col in range(len(plant_grid[row])):
                    p = plant_grid[row][col]
                    if p is not None and not p.alive():
                        plant_grid[row][col] = None

        # 3. 绘制
        screen.fill(WHITE)

        # 3.1 画网格
        grid.draw(screen)

        # 3.2 画植物、僵尸、子弹
        plants.draw(screen)
        zombies.draw(screen)
        bullets.draw(screen)

        # 3.3 显示简单文字信息
        text_surface = font.render(
            "左键点击格子种植植物  |  僵尸到达左侧则游戏结束",
            True,
            BLACK,
        )
        screen.blit(text_surface, (50, 10))

        if game_over:
            over_surface = font.render(
                "游戏结束！关掉窗口退出。", True, (255, 0, 0)
            )
            screen.blit(over_surface, (SCREEN_WIDTH // 2 - 100, 10))

        # 4. 刷新屏幕
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

