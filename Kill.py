#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @FileName  :Kill.py
# @Time      :2021/8/28 20:06
# @Author    :Amundsen Severus Rubeus Bjaaland


import os
try:
    with open("ProcessPid.txt", "r", encoding="UTF-8") as File:
        PIDs = File.read().rstrip("\n").split("\n")
    for PID in PIDs:
        print(os.popen('taskkill.exe /F /PID:' + str(PID)).read())
    os.remove("ProcessPid.txt")
except Exception:
    pass
finally:
    input()
