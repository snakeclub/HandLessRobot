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
# from HandLessRobot.lib.controls.appium.adb import AppDevice, AppElement
from HandLessRobot.lib.controls.appium_control import EnumAndroidKeycode


#############################
# 搜索页面：mFocusedApp=AppWindowToken{3dec63 token=Token{a6fca92 ActivityRecord{908981d u0 com.ss.android.ugc.aweme/.search.activity.SearchResultActivity t119}}}
# 搜索框id：com.ss.android.ugc.aweme:id/aia
# 搜索按钮：com.ss.android.ugc.aweme:id/j0o
# id: com.ss.android.ugc.aweme:id/e4a
# text:	臻纯翠正在直播
# class: android.widget.TextView
# 直播id： com.ss.android.ugc.aweme:id/cwe / com.ss.android.ugc.aweme:id/dru
# //android.widget.FrameLayout/
# //android.widget.ImageView[@content-desc="视频封面"]
# //android.widget.TextView[@text='说点什么...']
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

# 连接服务的参数 - 模拟器
DESIRED_CAPS_SIMULATOR = {
    'platformName': 'Android',  # 被测手机是安卓
    'platformVersion': '7.1',  # 模拟器安卓版本
    'deviceName': '127.0.0.1:21513',  # 设备名，安卓手机可以随意填写
    "appPackage": "com.ss.android.ugc.aweme",
    "appActivity": ".search.activity.SearchResultActivity",
    'unicodeKeyboard': True,  # 使用自带输入法，输入中文时填True
    'resetKeyboard': True,  # 执行完程序恢复原来输入法
    'noReset': True,       # 不要重置App，防止登录信息丢失
    # 'newCommandTimeout': 6000,
    # 'automationName': 'UiAutomator2'
}

# 连接服务的参数 - 真机
DESIRED_CAPS_REAL = {
    'platformName': 'Android',  # 被测手机是安卓
    'platformVersion': '9',  # 安卓版本
    'deviceName': 'WGY0217527000271',  # 设备名，安卓手机可以随意填写
    "appPackage": "com.ss.android.ugc.aweme",
    "appActivity": ".search.activity.SearchResultActivity",
    'unicodeKeyboard': True,  # 使用自带输入法，输入中文时填True
    'resetKeyboard': True,  # 执行完程序恢复原来输入法
    'noReset': True,       # 不要重置App，防止登录信息丢失
    # 'newCommandTimeout': 6000,
    # 'automationName': 'UiAutomator2'
}


DESIRED_CAPS = DESIRED_CAPS_SIMULATOR  # 用于切换模拟器的参数

TEMP_PATH = 'd:/douyin/temp/'


def get_user_name():
    # 连接首页
    _desired_caps = {
        'platformName': 'Android',  # 被测手机是安卓
        'platformVersion': '7.1',  # 模拟器安卓版本
        'deviceName': '127.0.0.1:21503',  # 设备名，安卓手机可以随意填写
        "appPackage": "com.ss.android.ugc.aweme",
        "appActivity": ".splash.SplashActivity",  # 首页
        'unicodeKeyboard': False,  # 使用自带输入法，输入中文时填True
        'resetKeyboard': False,  # 执行完程序恢复原来输入法
        'noReset': True,       # 不要重置App，防止登录信息丢失
    }

    _desired_caps1 = {
        'platformName': 'Android',  # 被测手机是安卓
        'platformVersion': '9',  # 模拟器安卓版本
        'deviceName': 'WGY0217527000271',  # 设备名，安卓手机可以随意填写
        "appPackage": "com.ss.android.ugc.aweme",
        "appActivity": ".splash.SplashActivity",  # 首页
        'unicodeKeyboard': False,  # 使用自带输入法，输入中文时填True
        'resetKeyboard': False,  # 执行完程序恢复原来输入法
        'noReset': True,       # 不要重置App，防止登录信息丢失
    }

    _app = AppDevice(
        appium_server=APPIUM_SERVER, desired_caps=_desired_caps1
    )

    _app.wait_activity('.splash.SplashActivity', 10.0, 0.2)

    # 获取页面并截图 //android.widget.TextView[@text='我']
    # _els = _app.find_elements(by=MobileBy.ID, value='com.ss.android.ugc.aweme:id/hsg')
    # # _els[4].screenshot(
    # #     filename=os.path.join(TEMP_PATH, 'hsg.png')
    # # )

    # _els[4].click()
    _el = _app.find_element(by=MobileBy.XPATH, value="//android.widget.TextView[@text='我']")
    _rect = _el.rect
    _app.tap_adb(
        x=_rect[0] + math.ceil(_rect[2] / 3.0),
        y=_rect[1] + math.ceil(_rect[2] / 2.0)
    )

    time.sleep(1)

    _els = _app.find_elements(by=MobileBy.ID, value='com.ss.android.ugc.aweme:id/fb3')
    if len(_els) == 0:
        print('no login')

    # for index in range(len(_els)):
    #     _els[index].screenshot(
    #         filename=os.path.join(TEMP_PATH, 'fb3%d.png' % index)
    #     )
    #     print(_els[index].text)

    time.sleep(20)


def into_line():
    # 直播间名
    _line_name = '丑小鸭'

    # 进入搜索页面
    _desired_caps = {
        'platformName': 'Android',  # 被测手机是安卓
        'platformVersion': '7.1',  # 模拟器安卓版本
        'deviceName': '127.0.0.1:21503',  # 设备名，安卓手机可以随意填写
        "appPackage": "com.ss.android.ugc.aweme",
        "appActivity": ".splash.SplashActivity",  # 首页
        'unicodeKeyboard': False,  # 使用自带输入法，输入中文时填True
        'resetKeyboard': False,  # 执行完程序恢复原来输入法
        'noReset': True,       # 不要重置App，防止登录信息丢失
        'automationName': 'UiAutomator2'
    }

    _desired_caps1 = {
        # "automationName": "UiAutomator1",
        'platformName': 'Android',
        'platformVersion': '9',
        'deviceName': 'WGY0217527000271',
        "appPackage": "com.ss.android.ugc.aweme",
        "appActivity": ".splash.SplashActivity",
        'unicodeKeyboard': False,
        'resetKeyboard': False,
        'noReset': True
    }

    _app = AppDevice(
        appium_server=APPIUM_SERVER, desired_caps=_desired_caps
    )

    _app.implicitly_wait(20)

    # time.sleep(10)

    # 找到首页搜索按钮
    # _els = _app.find_elements(by=MobileBy.ID, value='c8u')
    # _el: AppElement = _els[0]
    # _el.screenshot(
    #     filename=os.path.join(TEMP_PATH, 'c8u.png')
    # )
    # //android.widget.Button[@content-desc='搜索']
    # _el = _app.find_element(by=MobileBy.ID, value='c8u')
    # _el.click()
    _el = _app.find_element(by=MobileBy.XPATH, value="//android.widget.Button[@content-desc='搜索']")
    _el.click()
    # _rect = _el.rect
    # _app.tap_adb(
    #     x=_rect[0] + math.ceil(_rect[2] / 3.0),
    #     y=_rect[1] + math.ceil(_rect[2] / 2.0)
    # )

    print('end click1')

    # 找到搜索框并点击
    # _els = _app.find_elements(by=MobileBy.ID, value='aia')
    # _el: AppElement = _els[0]
    # _el.screenshot(
    #     filename=os.path.join(TEMP_PATH, 'aia.png')
    # )
    _app.wait_activity_adb('.search.activity.SearchResultActivity', 10, 0.1)

    _el = _app.find_element(by=MobileBy.ID, value='aia')
    # _el.click()
    # _rect = _el.rect
    # _app.tap_adb(
    #     x=_rect[0] + math.ceil(_rect[2] / 3.0),
    #     y=_rect[1] + math.ceil(_rect[2] / 2.0)
    # )
    print('end click2')

    # 发送文字
    _app.adb_keyboard_text(_line_name)
    # _el.send_keys(_line_name)
    print('end send key')

    # 找到搜索按钮并点击
    # _els = _app.find_elements(by=MobileBy.ID, value='j0o')
    # _el: AppElement = _els[0]
    # _el = _app.find_element(by=MobileBy.ID, value='j0o')
    # _el.click()
    _el = _app.find_element(by=MobileBy.XPATH, value='//android.widget.TextView[@text="搜索"]')
    _el.click()
    # _rect = _el.rect
    # _app.tap_adb(
    #     x=_rect[0] + math.ceil(_rect[2] / 3.0),
    #     y=_rect[1] + math.ceil(_rect[2] / 2.0)
    # )
    print('end click3')

    # 找到直播按钮
    # com.ss.android.ugc.aweme:id/hs_
    # /hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout[2]/android.view.ViewGroup/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.HorizontalScrollView
    # /hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout[2]/android.view.ViewGroup/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.HorizontalScrollView/android.widget.LinearLayout
    # /hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout[2]/android.view.ViewGroup/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.HorizontalScrollView/android.widget.LinearLayout/androidx.appcompat.app.ActionBar.Tab[6]
    # /hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout[2]/android.view.ViewGroup/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.HorizontalScrollView/android.widget.LinearLayout/androidx.appcompat.app.ActionBar.Tab[6]/android.widget.TextView
    _el = _app.find_element(
        by=MobileBy.XPATH, value='//android.widget.TextView[@text="直播"]'
    )
    _el.click()
    # _rect = _el.rect
    # _app.tap_adb(
    #     x=_rect[0] + math.ceil(_rect[2] / 3.0),
    #     y=_rect[1] + math.ceil(_rect[2] / 2.0)
    # )

    print('end click4')

    # 判断是否有直播
    # //android.widget.TextView[@text="丑小鸭"]/preceding-sibling::android.widget.FrameLayout
    _el = _app.find_element(
        by=MobileBy.XPATH,
        value='//android.widget.TextView[@text="%s"]/preceding-sibling::android.widget.FrameLayout' % _line_name
    )
    _el.click()
    # rect = _el.rect
    # _app.tap_adb(
    #     x=_rect[0] + math.ceil(_rect[2] / 3.0),
    #     y=_rect[1] + math.ceil(_rect[2] / 2.0)
    # )
    print('end click5')

    # //android.widget.Button[@content-desc="小心心"]
    # 	com.ss.android.ugc.aweme:id/bqp
    # /hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.EditText
    # //android.widget.Button[@content-desc="发送"]
    time.sleep(100)


def send_chat():
    _desired_caps1 = {
        # "automationName": "UiAutomator1",
        'platformName': 'Android',
        'platformVersion': '9',
        'deviceName': 'WGY0217527000271',
        "appPackage": "com.ss.android.ugc.aweme",
        "appActivity": ".splash.SplashActivity",
        'unicodeKeyboard': True,
        'resetKeyboard': True,
        'noReset': True
    }

    _app = AppDevice(
        appium_server=APPIUM_SERVER, desired_caps=_desired_caps1
    )

    _app.implicitly_wait(10)

    _el = _app.find_element(by=MobileBy.ID, value='bqp')
    _el.click()

    _rect = _el.rect
    print(_rect)
    x, y = _app.center(_el.rect)
    _app.tap(
        x=x, y=y
    )

    print('end click1')

    _el = _app.find_element(
        by=MobileBy.XPATH,
        value='//android.widget.EditText'
    )

    # 发送文字
    _el.send_keys('666')
    print('end send key')

    _el = _app.find_element(
        by=MobileBy.XPATH,
        value='//android.widget.Button[@content-desc="发送"]'
    )

    _el.click()

    time.sleep(100)


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    FileTool.create_dir(TEMP_PATH, exist_ok=True)
    # get_user_name()
    into_line()
    # send_chat()
