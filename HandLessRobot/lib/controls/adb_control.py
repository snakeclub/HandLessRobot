#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
adb方式的安卓手机控制
@module adb_control
@file adb_control.py
"""

import os
import sys
import math
import time
import datetime
import pyscreeze
from io import BytesIO
from PIL import Image
import threading
import base64
import random
import lxml.etree as ET
from appium.webdriver.common.mobileby import MobileBy
from HiveNetLib.base_tools.file_tool import FileTool
from HiveNetLib.base_tools.run_tool import RunTool
from HiveNetLib.simple_xml import SimpleXml, EnumXmlObjType
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))
from HandLessRobot.lib.controls.appium_control import EnumAndroidKeycode


__MOUDLE__ = 'adb_control'  # 模块名
__DESCRIPT__ = u'adb方式的安卓手机控制'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2021.01.23'  # 发布日期


class AppElement(object):
    """
    应用元素类
    """

    #############################
    # 构造函数
    #############################
    def __init__(self, element: ET.Element, device, xml_doc: SimpleXml):
        """
        应用元素类

        @param {Element} element - 初始化元素对象
        @param {AppDevice} device - 设备对象
        @param {SimpleXml} xml_doc - 元素所在的xml布局文档
        """
        self.element = element
        self.device = device
        self.xml_doc = xml_doc

    #############################
    # 属性
    #############################
    @property
    def text(self) -> str:
        """
        获取元素可见文本

        @property {str}
        """
        return self.element.get('text', default='')

    @property
    def tag_name(self) -> str:
        """
        获取元素标签名

        @property {str}
        """
        return self.element.get('class', default='')

    @property
    def is_selected(self) -> bool:
        """
        获取元素是否被选中

        @property {bool}
        """
        return self.element.get('selected', default='false') == 'true'

    @property
    def is_enabled(self) -> bool:
        """
        获取元素是否可操作

        @property {bool}
        """
        return self.element.get('enabled', default='true') == 'true'

    @property
    def is_displayed(self) -> bool:
        """
        获取元素是否可见

        @property {bool}
        """
        return self.element.get('displayed', default='true') == 'true'

    @property
    def location(self) -> tuple:
        """
        获取元素在页面中的位置(左上角)

        @property {tuple[int, int]} - (x, y) 坐标
        """
        _location = eval('[%s]' % self.element.get('bounds').replace('][', '],['))
        return _location[0][0], _location[0][1]

    @property
    def size(self) -> tuple:
        """
        获取元素大小

        @property {tuple[int, int]} - (width, height) 大小
        """
        _location = eval('[%s]' % self.element.get('bounds').replace('][', '],['))
        return _location[1][0] - _location[0][0], _location[1][1] - _location[0][1]

    @property
    def rect(self) -> tuple:
        """
        获取元素区域

        @property {tuple[int, int, int, int]} - (x, y, width, height)
        """
        _location = eval('[%s]' % self.element.get('bounds').replace('][', '],['))
        return (
            _location[0][0], _location[0][1],
            _location[1][0] - _location[0][0], _location[1][1] - _location[0][1]
        )

    def get_attribute(self, name: str) -> str:
        """
        获取元素指定名称的属性(attribute/property)

        @param {str} name - 属性名

        @returns {str} - 属性取值，如果属性不存在返回空字符串
        """
        return self.element.get(name)

    #############################
    # 屏幕操作
    #############################
    def screenshot(self, filename: str = None) -> Image:
        """
        保存元素截图

        @param {str} filename=None - 要保存的路径

        @returns {PIL.Image} - 图片对象
        """
        _image: Image = self.device.screenshot()
        _crop_image = _image.crop(self.rect)
        if filename is not None:
            _crop_image.save(filename)

        return _crop_image

    #############################
    # 对元素的操作
    #############################
    def click(self):
        """
        在元素的中心点进行点击
        """
        _rect = self.rect
        _x = _rect[0] + math.ceil(_rect[2] / 2.0)
        _y = _rect[1] + math.ceil(_rect[3] / 2.0)
        self.device.tap(x=_x, y=_y)

    def tap(self, count: int = 1):
        """
        点击元素

        @param {int} count=1 - 连续点击的次数
        """
        _rect = self.rect
        _x = _rect[0] + math.ceil(_rect[2] / 2.0)
        _y = _rect[1] + math.ceil(_rect[3] / 2.0)
        self.device.tap(x=_x, y=_y, count=count)

    def long_press(self, duration: int = 1000):
        """
        在元素上长按

        @param {int} duration=1000 - 经历时长，单位为毫秒
        """
        _rect = self.rect
        _x = _rect[0] + math.ceil(_rect[2] / 2.0)
        _y = _rect[1] + math.ceil(_rect[3] / 2.0)
        self.device.long_press(x=_x, y=_y, duration=duration)

    #############################
    # 元素查找
    #############################
    def find_element(self, by: str = MobileBy.ID, value=None,
                     timeout: float = 0.0, interval: float = 0.5):
        """
        查找元素

        @param {str|MobileBy} by=MobileBy.ID - 查找类型
        @param {str|dict} value=None - 查找类型对应的查找参数，不同类型的定义如下
            MobileBy.ID {str} - 要获取的元素的id属性，例如 'foo_id'
            MobileBy.XPATH {str} - 要获取元素的xpath字符串，例如 '//div/td[1]'
        @param {float} timeout=0.0 - 最大等待超时时间，单位为秒
        @param {float} interval=0.5 - 每次检查间隔时间，单位为秒

        @returns {AppElement} - 查找到的元素对象
        """
        _list = self.find_elements(by=by, value=value, timeout=timeout, interval=interval)
        if len(_list) <= 0:
            raise RuntimeError('Element not found!')

        return _list[0]

    def find_elements(self, by: str = MobileBy.ID, value=None,
                      timeout: float = 0.0, interval: float = 0.5) -> list:
        """
        查找元素

        @param {str|MobileBy} by=By.ID - 查找类型
        @param {str|dict} value=None - 查找类型对应的查找参数，不同类型的定义如下
            MobileBy.ID {str} - 要获取的元素的id属性，例如 'foo_id'
            MobileBy.XPATH {str} - 要获取元素的xpath字符串，例如 '//div/td[1]'
        @param {float} timeout=0.0 - 最大等待超时时间，单位为秒
        @param {float} interval=0.5 - 每次检查间隔时间，单位为秒

        @returns {list[AppElement]} - 查找到的对象
        """
        _list = list()
        _start = datetime.datetime.now()
        while len(_list) == 0:
            if by == MobileBy.ID:
                # 通过ID查找对象
                _current_package = self.device.current_package
                _nodes = self.xml_doc.get_childnodes_on_node(
                    self.element, '//*[@resource-id="%s:id/%s"]' % (_current_package, value)
                )
            else:
                # 通过xpath查找
                _nodes = self.xml_doc.get_childnodes_on_node(self.element, value)

            for _element in _nodes:
                _list.append(AppElement(_element, self.device, self.xml_doc))

            # 判断是否超时
            if (datetime.datetime.now() - _start).total_seconds() < timeout:
                time.sleep(interval)
                continue
            else:
                break

        return _list

    def find_element_by_xpath(self, xpath: str, timeout: float = 0.0, interval: float = 0.5):
        """
        通过xpath获取一个元素

        @param {str} xpath - 要获取元素的xpath字符串
        @param {float} timeout=0.0 - 最大等待超时时间，单位为秒
        @param {float} interval=0.5 - 每次检查间隔时间，单位为秒

        @returns {AppElement} - 获取到的元素对象

        @example
            element = driver.find_element_by_xpath('//div/td[1]')
        """
        return self.find_element(
            by=MobileBy.XPATH, value=xpath, timeout=timeout, interval=interval
        )

    def find_elements_by_xpath(self, xpath: str,
                               timeout: float = 0.0, interval: float = 0.5) -> list:
        """
        通过xpath获取多个元素

        @param {str} xpath - 要获取元素的xpath值
        @param {float} timeout=0.0 - 最大等待超时时间，单位为秒
        @param {float} interval=0.5 - 每次检查间隔时间，单位为秒

        @returns {list[AppElement]} - 获取到的元素对象

        @example
            elements = driver.find_elements_by_xpath("//div[contains(@class, 'foo')]")
        """
        return self.find_elements(
            by=MobileBy.XPATH, value=xpath, timeout=timeout, interval=interval
        )


class AppDevice(object):
    """
    移动设备操作模块
    """
    #############################
    # 静态的连接参数
    #############################
    @classmethod
    def get_app_device(cls, desired_caps: dict, **kwargs):
        """
        获取移动应用设备对象

        @param {dict} desired_caps=None - 设备连接参数字典
            deviceName {str} - 使用的手机或模拟器类型, 填入 adb devices -l 显示的设备连接名,
                示例: 127.0.0.1:21513
            appPackage {str} - 连接时运行的 Android 应用的包名, 例如: com.android.browser
            appActivity {str} - 包中所要启动的 Android acticity, 例如: .BrowserActivity
        @param {kwargs} - 扩展参数，支持的扩展参数包括
            shell_encoding {str} - shell命令的编码方式, 在使用到命令行工具时使用, 默认为 'utf-8'
            adb_name {str} - adb命令的启动名称, 安卓adb版专用, 默认为 'adb'
            tmp_path {str} - 临时目录, 处理adb资源文件, 安卓adb版专用, 默认为当前工作目录

        @returns {AppDevice} - 返回Appium的设备对象
        """
        return AppDevice(
            desired_caps=desired_caps, **kwargs
        )

    #############################
    # 工具类函数
    #############################
    @classmethod
    def center(cls, coords) -> tuple:
        """
        返回指定区域的中心位置

        @param {(int,int,int,int)} coords - 区域坐标(x, y, width, height)

        @returns {(int, int)} - 返回的中心位置(x, y)
        """
        _x = coords[0] + math.ceil(coords[2] / 2.0)
        _y = coords[1] + math.ceil(coords[3] / 2.0)
        return _x, _y

    #############################
    # 实例化的工具函数
    #############################
    def adb_run_inner(self, cmd: str, ignore_error: bool = False) -> list:
        """
        内部的adb执行命令

        @param {str} cmd - 要执行的命令
        @param {bool} ignore_error=False - 是否忽略错误

        @returns {list} - 返回执行的输出信息
        """
        return AdbTools.adb_run(
            self.adb_name, self._desired_caps['deviceName'], cmd,
            shell_encoding=self.shell_encoding, ignore_error=ignore_error
        )

    #############################
    # 构造函数及析构函数
    #############################

    def __init__(self, desired_caps: dict, **kwargs):
        """
        构造函数

        @param {dict} desired_caps=None - 设备连接参数字典
            deviceName {str} - 使用的手机或模拟器类型, 填入 adb devices -l 显示的设备连接名,
                示例: 127.0.0.1:21513
            appPackage {str} - 连接时运行的 Android 应用的包名, 例如: com.android.browser
            appActivity {str} - 包中所要启动的 Android acticity, 例如: .BrowserActivity
        @param {kwargs} - 扩展参数，支持的扩展参数包括
            shell_encoding {str} - shell命令的编码方式, 在使用到命令行工具时使用, 默认为 'utf-8'
            adb_name {str} - adb命令的启动名称, 安卓adb版专用, 默认为 'adb'
            tmp_path {str} - 临时目录, 处理adb资源文件, 安卓adb版专用, 默认为当前工作目录
        """
        self._desired_caps = {}
        self._desired_caps.update(desired_caps)

        # 其他参数
        self.shell_encoding = kwargs.get('shell_encoding', 'utf-8')
        self.adb_name = kwargs.get('adb_name', 'adb')
        self.tmp_path = os.path.abspath(kwargs.get('tmp_path', ''))
        FileTool.create_dir(self.tmp_path, exist_ok=True)

        # 判断命令行
        self.grep_str = 'findstr' if sys.platform == 'win32' else 'grep'

        # 缓存字典
        self.cache = dict()

        # 要安装到设备上的文件路径
        self._file_path = os.path.join(
            os.path.realpath(os.path.dirname(__file__)), 'adb_apk'
        )

    def __del__(self):
        """
        析构函数
        """
        pass

    def init_device(self):
        """
        初始化设备
        """
        # 传送获取界面xml的jar包
        if not AdbTools.adb_file_exists(
            self.adb_name, self._desired_caps['deviceName'],
            '/data/local/tmp/UiTestTools.jar', shell_encoding=self.shell_encoding
        ):
            _cmd = 'push %s /data/local/tmp/' % (
                os.path.join(self._file_path, 'UiTestTools.jar')
            )
            self.adb_run_inner(_cmd)

        # 安装ADBKeyboard.apk
        if not self.is_app_installed('com.android.adbkeyboard'):
            self.install_app(
                os.path.join(self._file_path, 'ADBKeyboard.apk'),
                replace=True
            )

        # 安装剪贴版应用
        if not self.is_app_installed('ca.zgrs.clipper'):
            self.install_app(
                os.path.join(self._file_path, 'clipper.apk'),
                replace=True
            )

        # 启动剪贴版服务
        _cmd = 'shell am startservice ca.zgrs.clipper/.ClipboardService'
        self.adb_run_inner(_cmd)

    #############################
    # 实例基础属性
    #############################
    @property
    def size(self) -> tuple:
        """
        获取屏幕大小
        @property {tuple[int, int]}
        """
        _cmd = 'shell wm size'
        _cmd_info = self.adb_run_inner(_cmd)
        if not _cmd_info[0].startswith('Physical size:'):
            raise RuntimeError('exec cmd [%s] error: %s' % (_cmd, '\n'.join(_cmd_info)))
        _size = _cmd_info[0][len('Physical size:'):].strip().split('x')
        return int(_size[0]), int(_size[1])

    @property
    def desired_caps(self) -> dict:
        """
        返回设备连接参数
        @property {dict}
        """
        return self._desired_caps

    #############################
    # 会话相关处理
    #############################
    @property
    def page_source(self) -> str:
        """
        获取当前页面源码

        @property {str}
        """
        # 生成源码
        _cmd = 'shell uiautomator runtest UiTestTools.jar -c com.snaker.testtools.uiDumpXml'
        self.adb_run_inner(_cmd)

        # 获取文件
        _cmd = 'pull /data/local/tmp/local/tmp/uidump.xml %s' % self.tmp_path
        self.adb_run_inner(_cmd)

        # 打开文件
        _page_source = ''
        _file = os.path.join(self.tmp_path, 'uidump.xml')
        with open(_file, 'r', encoding='utf-8') as _f:
            _page_source = _f.read()

        # 删除临时文件
        FileTool.remove_file(_file)

        return _page_source

    def get_clipboard_text(self) -> str:
        """
        获取剪切板文本

        @returns {str} - 获取到的文本，如果没有信息返回空字符串
        """
        _cmd = 'shell am broadcast -a clipper.get'
        _cmd_info = self.adb_run_inner(_cmd)
        _index = _cmd_info[1].find('data="')
        if _index < 0:
            raise RuntimeError('exec cmd [%s] error: %s' % (_cmd, '\n'.join(_cmd_info)))
        _data = _cmd_info[1][_index + 6:-1]
        return _data

    def set_clipboard_text(self, text: str):
        """
        设置剪贴版文本

        @param {str} text - 要设置的文本
        """
        _cmd = 'shell am broadcast -a clipper.set -e text "%s"' % text
        _cmd_info = self.adb_run_inner(_cmd)
        if not _cmd_info[1].endswith('data="Text is copied into clipboard."'):
            raise RuntimeError('exec cmd [%s] error: %s' % (_cmd, '\n'.join(_cmd_info)))

    #############################
    # app操作相关
    #############################
    @property
    def current_package(self) -> str:
        """
        得到当前的Android应用的包名

        @property {str}
        """
        _cmd = 'shell dumpsys window windows | %s mFocusedApp' % self.grep_str
        _cmd_info = self.adb_run_inner(_cmd)

        # mFocusedActivity: ActivityRecord{e903df8 u0 com.ss.android.ugc.aweme/.splash.SplashActivity t172}
        _findstr = 'ActivityRecord{'
        _temp = _cmd_info[0][_cmd_info[0].find(_findstr) + len(_findstr):].split(' ')
        _package = _temp[2][0: _temp[2].find('/')]

        return _package

    @property
    def current_activity(self) -> str:
        """
        得到当前的Android Activity名称

        @property {str}
        """
        _cmd = 'shell dumpsys window windows | %s mFocusedApp' % self.grep_str
        _cmd_info = self.adb_run_inner(_cmd)

        # mFocusedActivity: ActivityRecord{e903df8 u0 com.ss.android.ugc.aweme/.splash.SplashActivity t172}
        _findstr = 'ActivityRecord{'
        _temp = _cmd_info[0][_cmd_info[0].find(_findstr) + len(_findstr):].split(' ')
        _activity = _temp[2][_temp[2].find('/') + 1:].rstrip(',')

        return _activity

    def wait_activity(self, app_activity: str, timeout: float, interval: float = 1) -> bool:
        """
        等待指定的activity出现直到超时

        @param {str} app_activity - 要等待的页面Activity
        @param {float} timeout - 最大等待超时时间，单位为秒
        @param {float} interval=1 - 每次检查间隔时间，单位为秒

        @returns {bool} - 等到到页面返回True, 超时返回False
        """
        _start = datetime.datetime.now()
        while (datetime.datetime.now() - _start).total_seconds() < timeout:
            if app_activity == self.current_activity:
                return True

            # 等待下一次检查
            time.sleep(interval)

        # 超时返回失败
        return False

    def is_app_installed(self, app_id: str) -> bool:
        """
        是否安装了指定的应用程序

        @param {str} app_id - iOS bundleID或Android包名

        @returns {bool} - 检查结果
        """
        _cmd = 'shell pm path %s' % app_id
        _cmd_info = self.adb_run_inner(_cmd, ignore_error=True)

        if len(_cmd_info) > 0 and _cmd_info[0].startswith('package:'):
            return True
        else:
            return False

    def install_app(self, app_path: str, **options):
        """
        安装应用

        @param {str} app_path - app安装路径
        @param {kwargs} options - 安装参数（安卓专用）:
            replace (bool): [Android only] whether to reinstall/upgrade the package if it is
                already present on the device under test. True by default
        """
        _cmd = 'install%s %s' % (
            '' if options.get('replace', False) else ' -r',
            app_path
        )
        _cmd_info = self.adb_run_inner(_cmd)
        if len(_cmd_info) < 2 or not _cmd_info[-2].startswith('Success'):
            raise RuntimeError('exec cmd [%s] error: %s' % (_cmd, '\n'.join(_cmd_info)))

    def remove_app(self, app_id: str, **options):
        """
        删除应用

        @param {str} app_id - iOS appID, bundleID或Android包名
            示例: 'com.example.AppName'
        @param {kwargs} options - 卸载参数（安卓专用）:
            keepData (bool): [Android only] whether to keep application data and caches after it is uninstalled.
                False by default
        """
        _cmd = 'uninstall%s %s' % (
            ' -k' if options.get('keepData', True) else '',
            app_id
        )
        _cmd_info = self.adb_run_inner(_cmd)
        if not _cmd_info[0].startswith('Success'):
            raise RuntimeError('exec cmd [%s] error: %s' % (_cmd, '\n'.join(_cmd_info)))

    def launch_app(self, app_id: str = None, activity: str = None):
        """
        启动被测应用
        注：如果被测应用（AUT）已关闭或在后台运行，它将启动它。如果AUT已打开，它将使其放到后台并重新启动。

        @param {str} app_id=None - 启动的应用名，如果不传将尝试从desired_caps中获取
            示例: 'com.example.AppName'
        @param {str} activity=None - 启动的页面，如果不传将尝试从desired_caps中获取
        """
        _app_id = app_id
        _activity = activity
        if _app_id is None:
            _app_id = self._desired_caps.get('appPackage')
            _activity = self._desired_caps.get('appActivity')

        _cmd = 'shell am start -n %s/%s' % (
            _app_id, _activity
        )
        _cmd_info = self.adb_run_inner(_cmd)
        if len(_cmd_info) >= 2 and _cmd_info[-2].startswith('Error'):
            raise RuntimeError('exec cmd [%s] error: %s' % (_cmd, '\n'.join(_cmd_info)))

    def close_app(self, app_id: str = None):
        """
        关闭当前正在测试的应用

        @param {str} app_id=None - 启动的应用名，如果不传将尝试从desired_caps中获取
            示例: 'com.example.AppName'
        """
        _app_id = app_id
        if _app_id is None:
            _app_id = self._desired_caps.get('appPackage')

        _cmd = 'shell am force-stop %s' % _app_id
        self.adb_run_inner(_cmd)

    #############################
    # 设备操作
    #############################
    def is_screen_on(self) -> bool:
        """
        判断屏幕是否点亮

        @returns {bool} - 返回屏幕是否点亮的状态
        """
        _cmd = 'shell dumpsys window policy | %s mScreenOnEarly=' % self.grep_str
        _cmd_info = self.adb_run_inner(_cmd)
        if len(_cmd_info) > 0 and _cmd_info[0].find('mScreenOnEarly=true') >= 0:
            return True
        else:
            return False

    def is_showing_lock_screen(self) -> bool:
        """
        是否正在显示锁屏界面

        @returns {bool} - 是否正在锁屏界面
        """
        _cmd = 'shell dumpsys window policy | %s mShowingLockscreen=' % self.grep_str
        _cmd_info = self.adb_run_inner(_cmd)
        if len(_cmd_info) > 0 and _cmd_info[0].find('mShowingLockscreen=true') >= 0:
            return True
        else:
            return False

    def is_power_on(self) -> bool:
        """
        判断设备是否非休眠状态(有可能屏幕熄灭但可操作)

        @returns {bool} - 返回设备是否非休眠
        """
        _cmd = 'shell dumpsys window policy | %s mAwake=' % self.grep_str
        _cmd_info = self.adb_run_inner(_cmd)
        if len(_cmd_info) > 0 and _cmd_info[0].find('mAwake=true') >= 0:
            return True
        else:
            return False

    def set_power_stayon(self, stay_type: str = 'true'):
        """
        设置设备电源(屏幕)常开(不自动休眠)

        @param {str} stay_type='true' - 类型包括:
            true - 保持常亮
            false - 不保持常亮
            usb - 接入usb时常亮
            ac - 接入电源时常亮
            wireless - 接入无线时常亮
        """
        _cmd = 'shell svc power stayon %s' % stay_type
        self.adb_run_inner(_cmd)

    #############################
    # 屏幕操作
    #############################

    def screenshot(self, filename: str = None) -> Image:
        """
        保存屏幕截图

        @param {str} filename=None - 要保存的路径

        @returns {PIL.Image} - 图片对象
        """
        # 截图
        _cmd = 'shell uiautomator runtest UiTestTools.jar -c com.snaker.testtools.uiScreenShot'
        self.adb_run_inner(_cmd)

        # 获取文件
        _filename = filename
        if filename is None:
            _filename = os.path.join(self.tmp_path, 'uiShot.png')
        _cmd = 'pull /data/local/tmp/uiShot.png %s' % _filename
        self.adb_run_inner(_cmd)

        # 加载为对象
        with open(_filename, 'rb') as _f:
            _image = Image.open(BytesIO(_f.read()))

        if filename is None:
            # 删除临时文件
            FileTool.remove_file(_filename)

        return _image

    def locate_on_screen(self, image, minSearchTime: int = 0, **kwargs):
        """
        在屏幕中定位指定图片的位置

        @param {str|PIL.Image} image - 要定位的图片文件路径或图片对象
        @param {int} minSearchTime=0 - 最长搜索时间，单位为毫秒，设置这个值可以在找不到图片的情况下，循环等待屏幕变化重新匹配
        @param {dict} kwargs - 其他执行参数:
            {bool} grayscale=False - 是否转换图片为灰度检索(提升30%速度)
            {int} limit=10000 - 匹配数量限制
            {int} step=1 - 匹配步骤，支持送1或2，如果为2会跳过细节，大约能提升3倍速度，但有可能匹配不上
            {float} confidence=0.999 - 匹配度

        @returns {(int, int, int, int)} - 返回图片的位置(x, y, width, height), 找不到返回None
        """
        if type(image) == str:
            _image = Image.open(image)
        else:
            _image = image

        start = time.time()
        while True:
            try:
                screenshotIm = self.screenshot()
                retVal = pyscreeze.locate(_image, screenshotIm, **kwargs)
                if retVal or time.time() - start > minSearchTime:
                    return retVal
            except pyscreeze.ImageNotFoundException:
                return None

    def locate_all_on_screen(self, image, **kwargs):
        """
        在屏幕中定位指定图片的所有位置

        @param {str|PIL.Image} image - 要定位的图片文件路径或图片对象
        @param {dict} kwargs - 其他执行参数:
            {bool} grayscale=False - 是否转换图片为灰度检索(提升30%速度)
            {int} limit=10000 - 匹配数量限制
            {int} step=1 - 匹配步骤，支持送1或2，如果为2会跳过细节，大约能提升3倍速度，但有可能匹配不上
            {float} confidence=0.999 - 匹配度

        @returns {list} - 返回所找到的所有图片的位置
            [(x, y, width, height), ..]
        """
        if type(image) == str:
            _image = Image.open(image)
        else:
            _image = image

        screenshotIm = self.screenshot()
        retVal = pyscreeze.locateAll(_image, screenshotIm, **kwargs)
        return list(retVal)

    #############################
    # 动作 - 滑动
    #############################

    def swipe(self, start: tuple, end: tuple, duration: int = 0):
        """
        执行两点之间的滑动

        @param {tuple} start - 滑动开始点的 (x, y) 位置
        @param {tuple} end - 滑动结束点的 (x, y) 位置
        @param {int} duration=0 - 滑动经历时长，单位为毫秒
        """
        _cmd = 'shell input swipe %d %d %d %d%s' % (
            start[0], start[1], end[0], end[1],
            '' if duration == 0 else ' %d' % duration
        )
        self.adb_run_inner(_cmd)

    def swipe_up(self, x: int = None, y: int = None, swipe_len: int = None, duration: int = 0):
        """
        向上滑动

        @param {int} x=None - 滑动开始所在x坐标，不传代表在屏幕横向正中间位置
        @param {int} y=None - 滑动开始所在y坐标，不传代表在屏幕纵向正中间下方距离swipe_len一半的位置
        @param {int} swipe_len=None - 滑动的距离，不传默认为1/3屏幕高度
        @param {int} duration=0 - 滑动经历时长，单位为毫秒
        """
        # 计算滑动参数
        _w, _h = self.size
        if x is None:
            x = math.ceil(_w / 2.0)
        if swipe_len is None:
            swipe_len = math.ceil(_h / 3.0)
        if y is None:
            y = min(math.ceil(_h / 2.0 + swipe_len / 2.0), _h)

        # 执行滑动处理
        self.swipe(
            (x, y), (x, max(y - swipe_len, 0)), duration=duration
        )

    def swipe_down(self, x: int = None, y: int = None, swipe_len: int = None, duration: int = 0):
        """
        向下滑动

        @param {int} x=None - 滑动开始所在x坐标，不传代表在屏幕横向正中间位置
        @param {int} y=None - 滑动开始所在y坐标，不传代表在屏幕纵向正中间上方距离swipe_len一半的位置
        @param {int} swipe_len=None - 滑动的距离，不传默认为1/3屏幕高度
        @param {int} duration=0 - 滑动经历时长，单位为毫秒
        """
        # 计算滑动参数
        _w, _h = self.size
        if x is None:
            x = math.ceil(_w / 2.0)
        if swipe_len is None:
            swipe_len = math.ceil(_h / 3.0)
        if y is None:
            y = max(math.ceil(_h / 2.0 - swipe_len / 2.0), 0)

        # 执行滑动处理
        self.swipe(
            (x, y), (x, min(y + swipe_len, _h)), duration=duration
        )

    def swipe_left(self, x: int = None, y: int = None, swipe_len: int = None, duration: int = 0):
        """
        向左滑动

        @param {int} x=None - 滑动开始所在x坐标，不传代表在屏幕横向正中间右方距离swipe_len一半的位置
        @param {int} y=None - 滑动开始所在y坐标，不传代表在屏幕纵向正中间位置
        @param {int} swipe_len=None - 滑动的距离，不传默认为1/3屏幕宽度
        @param {int} duration=0 - 滑动经历时长，单位为毫秒
        """
        # 计算滑动参数
        _w, _h = self.size
        if y is None:
            y = math.ceil(_h / 2.0)
        if swipe_len is None:
            swipe_len = math.ceil(_w / 3.0)
        if x is None:
            x = min(math.ceil(_w / 2.0 + swipe_len / 2.0), _w)

        # 执行滑动处理
        self.swipe(
            (x, y), (max(x - swipe_len, 0), y), duration=duration
        )

    def swipe_right(self, x: int = None, y: int = None, swipe_len: int = None, duration: int = 0):
        """
        向左滑动

        @param {int} x=None - 滑动开始所在x坐标，不传代表在屏幕横向正中间左方距离swipe_len一半的位置
        @param {int} y=None - 滑动开始所在y坐标，不传代表在屏幕纵向正中间位置
        @param {int} swipe_len=None - 滑动的距离，不传默认为1/3屏幕宽度
        @param {int} duration=0 - 滑动经历时长，单位为毫秒
        """
        # 计算滑动参数
        _w, _h = self.size
        if y is None:
            y = math.ceil(_h / 2.0)
        if swipe_len is None:
            swipe_len = math.ceil(_w / 3.0)
        if x is None:
            x = max(math.ceil(_w / 2.0 - swipe_len / 2.0), 0)

        # 执行滑动处理
        self.swipe(
            (x, y), (min(x + swipe_len, _w), y), duration=duration
        )

    def swipe_plus(self, points: list, duration: int = 0):
        """
        超级滑动处理

        @param {list} points - 要滑动的点配置，每个点为一个 tuple(x, y)
        @param {int} duration=0 - 滑动经历时长，单位为毫秒
        """
        # 组成滑动点的参数
        _points = '%s-' % ','.join(points[0])
        for _i in range(1, len(points)):
            _points = _points + ','.join(points[_i])

        # 组成耗时时长的参数
        _seconds = ''
        if duration > 0:
            _seconds = ' -e seconds %s' % str(duration / 1000.0)

        _cmd = 'shell uiautomator runtest UiTestTools.jar -e points %s%s -c com.snaker.testtools.uiSwipe' % (
            _points, _seconds
        )
        self.adb_run_inner(_cmd)

    #############################
    # 动作 - 点击
    #############################
    def tap(self, x: int = None, y: int = None, count: int = 1, **kwargs):
        """
        点击指定位置

        @param {int} x=None - 要点击的x位置，如果不传默认为屏幕宽度中间
        @param {int} y=None - 要点击的y位置，如果不传默认为屏幕高度中间
        @param {int} count=1 - 点击的次数
        """
        # 计算点击位置
        if x is None or y is None:
            _w, _h = self.size
        if x is None:
            x = math.ceil(_w / 2.0)
        if y is None:
            y = math.ceil(_h / 2.0)

        _cmd_mode = '%s -s %s shell input tap' % (self.adb_name, self._desired_caps['deviceName'])
        _cmd_list = list()
        for i in range(count):
            _cmd_list.append('%s %d %d' % (_cmd_mode, x, y))
        _cmd = ' && '.join(_cmd_list)
        _code, _cmd_info = RunTool.exec_sys_cmd(_cmd, shell_encoding=self.shell_encoding)
        if _code != 0:
            raise RuntimeError('exec cmd [%s] error[%d]: %s' % (_cmd, _code, '\n'.join(_cmd_info)))

    def tap_continuity(self, pos_seed: list, times: float, thread_count: int = 2,
                       random_sleep: bool = False, sleep_min: float = 0.0, sleep_max: float = 0.5):
        """
        在指定范围随机连续点击

        @param {list} pos_seed - 允许点击的位置坐标清单[(x,y), ...], 随机获取
        @param {float} times - 要点击的时长, 单位为秒
        @param {int} thread_count=2 - 生产点击线程，数量越多点击频率越密集
        @param {bool} random_sleep=False - 每个线程点击期间是否自动休眠指定时长
        @param {float} sleep_min=0.0 - 每个线程点击期间自动休眠最小时长, 单位为秒
        @param {float} sleep_max=0.5 - 每个线程点击期间自动休眠最大时长, 单位为秒
        """
        # 参数准备
        _cmd_mode = 'shell input tap'
        _seed_len = len(pos_seed)

        # 定义点击线程函数
        def tap_thread_fun():
            while True:
                # 循环处理，自身不结束
                _pos = pos_seed[random.randint(0, _seed_len - 1)]
                _cmd = '%s %d %d' % (_cmd_mode, _pos[0], _pos[1])
                # 不检查结果
                self.adb_run_inner(_cmd, ignore_error=True)
                # 看是否休眠
                if random_sleep:
                    time.sleep(random.uniform(sleep_min, sleep_max))

        # 启动执行动作
        _start = datetime.datetime.now()
        _thread_list = list()
        for i in range(thread_count):
            _running_thread = threading.Thread(
                target=tap_thread_fun,
                name='Thread-Tap-Running %s' % str(i)
            )
            _running_thread.setDaemon(True)
            _running_thread.start()

            # 添加到列表，用于停止线程
            _thread_list.append(_running_thread)

        # 监控时长
        while (datetime.datetime.now() - _start).total_seconds() < times:
            time.sleep(0.01)

        # 停止线程
        for _thread in _thread_list:
            RunTool.stop_thread(_thread)

    def long_press(self, x: int = None, y: int = None, duration: int = 1000):
        """
        在指定位置长按

        @param {int} x=None - 要点击的x位置，如果不传默认为屏幕宽度中间
        @param {int} y=None - 要点击的y位置，如果不传默认为屏幕高度中间
        @param {int} duration=1000 - 经历时长，单位为毫秒
        """
        if x is None or y is None:
            _w, _h = self.size
        if x is None:
            x = math.ceil(_w / 2.0)
        if y is None:
            y = math.ceil(_h / 2.0)

        # 利用swipe来实现长按
        self.swipe((x, y), (x + 1, y + 1), duration=duration)

    #############################
    # 动作 - 按键
    #############################
    def press_keycode(self, key_code, *args):
        """
        通过adb方式输入按钮

        @param {int|str} key_code - 要按下的按键代码，支持传入int、EnumAndroidKeycode和str三种格式
            注：传入的str格式字符串必须与 EnumAndroidKeycode 定义的名称一致
        @param {args} - 如果需要同时按多个按键，则传入多个值
        """
        _key_code = key_code
        if type(key_code) == str:
            # 通过字符串获取key值
            _key_code = eval('EnumAndroidKeycode.%s' % key_code.upper()).value
        elif type(key_code) == EnumAndroidKeycode:
            _key_code = key_code.value

        if len(args) == 0:
            # 只发送一个按键
            _cmd = 'shell input keyevent %s' % str(_key_code)
        else:
            # 发送多个按键
            _key_list = [str(_key_code), ]
            for _key in args:
                if type(_key) == str:
                    # 通过字符串获取key值
                    _key = eval('EnumAndroidKeycode.%s' % _key.upper()).value
                elif type(_key) == EnumAndroidKeycode:
                    _key = _key.value

                _key_list.append(str(_key))

            _cmd = 'shell input keyevent %s' % ' '.join(_key_list)

        # 执行发送
        self.adb_run_inner(_cmd)

    def get_default_ime(self) -> str:
        """
        获取手机当前默认输入法

        @returns {str} - 输入法
        """
        _cmd = 'shell settings get secure default_input_method'
        _cmd_info = self.adb_run_inner(_cmd)
        if _cmd_info[0].startswith('Error'):
            raise RuntimeError('exec cmd [%s] error: %s' % (_cmd, '\n'.join(_cmd_info)))

        # 返回输入法
        return _cmd_info[0]

    def set_default_ime(self, ime):
        """
        设置输入法

        @param {str} ime - 要设置的输入法
        """
        _cmd = 'shell ime set %s' % ime
        _cmd_info = self.adb_run_inner(_cmd)
        if not _cmd_info[0].startswith('Input method'):
            raise RuntimeError('exec cmd [%s] error: %s' % (_cmd, '\n'.join(_cmd_info)))

    def set_first_ime(self):
        """
        设置手机的输入法为输入法列表的第一个输入法
        """
        # 查找手机输入法清单
        _cmd = 'shell ime list -a'
        _cmd_info = self.adb_run_inner(_cmd)
        if _cmd_info[0].startswith('Error'):
            raise RuntimeError('exec cmd [%s] error: %s' % (_cmd, '\n'.join(_cmd_info)))

        _ime = _cmd_info[0][0: -1]  # 去掉最后一个分号

        # 切换输入法
        self.set_default_ime(_ime)

    def set_adbime(self):
        """
        设置 ADBKeyBoard 为默认输入法
        (不支持Appium自带的send_keys)
        """
        _cmd = 'shell ime set com.android.adbkeyboard/.AdbIME'
        _cmd_info = self.adb_run_inner(_cmd)
        if not _cmd_info[0].startswith('Input method'):
            raise RuntimeError('exec cmd [%s] error: %s' % (_cmd, '\n'.join(_cmd_info)))

    def set_appium_ime(self):
        """
        设置 Appium UnicodeIME 为默认输入法
        (支持Appium自带的send_keys)
        """
        _cmd = 'shell ime set io.appium.settings/.UnicodeIME'
        _cmd_info = self.adb_run_inner(_cmd)
        if not _cmd_info[0].startswith('Input method'):
            raise RuntimeError('exec cmd [%s] error: %s' % (_cmd, '\n'.join(_cmd_info)))

    def adb_keyboard_text(self, text: str, use_base64: bool = False):
        """
        使用 ADBKeyBoard 输入文本
        参考: https://github.com/senzhk/ADBKeyBoard
        注意: 控制的安卓机必须安装 ADBKeyBoard 并设置为默认输入法

        @param {str} text - 要输入的文本
        @param {bool} use_base64=False - 是否转换为BASE64格式
        """
        _chars = text
        if use_base64:
            _charsb64 = str(base64.b64encode(_chars.encode('utf-8')))[1:]
            _cmd = 'shell am broadcast -a ADB_INPUT_B64 --es msg %s' % _charsb64
        else:
            _cmd = 'shell am broadcast -a ADB_INPUT_TEXT --es msg \'%s\'' % _chars

        # 执行发送
        _cmd_info = self.adb_run_inner(_cmd)
        if _cmd_info[1].strip() != 'Broadcast completed: result=0':
            raise RuntimeError('exec cmd [%s] error: %s' % (_cmd, '\n'.join(_cmd_info)))

    def adb_keyboard_keycode(self, key_code, *args):
        """
        使用 ADBKeyBoard 按下物理按键

        @param {int|str} key_code - 要按下的按键代码，支持传入int、EnumAndroidKeycode和str三种格式
            注：传入的str格式字符串必须与 EnumAndroidKeycode 定义的名称一致
        @param {args} - 如果需要同时按多个按键，则传入多个值
        """
        _key_code = key_code
        if type(key_code) == str:
            # 通过字符串获取key值
            _key_code = eval('EnumAndroidKeycode.%s' % key_code.upper()).value
        elif type(key_code) == EnumAndroidKeycode:
            _key_code = key_code.value

        if len(args) == 0:
            # 只发送一个按键
            _cmd = 'shell am broadcast -a ADB_EDITOR_CODE --ei code %s' % str(_key_code)
        else:
            # 发送多个按键
            _key_list = [str(_key_code), ]
            for _key in args:
                if type(_key) == str:
                    # 通过字符串获取key值
                    _key = eval('EnumAndroidKeycode.%s' % _key.upper()).value
                elif type(_key) == EnumAndroidKeycode:
                    _key = _key.value

                _key_list.append(str(_key))

            _cmd = 'shell am broadcast -a ADB_INPUT_MCODE --eia mcode \'%s\'' % ','.join(_key_list)

        # 执行发送
        _cmd_info = self.adb_run_inner(_cmd)
        if _cmd_info[1].strip() != 'Broadcast completed: result=0':
            raise RuntimeError('exec cmd [%s] error: %s' % (_cmd, '\n'.join(_cmd_info)))

    def adb_keyboard_clear(self):
        """
        使用 ADBKeyBoard 清除输入内容
        """
        _cmd = 'shell am broadcast -a ADB_CLEAR_TEXT'
        _cmd_info = self.adb_run_inner(_cmd)
        if _cmd_info[1].strip() != 'Broadcast completed: result=0':
            raise RuntimeError('exec cmd [%s] error: %s' % (_cmd, '\n'.join(_cmd_info)))

    #############################
    # 元素查找
    #############################

    def find_element(self, by: str = MobileBy.ID, value=None,
                     timeout: float = 0.0, interval: float = 0.5) -> AppElement:
        """
        查找元素

        @param {str|MobileBy} by=MobileBy.ID - 查找类型
        @param {str|dict} value=None - 查找类型对应的查找参数，不同类型的定义如下
            MobileBy.ID {str} - 要获取的元素的id属性，例如 'foo_id'
            MobileBy.XPATH {str} - 要获取元素的xpath字符串，例如 '//div/td[1]'
        @param {float} timeout=0.0 - 最大等待超时时间，单位为秒
        @param {float} interval=0.5 - 每次检查间隔时间，单位为秒

        @returns {AppElement} - 查找到的元素对象
        """
        _list = self.find_elements(by=by, value=value, timeout=timeout, interval=interval)
        if len(_list) <= 0:
            raise RuntimeError('Element not found!')

        return _list[0]

    def find_elements(self, by: str = MobileBy.ID, value=None,
                      timeout: float = 0.0, interval: float = 0.5) -> list:
        """
        查找元素

        @param {str|MobileBy} by=By.ID - 查找类型
        @param {str|dict} value=None - 查找类型对应的查找参数，不同类型的定义如下
            MobileBy.ID {str} - 要获取的元素的id属性，例如 'foo_id'
            MobileBy.XPATH {str} - 要获取元素的xpath字符串，例如 '//div/td[1]'
        @param {float} timeout=0.0 - 最大等待超时时间，单位为秒
        @param {float} interval=0.5 - 每次检查间隔时间，单位为秒

        @returns {list[AppElement]} - 查找到的对象
        """
        _list = list()
        _current_package = self.current_package
        _page_source = self.page_source
        _doc = SimpleXml(_page_source, obj_type=EnumXmlObjType.String)
        _start = datetime.datetime.now()
        while len(_list) == 0:
            if by == MobileBy.ID:
                # 通过ID查找对象
                _nodes = _doc.get_nodes(
                    '//*[@resource-id="%s:id/%s"]' % (_current_package, value)
                )
            else:
                # 通过xpath查找
                _nodes = _doc.get_nodes(value)

            for _element in _nodes:
                _list.append(AppElement(_element, self, _doc))

            # 判断是否超时
            if (datetime.datetime.now() - _start).total_seconds() < timeout:
                time.sleep(interval)
                continue
            else:
                break

        return _list

    def find_element_by_xpath(self, xpath: str,
                              timeout: float = 0.0, interval: float = 0.5) -> AppElement:
        """
        通过xpath获取一个元素

        @param {str} xpath - 要获取元素的xpath字符串
        @param {float} timeout=0.0 - 最大等待超时时间，单位为秒
        @param {float} interval=0.5 - 每次检查间隔时间，单位为秒

        @returns {AppElement} - 获取到的元素对象

        @example
            element = driver.find_element_by_xpath('//div/td[1]')
        """
        return self.find_element(
            by=MobileBy.XPATH, value=xpath, timeout=timeout, interval=interval
        )

    def find_elements_by_xpath(self, xpath: str,
                               timeout: float = 0.0, interval: float = 0.5) -> list:
        """
        通过xpath获取多个元素

        @param {str} xpath - 要获取元素的xpath值
        @param {float} timeout=0.0 - 最大等待超时时间，单位为秒
        @param {float} interval=0.5 - 每次检查间隔时间，单位为秒

        @returns {list[AppElement]} - 获取到的元素对象

        @example
            elements = driver.find_elements_by_xpath("//div[contains(@class, 'foo')]")
        """
        return self.find_elements(
            by=MobileBy.XPATH, value=xpath, timeout=timeout, interval=interval
        )


class AdbTools(object):
    """
    Adb命令工具
    """

    #############################
    # 静态工具
    #############################
    @classmethod
    def adb_run(cls, adb: str, device_name: str, cmd: str, shell_encoding: str = None,
                ignore_error: bool = False) -> list:
        """
        通用的adb执行命令

        @param {str} adb - 命令标识
        @param {str} device_name - 设备名, 传''代表不使用设备名
        @param {str} cmd - 要执行的命令
        @param {str} shell_encoding=None - 传入指定的编码
            注：如果不传入，尝试获取全局变量 SHELL_ENCODING, 如果也找不到，则默认为'utf-8'
        @param {bool} ignore_error=False - 是否忽略错误

        @returns {list} - 返回执行的输出信息
        """
        _cmd = '%s%s %s' % (
            adb,
            ' -s %s' % device_name if device_name != '' else '',
            cmd
        )
        _code, _cmd_info = RunTool.exec_sys_cmd(_cmd, shell_encoding=shell_encoding)
        if _code != 0 and not ignore_error:
            raise RuntimeError('run sys cmd [%s] error: %s' % (str(_code), '\n'.join(_cmd_info)))

        return _cmd_info

    @classmethod
    def adb_file_exists(cls, adb: str, device_name: str, file: str, shell_encoding: str = None) -> bool:
        """
        检查文件是否存在

        @param {str} adb - 命令标识
        @param {str} device_name - 设备名
        @param {str} file - 文件全路径
        @param {str} shell_encoding=None - 传入指定的编码
            注：如果不传入，尝试获取全局变量 SHELL_ENCODING, 如果也找不到，则默认为'utf-8'

        @returns {bool} - 文件是否存在
        """
        _cmd_info = cls.adb_run(
            adb, device_name, 'shell ls %s' % file, ignore_error=True
        )

        # 判断文件是否存在
        if _cmd_info[0].find('No such') >= 0:
            return False
        else:
            return True


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
