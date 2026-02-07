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

def confirm_quit():
    """
    显示退出确认窗口
    返回 True 表示确认退出，False 表示取消
    """
    try:
        import tkinter.messagebox as msgbox
        result = msgbox.askyesno("退出游戏", "确定要退出游戏吗？")
        return result
    except:
        # 如果 tkinter 不可用，直接返回 True
        return True

def create_shovel_icon():
    """
    创建铲子图标
    返回一个 Surface 对象
    """
    icon_size = 50
    icon = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
    
    # 绘制铲子（简单的几何图形）
    # 铲子把手（比棕框稍淡的棕色）
    pygame.draw.rect(icon, (174, 104, 54), (20, 5, 8, 25))
    # 铲子头部（灰色金属）
    pygame.draw.ellipse(icon, (128, 128, 128), (10, 25, 30, 20))
    # 铲子边缘高光
    pygame.draw.ellipse(icon, (180, 180, 180), (12, 27, 26, 16), 2)
    
    return icon

def draw_health_bar(surface, entity):
    """
    在实体头顶绘制血量条
    entity: Plant 或 Zombie 对象
    """
    # 血量条参数
    bar_width = 50
    bar_height = 6
    # 根据实体类型设置不同的偏移量
    # 使用 type(entity).__name__ 来检查类型，避免循环导入
    if type(entity).__name__ == 'Plant':
        offset_y = -17.5  # 植物血条高度（原来的一半）
    else:
        offset_y = -17.5  # 僵尸血条高度（half）
    
    # 计算血量百分比
    hp_ratio = max(0, min(1, entity.hp / entity.max_hp))
    
    # 血量条位置（实体头顶）
    bar_x = entity.rect.centerx - bar_width // 2
    bar_y = entity.rect.top + offset_y
    
    # 绘制背景（灰色）
    bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
    pygame.draw.rect(surface, (100, 100, 100), bg_rect)
    
    # 绘制血量（根据血量百分比变色：绿色->黄色->红色）
    hp_width = int(bar_width * hp_ratio)
    if hp_ratio > 0.6:
        hp_color = (0, 255, 0)  # 绿色
    elif hp_ratio > 0.3:
        hp_color = (255, 255, 0)  # 黄色
    else:
        hp_color = (255, 0, 0)  # 红色
    
    if hp_width > 0:
        hp_rect = pygame.Rect(bar_x, bar_y, hp_width, bar_height)
        pygame.draw.rect(surface, hp_color, hp_rect)
    
    # 绘制边框
    pygame.draw.rect(surface, (0, 0, 0), bg_rect, 1)

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
    # 使用Windows中文字体，避免乱码
    try:
        font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 24)  # 微软雅黑
    except:
        try:
            font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 24)  # 黑体
        except:
            font = pygame.font.SysFont("simhei", 24)  # 备用方案
    
    # ========== 铲子功能相关变量 ==========
    shovel_icon = create_shovel_icon()
    shovel_rect = shovel_icon.get_rect()
    shovel_rect.topright = (SCREEN_WIDTH - 10, 10)  # 右上角位置
    shovel_selected = False  # 铲子是否被选中
    shovel_alpha = 255  # 铲子图标透明度（255 = 完全不透明）
    # 铲子下层棕色框（用于取消选中）- 固定在右上角，不随鼠标移动
    shovel_bg_rect = pygame.Rect(SCREEN_WIDTH - 60, 10, 50, 50)
    shovel_bg_color = (139, 69, 19)  # 棕色
    # 右上角固定位置的铲子图标（选中时显示半透明）
    fixed_shovel_rect = pygame.Rect(SCREEN_WIDTH - 60, 10, 50, 50)
    # =====================================
    
    # ========== 游戏控制相关变量 ==========
    game_paused = False  # 游戏是否暂停
    pause_button_rect = pygame.Rect(SCREEN_WIDTH - 180, SCREEN_HEIGHT - 50, 80, 40)  # 暂停按钮（右下角）
    quit_button_rect = pygame.Rect(SCREEN_WIDTH - 90, SCREEN_HEIGHT - 50, 80, 40)  # 退出按钮（右下角）
    # =====================================

    # 主循环
    running = True
    while running:
        # 计算 dt：本帧经过的毫秒数
        dt = clock.tick(FPS)

        # 1. 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # ========== 键盘快捷键处理 ==========
            if event.type == pygame.KEYDOWN:
                # 空格键暂停/继续游戏
                if event.key == pygame.K_SPACE:
                    if not game_over:
                        game_paused = not game_paused
                # Q键退出游戏（弹出确认窗口）
                elif event.key == pygame.K_q:
                    if confirm_quit():
                        running = False
            # =====================================

            # 鼠标点击处理
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 左键点击
                if not game_over:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # ========== 游戏控制按钮处理 ==========
                    # 检查是否点击了暂停按钮
                    if pause_button_rect.collidepoint(mouse_pos):
                        if not game_over:
                            game_paused = not game_paused
                    # 检查是否点击了退出按钮
                    elif quit_button_rect.collidepoint(mouse_pos):
                        if confirm_quit():
                            running = False
                    # =====================================
                    
                    # ========== 铲子功能处理 ==========
                    # 如果铲子已选中，优先检查是否点击了植物或棕色框
                    if shovel_selected:
                        # 检查是否点击了棕色框（取消选中）- 棕色框固定在右上角
                        if shovel_bg_rect.collidepoint(mouse_pos):
                            shovel_selected = False
                            shovel_alpha = 255
                        else:
                            # 检查点击位置是否有植物（扩大检测范围，确保能检测到）
                            clicked_plant = None
                            for plant in plants:
                                # 扩大检测范围：不仅检测rect中心，还检测整个rect区域
                                # 使用更大的碰撞检测区域，确保点击植物时能检测到
                                expanded_rect = plant.rect.inflate(10, 10)  # 扩大10像素
                                if expanded_rect.collidepoint(mouse_pos):
                                    clicked_plant = plant
                                    break
                            
                            if clicked_plant:
                                # 移除植物
                                clicked_plant.kill()
                                # 清理 plant_grid
                                for row in range(len(plant_grid)):
                                    for col in range(len(plant_grid[row])):
                                        if plant_grid[row][col] == clicked_plant:
                                            plant_grid[row][col] = None
                                # 取消铲子选中状态
                                shovel_selected = False
                                shovel_alpha = 255
                    # 如果铲子未选中，检查是否点击了铲子图标或种植植物
                    else:
                        # 检查是否点击了铲子图标（使用固定的右上角位置检测）
                        if fixed_shovel_rect.collidepoint(mouse_pos):
                            shovel_selected = True
                            shovel_alpha = 128  # 选中时降低透明度（半透明）
                        else:
                            # 正常种植植物
                            cell_indices = grid.get_cell_indices_from_pos(mouse_pos)
                            if cell_indices is not None:
                                row, col = cell_indices
                                # 如果当前格子没有植物，则种一棵
                                if plant_grid[row][col] is None:
                                    cell_center = grid.get_cell_center(row, col)
                                    new_plant = Plant(cell_center)
                                    plants.add(new_plant)
                                    plant_grid[row][col] = new_plant
                    # =====================================

        # 2. 游戏逻辑更新（若已游戏结束或暂停，则不再更新实体）
        if not game_over and not game_paused:
            current_time = pygame.time.get_ticks()

            # 2.1 生成僵尸（根据时间间隔）
            if current_time - last_zombie_spawn_time >= ZOMBIE_SPAWN_INTERVAL:
                last_zombie_spawn_time = current_time
                # 随机选择一行
                spawn_row = random.randint(0, GRID_ROWS - 1)
                # 僵尸从屏幕右侧外生成（稍微靠内一点，确保立即可见）
                spawn_x = SCREEN_WIDTH - 20
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
            # 使用自定义碰撞函数，确保碰撞检测准确
            collisions = pygame.sprite.groupcollide(
                bullets, zombies, True, False,  # True: 碰撞后删除子弹；False: 先不删僵尸
                pygame.sprite.collide_rect  # 使用矩形碰撞检测
            )
            for bullet, hit_zombies in collisions.items():
                for zombie in hit_zombies:
                    zombie.take_damage(bullet.damage)
                    # 碰撞时打印信息（调试用，可选）
                    # print(f"子弹命中僵尸！僵尸剩余血量: {zombie.hp}")

            # 2.5 僵尸与植物碰撞检测
            # ========== 僵尸移动和碰撞处理逻辑 ==========
            # 先重置所有僵尸的攻击状态
            for zombie in zombies:
                zombie.is_attacking = False
            
            # 然后检测碰撞并更新状态
            for zombie in zombies:
                # 如果僵尸到达屏幕左侧（突破防线），判定游戏结束
                if zombie.rect.left <= 0:
                    game_over = True
                    break

                # 僵尸与所有植物的碰撞检测
                for plant in plants:
                    if zombie.rect.colliderect(plant.rect):
                        # 标记僵尸正在攻击植物（这样僵尸会停止移动）
                        zombie.is_attacking = True
                        # 僵尸在这一帧对植物造成伤害
                        plant.take_damage(zombie.attack_damage_per_frame)
                        # 碰撞时打印信息（调试用，可选）
                        # print(f"僵尸攻击植物！植物剩余血量: {plant.hp}")
                        break  # 一个僵尸只攻击一个植物
            # ==========================================

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
        
        # 3.2.1 绘制所有实体的血量条
        for plant in plants:
            draw_health_bar(screen, plant)
        for zombie in zombies:
            draw_health_bar(screen, zombie)

        # 3.3 显示简单文字信息
        text_surface = font.render(
            "左键点击格子种植植物  |  僵尸到达左侧则游戏结束",
            True,
            BLACK,
        )
        screen.blit(text_surface, (50, 10))
        
        # 3.4 绘制铲子图标
        # ========== 铲子图标绘制 ==========
        # 棕色背景框始终固定在右上角（最底层）
        pygame.draw.rect(screen, shovel_bg_color, shovel_bg_rect)
        pygame.draw.rect(screen, BLACK, shovel_bg_rect, 2)  # 边框
        
        if shovel_selected:
            # 如果铲子被选中，跟随鼠标的铲子图标
            mouse_pos = pygame.mouse.get_pos()
            shovel_rect.center = mouse_pos
            # 绘制跟随鼠标的铲子图标（半透明）
            shovel_icon.set_alpha(shovel_alpha)
            screen.blit(shovel_icon, shovel_rect)
            
            # 右上角显示固定的半透明铲子图标
            fixed_shovel_icon = create_shovel_icon()
            fixed_shovel_icon.set_alpha(128)  # 半透明
            screen.blit(fixed_shovel_icon, fixed_shovel_rect)
        else:
            # 如果未选中，固定在右上角（完全不透明）
            shovel_rect.topright = (SCREEN_WIDTH - 10, 10)
            shovel_icon.set_alpha(255)
            screen.blit(shovel_icon, shovel_rect)
        # =====================================
        
        # 3.5 绘制游戏控制按钮
        # ========== 暂停和退出按钮绘制 ==========
        # 绘制暂停按钮
        pause_color = (100, 150, 200) if not game_paused else (200, 150, 100)
        pygame.draw.rect(screen, pause_color, pause_button_rect)
        pygame.draw.rect(screen, BLACK, pause_button_rect, 2)
        pause_text = font.render("暂停" if not game_paused else "继续", True, BLACK)
        pause_text_rect = pause_text.get_rect(center=pause_button_rect.center)
        screen.blit(pause_text, pause_text_rect)
        
        # 绘制退出按钮
        pygame.draw.rect(screen, (200, 100, 100), quit_button_rect)
        pygame.draw.rect(screen, BLACK, quit_button_rect, 2)
        quit_text = font.render("退出", True, BLACK)
        quit_text_rect = quit_text.get_rect(center=quit_button_rect.center)
        screen.blit(quit_text, quit_text_rect)
        # =====================================
        
        # 3.6 显示暂停提示
        if game_paused:
            pause_surface = font.render("游戏已暂停 - 按空格键继续", True, (255, 0, 0))
            pause_rect = pause_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            # 绘制半透明背景
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            screen.blit(pause_surface, pause_rect)

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

