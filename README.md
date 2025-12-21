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

马里奥的任务形态，大小，buff等数据若直接加在代码里显得冗余且难以维护，但用数据库又有种“大炮打蚊子”的感觉
视频教程里提到用json格式的文件来解决这个问题