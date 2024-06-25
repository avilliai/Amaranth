# -*- mode: python -*-
#这个是打包脚本，运行即可
from PyInstaller.__main__ import run
import os

# 主程序文件
main_script = 'main.py'

# 直接指定需要包含的文件和文件夹路径
files_and_folders = [
    'main.py',  # 主程序文件
    'widgets/',
    'themes/',  # tools文件夹
    'modules/',  # QSS文件夹
    'images/'
]
# 转换为PyInstaller需要的格式
datas = []
for item in files_and_folders:
    if os.path.isdir(item):
        # 对于文件夹，添加整个文件夹
        datas.append((item + os.sep, item))
    else:
        # 对于文件，只添加文件本身
        datas.append((item, '.'))

# 构建PyInstaller命令
pyinstaller_command = [
    main_script,  # 主程序
    '--onefile',  # onefile模式
    '--windowed',  # 防止弹出命令行窗口
    '--icon=Launcher.ico',  # 使用app.ico作为软件图标
    '--name=Launcher',  # 设置打包后的文件名为app
    '--clean',  # 清理打包前的缓存和临时文件
    '--runtime-tmpdir=Temp',  # 设置运行时的临时目录为项目目录下的Temp文件夹
]
# 添加数据文件
for data in datas:
    pyinstaller_command.extend(['--add-data', f'{data[0]};{data[1]}'])

# 执行PyInstaller命令
run(pyinstaller_command)
