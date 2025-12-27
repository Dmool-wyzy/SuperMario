Super Mario Bros Level 1
![screenshot](https://raw.github.com/justinmeister/Mario-Level-1/master/screenshot.png)
=============
依赖：
Python
Pygame

使用Anaconda配置环境：\
`conda create -n game_env python=3.7`

激活环境：\
`conda activate game_env`

按照Pygame库：\
`pip install pygame`
如果网络有问题，使用清华源：\
`pip install pygame -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple`

运行：
`python mario_level_1.py`

1. 马里奥的任务形态，大小，buff等数据若直接加在代码里显得冗余且难以维护，但用数据库又有种“大炮打蚊子”的感觉
视频教程里提到用json格式的文件来解决这个问题
2. 新建save_menu和save_manager文件绘制存档选择菜单及管理存档操作
3. 测试发现↑↓键无法切换存档，原因是在 SaveMenu.update() 里有
    ```
    if keys[pg.K_UP]:
    self.selected_slot -= 1
    ```
   但update()每一帧都会执行，所以↑只要按住一瞬间，slot就会狂跳，马上被逻辑抵消，导致看上去没反应。采用和主菜单一样的解决方法，用事件式的输入系统，即KEYDOWN
    而不是状态式的get_pressed。
4. 存档逻辑实现后发现，在游玩一个存档时，死一次之后按下esc无法正常关闭游戏，而是卡在第二条命的开始界面循环，推测是读档逻辑有误
    原游戏中死一次之后只会重新设置生命数和分数，