#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
钉钉日志自动置已读
@module dingtalk_daily_read
@file dingtalk_daily_read.py
"""

import os
import sys
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
from HandLessRobot.robot import PreDefinedModuleClass
from HandLessRobot.platform.control.windows import Window, Mouse, Keyboard, Screen


class DingTalkDailyRead(PreDefinedModuleClass):
    """
    钉钉未读日志自动处理
    """

    #############################
    # 公共函数
    #############################
    def get_call_name(self):
        """
        获取调用名

        @retrun {str} - 调用名
        """
        return 'DingTalkDailyRead'

    def get_supports(self):
        """
        获取模块的平台支持参数

        @returns {dict} - 支持执行的平台清单
            key {str} - 支持的平台名称(例如Windows、Linux), 可通过'platform.system()'获取, '*'代表全平台支持,
            value {tuple} - 支持的版本清单, 例如('7', '10', 'nt') ,None代表全版本支持
        """
        return {'*': None}

    def run(self):
        """
        执行操作
        """
        _top_win_find_para = {
            'top_level_only': True,
            'class_name': 'StandardFrame_DingTalk',
            'title': '钉钉'
        }
        _top_win = Window.find_window(**_top_win_find_para)
        # _top_win.move(x=0, y=0)
        Window.print_window_info(_top_win, screen_shot_save_path='d:/test_win/')


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    DingTalkDailyRead().run()
