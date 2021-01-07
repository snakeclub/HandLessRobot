#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import sys
import os
import time
import math
from appium.webdriver.common.mobileby import MobileBy
from HiveNetLib.base_tools.file_tool import FileTool
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from HandLessRobot.lib.controls.appium.android import AppDevice, AppElement
from HandLessRobot.lib.controls.appium_control import EnumAndroidKeycode


#############################
# 搜索页面：mFocusedApp=AppWindowToken{3dec63 token=Token{a6fca92 ActivityRecord{908981d u0 com.ss.android.ugc.aweme/.search.activity.SearchResultActivity t119}}}
# 搜索框id：com.ss.android.ugc.aweme:id/aia
# 搜索按钮：com.ss.android.ugc.aweme:id/j0o
# id: com.ss.android.ugc.aweme:id/e4a
# text:	正在直播
# class: android.widget.TextView
# 直播id： com.ss.android.ugc.aweme:id/cwe / com.ss.android.ugc.aweme:id/dru
# //android.widget.FrameLayout/
# //android.widget.ImageView[@content-desc="视频封面"]
#
# driver.setSetting(Setting.WAIT_FOR_IDLE_TIMEOUT, 100)

# [40,502][184,714]
# adb shell input tap 110 600
# adb shell input tap 400 400 && adb shell input tap 400 400 && adb shell input tap 400 400 && adb shell input tap 400 400
# [328,290][472,502]

# adb shell uiautomator dump /data/local/tmp/uidump.xml
# adb pull /data/local/tmp/uidump.xml d:/temp/
#############################


#############################
# 配置参数
#############################
APPIUM_SERVER = 'http://localhost:4723/wd/hub'  # Appium服务连接串

TEMP_PATH = 'd:/douyin/temp/'


def test():
    # 连接首页
    _desired_caps = {
        'platformName': 'Android',  # 被测手机是安卓
        # 'platformVersion': '9',  # 模拟器安卓版本
        # 'deviceName': 'WGY0217527000271',  # 设备名，安卓手机可以随意填写
        'platformVersion': '6.0',  # 模拟器安卓版本
        'deviceName': 'C6Y9KJYPSSTC7L8L',  # 设备名，安卓手机可以随意填写
        "appPackage": "com.ss.android.ugc.aweme",
        "appActivity": ".splash.SplashActivity",  # 首页
        'unicodeKeyboard': True,  # 使用自带输入法，输入中文时填True
        'resetKeyboard': True,  # 执行完程序恢复原来输入法
        'noReset': True,       # 不要重置App，防止登录信息丢失
        "dontStopOnReset": True,
        "fullReset": False,
        "automationName": "UiAutomator2",
        "newCommandTimeout": 20000,
        "noSign": True
    }

    _app = AppDevice(
        appium_server=APPIUM_SERVER, desired_caps=_desired_caps
    )

    _app.wait_activity('.splash.SplashActivity', 10.0, 0.1)

    print('appium.size: ', _app.size)
    print('adb.size: ', _app.size_adb)

    print('appium.current_activity: ', _app.current_activity)   #
    print('adb.current_activity: ', _app.current_activity_adb)  # .live.LivePlayActivity

    _page_source = _app.page_source
    with open(os.path.join(TEMP_PATH, 'appium.xml'), 'w', encoding='utf-8') as _f:
        _f.write(_page_source)
        _f.flush()

    # _app.tap_adb_continuity(
    #     [(math.ceil(1440 / 2.0), math.ceil(2560 / 2.0)), ], 10, thread_count=5
    # )

    # 直播页面  .live.LivePlayActivity


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    FileTool.create_dir(TEMP_PATH, exist_ok=True)
    test()
