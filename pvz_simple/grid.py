# grid.py
"""
处理草坪网格的绘制和坐标转换
"""

import pygame
from settings import (
    GRID_ROWS,
    GRID_COLS,
    CELL_SIZE,
    GRID_OFFSET_X,
    GRID_OFFSET_Y,
    GREEN,
    DARK_GREEN,
    BLACK,
)

class Grid:
    def __init__(self):
        # 预先计算出每个格子的 rect，用于绘制和点击检测
        self.cells = []
        for row in range(GRID_ROWS):
            row_cells = []
            for col in range(GRID_COLS):
                x = GRID_OFFSET_X + col * CELL_SIZE
                y = GRID_OFFSET_Y + row * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                row_cells.append(rect)
            self.cells.append(row_cells)

    def draw(self, surface):
        """
        在给定的 surface（一般是屏幕）上绘制网格
        """
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                rect = self.cells[row][col]
                # 使用两种绿色，形成棋盘格效果
                color = GREEN if (row + col) % 2 == 0 else DARK_GREEN
                pygame.draw.rect(surface, color, rect)
                # 画格子边框
                pygame.draw.rect(surface, BLACK, rect, 1)

    def get_cell_indices_from_pos(self, pos):
        """
        根据鼠标点击的像素坐标，返回所在的格子索引 (row, col)
        如果不在网格范围内，返回 None
        """
        x, y = pos
        # 判断是否在整个网格的框中
        grid_rect = pygame.Rect(
            GRID_OFFSET_X,
            GRID_OFFSET_Y,
            GRID_COLS * CELL_SIZE,
            GRID_ROWS * CELL_SIZE,
        )
        if not grid_rect.collidepoint(x, y):
            return None

        col = (x - GRID_OFFSET_X) // CELL_SIZE
        row = (y - GRID_OFFSET_Y) // CELL_SIZE
        return int(row), int(col)

    def get_cell_center(self, row, col):
        """
        根据格子索引 (row, col)，返回该格子中心点像素坐标
        用于放置植物、子弹生成位置等
        """
        rect = self.cells[row][col]
        return rect.center

