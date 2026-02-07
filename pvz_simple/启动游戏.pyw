# -*- coding: utf-8 -*-
"""
植物大战僵尸简化版 - 启动程序
双击此文件即可启动游戏
"""

import sys
import os

# 切换到脚本所在目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 导入并运行主程序
try:
    from main import main
    main()
except Exception as e:
    import tkinter.messagebox as msgbox
    msgbox.showerror("启动错误", f"游戏启动失败：\n{str(e)}\n\n请确保已安装 pygame 库：\npip install pygame")
    sys.exit(1)

