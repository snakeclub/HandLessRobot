#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# Copyright 2019 黎慧剑
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import os
import sys
import time
import traceback
import uiautomation as auto
from urllib.parse import urlparse
from bs4 import BeautifulSoup, PageElement
from uiautomation import ControlType, Keys
from HiveNetLib.base_tools.file_tool import FileTool
from HiveNetLib.base_tools.run_tool import RunTool
from HiveNetLib.simple_queue import MemoryQueue
# 根据当前文件路径将包路径纳入，在非安装的情况下可以引用到
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), os.path.pardir, os.path.pardir)))
from HandLessRobot.robot import Robot
from HandLessRobot.lib.actions.common_action import CommonAction
from HandLessRobot.lib.actions.windows_action import WindowsAction, WindowsUiaAction
from HandLessRobot.lib.actions.chrome_action import WindowsChromeAction
from HandLessRobot.lib.controls.windows.uia import Window, WindowControlSpec
from HandLessRobot.lib.controls.base_control import Keyboard, Screen, Clipboard


class MyRobot(object):
    """
    机器人处理类
    """

    #############################
    # 构造函数
    #############################
    def __init__(self, url: str, sub_name: str, save_path: str,
                 parallel_num: int = 5, global_wait_time: float = 0.5, auto_redo: bool = True,
                 page_down_times: int = 5, pic_down_overtime: float = 60.0,
                 force_update: bool = False,
                 chrome_bin_path: str = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
                 chrome_download_path: str = 'D:\\download\\',
                 chrome_start_para: list = ['--force-renderer-accessibility'],
                 fatkun_dir_name: str = 'Fatkun',
                 **kwargs):
        """
        构造函数

        @param {str} url - 商品信息列表地址
        @param {str} sub_name - 对应url的子目录名
        @param {str} save_path - 保存目录
        @param {int} parallel_num=5 - 并发打开页面的数量
        @param {float} global_wait_time=0.5 - 全局操作间歇等待时长设置
        @param {bool} auto_redo=True - 失败是否自动重处理
        @param {int} page_down_times=5 - 每个页面按下翻页的次数
        @param {float} pic_down_overtime = 60.0 - 图片下载超时时间，默认1分钟
        @param {bool} force_update=False - 是否强制重新更新商品清单
        @param {str} chrome_bin_path='C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe' - chrome浏览器启动文件
        @param {str} chrome_download_path='D:\\download\\' - 浏览器下载目录
        @param {list} chrome_start_para=['--force-renderer-accessibility'] - 浏览器启动参数
        @param {str} fatkun_dir_name='Fatkun' - Fatkun扩展插件保存固定目录名
        """
        # 传入参数
        self.url = url
        self.sub_name = sub_name
        self.save_path = save_path
        self.parallel_num = parallel_num
        self.global_wait_time = global_wait_time
        self.auto_redo = auto_redo
        self.page_down_times = page_down_times
        self.pic_down_overtime = pic_down_overtime
        self.force_update = force_update
        self.chrome_bin_path = chrome_bin_path
        self.chrome_download_path = chrome_download_path
        self.chrome_start_para = chrome_start_para
        self.fatkun_dir_name = fatkun_dir_name

        # 初始化
        self._chrome: WindowControlSpec = None
        self._robot_info: dict = None
        self._save_path = os.path.realpath(os.path.join(self.save_path, self.sub_name))
        self._down_info_file = os.path.join(self._save_path, 'down.json')
        self._download_path = os.path.realpath(
            os.path.join(self.chrome_download_path, self.fatkun_dir_name)
        )
        FileTool.create_dir(self._save_path, exist_ok=True)

        # 从持久化文件中装载运行内存信息
        self._down_info: dict = None
        if os.path.exists(self._down_info_file):
            self._load_down_info()
        else:
            self._down_info = {
                'url': self.url,
                'status': 'list',  # 整体处理状态：list-获取商品清单, download-下载中, done-完成
                # 实际上处理的每个商品列表分页信息，每行为一个数组 [url, status], status状态：list-获取商品清单, done-分页处理完成
                # 注：从第一个url开始，每次开始解析分页时，向数组里添加信息
                'urls': [],
                # 产品清单，key为产品编号（注意不同商家的产品编号有可能重复），value为下载信息字典，定义如下
                #     url - 商品详情页面地址
                #     status - 处理状态：page-获取页面代码, download-下载中, done-完成, error-出现错误
                'products': {},
            }
            self._save_down_info()

    #############################
    # 公共函数
    #############################
    def run_robot(self):
        """
        运行机器人
        """
        # 先做完成状态的判断
        if self.url != self._down_info['url']:
            if self._down_info['status'] == 'list':
                # 上一url还在解析商品信息，不应处理新的url
                print('Last url is listing, please add new url after this done!')
                return
            else:
                # 补充新的url
                self._down_info['url'] = self.url
                self._down_info['status'] = 'list'
                self._down_info['urls'].clear()
                self._save_down_info()

        if self._down_info['status'] == 'done':
            # 已完成
            if self.force_update:
                # 强制重新刷新清单获取
                self._down_info['status'] = 'list'
                self._down_info['urls'].clear()
                self._save_down_info()
                print('Force update finished url: %s' % self.url)
            else:
                print('The url has finished: %s' % self.url)
                return

        print('Start robot job with url: %s' % self.url)

        # 初始化机器人
        _robot = Robot(use_action_types=['winuia'], ignore_version=True)
        self._robot_info = _robot.robot_info

        # 启动Chrome浏览器
        self._chrome = WindowsChromeAction.get_chrome_window(
            _robot.robot_info, 'get_chrome_window', bin_path=self.chrome_bin_path,
            run_paras=self.chrome_start_para
        )

        # 将浏览器放在最前面, 否则会获取不到对象
        WindowsAction.common_attr_call(
            _robot.robot_info, 'WINDOW_SET_FOREGROUND', self._chrome
        )

        # 处理产品清单的获取
        if not self._get_product_list():
            return

        # 处理产品信息获取
        if not self._get_product_info():
            return

        # 全部完成
        print('Success finish robot job with url: %s' % self.url)

    #############################
    # 下载信息的持久化处理
    #############################
    def _load_down_info(self):
        """
        从文件中获取下载信息
        """
        with open(self._down_info_file, 'rb') as f:
            _eval = str(f.read(), encoding='utf-8')
            self._down_info = eval(_eval)

    def _save_down_info(self):
        """
        保存下载信息到文件中
        """
        _json = str(self._down_info)
        with open(self._down_info_file, 'wb') as f:
            f.write(str.encode(_json, encoding='utf-8'))

    #############################
    # 产品清单解析
    #############################
    def _analyse_list_products(self, url: str, soup: BeautifulSoup):
        """
        解析清单页获取产品清单

        @param {str} url - 要解析的清单页url
        @param {BeautifulSoup} soup - 要解析的dom对象
        """
        _url_info = urlparse(url)
        _div: PageElement = soup.findAll('div', attrs={'class': 'J_TItems'})[0]
        _next_url = ''  # 当前页的下一页地址
        for _line in _div.children:
            if _line.name != 'div':
                continue

            if 'pagination' in _line['class']:
                # 获取到页跳转信息，处理完成，跳出处理
                for _a in _line.children:
                    if _a.name == 'a' and _a.string == '下一页':
                        if 'disable' not in _a['class']:
                            _next_url = '%s:%s' % (_url_info.scheme, _a['href'])
                        break
                break
            elif 'comboHd' in _line['class']:
                # 没有搜索到商品，跳出处理
                break
            else:
                # 获取到行信息
                for _product in _line.children:
                    if _product.name != 'dl':
                        continue
                    _data_id = _product['data-id']
                    _data_url = '%s:%s' % (_url_info.scheme, _product.dt.a['href'])
                    # 放入产品处理清单中
                    if _data_id not in self._down_info['products'].keys():
                        self._down_info['products'][_data_id] = {
                            'url': _data_url,
                            'status': 'page'
                        }
                        self._save_down_info()

        # 更新当前页的处理状态, 并把下一页放入清单
        self._down_info['urls'][len(self._down_info['urls']) - 1][1] = 'done'
        if _next_url != '':
            self._down_info['urls'].append([_next_url, 'list'])

        self._save_down_info()

    def _analyse_list_url(self, url: str):
        """
        解析商品清单url

        @param {str} - 要解析的url

        @returns {bool} - 处理结果
        """
        print('Start analyse list url: %s' % url)
        try:
            # 固定选中第一个标签页
            WindowsChromeAction.chrome_select_tab(
                self._robot_info, 'chrome_select_tab', self._chrome, index=0
            )

            # 打开url
            WindowsChromeAction.chrome_goto_url(
                self._robot_info, 'chrome_goto_url', url,
                chrome_win=self._chrome
            )

            # 等待页面加载完成
            CommonAction.time_wait_global(
                self._robot_info, 'time_wait_global', multiple=2
            )

            # 滚动到结尾, 防止有动态加载的情况
            Keyboard.press('pgdn', presses=self.page_down_times, interval=0.2)

            # 获取页面dom代码
            _dom = WindowsChromeAction.chrome_get_dom_html(
                self._robot_info, 'chrome_get_dom_html', self._chrome,
                check_complete={
                    'name': 'div', 'attrs': {'class': 'J_TItems'}
                }
            )
            _soup = BeautifulSoup(_dom, 'html.parser')

            # 解析产品信息, 同时也会产生下一页的内容
            self._analyse_list_products(url, _soup)
        except:
            print('Analyse list url error: %s\r\n%s' % (url, traceback.format_exc()))
            return False

        print('Finish analyse list url: %s' % url)
        return True

    def _get_product_list(self):
        """
        获取产品清单

        @returns {bool} - 是否处理成功
        """
        # 如果是第一个，添加第一页的url
        if len(self._down_info['urls']) == 0:
            self._down_info['urls'].append([self.url, 'list'])
            self._save_down_info()

        # 通过循环控制失败重新处理
        while True:
            _index = len(self._down_info['urls']) - 1
            if self._down_info['urls'][_index][1] == 'done':
                # 已经全部处理成功
                print('All list urls has finished!')
                return True

            # 解析当前url
            _result = self._analyse_list_url(self._down_info['urls'][_index][0])
            if not _result:
                # 处理失败
                if self.auto_redo:
                    # 失败自动重处理
                    print('Some url deal fail, auto redo get_product_list!')
                    continue
                else:
                    # 直接返回失败
                    print('Deal list url fail: %s' % self._down_info['urls'][_index][0])
                    return False

    #############################
    # 产品信息获取
    #############################
    def _open_product_url(self, data_id: str, url: str, index: int):
        """
        在指定标签页打开产品页面

        @param {str} data_id - 产品id
        @param {str} url - 产品页面url
        @param {int} index - 打开的标签索引位置
        """
        print('Open product [%s]: %s' % (data_id, url))
        WindowsChromeAction.chrome_select_tab(
            self._robot_info, 'chrome_select_tab', self._chrome, index=index
        )
        CommonAction.time_wait_global(
            self._robot_info, 'time_wait_global'
        )
        WindowsChromeAction.chrome_goto_url(
            self._robot_info, 'chrome_select_tab', url, chrome_win=self._chrome
        )
        CommonAction.time_wait_global(
            self._robot_info, 'time_wait_global', multiple=2
        )
        # 滚动到结尾, 防止有动态加载的情况
        Keyboard.press('pgdn', presses=self.page_down_times, interval=0.2)

    def _analyse_product_page(self, data_id: str, index: int):
        """
        解析产品页面进行处理

        @param {str} data_id - 页面产品id
        @param {int} index - 页面位置

        @returns {boot} - 是否处理成功
        """
        print('Analyse product page: %s' % data_id)
        try:
            # 创建目录
            _path = os.path.join(self._save_path, data_id)
            if os.path.exists(_path):
                # 清空目录
                FileTool.remove_all_with_path(path=_path, with_sub_path=True)
            else:
                FileTool.create_dir(_path, exist_ok=True)

            # 清空下载目录
            if os.path.exists(self._download_path):
                FileTool.remove_all_with_path(path=self._download_path, with_sub_path=True)

            # 跳转到标签
            WindowsChromeAction.chrome_select_tab(
                self._robot_info, 'chrome_select_tab', self._chrome, index=index
            )
            CommonAction.time_wait_global(
                self._robot_info, 'time_wait_global'
            )
            # 滚动到结尾, 防止有动态加载的情况
            Keyboard.press('pgdn', presses=5, interval=0.3)

            # 等待页面加载完成
            CommonAction.time_wait_global(
                self._robot_info, 'time_wait_global', multiple=2
            )

            # 获取页面dom代码
            _dom = WindowsChromeAction.chrome_get_dom_html(
                self._robot_info, 'chrome_get_dom_html', self._chrome
            )

            # 保存dom代码
            with open(os.path.join(_path, 'dom.html'), 'w', encoding='utf-8') as _f:
                _f.write(_dom)

            # 下载图片, 找到扩展插件
            _first = WindowsChromeAction.chrome_get_extension(
                self._robot_info, 'chrome_get_extension', self._chrome, name_with='Fat'
            )

            _first._win_object.RightClick()

            CommonAction.time_wait_global(
                self._robot_info, 'time_wait_global'
            )

            WindowsChromeAction.chrome_click_pop_menu(
                self._robot_info, 'chrome_get_extension', self._chrome,
                [[None, '批量下载'], ]
            )

            CommonAction.time_wait_global(
                self._robot_info, 'time_wait_global', multiple=3
            )

            # 获取页面
            _doc = WindowsChromeAction.chrome_get_page_doc(
                self._robot_info, 'chrome_get_extension', self._chrome
            )

            # 获取下载按钮
            _header = Window.find_window(
                parent=_doc, automation_id='header', control_type=ControlType.GroupControl
            )

            _down_btn = Window.find_window(
                parent=_header, name='下载', control_type=ControlType.ButtonControl
            )

            _down_btn.automation_control.Click()

            # 检查是否已下载完成
            _is_over_time = False
            _check_time = 0
            while True:
                _pic_total = Window.find_window(
                    parent=_header, automation_id='total-num', control_type=ControlType.GroupControl
                ).get_childrens()[0]
                _pic_total_num = _pic_total.name.replace(
                    '总共 : ', '').replace('/', '').replace(' ', '')

                _pic_down = Window.find_window(
                    parent=_header, automation_id='downloaded-num', control_type=ControlType.GroupControl
                ).get_childrens()[0]
                _pic_down_num = _pic_down.name.replace('已下载 : ', '').replace(' ', '')

                if _pic_total_num == _pic_down_num:
                    break
                else:
                    if _check_time < self.pic_down_overtime:
                        _check_time += 1
                        time.sleep(1)
                        continue
                    else:
                        # 超时
                        _is_over_time = True
                        break

            if not _is_over_time:
                # 下载成功，移动文件到目录
                FileTool.copy_all_with_path(src_path=self._download_path, dest_path=_path)

            # 清空下载目录
            FileTool.remove_all_with_path(path=self._download_path, with_sub_path=True)

            # 关闭当前下载页面
            _down_tab = WindowsChromeAction.chrome_get_selected_tab(
                self._robot_info, 'chrome_get_selected_tab', self._chrome
            )
            WindowsChromeAction.chrome_close_tab(
                self._robot_info, 'chrome_close_tab', chrome_tab=_down_tab
            )

            if _is_over_time:
                print('Analyse product page error, pic download overtime: %s' % (data_id, ))
                return False
        except:
            # 关闭窗口
            _down_tab = WindowsChromeAction.chrome_get_selected_tab(
                self._robot_info, 'chrome_get_selected_tab', self._chrome
            )
            if _down_tab.name.find('chrome-extension') >= 0:
                WindowsChromeAction.chrome_close_tab(
                    self._robot_info, 'chrome_close_tab', chrome_tab=_down_tab
                )

            print('Analyse product page error: %s\r\n%s' % (data_id, traceback.format_exc()))
            return False

        print('Finish analyse product: %s' % data_id)
        return True

    def _get_product_info(self):
        """
        获取下载清单中的产品信息
        """
        # 把未完成的任务放入队列中进行处理
        _task_q = MemoryQueue()
        for _data_id in self._down_info['products']:
            if self._down_info['products'][_data_id]['status'] != 'done':
                _task_q.put(_data_id)

        # 根据并发数设置足够的页签
        _tabs = WindowsChromeAction.chrome_get_tabs(
            self._robot_info, 'chrome_get_tabs', self._chrome
        )
        _create_num = self.parallel_num - len(_tabs) + 1
        while _create_num > 0:
            WindowsChromeAction.chrome_new_tab(
                self._robot_info, 'chrome_new_tab', self._chrome
            )
            _create_num -= 1
            CommonAction.time_wait_global(
                self._robot_info, 'time_wait_global'
            )

        # 设置初始打开的页面
        _index = 0
        _stack = []  # 按位置确定哪个标签页访问的数据
        while _index < self.parallel_num:
            if not _task_q.empty():
                _data_id = _task_q.get()
                _stack.append(_data_id)
                self._open_product_url(
                    _data_id, self._down_info['products'][_data_id]['url'], _index
                )
            else:
                _stack.append('')  # 空代表没有数据了

            _index += 1

        # 循环进行页面解析处理
        _index = 0
        _all_done = True
        while True:
            if _stack[_index] == '':
                # 遇到堆栈没有数据的情况, 说明全部已经处理完成
                if _all_done:
                    print('All product download has finished!')
                    return True
                else:
                    print('Deal product download fail!')
                    return False

            if self._analyse_product_page(_stack[_index], _index):
                # 更新状态
                self._down_info['products'][_stack[_index]]['status'] = 'done'
                self._save_down_info()
            else:
                # 处理失败
                if self.auto_redo:
                    # 失败自动重处理
                    _task_q.put(_stack[_index])
                    print('Product [%s] deal fail, auto put back to queue!' % _stack[_index])
                else:
                    # 标记存在失败记录
                    _all_done = False

            # 清空并将下一个产品放进堆栈
            _stack[_index] = ''
            if not _task_q.empty():
                _data_id = _task_q.get()
                _stack[_index] = _data_id
                self._open_product_url(
                    _data_id, self._down_info['products'][_data_id]['url'], _index
                )

            # 下一次循环
            if _index < self.parallel_num - 1:
                _index += 1
            else:
                _index = 0

            time.sleep(0.01)


def robot_run(url: str):
    """
    运行天猫商品信息获取机器人

    @param {str} url - 商品信息列表地址
    """
    # 初始化机器人
    _robot = Robot(use_action_types=['winuia'], ignore_version=True)

    # 启动Chrome浏览器, 获取主窗口
    _chrome = WindowsChromeAction.get_chrome_window(
        _robot.robot_info, 'chorme_start',
        bin_path='C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
    )

    # 将窗口置于最前方
    WindowsAction.common_attr_call(
        _robot.robot_info, 'WINDOW_SET_FOREGROUND', _chrome
    )

    # 打开第一个标签
    WindowsChromeAction.chrome_select_tab(
        _robot.robot_info, 'chrome_select_tab', _chrome, index=0
    )

    _dom_html = WindowsChromeAction.chrome_get_dom_html(
        _robot.robot_info, 'chrome_get_dom_html', _chrome
    )

    print('ok')

    # Window.print_window_info(_dom_edit, to_json_str=True, print_to_file='d:/test.json')

    # Window.print_window_info(_win, print_to_file='d:/test.json', to_json_str=True)

    # _call_para = [[5, ], {}]
    # _robot.call_action('time_wait', call_para=_call_para)
    # 关闭浏览器，要强制关闭
    # _call_para = [[_app, ], {'soft': False}]
    # _robot.call_action('KILL_APPLICATION', call_para=_call_para)


if __name__ == '__main__':
    # 当程序自己独立运行时执行的操作
    # _url = 'www.baidu.com'
    # _url = 'https://detail.tmall.com/item.htm?spm=a211oj.13285558.7993390550.17.18816dd0qJWK5v&pos=17&acm=ak-zebra-236012-271493.1003.1.2783047&id=581825320110&rmdChannelCode=promotion&scm=1007.12144.167873.8364007_0_0&sku_properties=10004:827902415;5919063:6536025'
    # _url = 'https://zhuowasm.tmall.com/search.htm?spm=a1z10.3-b-s.w4011-16375826183.1.14a67bcdIOeuCn'
    # robot_run(_url)
    _args = RunTool.get_kv_opts()
    _url = _args.pop('url', '')
    _sub_name = _args.pop('sub_name', 'test')
    _save_path = _args.pop('save_path', 'd:/auto_down/')

    _robot = MyRobot(
        _url,
        _sub_name,
        _save_path,
        **_args
    )
    _robot.run_robot()
