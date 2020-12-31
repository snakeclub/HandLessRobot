#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
appium移动端的动作模块
@module appium_action
@file appium_action.py
"""

import os
import sys
from HiveNetLib.base_tools.run_tool import RunTool
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir)))
from HandLessRobot.lib.actions.base_action import BaseAction
from HandLessRobot.lib.controls.appium_control import AppDevice, AppElement
from HandLessRobot.lib.controls.appium.android import AppDevice as AndroidAppDevice, AppElement as AndroidAppElement


__MOUDLE__ = 'appium_action'  # 模块名
__DESCRIPT__ = u'appium移动端的动作模块'  # 模块描述
__VERSION__ = '0.1.0'  # 版本
__AUTHOR__ = u'黎慧剑'  # 作者
__PUBLISH__ = '2020.11.25'  # 发布日期


# 一些公共的全局变量
APPIUM_FUN_ROUTER = {
    # 对应用的操作
    'GET_RECT_CENTER': AppDevice.center,
    'GET_APPIUM_DEVICE': AppDevice.get_app_device
}

APPIUM_ATTR_ROUTER = {
    # 实例对象属性
    'APPIUM_DV_ATTR_DRIVER': ['appium_driver', AppDevice.appium_driver],
    'APPIUM_DV_ATTR_SIZE': ['size', AppDevice.size],
    'APPIUM_DV_ATTR_DESIRED_CAPS': ['desired_caps', AppDevice.desired_caps],
    'APPIUM_DV_ATTR_SERVER': ['appium_server', AppDevice.appium_server],
    'APPIUM_DV_ATTR_PAGE_SOURCE': ['page_source', AppDevice.page_source],
    'APPIUM_DV_ATTR_ORIENTATION': ['orientation', AppDevice.orientation],
    'APPIUM_EL_ATTR_ID': ['id', AppElement.id],
    'APPIUM_EL_ATTR_ELEMENT': ['appium_element', AppElement.appium_element],
    'APPIUM_EL_ATTR_DRIVER': ['appium_driver', AppElement.appium_driver],
    'APPIUM_EL_ATTR_TEXT': ['text', AppElement.text],
    'APPIUM_EL_ATTR_TAG_NAME': ['tag_name', AppElement.tag_name],
    'APPIUM_EL_ATTR_IS_SELECTED': ['is_selected', AppElement.is_selected],
    'APPIUM_EL_ATTR_IS_ENABLED': ['is_enabled', AppElement.is_enabled],
    'APPIUM_EL_ATTR_IS_DISPLAYED': ['is_displayed', AppElement.is_displayed],
    'APPIUM_EL_ATTR_LOCATION': ['location', AppElement.location],
    'APPIUM_EL_ATTR_LOCATION_IN_VIEW': ['location_in_view', AppElement.location_in_view],
    'APPIUM_EL_ATTR_SIZE': ['size', AppElement.size],
    'APPIUM_EL_ATTR_RECT': ['rect', AppElement.rect],

    # 实例对象函数
    'APPIUM_UPDATE_SETTINGS': ['update_settings', AppDevice.update_settings],
    'APPIUM_GET_CLIPBOARD_TEXT': ['get_clipboard_text', AppDevice.get_clipboard_text],
    'APPIUM_SET_CLIPBOARD_TEXT': ['set_clipboard_text', AppDevice.set_clipboard_text],
    'APPIUM_QUERY_APP_STATE': ['query_app_state', AppDevice.query_app_state],
    'APPIUM_IS_APP_INSTALLED': ['is_app_installed', AppDevice.is_app_installed],
    'APPIUM_INSTALL_APP': ['install_app', AppDevice.install_app],
    'APPIUM_REMOVE_APP': ['remove_app', AppDevice.remove_app],
    'APPIUM_LAUNCH_APP': ['launch_app', AppDevice.launch_app],
    'APPIUM_BACKGROUND_APP': ['background_app', AppDevice.background_app],
    'APPIUM_CLOSE_APP': ['close_app', AppDevice.close_app],
    'APPIUM_RESET_APP': ['reset_app', AppDevice.reset_app],
    'APPIUM_ACTIVATE_APP': ['activate_app', AppDevice.activate_app],
    'APPIUM_TERMINATE_APP': ['terminate_app', AppDevice.terminate_app],
    'APPIUM_WAIT': ['wait', AppDevice.wait],
    'APPIUM_SET_ORIENTATION': ['set_orientation', AppDevice.set_orientation],
    'APPIUM_SCREENSHOT': ['screenshot', AppDevice.screenshot],
    'APPIUM_LOCATE_ON_SCREEN': ['locate_on_screen', AppDevice.locate_on_screen],
    'APPIUM_LOCATE_ALL_ON_SCREEN': ['locate_all_on_screen', AppDevice.locate_all_on_screen],
    'APPIUM_SWIPE': ['swipe', AppDevice.swipe],
    'APPIUM_SWIPE_UP': ['swipe_up', AppDevice.swipe_up],
    'APPIUM_SWIPE_DOWN': ['swipe_down', AppDevice.swipe_down],
    'APPIUM_SWIPE_LEFT': ['swipe_left', AppDevice.swipe_left],
    'APPIUM_SWIPE_RIGHT': ['swipe_right', AppDevice.swipe_right],
    'APPIUM_SWIPE_PLUS': ['swipe_plus', AppDevice.swipe_plus],
    'APPIUM_SWIPE_ZOOM_IN': ['swipe_zoom_in', AppDevice.swipe_zoom_in],
    'APPIUM_SWIPE_ZOOM_OUT': ['swipe_zoom_out', AppDevice.swipe_zoom_out],
    'APPIUM_TAP': ['tap', AppDevice.tap],
    'APPIUM_PRESS': ['press', AppDevice.press],
    'APPIUM_RELEASE': ['release', AppDevice.release],
    'APPIUM_LONG_PRESS': ['long_press', AppDevice.long_press],
    'APPIUM_PRESS_KEYCODE': ['press_keycode', AppDevice.press_keycode],
    'APPIUM_LONG_PRESS_KEYCODE': ['long_press_keycode', AppDevice.long_press_keycode],
    'APPIUM_IS_KEYBOARD_SHOWN': ['is_keyboard_shown', AppDevice.is_keyboard_shown],
    'APPIUM_HIDE_KEYBOARD': ['hide_keyboard', AppDevice.hide_keyboard],
    'APPIUM_IMPLICITLY_WAIT': ['implicitly_wait', AppDevice.implicitly_wait],
    'APPIUM_GET_ACTIVE_ELEMENT': ['get_active_element', AppDevice.get_active_element],
    'APPIUM_FIND_ELEMENT': ['find_element', AppDevice.find_element],
    'APPIUM_FIND_ELEMENTS': ['find_elements', AppDevice.find_elements],
    'APPIUM_FIND_ELEMENT_BY_XPATH': ['find_element_by_xpath', AppDevice.find_element_by_xpath],
    'APPIUM_FIND_ELEMENTS_BY_XPATH': ['find_elements_by_xpath', AppDevice.find_elements_by_xpath],
    'APPIUM_FIND_ELEMENT_BY_IMAGE': ['find_element_by_image', AppDevice.find_element_by_image],
    'APPIUM_FIND_ELEMENTS_BY_IMAGE': ['find_elements_by_image', AppDevice.find_elements_by_image],
    'APPIUM_EL_GET_ATTRIBUTE': ['get_attribute', AppElement.get_attribute],
    'APPIUM_EL_GET_CSS_PROPERTY': ['get_css_property', AppElement.get_css_property],
    'APPIUM_EL_SCREENSHOT': ['screenshot', AppElement.screenshot],
    'APPIUM_EL_SET_VALUE': ['set_value', AppElement.set_value],
    'APPIUM_EL_CLICK': ['click', AppElement.click],
    'APPIUM_EL_CLEAR': ['clear', AppElement.clear],
    'APPIUM_EL_SEND_KEYS': ['send_keys', AppElement.send_keys],
    'APPIUM_EL_TAP': ['tap', AppElement.tap],
    'APPIUM_EL_LONG_PRESS': ['long_press', AppElement.long_press],
    'APPIUM_EL_DRAG_AND_DROP': ['drag_and_drop', AppElement.drag_and_drop]
}

APPIUM_ANDROID_ATTR_ROUTER = {
    # 实例对象属性
    'ANDROID_DV_ATTR_current_package': ['current_package', AndroidAppDevice.current_package],
    'ANDROID_DV_ATTR_current_activity': ['current_activity', AndroidAppDevice.current_activity],
    'ANDROID_DV_ATTR_is_ime_active': ['is_ime_active', AndroidAppDevice.is_ime_active],

    # 实例对象函数
    'ANDROID_DV_start_activity': ['start_activity', AndroidAppDevice.start_activity],
    'ANDROID_EL_set_text': ['set_text', AndroidAppElement.set_text]
}


class AppiumAction(BaseAction):
    """
    移动应用Appium的动作模块
    """
    @classmethod
    def support_action_types(cls) -> list:
        """
        返回支持的动作类别列表(主要基于列表区分不同平台及技术兼容的动作)

        @returns {list} - 支持的动作类别列表，例如：
            ['*'] - 代表支持所有分类
            ['win32', 'winuia'] - 代表支持win32和winuia两种分类使用
        """
        return ['*']

    @classmethod
    def support_platform(cls) -> dict:
        """
        返回支持的平台字典
        (用于自动生成路由表，默认支持全平台全版本，如需要指定需修改该函数返回值)

        @returns {dict} - 支持的平台字典，key为system，value为ver
            system='*' - 支持的平台名称(例如Windows、Linux), '*'代表全平台支持
            ver=None - 支持的版本清单, 例如('7', '10', 'nt') , None代表全版本支持
        """
        return {'IOS': None, 'Android': None}

    #############################
    # 静态函数通用映射
    #############################
    @classmethod
    def get_common_fun_dict(cls):
        """
        获取静态函数通用映射字典
        (如果需要实现映射，请继承并修改该函数的返回值)

        @returns {dict} - 返回静态函数通用映射字典
            key - 动作名(action_name), 必须为大写
            value - 动作对应的执行函数对象
        """
        return APPIUM_FUN_ROUTER

    #############################
    # 窗口实例对象的通用方法调用
    #############################
    @classmethod
    def get_common_attr_dict(cls):
        """
        获取实例对象内部方法及属性映射字典
        (如果需要实现映射，请继承并修改该函数的返回值)

        @returns {dict} - 返回实例对象内部方法及属性映射字典
            key - 动作名(action_name), 必须为大写
            value - [属性或函数名(字符串), 属性或函数对象]
        """
        return APPIUM_ATTR_ROUTER


class AppiumAndroidAction(BaseAction):
    """
    安卓移动应用Appium的动作模块
    """
    @classmethod
    def support_action_types(cls) -> list:
        """
        返回支持的动作类别列表(主要基于列表区分不同平台及技术兼容的动作)

        @returns {list} - 支持的动作类别列表，例如：
            ['*'] - 代表支持所有分类
            ['win32', 'winuia'] - 代表支持win32和winuia两种分类使用
        """
        return ['*']

    @classmethod
    def support_platform(cls) -> dict:
        """
        返回支持的平台字典
        (用于自动生成路由表，默认支持全平台全版本，如需要指定需修改该函数返回值)

        @returns {dict} - 支持的平台字典，key为system，value为ver
            system='*' - 支持的平台名称(例如Windows、Linux), '*'代表全平台支持
            ver=None - 支持的版本清单, 例如('7', '10', 'nt') , None代表全版本支持
        """
        return {'Android': None}

    #############################
    # 窗口实例对象的通用方法调用
    #############################
    @classmethod
    def get_common_attr_dict(cls):
        """
        获取实例对象内部方法及属性映射字典
        (如果需要实现映射，请继承并修改该函数的返回值)

        @returns {dict} - 返回实例对象内部方法及属性映射字典
            key - 动作名(action_name), 必须为大写
            value - [属性或函数名(字符串), 属性或函数对象]
        """
        return APPIUM_ANDROID_ATTR_ROUTER


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # 打印版本信息
    print(('模块名：%s  -  %s\n'
           '作者：%s\n'
           '发布日期：%s\n'
           '版本：%s' % (__MOUDLE__, __DESCRIPT__, __AUTHOR__, __PUBLISH__, __VERSION__)))
