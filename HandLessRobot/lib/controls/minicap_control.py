#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
使用minicap的屏幕同步控件
@module minicap_control
@file minicap_control.py
"""

import os
import sys
import time
import copy
import math
import threading
import traceback
import logging
from HiveNetLib.base_tools.run_tool import RunTool
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))
from HandLessRobot.lib.controls.adb_control import AdbTools


__MOUDLE__ = 'minicap_control'  # 模块名
__DESCRIPT__ = u'使用minicap的屏幕同步控件'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2021.01.24'  # 发布日期


class MiniCapServer(object):
    """
    minicap服务, 支持多台手机屏幕同步
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
        @param {str} shared_path - 预编译的minicap文件所在路径，该路径下文件应按该目录结构存放:
            shared_path/stf_libs/{abi}/minicap
            shared_path/stf_libs/minicap-shared/aosp/libs/android-{sdk}/{abi}/minicap.so
            其中{abi}为设备的cpu架构, 例如 arm64-v8a
            {sdk} 为设备的安卓版本号, 例如 23
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
        _minicap_file = 'minicap' if int(_sdk) >= 16 else 'minicap-nopie'
        if not AdbTools.adb_file_exists(
            adb_name, device_name, '/data/local/tmp/minicap.so', shell_encoding=shell_encoding
        ):
            # 推送相应文件到设备
            AdbTools.adb_run(
                adb_name, device_name, 'push %s /data/local/tmp' % os.path.join(
                    shared_path, 'stf_libs', _cpu,
                    _minicap_file
                )
            )
            AdbTools.adb_run(
                adb_name, device_name, 'push %s /data/local/tmp' % os.path.join(
                    shared_path,
                    'stf_libs/minicap-shared/aosp/libs/android-%s/%s' % (_sdk, _cpu),
                    'minicap.so'
                )
            )

            # 授权
            AdbTools.adb_run(
                adb_name, device_name, 'shell chmod 777 /data/local/tmp/%s' % _minicap_file,
                shell_encoding=shell_encoding
            )
            AdbTools.adb_run(
                adb_name, device_name, 'shell chmod 777 /data/local/tmp/minicap.so',
                shell_encoding=shell_encoding
            )

    @classmethod
    def get_screen_wm(cls, device_name: str, adb_name: str = 'adb',
                      shell_encoding: str = None) -> tuple:
        """
        获取设备屏幕大小

        @param {str} device_name - 设备名
        @param {str} adb_name='adb' - adb命令名
        @param {str} shell_encoding=None - shell的编码

        @returns {tuple} - 设备屏幕大小，width, height
        """
        _cmd_info = AdbTools.adb_run(
            adb_name, device_name, 'shell wm size',
            shell_encoding=shell_encoding
        )
        _size_str = _cmd_info[0].split(':')[1].strip().split('x')
        return int(_size_str[0]), int(_size_str[1])

    def get_show_size(self, real_size: tuple, show_size: tuple) -> tuple:
        """
        获取设备显示大小

        @param {tuple} real_size - 真实设备屏幕大小
        @param {tuple} show_size - 显示屏幕大小

        @returns {tuple} - 返回实际显示大小
        """
        _width = show_size[0]
        _height = show_size[1]

        # 看是否锁定比例
        if self.lock_scale:
            if self.lock_by == 'height':
                # 根据高度比例处理
                _width = math.ceil(real_size[0] * (_height / real_size[1]))
            else:
                # 根据宽度比例处理
                _height = math.ceil(real_size[1] * (_width / real_size[0]))

        # 返回结果
        return _width, _height

    #############################
    # 构造函数
    #############################

    def __init__(self, adb_name: str = 'adb', webserver_port: int = 9002,
                 foward_port_start: int = 1701, foward_port_end: int = 1799,
                 shell_encoding: str = None, lock_scale: bool = True, lock_by: str = 'width',
                 start_wait_time: float = 1.0, status_callback=None, logger=None,
                 **kwargs):
        """
        minicap服务

        @param {str} adb_name='adb' - adb命令名
        @param {int} webserver_port=9002 - webserver监听端口
        @param {int} foward_port_start=1601 - 设备服务映射端口范围开始
        @param {int} foward_port_end=1699 - 设备服务映射端口范围结束
        @param {str} shell_encoding=None - shell的编码
        @param {bool} lock_scale=True - 锁定比例变形比例
        @param {str} lock_by='width' - 按宽还是高锁定变形比例, 默认按宽
        @param {float} start_wait_time=1.0 - 等待服务启动时长, 如果设备较差时间可以设长
        @param {function} status_callback=None - 当指定设备服务状态发生变化时执行的回调函数
            callback(device_name, status, msg) : 其中status可能传入stop/error两种状态
        @param {Logger} logger - 日志对象
        """
        # 参数
        self.adb_name = adb_name
        self.webserver_port = webserver_port
        self.foward_port_start = foward_port_start
        self.foward_port_end = foward_port_end
        self.shell_encoding = shell_encoding
        self.start_wait_time = start_wait_time
        self.lock_scale = lock_scale
        self.lock_by = lock_by
        self.status_callback = status_callback
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger()

        # 端口资源处理
        self.minicap_ports = list(range(
            self.foward_port_start, self.foward_port_end + 1
        ))

        # 网络服务器线程
        self.webserver_thread = None
        self.webserver_stop_var = [False, ]

        # 已加载的设备清单, key为设备名, value为信息字典
        # port {int} - 映射的端口
        # minicap_file {str} - minicap的文件名
        # server_thread {Thread} - 启动设备服务的线程
        # stop_var {list} - 控制停止设备服务后台进程的变量
        # connection {} - 连接对象
        self.devices = dict()

    #############################
    # Web服务启停
    #############################
    def start_webserver(self):
        """
        启动 minicap 的 node 服务
        注：必须要部署好依赖的 node.js 环境
        """
        if self.webserver_thread is not None:
            raise RuntimeError('minicap web server is running!')

        self.webserver_stop_var[0] = False  # 不暂停

        self.webserver_thread = threading.Thread(
            target=self._webserver_thread_fun,
            name='Thread-minicap-server-Running'
        )
        self.webserver_thread.setDaemon(True)
        self.webserver_thread.start()

    def stop_webserver(self):
        """
        结束minicap服务
        """
        self.webserver_stop_var[0] = True
        while self.webserver_thread is not None:
            # 等待线程结束
            time.sleep(0.1)

    #############################
    # 设备服务启停
    #############################

    def start_device_server(self, device_name: str, show_size: tuple = None, canvas_size: tuple = None,
                            orientation: int = 0, quality: int = 80) -> int:
        """
        启动设备的minicap服务
        注：必须要先通过 init_device_server 对设备进行初始化处理

        @param {str} device_name - 设备号
        @param {tuple} show_size=None - 显示大小，(宽, 高)，默认原生大小
        @param {tuple} canvas_size=None - 画布大小，(宽, 高)，默认原生大小
        @param {int} orientation=0 - 手机旋转角度，支持 0 | 90 | 180 | 270
        @param {int} quality=80 - 视频质量，可设置0-100，降低视频质量可提高性能

        @param {dict} - 返回设备信息
        """
        # 获取该设备使用的端口
        if device_name in self.devices.keys():
            # 未回收端口，继续复用
            _port = self.devices[device_name]['port']
        else:
            # 新申请端口
            _port = self.minicap_ports.pop(0)

        # 处理显示大小
        _real_size = self.get_screen_wm(
            device_name, adb_name=self.adb_name, shell_encoding=self.shell_encoding
        )
        _show_size = show_size
        if show_size is None:
            _show_size = copy.deepcopy(_real_size)
        else:
            _show_size = self.get_show_size(
                _real_size, _show_size
            )

        # 处理画布大小
        _canvas_size = canvas_size
        if canvas_size is None:
            _canvas_size = copy.deepcopy(_real_size)
        else:
            _canvas_size = self.get_show_size(
                _real_size, _canvas_size
            )

        # 添加到设备清单
        self.devices[device_name] = {
            'port': _port,
            'stop_var': [False, ],  # 控制停止的参数
            'real_size': _real_size,
            'orientation': orientation,
            'quality': quality,
            'show_size': _show_size,
            'canvas_size': _canvas_size,
        }

        # 执行处理
        try:
            # 获取设备minicap版本
            _sdk = AdbTools.adb_run(
                self.adb_name, device_name, 'shell getprop ro.build.version.sdk',
                shell_encoding=self.shell_encoding
            )[0]
            self.devices[device_name]['minicap_file'] = 'minicap' if int(
                _sdk) >= 16 else 'minicap-nopie'

            # 映射端口，映射前需要回收端口
            AdbTools.adb_run(
                self.adb_name, device_name, 'forward --remove tcp:%d' % _port,
                shell_encoding=self.shell_encoding, ignore_error=True
            )

            AdbTools.adb_run(
                self.adb_name, device_name, 'forward tcp:%d localabstract:minicap' % _port,
                shell_encoding=self.shell_encoding
            )

            # 启动服务
            self._start_device_server(device_name)

            # 等待设备启动并检查状态
            time.sleep(self.start_wait_time)
            if self.devices[device_name].get('server_thread', None) is None:
                raise RuntimeError('server thread exited!')
        except:
            # 出现异常代表失败，将端口放回列表
            self.stop_device_server(device_name)  # 先尝试关闭服务
            self.devices.pop(device_name, None)
            self.minicap_ports.append(_port)
            self.logger.error(
                'start devices[%s] minicap server error: %s' % (
                    device_name, traceback.format_exc()
                )
            )
            raise

        return self.devices[device_name]

    def stop_device_server(self, device_name: str):
        """
        停止设备的minicap服务（不清除端口）

        @param {str} device_name - 设备名
        """
        # 为后台线程送停止的参数
        self.devices[device_name]['stop_var'][0] = True

        # 获取minicap进程id
        _pid = None
        try:
            _cmd_info = AdbTools.adb_run(
                self.adb_name, device_name, 'shell ps | %s %s' % (
                    'findstr' if sys.platform == 'win32' else 'grep',
                    self.devices[device_name]['minicap_file']
                ),
                shell_encoding=self.shell_encoding
            )
            # shell        31976 31974 2169772   6832 __skb_wait_for_more_packets 0 S minicap
            _pid = _cmd_info[0][_cmd_info[0].find(' '):].strip().split(' ')[0]
        except:
            self.logger.warning(
                'get device[%s] minicap pid by adb error: %s' % (
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
        self.minicap_ports.append(_port)

    #############################
    # 内部函数
    #############################

    def _webserver_thread_fun(self):
        """
        minicap服务线程函数
        """
        _server_file = os.path.join(
            os.path.dirname(__file__), 'minicap_node_server.js'
        )
        _cmd = 'node %s -p %d' % (
            _server_file, self.webserver_port
        )

        self.logger.log(
            logging.INFO, 'exec sys cmd: %s' % _cmd
        )
        _exit_code, _cmd_info = RunTool.exec_sys_cmd_not_output(
            _cmd, stop_var=self.webserver_stop_var
        )

        if _exit_code != 0:
            # 出现异常
            self.logger.log(
                logging.ERROR, 'exec sys cmd [%s] error: %s' % (_cmd, '\n'.join(_cmd_info))
            )

        # 将线程置空
        self.webserver_thread = None

    def _start_device_server(self, device_name: str):
        """
        实际启动服务的函数

        @param {str} device_name - 设备号
        """
        if self.devices[device_name].get('server_thread', None) is not None:
            # 原线程仍存在，不创建新线程
            self.logger.warning(
                'the minicap server of device [%s] exits, use older server!'
            )

        # 通过多线程启动控制
        self.devices[device_name]['server_thread'] = threading.Thread(
            target=self._minicap_thread_fun,
            name='Thread-minicap-%s-Running' % device_name,
            args=(device_name, )
        )
        self.devices[device_name]['server_thread'].setDaemon(True)
        self.devices[device_name]['server_thread'].start()

    def _minicap_thread_fun(self, device_name):
        """
        minicap服务线程

        @param {str} device_name - 设备名
        """
        # 通过启动新进程处理
        _real_size = self.devices[device_name]['real_size']
        _canvas_size = self.devices[device_name]['canvas_size']
        _cmd = '%s%s %s' % (
            self.adb_name,
            ' -s %s' % device_name if device_name != '' else '',
            'shell LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/%s -P %dx%d@%dx%d/%d -S -Q %d' % (
                self.devices[device_name]['minicap_file'],
                _real_size[0], _real_size[1], _canvas_size[0], _canvas_size[1],
                self.devices[device_name]['orientation'],
                self.devices[device_name]['quality']
            )
        )

        # 执行命令
        self.logger.log(
            logging.INFO, 'exec sys cmd: %s' % _cmd
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


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
