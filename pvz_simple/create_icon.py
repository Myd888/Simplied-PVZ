# -*- coding: utf-8 -*-
"""
创建游戏图标
使用 PIL/Pillow 创建一个精美的游戏图标
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    # 创建 256x256 的图标
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制背景（绿色草地）
    draw.ellipse([20, 20, size-20, size-20], fill=(50, 180, 75))
    draw.ellipse([30, 30, size-30, size-30], fill=(30, 120, 50))
    
    # 绘制植物（蓝色方块代表向日葵）
    plant_size = 80
    plant_x = size // 2 - plant_size // 2
    plant_y = size // 2 - plant_size // 2 + 20
    draw.rectangle([plant_x, plant_y, plant_x + plant_size, plant_y + plant_size], 
                   fill=(50, 150, 255), outline=(0, 0, 0), width=3)
    
    # 绘制眼睛
    eye_size = 12
    draw.ellipse([plant_x + 20, plant_y + 25, plant_x + 20 + eye_size, plant_y + 25 + eye_size], 
                 fill=(255, 255, 0))
    draw.ellipse([plant_x + 50, plant_y + 25, plant_x + 50 + eye_size, plant_y + 25 + eye_size], 
                 fill=(255, 255, 0))
    
    # 绘制僵尸（红色方块）
    zombie_size = 60
    zombie_x = size - 100
    zombie_y = size - 100
    draw.rectangle([zombie_x, zombie_y, zombie_x + zombie_size, zombie_y + zombie_size], 
                   fill=(120, 20, 20), outline=(0, 0, 0), width=3)
    
    # 保存为 ICO 格式
    img.save('game_icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    print("图标已创建：game_icon.ico")
    
except ImportError:
    print("需要安装 Pillow 库：pip install Pillow")
except Exception as e:
    print(f"创建图标失败：{e}")

