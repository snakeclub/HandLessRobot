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
import uiautomation as auto
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir)))
from HandLessRobot.lib.controls.windows.uia import Window, Mouse, Keyboard, Screen


class DingTalkDailyRead(object):
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
        # 找到Notepad主窗口
        _top_win_find_para = {
            'top_level_only': True,
            'class_name': 'Notepad'
        }
        # 找到Notepad主进程和激活窗口
        _note_win = Window.find_window(**_top_win_find_para)

        _note_win.set_foreground()

        # 找到编辑控件
        _edit_win = Window.find_window(
            class_name='Edit',
            parent=_note_win
        )

        print('v', _edit_win.v_scroll_range, _edit_win.v_scroll_pos)
        print('h', _edit_win.h_scroll_range, _edit_win.h_scroll_pos)

        # print(_edit_win.v_scroll_to(20))

        # print(_edit_win.h_scroll_to(100))

        _scroll: auto.ScrollPattern = _edit_win.automation_control.GetPattern(
            auto.PatternId.ScrollPattern
        )

        print(_scroll.VerticallyScrollable, _scroll.VerticalViewSize, _scroll.VerticalScrollPercent,
              _scroll.HorizontallyScrollable, _scroll.HorizontalViewSize, _scroll.HorizontalScrollPercent)

        # _scroll.SetScrollPercent(50.0, 50.0)

        # Window.print_window_info(_active_win, screen_shot_save_path='d:/test_win/',
        #                          print_to_file='d:/test_win/info.txt', depth=8)


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    DingTalkDailyRead().run()
