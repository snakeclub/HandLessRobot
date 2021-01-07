#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
安卓设备的控制模块
@module android
@file android.py
"""

import os
import sys
import uuid
import time
import datetime
import threading
import inspect
import ctypes
import base64
import random
from HiveNetLib.base_tools.file_tool import FileTool
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir, os.path.pardir)))
import HandLessRobot.lib.controls.appium_control as appium_control
from HandLessRobot.lib.controls.appium_control import EnumAndroidKeycode


__MOUDLE__ = 'android'  # 模块名
__DESCRIPT__ = u'安卓设备的控制模块'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2020.11.19'  # 发布日期


class AppElement(appium_control.AppElement):
    """
    应用元素对象
    """

    #############################
    # 对元素的操作
    #############################

    def set_text(self, keys: str = ''):
        """
        设置元素的可见文本

        @param {str} keys='' - 要设置的文本
        """
        self.element.set_text(keys=keys)


class AppDevice(appium_control.AppDevice):
    """
    安卓设备控制模块
    """
    #############################
    # 实例基础属性
    #############################
    @property
    def size_adb(self) -> tuple:
        """
        获取屏幕大小
        @property {tuple[int, int]}
        """
        _cmd = '%s -s %s shell wm size' % (self.adb_name, self._desired_caps['deviceName'])
        _code, _cmd_info = self._exec_sys_cmd(_cmd)
        if _code != 0 or not _cmd_info[0].startswith('Physical size:'):
            raise RuntimeError('exec cmd [%s] error[%d]: %s' % (_cmd, _code, '\n'.join(_cmd_info)))
        _size = _cmd_info[0][len('Physical size:'):].strip().split('x')
        return int(_size[0]), int(_size[1])

    #############################
    # app操作相关
    #############################
    @property
    def current_package(self) -> str:
        """
        得到当前的Android应用的包名

        @property {str}
        """
        return self.driver.current_package

    @property
    def current_activity(self) -> str:
        """
        得到当前的Android Activity名称

        @property {str}
        """
        return self.driver.current_activity

    @property
    def current_activity_adb(self) -> str:
        """
        得到当前的Android Activity名称

        @property {str}
        """
        _cmd = '%s -s %s shell dumpsys window windows | %s mFocusedApp' % (
            self.adb_name, self._desired_caps['deviceName'], self.grep_str
        )
        _code, _cmd_info = self._exec_sys_cmd(_cmd)
        if _code != 0:
            raise RuntimeError('exec cmd [%s] error[%d]: %s' % (_cmd, _code, '\n'.join(_cmd_info)))

        # mFocusedActivity: ActivityRecord{e903df8 u0 com.ss.android.ugc.aweme/.splash.SplashActivity t172}
        _findstr = 'ActivityRecord{'
        _temp = _cmd_info[0][_cmd_info[0].find(_findstr) + len(_findstr):].split(' ')
        _activity = _temp[2][_temp[2].find('/') + 1:].rstrip(',')

        return _activity

    def start_activity(self, app_package, app_activity, **opts):
        """
        通过提供包名和Activity名来启动一个Android Activity

        @param {str} app_package - 包名, 例如 "com.example"
        @param {str} app_activity - Activity名
        @param {kwargs} opts - 其他启动参数
            参考：https://www.kancloud.cn/testerhome/appium_docs_cn/2001714

        @return {appium.webdriver.extensions.android.activities.Activities} - 返回Android Activity对象
        """
        return self.driver.start_activity(app_package, app_activity, **opts)

    def wait_activity(self, app_activity: str, timeout: float, interval: float = 1) -> bool:
        """
        等待指定的activity出现直到超时

        @param {str} app_activity - 要等待的页面Activity
        @param {float} timeout - 最大等待超时时间，单位为秒
        @param {float} interval=1 - 每次检查间隔时间，单位为秒

        @returns {bool} - 等到到页面返回true
        """
        return self.driver.wait_activity(app_activity, timeout, interval=interval)

    def wait_activity_adb(self, app_activity: str, timeout: float, interval: float = 1) -> bool:
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

    #############################
    # 动作 - 输入
    #############################
    def adb_keycode(self, key_code, *args):
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
            _cmd = '%s -s %s shell input keyevent %s' % (
                self.adb_name, self._desired_caps['deviceName'], str(_key_code)
            )
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

            _cmd = '%s -s %s shell input keyevent %s' % (
                self.adb_name, self._desired_caps['deviceName'], ' '.join(_key_list)
            )

        # 执行发送
        _code, _cmd_info = self._exec_sys_cmd(_cmd)
        if _code != 0:
            raise RuntimeError('exec cmd [%s] error[%d]: %s' % (_cmd, _code, '\n'.join(_cmd_info)))

    def adb_get_default_ime(self) -> str:
        """
        获取手机当前默认输入法

        @returns {str} - 输入法
        """
        _cmd = '%s -s %s shell settings get secure default_input_method' % (
            self.adb_name, self._desired_caps['deviceName']
        )
        _code, _cmd_info = self._exec_sys_cmd(_cmd)
        if _code != 0 and _cmd_info[0].startswith('Error'):
            raise RuntimeError('exec cmd [%s] error[%d]: %s' % (_cmd, _code, '\n'.join(_cmd_info)))

        # 返回输入法
        return _cmd_info[0]

    def adb_set_default_ime(self, ime):
        """
        设置输入法

        @param {str} ime - 要设置的输入法
        """
        _cmd = '%s -s %s shell ime set %s' % (
            self.adb_name, self._desired_caps['deviceName'], ime
        )
        _code, _cmd_info = self._exec_sys_cmd(_cmd)
        if _code != 0 and not _cmd_info[0].startswith('Input method'):
            raise RuntimeError('exec cmd [%s] error[%d]: %s' % (_cmd, _code, '\n'.join(_cmd_info)))

    def adb_set_first_ime(self):
        """
        设置手机的输入法为输入法列表的第一个输入法
        """
        # 查找手机输入法清单
        _cmd = '%s -s %s shell ime list -a' % (
            self.adb_name, self._desired_caps['deviceName']
        )
        _code, _cmd_info = self._exec_sys_cmd(_cmd)
        if _code != 0 and _cmd_info[0].startswith('Error'):
            raise RuntimeError('exec cmd [%s] error[%d]: %s' % (_cmd, _code, '\n'.join(_cmd_info)))

        _ime = _cmd_info[0][0: -1]  # 去掉最后一个分号

        # 切换输入法
        self.adb_keyboard_set_ime(_ime)

    def adb_set_adbime(self):
        """
        设置 ADBKeyBoard 为默认输入法
        (不支持Appium自带的send_keys)
        """
        _cmd = '%s -s %s shell ime set com.android.adbkeyboard/.AdbIME' % (
            self.adb_name, self._desired_caps['deviceName']
        )
        _code, _cmd_info = self._exec_sys_cmd(_cmd)
        if _code != 0 and not _cmd_info[0].startswith('Input method'):
            raise RuntimeError('exec cmd [%s] error[%d]: %s' % (_cmd, _code, '\n'.join(_cmd_info)))

    def adb_set_appium_ime(self):
        """
        设置 Appium UnicodeIME 为默认输入法
        (支持Appium自带的send_keys)
        """
        _cmd = '%s -s %s shell ime set io.appium.settings/.UnicodeIME' % (
            self.adb_name, self._desired_caps['deviceName']
        )
        _code, _cmd_info = self._exec_sys_cmd(_cmd)
        if _code != 0 and not _cmd_info[0].startswith('Input method'):
            raise RuntimeError('exec cmd [%s] error[%d]: %s' % (_cmd, _code, '\n'.join(_cmd_info)))

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
            _cmd = '%s -s %s shell am broadcast -a ADB_INPUT_B64 --es msg %s' % (
                self.adb_name, self._desired_caps['deviceName'], _charsb64
            )
        else:
            _cmd = '%s -s %s shell am broadcast -a ADB_INPUT_TEXT --es msg \'%s\'' % (
                self.adb_name, self._desired_caps['deviceName'], _chars
            )

        # 执行发送
        _code, _cmd_info = self._exec_sys_cmd(_cmd)
        if _code != 0 and _cmd_info[1].strip() != 'Broadcast completed: result=0':
            raise RuntimeError('exec cmd [%s] error[%d]: %s' % (_cmd, _code, '\n'.join(_cmd_info)))

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
            _cmd = '%s -s %s shell am broadcast -a ADB_EDITOR_CODE --ei code %s' % (
                self.adb_name, self._desired_caps['deviceName'], str(_key_code)
            )
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

            _cmd = '%s -s %s shell am broadcast -a ADB_INPUT_MCODE --eia mcode \'%s\'' % (
                self.adb_name, self._desired_caps['deviceName'], ','.join(_key_list)
            )

        # 执行发送
        _code, _cmd_info = self._exec_sys_cmd(_cmd)
        if _code != 0 and _cmd_info[1].strip() != 'Broadcast completed: result=0':
            raise RuntimeError('exec cmd [%s] error[%d]: %s' % (_cmd, _code, '\n'.join(_cmd_info)))

    def adb_keyboard_clear(self):
        """
        使用 ADBKeyBoard 清除输入内容
        """
        _cmd = '%s -s %s shell am broadcast -a ADB_CLEAR_TEXT' % (
            self.adb_name, self._desired_caps['deviceName']
        )
        _code, _cmd_info = self._exec_sys_cmd(_cmd)
        if _code != 0 and _cmd_info[1].strip() != 'Broadcast completed: result=0':
            raise RuntimeError('exec cmd [%s] error[%d]: %s' % (_cmd, _code, '\n'.join(_cmd_info)))

    #############################
    # 动作 - 点击
    #############################

    def tap_adb(self, x: int = None, y: int = None, count: int = 1, **kwargs):
        """
        点击指定位置

        @param {int} x=None - 要点击的x位置，如果不传默认为屏幕宽度中间
        @param {int} y=None - 要点击的y位置，如果不传默认为屏幕高度中间
        @param {int} count=1 - 点击的次数
        """
        _cmd_mode = '%s -s %s shell input tap' % (self.adb_name, self._desired_caps['deviceName'])
        _cmd_list = list()
        for i in range(count):
            _cmd_list.append('%s %d %d' % (_cmd_mode, x, y))
        _cmd = ' && '.join(_cmd_list)
        _code, _cmd_info = self._exec_sys_cmd(_cmd)
        if _code != 0:
            raise RuntimeError('exec cmd [%s] error[%d]: %s' % (_cmd, _code, '\n'.join(_cmd_info)))

    def tap_adb_continuity(self, pos_seed: list, times: float, thread_count: int = 2,
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
        _cmd_mode = '%s -s %s shell input tap' % (self.adb_name, self._desired_caps['deviceName'])
        _seed_len = len(pos_seed)

        # 定义点击线程函数
        def tap_thread_fun():
            while True:
                # 循环处理，自身不结束
                _pos = pos_seed[random.randint(0, _seed_len - 1)]
                _cmd = '%s %d %d' % (_cmd_mode, _pos[0], _pos[1])
                # 不检查结果
                _code, _cmd_info = self._exec_sys_cmd(_cmd)
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
            self.stop_thread(_thread)

    #############################
    # 动作 - 按键
    #############################
    @property
    def is_ime_active(self) -> bool:
        """
        是否有打开输入法

        @property {bool}
        """
        return self.driver.is_ime_active()

    #############################
    # 内部函数 - 结束线程
    #############################

    def _async_raise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def stop_thread(self, thread):
        self._async_raise(thread.ident, SystemExit)


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
