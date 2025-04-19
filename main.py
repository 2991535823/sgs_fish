import multiprocessing
import os
import re
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk
from threading import Thread
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import pygetwindow as gw

from control import Direction, TouchController
from coordinate import GameCoordinate
from exit import EscMonitor
from info import GameInfo


class SimpleWindowLocator:
    def __init__(self, title_keywords):
        """
        :param title_keywords: 窗口标题关键词（支持字符串或列表）
        """
        self.keywords = [title_keywords] if isinstance(title_keywords, str) else title_keywords
        self.dpi_scale = self._get_dpi_scale()
        self.valid_windows = []
    def _get_dpi_scale(self):
        """通过Tkinter获取DPI缩放比例"""
        root = tk.Tk()
        root.withdraw()  # 隐藏临时窗口
        dpi = root.winfo_fpixels('1i')
        root.destroy()
        return dpi / 96.0

    def _is_target_window(self, window):
        """使用模糊匹配验证窗口"""
        try:
            title = window.title.lower()
            # 组合匹配逻辑：至少包含一个关键词且不包含排除词
            return (any(re.search(kw.lower(), title) for kw in self.keywords) 
                    and "error" not in title)  # 示例排除词
        except:
            return False


    def get_window_rect(self):
        all_windows = gw.getAllWindows()
        self.valid_windows.clear()
        for w in all_windows:
            try:
                # 验证窗口有效性并检查可见性
                if (self._is_target_window(w)
                    and w.visible
                    and not w.isMinimized):  # 排除最小化窗口
                    self.valid_windows.append(w)
            except Exception as e:
                print(f"窗口 {w.title} 检查失败: {str(e)}")
                continue
        if not self.valid_windows:
            raise WindowNotFound(f"未找到含 {self.keywords} 的可见窗口")

        target= self.valid_windows[0]
        # DPI转换补偿计算
        def scale(value):
            return int(value * self.dpi_scale + 0.5)  # 四舍五入

        return (
            scale(target.left),
            scale(target.top),
            scale(target.width),
            scale(target.height)
        )

class WindowNotFound(Exception):
    pass

class GameOperator(SimpleWindowLocator):
    def __init__(self, keywords,bias_y):
        super().__init__(keywords)
        self.controller = TouchController(drag_duration=(0.1,0.15))
        self.bias_y=bias_y
        self.window_rect = self.get_window_rect()
        self.gc=GameCoordinate(self.window_rect,self.bias_y)
        print('当前比率',((self.window_rect[3]-self.bias_y)/self.window_rect[2]))
        if 0.562<((self.window_rect[3] - 30) / self.window_rect[2])<0.563:
            print('窗口大小合适')
        else:
            width=800
            height=450+self.bias_y
            print(f'重新设置 宽度{width},高度{height}')
            self.valid_windows[0].resizeTo(width, height)
            self.window_rect = self.get_window_rect()
            self.gc = GameCoordinate(self.window_rect,self.bias_y)
            resize_btn=(self.gc.cal_pose(1,1)[0]-50,self.gc.cal_pose(1,1)[1]-50)
            self.controller.click(resize_btn,0.5)
            time.sleep(2)
            messagebox.showinfo("提示","重设游戏窗口大小,待窗口重新启动后点击确定")

        self.kbs={'up':(0.1854,0.6111),'down':(0.1854,0.8479),'left':(0.1124,0.7347),'right':(0.2584,0.7347),
                  'feng':(0.8090,0.6121),'huo':(0.7416,0.7347),'lei':(0.8090,0.8479),'dian':(0.8764,0.7347)}
    def lambda_click(self,x,y):
        self.controller.click(self.gc.cal_pose(x,y),0.1)
    def click_relative(self, rel_x, rel_y,delay=0.1):
        """点击相对窗口的位置（0~1范围）"""
        self.controller.click(self.gc.cal_pose(rel_x,rel_y),delay)
    def mouse_click(self,rel_x,rel_y):
        self.controller.mouse_click(self.gc.cal_pose(rel_x,rel_y))
    def drag_relative(self, rel_x,rel_y,dir,dis=100):
        """窗口内相对坐标拖拽"""
        self.controller.drag(self.gc.cal_pose(rel_x,rel_y),dir,dis)
    def kill(self,res):
        for action in res:
            self.lambda_click(*self.kbs[action])
# 使用示例

def delayMsecond(t):
    start, end = 0, 0
    start = time.time_ns()  # 精确至ns级别
    while end - start < t * 1000000:
        end = time.time_ns()


class FishingSettingsWindow:
    def __init__(self, master):
        self.master = master
        master.title("钓鱼参数设置")
        master.geometry("450x700")
        master.resizable(False, False)

        # 使用ttkbootstrap的darkly主题
        self.style = tb.Style(theme="darkly")

        # 创建主容器
        main_frame = tb.Frame(master, padding=20)
        main_frame.pack(fill="both", expand=True)

        # 标题
        tb.Label(main_frame, text="钓鱼参数设置中心", font=("Helvetica", 16, "bold"),
                 bootstyle="primary").pack(pady=(0, 20))

        # 创建变量存储用户设置
        self.window_title = tk.StringVar(value="三国杀")
        self.progress_tracking = tk.DoubleVar(value=0.9)  # 默认进度跟踪80%
        self.delay_ms = tk.IntVar(value=6000)  # 默认刺鱼延时500ms
        self.kp = tk.DoubleVar(value=50)  # 默认Kp值
        self.ki = tk.DoubleVar(value=1)  # 默认Ki值
        self.kd = tk.DoubleVar(value=2)  # 默认Kd值
        self.esc_ms = tk.DoubleVar(value=0.05)  # 默认esc值
        self.fish_wait = tk.IntVar(value=2000)  # 默认钓鱼间隔值
        self.detect_conf=tk.DoubleVar(value=0.65)
        self.title_height=tk.IntVar(value=30)

        # 创建输入控件
        self._create_entry(main_frame, "钓鱼窗口名字:", self.window_title, 0)
        self._create_spinbox(main_frame, "进度跟踪:", self.progress_tracking, 0, 1, 1)
        self._create_slider(main_frame, "比例系数(Kp):", self.kp, 1, 100, 2)
        self._create_slider(main_frame, "积分系数(Ki):", self.ki, 0.01, 10, 3)
        self._create_slider(main_frame, "微分系数(Kd):", self.kd, 0.01, 10, 4)
        self._create_spinbox(main_frame, "刺鱼延时(ms):", self.delay_ms, 1000, 10000, 5)
        self._create_spinbox(main_frame, "ESC检测(s):", self.esc_ms, 0.01, 1, 6)
        self._create_spinbox(main_frame, "钓鱼间隔(s):", self.fish_wait, 1000, 10000, 7)
        self._create_spinbox(main_frame, "斩杀检测置信度:", self.detect_conf, 0, 1, 8)
        self._create_spinbox(main_frame, "标题栏高度(pixel):", self.title_height, 0, 100, 9)

        # 确认按钮
        btn_frame = tb.Frame(main_frame)
        btn_frame.pack(pady=(20, 0))

        tb.Button(btn_frame, text="确认设置", bootstyle="success",
                  command=self.close_window, width=15).pack(pady=10)

        # 窗口关闭时的回调
        master.protocol("WM_DELETE_WINDOW", self.close_window)

    def _create_entry(self, parent, label_text, variable, row):
        """创建文本输入框"""
        frame = tb.Frame(parent)
        frame.pack(fill="x", pady=5)

        tb.Label(frame, text=label_text, width=15).pack(side="left", padx=(0, 10))

        entry = tb.Entry(frame, textvariable=variable)
        entry.pack(side="right", fill="x", expand=True)

    def _create_spinbox(self, parent, label_text, variable, from_, to, row):
        """创建数字输入框"""
        frame = tb.Frame(parent)
        frame.pack(fill="x", pady=5)

        tb.Label(frame, text=label_text, width=15).pack(side="left", padx=(0, 10))

        spinbox = tb.Spinbox(frame, from_=from_, to=to, textvariable=variable)
        spinbox.pack(side="right", fill="x", expand=True)

    def _create_slider(self, parent, label_text, variable, from_, to, row):
        """创建滑块控件"""
        frame = tb.Frame(parent)
        frame.pack(fill="x", pady=10)

        # 标签和值显示
        top_frame = tb.Frame(frame)
        top_frame.pack(fill="x")

        tb.Label(top_frame, text=label_text, width=15).pack(side="left")

        value_label = tb.Label(top_frame, textvariable=variable, width=5,
                               bootstyle="info")
        value_label.pack(side="right")

        # 滑块
        slider = tb.Scale(frame, from_=from_, to=to, variable=variable,
                          command=lambda v: variable.set(round(float(v), 2)),
                          bootstyle="info")
        slider.pack(fill="x")

    def close_window(self):
        """关闭窗口并保存设置"""
        self.settings = {
            "window_title": self.window_title.get(),
            "progress_tracking": self.progress_tracking.get(),
            "delay_ms": round(self.delay_ms.get(), 2),
            "kp": round(self.kp.get(), 2),
            "ki": round(self.ki.get(), 2),
            "kd": round(self.kd.get(), 2),
            'esc_ms':self.esc_ms.get(),
            'fish_wait': self.fish_wait.get(),
            'detect_conf':self.detect_conf.get(),
            'title_height': self.title_height.get(),
        }
        self.master.destroy()
def main(settings):
    try:
        # 初始化定位器
        qm = EscMonitor(settings['esc_ms'])
        qm.start()

        locator = GameOperator([settings['window_title']],settings['title_height'])

        # 获取窗口位置信息
        left, top, width, height = locator.get_window_rect()
        true_rect = (left + 7, top, width - 14, height - 7)

        print(f"窗口位置：X={left} Y={top} 宽度={width} 高度={height}")

        game_info = GameInfo((left, top, width, height),settings)
        game_info.start()

        while True:
            # time.sleep(0.5)
            delayMsecond(500)
            if not game_info.start_fish:
                locator.mouse_click(0.8083, 0.8375)
                delayMsecond(2000)
                locator.drag_relative(0.8083, 0.7875, Direction.UP, 100)
                delayMsecond(settings['delay_ms'])
                locator.click_relative(0.8083, 0.8375)
                delayMsecond(800)
            if game_info.start_fish:
                while True:
                    delayMsecond(max(1, round(game_info.click_delay * 1000)))
                    locator.click_relative(0.8483, 0.8075, 0.001)
                    bp = game_info.cy_process
                    if game_info.is_baigan:
                        game_info.is_baigan = False
                        locator.drag_relative(0.1562, 0.8019, Direction.LEFT)
                        locator.drag_relative(0.1562, 0.8019, Direction.RIGHT)
                    if bp >= 0.99:
                        locator.drag_relative(0.8483, 0.8075, Direction.UP)
                        print("刺鱼中")
                        delayMsecond(100)
                    if not game_info.start_fish:
                        delayMsecond(500)
                        if game_info.start_fish:
                            continue
                        else:
                            delayMsecond(1000)
                        print(f'斩杀与结束判断？{"斩杀" if game_info.start_kill else "结束"}')
                        kill = False
                        if game_info.start_kill:
                            kill = True
                            print('进入斩杀')
                            while game_info.start_kill:
                                res = game_info.kill_res
                                game_info.stop_cap()
                                if res:
                                    print('开启斩杀', res)
                                    locator.kill(res)
                                    delayMsecond(2000)
                                    game_info.start_cap()
                                    delayMsecond(100)
                                    if game_info.start_kill:
                                        game_info.down_conf()
                                    else:
                                        break
                                    # game_info.down_conf()
                                else:
                                    game_info.start_cap()
                            print('结束斩杀')
                            delayMsecond(1500)
                            if game_info.start_fish:
                                print('斩杀失败')
                        else:
                            if not kill:
                                print('完成一条')
                            break
            delayMsecond(settings['fish_wait'])
    except WindowNotFound as e:

        messagebox.showerror("错误", str(e))

if __name__ == "__main__":
    multiprocessing.freeze_support()
    root = tk.Tk()
    app = FishingSettingsWindow(root)

    # 运行主循环，等待用户操作
    root.mainloop()

    # 窗口关闭后，获取用户设置并执行剩余代码
    print("用户设置的参数:", app.settings)
    main( app.settings)


