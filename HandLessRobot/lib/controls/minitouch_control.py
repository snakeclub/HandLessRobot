#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
通过minitouch控制手机触屏的控件
@module minitouch_control
@file minitouch_control.py
"""

import os
import sys
import math
import random
import socket
import threading
import logging
import time
import datetime
import traceback
from HiveNetLib.base_tools.run_tool import RunTool
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))
from HandLessRobot.lib.controls.adb_control import AdbTools


__MOUDLE__ = 'minitouch_control'  # 模块名
__DESCRIPT__ = u'通过minitouch控制手机触屏的控件'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2021.01.23'  # 发布日期


class MiniTouchConnection(object):
    """
    minitouch的socket连接对象
    """
    #############################
    # 构造函数
    #############################

    def __init__(self, host: str, port: str, buffer_size: int = 0, encoding: str = 'utf-8',
                 logger=None):
        """
        进行MiniTouch的连接对象

        @param {str} host - 要连接的host地址，例如 '127.0.0.1'
        @param {str} port - 要连接的映射端口，例如 1601
        @param {int} buffer_size=0 - 收取数据的socket缓存大小
        @param {str} encoding='utf-8' - socket传输数据编码
        @param {Logger} logger=None - 日志对象
        """
        # 参数处理
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.encoding = encoding
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger()

        # 连接连接客户端
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.host, self.port))
        self.client = client

        # 获取连接的minitouch的信息
        socket_out = client.makefile()

        # v <version>
        # protocol version, usually it is 1. needn't use this
        self.version = socket_out.readline()

        # 获取设备信息
        # ^ <max-contacts> <max-x> <max-y> <max-pressure>
        _, max_contacts, max_x, max_y, max_pressure, *_ = (
            socket_out.readline().replace("\n", "").replace("\r", "").split(" ")
        )
        self.max_contacts = max_contacts  # 支持最大触点数量
        self.max_x = max_x  # 最大点击的x范围
        self.max_y = max_y  # 最大点击的y范围
        self.max_pressure = max_pressure  # 支持最大的压力值

        # 获取minitouch服务在设备上的pid
        # $ <pid>
        _, pid = socket_out.readline().replace("\n", "").replace("\r", "").split(" ")
        self.pid = pid

        self.logger.debug(
            "minitouch running on port: {}, pid: {}".format(self.port, self.pid)
        )
        self.logger.debug(
            "max_contact: {}; max_x: {}; max_y: {}; max_pressure: {}".format(
                max_contacts, max_x, max_y, max_pressure
            )
        )

    def disconnect(self):
        """
        断开连接
        """
        if self.client:
            self.client.close()
        self.client = None
        self.logger.debug("minitouch disconnected")

    def send(self, content: str):
        """
        发送信息并获取回复信息

        @param {str} content - 要发送的信息

        @returns {} - 返回的信息
        """
        # 转换为二进制
        byte_content = content.encode(self.encoding)
        self.client.sendall(byte_content)
        return self.client.recv(self.buffer_size)


class MiniTouchServer(object):
    """
    minitouch服务, 支持多台手机操作
    """

    #############################
    # 工具函数
    #############################
    @classmethod
    def init_device_server(cls, device_name: str, shared_path: str, adb_name: str = 'adb',
                           shell_encoding: str = None):
        """
        初始化设备上的服务文件

        @param {str} device_name - 设备名
        @param {str} shared_path - 预编译的minitouch文件所在路径，该路径下文件应按该目录结构存放:
            shared_path/stf_libs/{abi}/minitouch
            其中{abi}为设备的cpu架构, 例如 arm64-v8a
        @param {str} adb_name='adb' - adb命令名
        @param {str} shell_encoding=None - shell的编码
        """
        # 检查sdk版本和cpu架构
        _cpu = AdbTools.adb_run(
            adb_name, device_name, 'shell getprop ro.product.cpu.abi', shell_encoding=shell_encoding
        )[0]
        _sdk = AdbTools.adb_run(
            adb_name, device_name, 'shell getprop ro.build.version.sdk', shell_encoding=shell_encoding
        )[0]

        # sdk小于16的版本要用nopie版本
        _minitouch_file = 'minitouch' if int(_sdk) >= 16 else 'minitouch-nopie'
        if not AdbTools.adb_file_exists(
            adb_name, device_name, '/data/local/tmp/%s' % _minitouch_file, shell_encoding=shell_encoding
        ):
            # 推送相应文件到设备
            AdbTools.adb_run(
                adb_name, device_name, 'push %s /data/local/tmp' % os.path.join(
                    shared_path, 'stf_libs', _cpu, _minitouch_file
                ), shell_encoding=shell_encoding
            )
            # 授权
            AdbTools.adb_run(
                adb_name, device_name, 'shell chmod 777 /data/local/tmp/%s' % _minitouch_file,
                shell_encoding=shell_encoding
            )

    #############################
    # 构造函数
    #############################

    def __init__(self, adb_name: str = 'adb', foward_port_start: int = 1601, foward_port_end: int = 1699,
                 shell_encoding: str = None, buffer_size: int = 0, encoding: str = 'utf-8',
                 start_wait_time: float = 1.0, status_callback=None, logger=None,
                 **kwargs):
        """
        minitouch服务

        @param {str} adb_name='adb' - adb命令名
        @param {int} foward_port_start=1601 - 设备服务映射端口范围开始
        @param {int} foward_port_end=1699 - 设备服务映射端口范围结束
        @param {str} shell_encoding=None - shell的编码
        @param {int} buffer_size=0 - 收取数据的socket缓存大小
        @param {str} encoding='utf-8' - socket传输数据编码
        @param {float} start_wait_time=1.0 - 等待服务启动时长, 如果设备较差时间可以设长
        @param {function} status_callback=None - 当指定设备服务状态发生变化时执行的回调函数
            callback(device_name, status, msg) : 其中status可能传入stop/error两种状态
        @param {Logger} logger - 日志对象
        """
        # 参数
        self.adb_name = adb_name
        self.foward_port_start = foward_port_start
        self.foward_port_end = foward_port_end
        self.shell_encoding = shell_encoding
        self.start_wait_time = start_wait_time
        self.buffer_size = buffer_size
        self.encoding = encoding
        self.status_callback = status_callback
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger()

        # 端口资源处理
        self.minitouch_ports = list(range(
            self.foward_port_start, self.foward_port_end + 1
        ))

        # 已加载的设备清单, key为设备名, value为信息字典
        # port {int} - 映射的端口
        # minitouch_file {str} - minitouch的文件名
        # server_thread {Thread} - 启动设备服务的线程
        # stop_var {list} - 控制停止设备服务后台进程的变量
        # connection {} - 连接对象
        self.devices = dict()

    #############################
    # 执行minitouch命令
    #############################
    def publish_cmd(self, devices: list, cmd_builder):
        """
        执行命令

        @param {list} devices - 设备清单
        @param {MiniTouchCmdBuilder} cmd_builder - 要执行的命令创建对象
        """
        # 生成设备连接清单
        _connections = list()
        for _device_name in devices:
            _connection = self.devices.get(_device_name, {}).get('connection', None)
            if _connection is not None:
                _connections.append(_connection)

        # 执行命令
        cmd_builder.publish(_connections)

    #############################
    # 屏幕点击操作
    #############################
    def tap(self, devices: list, x: int = None, y: int = None, count: int = 1,
            duration: int = 10, pressure: int = 50):
        """
        点击指定位置

        @param {list} devices - 设备清单
        @param {int} x=None - 要点击的x位置，如果不传默认为屏幕宽度中间
        @param {int} y=None - 要点击的y位置，如果不传默认为屏幕高度中间
        @param {int} count=1 - 点击的次数
        @param {int} pressure=50 - 按下的压力
        """
        _builder = MiniTouchCmdBuilder(default_delay=0.0, logger=self.logger)
        # 从第一个设备获取设备信息
        _conn = self.devices[devices[0]]['connection']
        _pressure = min(pressure, int(_conn.max_pressure))
        _size = (int(_conn.max_x), int(_conn.max_y))

        # 计算点击位置
        if x is None or y is None:
            _w, _h = _size
        if x is None:
            x = math.ceil(_w / 2.0)
        if y is None:
            y = math.ceil(_h / 2.0)

        _wait = 0
        if duration > 0:
            _wait = math.ceil((duration / count) / 2)

        for i in range(count):
            _builder.down(0, x, y, _pressure)
            if _wait > 0:
                _builder.wait(_wait)
            _builder.commit()
            _builder.up(0)
            _builder.wait(_wait)
            _builder.commit()

        # 执行操作
        self.publish_cmd(devices, _builder)

    def tap_continuity(self, devices: list, pos_seed: list, times: float, thread_count: int = 2,
                       random_sleep: bool = False, sleep_min: float = 0.0, sleep_max: float = 0.5,
                       pressure: int = 50):
        """
        在指定范围随机连续点击

        @param {list} devices - 设备清单
        @param {list} pos_seed - 允许点击的位置坐标清单[(x,y), ...], 随机获取
        @param {float} times - 要点击的时长, 单位为秒
        @param {bool} random_sleep=False - 两个点击间是否自动休眠指定时长
        @param {float} sleep_min=0.0 - 两个点击间自动休眠最小时长, 单位为秒
        @param {float} sleep_max=0.5 - 两个点击间自动休眠最大时长, 单位为秒
        @param {int} pressure=50 - 按下的压力
        """
        # 从第一个设备获取设备信息
        _conn = self.devices[devices[0]]['connection']
        _pressure = min(pressure, int(_conn.max_pressure))

        # 参数准备
        _seed_len = len(pos_seed)

        # 定义点击线程函数
        def tap_thread_fun(device_name):
            while True:
                # 循环处理，自身不结束
                _pos = pos_seed[random.randint(0, _seed_len - 1)]
                self.tap(
                    [device_name, ], x=_pos[0], y=_pos[1], count=1, duration=10,
                    pressure=_pressure
                )

                # 看是否休眠
                if random_sleep:
                    time.sleep(random.uniform(sleep_min, sleep_max))

        # 启动执行动作
        _start = datetime.datetime.now()
        _thread_list = list()
        for _device_name in devices:
            _running_thread = threading.Thread(
                target=tap_thread_fun,
                name='Thread-Tap-Running-%s' % _device_name,
                args=(_device_name, )
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

    def long_press(self, devices: list, x: int = None, y: int = None,
                   duration: int = 1000, pressure: int = 50):
        """
        在指定位置长按

        @param {list} devices - 设备清单
        @param {int} x=None - 要点击的x位置，如果不传默认为屏幕宽度中间
        @param {int} y=None - 要点击的y位置，如果不传默认为屏幕高度中间
        @param {int} duration=1000 - 经历时长，单位为毫秒
        @param {int} pressure=50 - 按下的压力
        """
        _builder = MiniTouchCmdBuilder(default_delay=0.0, logger=self.logger)
        # 从第一个设备获取设备信息
        _conn = self.devices[devices[0]]['connection']
        _pressure = min(pressure, int(_conn.max_pressure))
        _size = (int(_conn.max_x), int(_conn.max_y))

        if x is None or y is None:
            _w, _h = _size
        if x is None:
            x = math.ceil(_w / 2.0)
        if y is None:
            y = math.ceil(_h / 2.0)

        _builder.down(0, x, y, _pressure)
        _builder.wait(duration)
        _builder.commit()
        _builder.up(0)
        _builder.commit()

        # 执行操作
        self.publish_cmd(devices, _builder)

    #############################
    # 屏幕滑动操作
    #############################
    def swipe(self, devices: list, points: list, duration: int = 0, pressure: int = 50,
              smooth_step: int = 0, with_down: bool = True, with_up: bool = True):
        """
        执行两点之间的滑动

        @param {list} devices - 设备清单
        @param {list} points - 滑动经过的点
        @param {int} duration=0 - 滑动经历全时长，单位为毫秒
        @param {int} pressure=50 - 按下的压力
        @param {int} smooth_step=0 - 插值让滑动平滑的步长
            值 <= 0 - 不进行插值，直接按点滑动
            值 > 0 - 两点间距离按步长插值
        @param {bool} with_down=True - 是否包含按下动作
        @param {bool} with_up=True - 是否包含释放动作
        """
        _builder = MiniTouchCmdBuilder(default_delay=0.0, logger=self.logger)

        # 从第一个设备获取设备信息
        _conn = self.devices[devices[0]]['connection']
        _pressure = min(pressure, int(_conn.max_pressure))

        # 计算平滑模式的插入点
        _points = []
        if smooth_step <= 0:
            _points = points
        else:
            _points.append(points[0])
            for i in range(1, len(points)):
                _cur_point = points[i - 1]
                _next_point = points[i]

                # 求距离
                _distance = abs(math.sqrt(
                    (_next_point[0] - _cur_point[0])**2 + (_next_point[1] - _cur_point[1])**2
                ))

                # 计算要插入的点数, 不足一个位置的不增加插入点
                _split_count = math.ceil(_distance / smooth_step)
                if _split_count > 1:
                    _x_step = (_next_point[0] - _cur_point[0]) / _split_count
                    _y_step = (_next_point[1] - _cur_point[1]) / _split_count
                    for j in range(_split_count - 1):
                        _points.append((
                            math.ceil(_cur_point[0] + _x_step * (j + 1)),
                            math.ceil(_cur_point[1] + _y_step * (j + 1))
                        ))

                # 插入结尾的点
                _points.append(_next_point)

        # 计算延迟时长
        _wait = 0
        if duration > 0:
            _wait = math.ceil(
                duration / (len(_points) - 1)
            )

        if with_down:
            _builder.down(0, _points[0][0], _points[0][1], _pressure)
            _builder.commit()

        for _pos in _points:
            _builder.move(0, _pos[0], _pos[1], _pressure)
            if _wait > 0:
                _builder.wait(_wait)
            _builder.commit()

        if with_up:
            _builder.up(0)
            _builder.commit()

        # 执行操作
        self.publish_cmd(devices, _builder)

    def swipe_up(self, devices: list, x: int = None, y: int = None, swipe_len: int = None,
                 duration: int = 0, pressure: int = 50, smooth_step: int = 0):
        """
        向上滑动

        @param {list} devices - 设备清单
        @param {int} x=None - 滑动开始所在x坐标，不传代表在屏幕横向正中间位置
        @param {int} y=None - 滑动开始所在y坐标，不传代表在屏幕纵向正中间下方距离swipe_len一半的位置
        @param {int} swipe_len=None - 滑动的距离，不传默认为1/3屏幕高度
        @param {int} duration=0 - 滑动经历时长，单位为毫秒
        @param {int} pressure=50 - 按下的压力
        @param {int} smooth_step=0 - 插值让滑动平滑的步长
            值 <= 0 - 不进行插值，直接按点滑动
            值 > 0 - 两点间距离按步长插值
        """
        # 从第一个设备获取设备信息
        _conn = self.devices[devices[0]]['connection']
        _w = int(_conn.max_x)
        _h = int(_conn.max_y)

        # 计算滑动参数
        if x is None:
            x = math.ceil(_w / 2.0)
        if swipe_len is None:
            swipe_len = math.ceil(_h / 3.0)
        if y is None:
            y = min(math.ceil(_h / 2.0 + swipe_len / 2.0), _h)

        # 执行滑动处理
        self.swipe(
            devices, [(x, y), (x, max(y - swipe_len, 0))], duration=duration,
            pressure=pressure, smooth_step=smooth_step
        )

    def swipe_down(self, devices: list, x: int = None, y: int = None, swipe_len: int = None,
                   duration: int = 0, pressure: int = 50, smooth_step: int = 0):
        """
        向下滑动

        @param {list} devices - 设备清单
        @param {int} x=None - 滑动开始所在x坐标，不传代表在屏幕横向正中间位置
        @param {int} y=None - 滑动开始所在y坐标，不传代表在屏幕纵向正中间上方距离swipe_len一半的位置
        @param {int} swipe_len=None - 滑动的距离，不传默认为1/3屏幕高度
        @param {int} duration=0 - 滑动经历时长，单位为毫秒
        @param {int} pressure=50 - 按下的压力
        @param {int} smooth_step=0 - 插值让滑动平滑的步长
            值 <= 0 - 不进行插值，直接按点滑动
            值 > 0 - 两点间距离按步长插值
        """
        # 从第一个设备获取设备信息
        _conn = self.devices[devices[0]]['connection']
        _w = int(_conn.max_x)
        _h = int(_conn.max_y)

        # 计算滑动参数
        if x is None:
            x = math.ceil(_w / 2.0)
        if swipe_len is None:
            swipe_len = math.ceil(_h / 3.0)
        if y is None:
            y = max(math.ceil(_h / 2.0 - swipe_len / 2.0), 0)

        # 执行滑动处理
        self.swipe(
            devices, [(x, y), (x, min(y + swipe_len, _h))], duration=duration,
            pressure=pressure, smooth_step=smooth_step
        )

    def swipe_left(self, devices: list, x: int = None, y: int = None, swipe_len: int = None,
                   duration: int = 0, pressure: int = 50, smooth_step: int = 0):
        """
        向左滑动

        @param {list} devices - 设备清单
        @param {int} x=None - 滑动开始所在x坐标，不传代表在屏幕横向正中间右方距离swipe_len一半的位置
        @param {int} y=None - 滑动开始所在y坐标，不传代表在屏幕纵向正中间位置
        @param {int} swipe_len=None - 滑动的距离，不传默认为1/3屏幕宽度
        @param {int} duration=0 - 滑动经历时长，单位为毫秒
        @param {int} pressure=50 - 按下的压力
        @param {int} smooth_step=0 - 插值让滑动平滑的步长
            值 <= 0 - 不进行插值，直接按点滑动
            值 > 0 - 两点间距离按步长插值
        """
        # 从第一个设备获取设备信息
        _conn = self.devices[devices[0]]['connection']
        _w = int(_conn.max_x)
        _h = int(_conn.max_y)

        # 计算滑动参数
        if y is None:
            y = math.ceil(_h / 2.0)
        if swipe_len is None:
            swipe_len = math.ceil(_w / 3.0)
        if x is None:
            x = min(math.ceil(_w / 2.0 + swipe_len / 2.0), _w)

        # 执行滑动处理
        self.swipe(
            devices, [(x, y), (max(x - swipe_len, 0), y)], duration=duration,
            pressure=pressure, smooth_step=smooth_step
        )

    def swipe_right(self, devices: list, x: int = None, y: int = None, swipe_len: int = None,
                    duration: int = 0, pressure: int = 50, smooth_step: int = 0):
        """
        向左滑动

        @param {list} devices - 设备清单
        @param {int} x=None - 滑动开始所在x坐标，不传代表在屏幕横向正中间左方距离swipe_len一半的位置
        @param {int} y=None - 滑动开始所在y坐标，不传代表在屏幕纵向正中间位置
        @param {int} swipe_len=None - 滑动的距离，不传默认为1/3屏幕宽度
        @param {int} duration=0 - 滑动经历时长，单位为毫秒
        @param {int} pressure=50 - 按下的压力
        @param {int} smooth_step=0 - 插值让滑动平滑的步长
            值 <= 0 - 不进行插值，直接按点滑动
            值 > 0 - 两点间距离按步长插值
        """
        # 从第一个设备获取设备信息
        _conn = self.devices[devices[0]]['connection']
        _w = int(_conn.max_x)
        _h = int(_conn.max_y)

        # 计算滑动参数
        if y is None:
            y = math.ceil(_h / 2.0)
        if swipe_len is None:
            swipe_len = math.ceil(_w / 3.0)
        if x is None:
            x = max(math.ceil(_w / 2.0 - swipe_len / 2.0), 0)

        # 执行滑动处理
        self.swipe(
            devices, [(x, y), (min(x + swipe_len, _w), y)], duration=duration,
            pressure=pressure, smooth_step=smooth_step
        )

    #############################
    # 设备服务启停
    #############################

    def start_device_server(self, device_name: str) -> int:
        """
        启动设备的minitouch服务
        注：必须要先通过 init_device_server 对设备进行初始化处理

        @param {str} device_name - 设备号

        @param {int} - minitouch映射的监听端口
        """
        # 获取该设备使用的端口
        if device_name in self.devices.keys():
            # 未回收端口，继续复用
            _port = self.devices[device_name]['port']
        else:
            # 新申请端口
            _port = self.minitouch_ports.pop(0)

        # 添加到设备清单
        self.devices[device_name] = {
            'port': _port,
            'stop_var': [False, ],  # 控制停止的参数
        }

        # 执行处理
        try:
            # 获取设备minitouch版本
            _sdk = AdbTools.adb_run(
                self.adb_name, device_name, 'shell getprop ro.build.version.sdk',
                shell_encoding=self.shell_encoding
            )[0]
            self.devices[device_name]['minitouch_file'] = 'minitouch' if int(
                _sdk) >= 16 else 'minitouch-nopie'

            # 映射端口，映射前需要回收端口
            AdbTools.adb_run(
                self.adb_name, device_name, 'forward --remove tcp:%d' % _port,
                shell_encoding=self.shell_encoding, ignore_error=True
            )

            AdbTools.adb_run(
                self.adb_name, device_name, 'forward tcp:%d localabstract:minitouch' % _port,
                shell_encoding=self.shell_encoding
            )

            # 启动服务
            self._start_device_server(device_name)

            # 等待设备启动并检查状态
            time.sleep(self.start_wait_time)
            if self.devices[device_name].get('server_thread', None) is None:
                raise RuntimeError('server thread exited!')

            # 连接设备
            self.devices[device_name]['connection'] = MiniTouchConnection(
                '127.0.0.1', self.devices[device_name]['port'], buffer_size=self.buffer_size,
                encoding=self.encoding, logger=self.logger
            )
        except:
            # 出现异常代表失败，将端口放回列表
            self.stop_device_server(device_name)  # 先尝试关闭服务
            self.devices.pop(device_name, None)
            self.minitouch_ports.append(_port)
            self.logger.error(
                'start devices[%s] minitouch server error: %s' % (
                    device_name, traceback.format_exc()
                )
            )
            raise

        return _port

    def stop_device_server(self, device_name: str):
        """
        停止设备的minitouch服务（不清除端口）

        @param {str} device_name - 设备名
        """
        # 为后台线程送停止的参数
        self.devices[device_name]['stop_var'][0] = True

        # 获取minitouch进程id
        _pid = None
        _connection: MiniTouchConnection = self.devices[device_name].pop('connection', None)
        if _connection is not None:
            _pid = _connection.pid
            # 停止socket连接
            _connection.disconnect()
        else:
            # 通过adb shell查找进程id
            try:
                _cmd_info = AdbTools.adb_run(
                    self.adb_name, device_name, 'shell ps | %s %s' % (
                        'findstr' if sys.platform == 'win32' else 'grep',
                        self.devices[device_name]['minitouch_file']
                    ),
                    shell_encoding=self.shell_encoding
                )
                # shell        31976 31974 2169772   6832 __skb_wait_for_more_packets 0 S minicap
                _pid = _cmd_info[0][_cmd_info[0].find(' '):].strip().split(' ')[0]
            except:
                self.logger.warning(
                    'get device[%s] minitouch pid by adb error: %s' % (
                        device_name, traceback.format_exc()
                    )
                )

        # 结束进程
        if _pid is not None:
            AdbTools.adb_run(
                self.adb_name, device_name, 'shell kill %s' % _pid,
                shell_encoding=self.shell_encoding, ignore_error=True
            )

        # 等待线程结束
        while self.devices[device_name]['server_thread'] is not None:
            time.sleep(0.1)

    def remove_device(self, device_name: str):
        """
        移除设备

        @param {str} device_name - 设备号
        """
        # 结束服务
        self.stop_device_server(device_name)

        # 删除信息并归还端口
        _port = self.devices[device_name]['port']
        self.devices.pop(device_name, None)
        self.minitouch_ports.append(_port)

    #############################
    # 内部函数
    #############################
    def _start_device_server(self, device_name: str):
        """
        实际启动服务的函数

        @param {str} device_name - 设备号
        """
        if self.devices[device_name].get('server_thread', None) is not None:
            # 原线程仍存在，不创建新线程
            self.logger.warning(
                'the minitouch server of device [%s] exits, use older server!'
            )

        # 通过多线程启动控制
        self.devices[device_name]['server_thread'] = threading.Thread(
            target=self._minitouch_thread_fun,
            name='Thread-minitouch-%s-Running' % device_name,
            args=(device_name, )
        )
        self.devices[device_name]['server_thread'].setDaemon(True)
        self.devices[device_name]['server_thread'].start()

    def _minitouch_thread_fun(self, device_name):
        """
        minitouch服务线程

        @param {str} device_name - 设备名
        """
        # 通过启动新进程处理
        _cmd = '%s%s %s' % (
            self.adb_name,
            ' -s %s' % device_name if device_name != '' else '',
            'shell /data/local/tmp/%s' % self.devices[device_name]['minitouch_file']
        )

        # 执行命令
        self.logger.log(
            logging.DEBUG, 'exec sys cmd: %s' % _cmd
        )
        _exit_code, _cmd_info = RunTool.exec_sys_cmd_not_output(
            _cmd, shell_encoding=self.shell_encoding,
            stop_var=self.devices[device_name]['stop_var']
        )

        # 如果执行到这里，说明服务中止了
        _status = 'stop'
        _msg = ''
        if _exit_code != 0 and not self.devices[device_name]['stop_var'][0]:
            # 出现异常, 并且这个异常并不是由于关闭服务导致
            _status = 'error'
            _msg = '\n'.join(_cmd_info)
            self.logger.log(
                logging.ERROR, 'exec sys cmd [%s] error: %s' % (_cmd, _msg)
            )

        # 线程结束
        if device_name in self.devices.keys():
            self.devices[device_name]['server_thread'] = None

        # callback
        if self.status_callback is not None and _status != 'stop':
            # 非主动关闭的才执行callback
            try:
                self.status_callback(device_name, _status, _msg)
            except:
                self.logger.log(
                    logging.ERROR, 'execute status_callback error: %s' % traceback.format_exc()
                )


class MiniTouchCmdBuilder(object):
    """
    minitouch命令文本创建器

    @example 使用用例
        builder = MiniTouchCmdBuilder()
        builder.down(0, 400, 400, 50)
        builder.commit()
        builder.move(0, 500, 500, 50)
        builder.commit()
        builder.move(0, 800, 400, 50)
        builder.commit()
        builder.up(0)
        builder.commit()
        builder.publish(connection)
    """

    def __init__(self, default_delay: float = 0.05, logger=None):
        """
        minitouch命令文本创建器

        @param {float} default_delay=0.05 - 每次提交后默认等待的时长，单位为秒
        @param {Logger} logger=None - 日志对象
        """
        self._content = ""  # 最后生成的文本
        self._delay = 0  # 命令总共延时时长
        self.default_delay = default_delay
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger()

    def append(self, new_content):
        """
        添加新命令文本

        @param {str} new_content - minitouch格式的一个命令文本
        """
        self._content += new_content + "\n"

    def commit(self):
        """
        提交设备执行前面的输入命令
        minitouch命令: c
        """
        self.append("c")

    def wait(self, ms):
        """
        等待指定毫秒
        minitouch命令: w <ms>

        @param {float} ms - 要等待的时长，单位为毫秒
        """
        self.append("w {}".format(ms))
        self._delay += ms

    def up(self, contact_id: int = 0):
        """
        手指离开屏幕
        minitouch命令: u <contact_id>

        @param {int} contact_id=0 - 关联动作id
        """
        self.append("u {}".format(contact_id))

    def down(self, contact_id, x, y, pressure):
        """
        压下手指
        minitouch命令: d <contact_id> <x> <y> <pressure>

        @param {int} contact_id - 关联动作id
        @param {int} x - x坐标
        @param {int} y - y坐标
        @param {int} pressure - 压力值，例如100
        """
        self.append("d {} {} {} {}".format(contact_id, x, y, pressure))

    def move(self, contact_id, x, y, pressure):
        """
        移动手指
        minitouch命令: m <contact_id> <x> <y> <pressure>

        @param {int} contact_id - 关联动作id
        @param {int} x - x坐标
        @param {int} y - y坐标
        @param {int} pressure - 压力值，例如100
        """
        """ add minitouch command: 'm <contact_id> <x> <y> <pressure>\n' """
        self.append("m {} {} {} {}".format(contact_id, x, y, pressure))

    def publish(self, connection):
        """
        提交当前指令并发送给设备

        @param {MiniTouchConnection|list} connection - 已连接设备的socket连接
            注: 如果传入的时列表，则代表发给多个设备
        """
        self.commit()
        final_content = self._content
        self.logger.debug("send operation: {}".format(final_content.replace("\n", "\\n")))
        if type(connection) == list:
            # 发送给多个设备，忽略异常
            try:
                for _connection in connection:
                    _connection.send(final_content)
            except:
                pass
        else:
            # 单个设备发送
            connection.send(final_content)
        time.sleep(self._delay / 1000 + self.default_delay)
        self.reset()

    def reset(self):
        """
        清空所有命令及缓存
        """
        self._content = ""
        self._delay = 0


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
