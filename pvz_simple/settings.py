# settings.py
"""
游戏全局设置：窗口大小、网格配置、速度参数、颜色等
"""

# 窗口相关
SCREEN_WIDTH = 900      # 窗口宽度
SCREEN_HEIGHT = 500     # 窗口高度
FPS = 60                # 帧率

# 网格相关（类似植物大战僵尸的草坪）
GRID_ROWS = 5           # 行数
GRID_COLS = 9           # 列数
CELL_SIZE = 80          # 每个格子的像素大小
GRID_OFFSET_X = 50      # 网格左边距
GRID_OFFSET_Y = 50      # 网格上边距

# 颜色定义（RGB）
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
GREEN = (50, 180, 75)
DARK_GREEN = (30, 120, 50)
RED = (200, 50, 50)
DARK_RED = (120, 20, 20)
BLUE = (50, 150, 255)
YELLOW = (255, 220, 0)

# 植物参数
PLANT_MAX_HP = 100           # 每棵植物血量
PLANT_FIRE_INTERVAL = 1000   # 开火间隔（毫秒），1000 = 1秒

# 僵尸参数
ZOMBIE_MAX_HP = 150          # 僵尸血量
ZOMBIE_SPEED = 0.5           # 僵尸水平移动速度（像素/帧）

# 子弹参数
BULLET_SPEED = 5             # 子弹水平速度（像素/帧）
BULLET_DAMAGE = 25           # 子弹伤害

# 僵尸生成（刷怪）参数
ZOMBIE_SPAWN_INTERVAL = 3000  # 生成间隔毫秒（3秒一个）

