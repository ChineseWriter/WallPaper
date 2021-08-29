#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :WallPaper.py
# @Time      :2021/8/29 12:40
# @Author    :Amundsen Severus Rubeus Bjaaland


# 导入必要库
import os
import ctypes
import random
import time
import threading
import copy
import json
import sys

from DealException import DisplayErrorMessage


# 全局变量
IMAGE_LIST = []  # 图像文件路径列表
LOCK = threading.Lock()  # 线程锁，防止图像文件列表被同时访问
WorkPath = os.getcwd().replace("\\", "/")  # 获取工作目录


# 检查工作目录下的Settings.json文件是否存在，若不存在则弹出警告消息并创建文件
if not os.path.exists("./Settings.json"):
    # 弹出警告消息
    DisplayErrorMessage(f"未找到文件'{WorkPath}/Settings.json'。")
    # 创建文件
    json.dump(
        {"FolderPath": "./", "Sleep": 5},
        open("./Settings.json", "w", encoding="UTF-8")
    )

# 加载Settings.json文件中的配置
Settings = json.load(open("./Settings.json", "r", encoding="UTF-8"))
try:
    # 获取文件目录设置
    PATH = Settings["FolderPath"]
    # 获取切换时长设置
    SLEEP = Settings["Sleep"]
except KeyError:
    # 若无此设置，则弹出错误警告并重新创建文件
    DisplayErrorMessage(f"文件'{WorkPath}/Settings.json'已损坏。")
    json.dump(
        {"FolderPath": "./", "Sleep": 5},
        open("./Settings.json", "w", encoding="UTF-8")
    )
else:
    if not os.path.exists(PATH):
        DisplayErrorMessage(f"配置的路径{PATH}不存在。")
        sys.exit()

# 从指定路径加载文件列表
for root, dirs, files in os.walk(PATH, topdown=False):
    # 获取所有文件
    for name in files:
        # 判断文件后缀名，为.jpg则添加至图像文件路径列表
        if os.path.splitext(name)[1] == ".jpg":
            # 天健至图像文件路径列表
            IMAGE_LIST.append(os.path.join(root, name).replace("\\", "/"))

# 记录该进程的PID，以便可以从外部终止该进程
with open("ProcessPid.txt", "a+", encoding="UTF-8") as File:
    File.write(str(os.getpid()))
    File.write("\n")


def GetTimeInfo(Path):
    LOCK.acquire()
    try:
        TimeInfo = os.stat(Path).st_mtime
    except Exception:
        LOCK.release()
        return None
    else:
        LOCK.release()
        return TimeInfo


def ProbeSetting():
    global PATH
    global SLEEP
    LastModificationTime = GetTimeInfo("./Settings.json")
    if LastModificationTime is None:
        ErrorPath = os.path.join(WorkPath, "./Settings.json").replace('\\', '/')
        DisplayErrorMessage(f"获取文件{ErrorPath}信息失败。")
        return None
    while True:
        ThisTime = GetTimeInfo("./Settings.json")
        if ThisTime is not None:
            if ThisTime != LastModificationTime:
                Settings = json.load(open("./Settings.json", "r", encoding="UTF-8"))
                LOCK.acquire()
                try:
                    # 获取文件目录设置
                    PATH = Settings["FolderPath"]
                    # 获取切换时长设置
                    SLEEP = Settings["Sleep"]
                except KeyError:
                    # 若无此设置，则弹出错误警告并重新创建文件
                    DisplayErrorMessage(f"文件'{WorkPath}/Settings.json'已损坏。")
                    json.dump(
                        {"FolderPath": "./", "Sleep": 5},
                        open("./Settings.json", "w", encoding="UTF-8")
                    )
                else:
                    if not os.path.exists(PATH):
                        DisplayErrorMessage(f"配置的路径{PATH}不存在。")
                    print("Update settings.")
                finally:
                    LOCK.release()
                LastModificationTime = copy.deepcopy(ThisTime)
        else:
            print("!!!!!!!!!!!")
        time.sleep(SLEEP / 2)


def ProbeDir():
    global PATH
    global SLEEP
    global IMAGE_LIST
    LastModificationTime = GetTimeInfo(PATH)
    if LastModificationTime is None:
        DisplayErrorMessage(f"获取文件夹{PATH}信息失败。")
        return None
    while True:
        ThisTime = GetTimeInfo(PATH)
        if ThisTime is not None:
            if ThisTime != LastModificationTime:
                print("Folder changes detected.")
                LOCK.acquire()
                try:
                    IMAGE_LIST.clear()
                    for Root, Dirs, Files in os.walk(PATH, topdown=False):
                        for FileName in Files:
                            if os.path.splitext(FileName)[1] == ".jpg":
                                IMAGE_LIST.append(os.path.join(Root, FileName).replace("\\", "/"))
                except Exception:
                    print("Failed to update wallpaper list.")
                else:
                    print(f"Update wallpaper list. {len(IMAGE_LIST)} items.")
                finally:
                    LOCK.release()
                LastModificationTime = copy.deepcopy(ThisTime)
        else:
            print(f"获取文件夹{PATH}信息失败。")
        time.sleep(SLEEP / 2)


def Main():
    global IMAGE_LIST
    global SLEEP
    while True:
        LOCK.acquire()
        try:
            FilePath = random.choice(IMAGE_LIST)
        except Exception:
            print("Failed to update wallpaper.")
        else:
            ctypes.windll.user32.SystemParametersInfoW(20, 0, FilePath, 0)
            print(f"Update wallpaper. located in {FilePath}.")
        finally:
            LOCK.release()
        time.sleep(SLEEP)


if __name__ == "__main__":
    MainThread = threading.Thread(target=Main)
    DirProbeThread = threading.Thread(target=ProbeDir)
    SettingProbeThread = threading.Thread(target=ProbeSetting)
    DirProbeThread.start()
    SettingProbeThread.start()
    time.sleep(1)
    MainThread.start()
    MainThread.join()
