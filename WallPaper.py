# coding = UTF-8


import os
import ctypes
import random
import time
import threading
import copy
import json

Settings = json.load(open("./Settings.json", "r", encoding="UTF-8"))
PATH = Settings["FolderPath"]
SLEEP = Settings["Sleep"]
assert os.path.exists(PATH)

IMAGE_LIST = []
LOCK = threading.Lock()

for root, dirs, files in os.walk(PATH, topdown=False):
    for name in files:
        IMAGE_LIST.append(os.path.join(root, name).replace("\\", "/"))

with open("ProcessPid.txt", "a+", encoding="UTF-8") as File:
    File.write(str(os.getpid()))
    File.write("\n")


def ProbeFile():
    LastModificationTime = os.stat(PATH).st_mtime
    while True:
        ThisTime = os.stat(PATH).st_mtime
        if ThisTime != LastModificationTime:
            print("Folder changes detected.")
            LOCK.acquire()
            try:
                IMAGE_LIST.clear()
                for Root, Dirs, Files in os.walk(PATH, topdown=False):
                    for FileName in Files:
                        IMAGE_LIST.append(os.path.join(Root, FileName).replace("\\", "/"))
            except Exception:
                print("Failed to update wallpaper list.")
            else:
                print(f"Update wallpaper list. {len(IMAGE_LIST)} items.")
            finally:
                LOCK.release()
            LastModificationTime = copy.deepcopy(ThisTime)
        try:
            time.sleep(SLEEP / 2)
        except KeyboardInterrupt:
            break


def Main():
    while True:
        LOCK.acquire()
        try:
            FilePath = random.choice(IMAGE_LIST)
        except Exception:
            print("Failed to update wallpaper.")
        else:
            print(f"Update wallpaper. located in {FilePath}.")
            ctypes.windll.user32.SystemParametersInfoW(20, 0, FilePath, 0)
        finally:
            LOCK.release()
        try:
            time.sleep(SLEEP)
        except KeyboardInterrupt:
            break


MainThread = threading.Thread(target=Main)
ProbeThread = threading.Thread(target=ProbeFile)
ProbeThread.start()
time.sleep(1)
MainThread.start()
MainThread.join()
ProbeThread.join()
