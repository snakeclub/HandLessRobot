#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
测试安卓处理功能
@module test_android
@file test_android.py
"""

import sys
import os
import time
from appium.webdriver.common.mobileby import MobileBy
from HiveNetLib.base_tools.file_tool import FileTool
from HiveNetLib.base_tools.string_tool import StringTool
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from HandLessRobot.lib.controls.appium_sub.android import AppDevice, AppElement


def print_element(element: AppElement, level: int, max_level: int = 5):
    print(
        '%s%d [%s] %s' % (
            StringTool.fill_fix_string('', level * 2, ' '), level,
            element.id,
            element.get_attribute('class')
        )
    )
    if level < max_level:
        _elements = element.find_elements(by=MobileBy.XPATH, value='child::*')
        for _element in _elements:
            print_element(_element, level + 1, max_level=max_level)


# 注意：测试采用的是逍遥模拟器，安卓7.1版本
if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 准备临时目录
    _test_path = os.path.dirname(__file__)
    _temp_path = os.path.abspath(os.path.join(_test_path, os.path.pardir, 'temp/test_android'))
    FileTool.create_dir(_temp_path, exist_ok=True)
    FileTool.remove_files(_temp_path)

    # 执行处理
    desired_caps = {
        'platformName': 'Android',  # 被测手机是安卓
        'platformVersion': '7.1',  # 模拟器安卓版本
        'deviceName': '127.0.0.1:21513',  # 设备名，安卓手机可以随意填写
        # 'appPackage': 'com.android.settings',  # 启动APP Package名称
        # 'appActivity': '.Settings',  # 启动Activity名称
        "appPackage": "com.android.browser",
        "appActivity": ".BrowserActivity",
        # 'unicodeKeyboard': True,  # 使用自带输入法，输入中文时填True
        # 'resetKeyboard': True,  # 执行完程序恢复原来输入法
        'noReset': True,       # 不要重置App，防止登录信息丢失
        # 'newCommandTimeout': 6000,
        # 'automationName': 'UiAutomator2'
    }

    _device = AppDevice(
        appium_server='http://localhost:4723/wd/hub', desired_caps=desired_caps
    )

    # _device.swipe_up()

    # _page_soure = _device.page_source

    # _elements = _device.find_elements_by_xpath("/child::*")
    _element = _device.find_element(
        by=MobileBy.ID, value="com.android.browser:id/taburlbar")
    print_element(_element, 0, max_level=10)

    # _element = _device.find_element(
    #     by=MobileBy.XPATH, value="//android.widget.TextView[@text='应用' and @resource-id='android:id/title']")

    # _attrs = _element.get_attributes()

    # _elements = _element.get_childrens()

    # _el1 = _element.find_elements_by_xpath('child::*')

    # print(_element.tag_name)

    # _element1 = _device.find_elements(
    #     by=MobileBy.XPATH, value='/child::*/child::*/child::*/child::*/child::*/child::*')

    # _image_screen = _device.screenshot(filename=os.path.join(_temp_path, 'full_screen.png'))

    # _image_el = _element.screenshot(filename=os.path.join(_temp_path, 'el.png'))

    time.sleep(5)
