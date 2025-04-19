import time
import tkinter as tk
import re
from tkinter import messagebox

import pygetwindow as gw

from control import TouchController
from coordinate import GameCoordinate
from gameexception import  WindowNotFound,ConfigFail

class SimpleWindowLocator:
    def __init__(self, title_keywords):
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

        if len(self.valid_windows)>1:
            raise ConfigFail(f'存在多个匹配窗口，不要将脚本放到名为(MUMU/雷电)的文件夹\n请修改脚本存放文件夹名称，当前钓鱼窗口名字匹配了{len(self.valid_windows)}个窗口\n请从下列匹配列表填写完整模拟器名称\n[{" | ".join([i.title for i in self.valid_windows])}]')
        # DPI转换补偿计算
        def scale(value):
            return int(value * self.dpi_scale + 0.5)  # 四舍五入

        return (
            scale(target.left),
            scale(target.top),
            scale(target.width),
            scale(target.height)
        )
class GameOperator(SimpleWindowLocator):
    def __init__(self, keywords,settings):
        super().__init__(keywords)
        self.controller = TouchController(drag_duration=settings['delay'])
        self.bias_y=settings['title_height']
        self.window_rect = self.get_window_rect()
        self.gc=GameCoordinate(self.window_rect,self.bias_y)
        print('当前比率',((self.window_rect[3]-self.bias_y)/self.window_rect[2]),'推荐比率16：9（0.5625）')
        if settings['window_title']== '三国杀':
            if 0.562<((self.window_rect[3] - 30) / self.window_rect[2])<0.563:
                print('窗口大小合适')
            else:
                width=800
                height=450+self.bias_y
                print(f'重新设置模拟器窗口 宽度{width},高度{height}')
                self.valid_windows[0].resizeTo(width, height)
                self.window_rect = self.get_window_rect()
                print(f'{self.window_rect}')
                self.gc = GameCoordinate(self.window_rect,self.bias_y)
                resize_btn=(self.gc.cal_pose(1,1)[0]-50,self.gc.cal_pose(1,1)[1]-50)
                self.controller.click(resize_btn,0.5)
                time.sleep(2)
                messagebox.showinfo("提示","重设游戏窗口比例16：9")

        self.kbs={'up':settings['up'],'down':settings['down'],'left':settings['left'],'right':settings['right'],
                  'feng':settings['wind'],'huo':settings['fire'],'lei':settings['thunder'],'dian':settings['electricity']}
    def lambda_click(self,x,y):
        self.controller.click(self.gc.cal_pose(x,y),0.1)
    def click_relative(self, rel_x, rel_y,delay=0.1):
        """点击相对窗口的位置（0~1范围）"""
        self.controller.click(self.gc.cal_pose(rel_x,rel_y),delay)
    def mouse_click(self,rel_x,rel_y):
        self.controller.mouse_click(self.gc.cal_pose(rel_x,rel_y))
    def drag_relative(self, rel_x,rel_y,dir,dis=100,duration=None):
        """窗口内相对坐标拖拽"""
        self.controller.drag(self.gc.cal_pose(rel_x,rel_y),dir,dis,duration)
    def kill(self,res):
        for action in res:
            self.lambda_click(*self.kbs[action])