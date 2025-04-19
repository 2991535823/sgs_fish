import  os
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
import yaml

from coordinate import GameCoordinate
from gameexception import ConfigFail
from info import  get_path
from getscale import  get_system_scale,get_real_resolution,get_screen_size
class FishingSettingsWindow:
    def __init__(self, master):
        self.master = master
        master.title("钓鱼参数设置")
        resolution=get_real_resolution()
        screen=get_screen_size()
        self.sys_scale=get_system_scale()
        print(self.sys_scale)
        self.res_scale=round((resolution[0]/1920)*resolution[1]/1080,1)
        master.geometry(f"{int(resolution[0]*0.25)}x{int(resolution[1]*0.85)}+50+10")

        master.resizable(False, True)
        self.config_path=os.path.expanduser('~\Documents')+'\\fishing_config.yaml'
        # 使用ttkbootstrap的darkly主题
        self.style = tb.Style(theme="darkly")
        self.style.configure('auto.TButton',font=("微软雅黑", int(10/self.sys_scale)))
        self.style.configure('success.TButton',font=("微软雅黑", int(10/self.sys_scale)),backgroud="#00ff00")
        self.font=("微软雅黑", int(10*self.res_scale/self.sys_scale))
        self.head_font=("微软雅黑", int(20*self.res_scale/self.sys_scale),"bold")
        self.info_font=("微软雅黑", int(12*self.res_scale/self.sys_scale))
        # 创建主容器
        self.main_frame = tb.Frame(master)
        self.main_frame.pack(fill="both", expand=True)

        # 顶部标题区域
        self.top_frame = tb.Frame(self.main_frame, padding=20)
        self.top_frame.pack(fill="x")

        tb.Label(self.top_frame, text="脚本免费使用，倒卖者死全家\n  作者B站ID：199276846", font=self.head_font,
                 bootstyle="primary").pack(pady=(0,0))

        # 中间内容区域 - 用于放置基本和高级参数
        self.content_frame = tb.Frame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True, padx=20,pady=(0,0))

        # 底部按钮区域
        self.bottom_frame = tb.Frame(self.main_frame, padding=(20,10))
        self.bottom_frame.pack(fill="x", side="bottom")
        self.settings={}
        self.config_settings={}
        self._config_set()
        # 创建基本参数界面
        self._create_basic_settings()
        # 高级参数切换按钮
        self.advanced_btn = tb.Button(
            self.bottom_frame,
            text="显示高级参数(针对其他模拟器)",
            bootstyle="outline",
            style='auto.TButton',
            command=self.toggle_advanced_settings
        )
        self.advanced_btn.pack(pady=10)
        self.donate_btn=tb.Button(
            self.bottom_frame,
            text="捐赠",
            style='auto.TButton',
            bootstyle="info",
            command=self.toggle_donate
        )
        self.donate_btn.pack(side="left", expand=True, padx=5)
        tb.Button(
            self.bottom_frame,
            text="读取配置",
            bootstyle="info",
            style='auto.TButton',
            command=self.load_settings
        ).pack(side="left", expand=True, padx=5)

        tb.Button(
            self.bottom_frame,
            text="保存配置",
            bootstyle="info",
            style='auto.TButton',
            command=self.save_settings
        ).pack(side="left", expand=True, padx=5)
        # 确认按钮（保持在底部）
        tb.Button(self.bottom_frame, text="确认设置(请设置地图!!!)", bootstyle="success",
            style='success.TButton',command=self.close_window, width=100).pack()

        # 窗口关闭时的回调
        master.protocol("WM_DELETE_WINDOW", self.close_window)
    def _config_set(self):
        self.config_settings['window_title']= tk.StringVar(value="模拟器")
        self.config_settings['progress_tracking'] = tk.DoubleVar(value=0.9)
        self.config_settings['delay_ms'] = tk.IntVar(value=6000)
        self.config_settings['kp'] = tk.DoubleVar(value=50)
        self.config_settings['ki'] = tk.DoubleVar(value=1)
        self.config_settings['kd'] = tk.DoubleVar(value=2)
        self.config_settings['esc_ms'] = tk.DoubleVar(value=0.05)
        self.config_settings['fish_wait'] = tk.IntVar(value=2000)
        self.config_settings['detect_conf'] = tk.DoubleVar(value=0.65)
        self.config_settings['title_height'] = tk.IntVar(value=35)
        self.config_settings['cap_fps'] = tk.IntVar(value=30)
        self.config_settings['debug'] = tk.BooleanVar(value=False)

        # 高级参数变量
        self.config_settings['kill_tl'] = [tk.DoubleVar(value=0.1625), tk.DoubleVar(value=0.1111)]
        self.config_settings['kill_br'] = [tk.DoubleVar(value=0.8375), tk.DoubleVar(value=0.2889)]
        self.config_settings['cy_tl'] = [tk.DoubleVar(value=0.29), tk.DoubleVar(value=0.14)]
        self.config_settings['cy_br'] = [tk.DoubleVar(value=0.71), tk.DoubleVar(value=0.1667)]
        self.config_settings['process_tl'] = [tk.DoubleVar(value=0.31), tk.DoubleVar(value=0.06)]
        self.config_settings['process_br'] = [tk.DoubleVar(value=0.7), tk.DoubleVar(value=0.1330)]
        self.config_settings['fish'] = [tk.DoubleVar(value=0.8083), tk.DoubleVar(value=0.8375)]
        self.config_settings['click'] = [tk.DoubleVar(value=0.8483), tk.DoubleVar(value=0.8075)]

        self.config_settings['up'] = [tk.DoubleVar(value=0.1854), tk.DoubleVar(value=0.6111)]
        self.config_settings['down'] = [tk.DoubleVar(value=0.1854), tk.DoubleVar(value=0.8479)]
        self.config_settings['left'] = [tk.DoubleVar(value=0.1124), tk.DoubleVar(value=0.7347)]
        self.config_settings['right'] = [tk.DoubleVar(value=0.2584), tk.DoubleVar(value=0.7347)]
        self.config_settings['wind'] = [tk.DoubleVar(value=0.8090), tk.DoubleVar(value=0.6121)]
        self.config_settings['fire'] = [tk.DoubleVar(value=0.7416), tk.DoubleVar(value=0.7347)]
        self.config_settings['thunder'] = [tk.DoubleVar(value=0.8090), tk.DoubleVar(value=0.8479)]
        self.config_settings['electricity'] = [tk.DoubleVar(value=0.8764), tk.DoubleVar(value=0.7347)]
        self.config_settings['switch'] = [tk.DoubleVar(value=0.6178), tk.DoubleVar(value=0.2602)]
        self.config_settings['delay'] = [tk.DoubleVar(value=0.1), tk.DoubleVar(value=0.12)]

    def _create_donate(self):
        """创建捐赠界面，显示捐赠二维码图片"""
        if hasattr(self, 'donate_frame'):
            self.donate_frame.destroy()
        self.donate_frame = tb.Frame(self.content_frame, padding=(10, 10))
        self.donate_frame.pack(fill="both", expand=True)
        try:
            wechat_img = tk.PhotoImage(file=get_path("wechat.png"))  # 替换为你的微信二维码路径
            alipay_img = tk.PhotoImage(file=get_path("alipay.png"))  # 替换为你的支付宝二维码路径

            # 微信二维码部分（上）
            wechat_frame = tb.Frame(self.donate_frame)
            wechat_frame.pack(fill="x", pady=(0, 20))  # 添加下边距分隔两个二维码
            tb.Label(
                wechat_frame,
                text="微信捐赠",
                font=self.font,
                bootstyle="info"
            ).pack(pady=(0, 5))
            tb.Label(
                wechat_frame,
                image=wechat_img
            ).pack()

            # 支付宝二维码部分（下）
            alipay_frame = tb.Frame(self.donate_frame)
            alipay_frame.pack(fill="x")
            tb.Label(
                alipay_frame,
                text="支付宝捐赠",
                font=self.font,
                bootstyle="info"
            ).pack(pady=(0, 5))
            tb.Label(
                alipay_frame,
                image=alipay_img
            ).pack()

            # 保存图片引用
            self.donate_frame.wechat_img = wechat_img
            self.donate_frame.alipay_img = alipay_img

            # 底部文字
            tb.Label(
                self.donate_frame,
                text="扫描上方二维码即可捐赠，您的支持是我前进的动力！",
                font=self.font,
                bootstyle="secondary"
            ).pack(pady=(20, 0))

        except Exception as e:
            print(str(e))

    def _create_basic_settings(self):
        """创建基本参数设置界面"""
        # 清除可能存在的旧框架
        if hasattr(self, 'basic_frame'):
            self.basic_frame.destroy()

        self.basic_frame = tb.Frame(self.content_frame, padding=(0, 0))
        self.basic_frame.pack(fill="both", expand=True)

        # 创建输入控件
        self._create_entry(self.basic_frame, "钓鱼窗口:", self.config_settings['window_title'], 0)
        self._create_spinbox(self.basic_frame, "进度跟踪:", self.config_settings['progress_tracking'], 0, 1, 1)
        self._create_slider(self.basic_frame, "比例系数(Kp):", self.config_settings['kp'], 1, 100, 2)
        self._create_slider(self.basic_frame, "积分系数(Ki):", self.config_settings['ki'], 0.01, 10, 3)
        self._create_slider(self.basic_frame, "微分系数(Kd):", self.config_settings['kd'], 0.01, 10, 4)
        self._create_spinbox(self.basic_frame, "刺鱼延时(ms):", self.config_settings['delay_ms'], 1000, 10000, 5)
        self._create_spinbox(self.basic_frame, "ESC检测(s):", self.config_settings['esc_ms'], 0.01, 1, 6)
        self._create_spinbox(self.basic_frame, "钓鱼间隔(ms):", self.config_settings['fish_wait'], 1000, 10000, 7)
        self._create_spinbox(self.basic_frame, "斩杀检测置信度:", self.config_settings['detect_conf'], 0, 1, 8)
        self._create_spinbox(self.basic_frame, "标题栏高度(pixel):", self.config_settings['title_height'], 0, 100, 9)
        self._create_spinbox(self.basic_frame, "检测帧率（fps):", self.config_settings['cap_fps'], 15, 240, 10)
        self._create_point_box(self.basic_frame, "拖动延迟:", self.config_settings['delay'], 0, 1, 11)
        self._create_switch(self.basic_frame,'日志(Experiment)',self.config_settings['debug'],12)

        tb.Label(
            self.basic_frame,
            text="系统屏幕缩放设置100%，模拟器800x450分辨率\n钓鱼窗口=(MuMu/雷电)模拟器,标题栏高度尝试设置35\n当前版本适配三国杀V4.3.6-1",
            font=self.info_font,
            bootstyle="primary",
        ).pack(pady=(20, 20))
    def _create_advanced_settings(self):
        """创建高级参数设置界面"""
        if hasattr(self, 'advanced_frame'):
            self.advanced_frame.destroy()

        self.advanced_frame = tb.Frame(self.content_frame, padding=(0, 0))
        self.advanced_frame.pack(fill="both", expand=True)

        # 添加高级参数控件
        self._create_point_box(self.advanced_frame, "钓鱼点击点:", self.config_settings['click'], 0, 1, 1)
        self._create_point_box(self.advanced_frame, "滑动钓鱼点:", self.config_settings['fish'], 0, 1, 2)

        self._create_point_box(self.advanced_frame, "爆发进度_左上:", self.config_settings['cy_tl'], 0, 1, 3)
        self._create_point_box(self.advanced_frame, "爆发进度_右下:", self.config_settings['cy_br'], 0, 1, 4)
        self._create_point_box(self.advanced_frame, "钓鱼进度_左上:", self.config_settings['process_tl'], 0, 1, 5)
        self._create_point_box(self.advanced_frame, "钓鱼进度_右下:", self.config_settings['process_br'], 0, 1, 6)

        self._create_point_box(self.advanced_frame, "斩杀_左上:", self.config_settings['kill_tl'], 0, 1, 7)
        self._create_point_box(self.advanced_frame, "斩杀_右下:", self.config_settings['kill_br'], 0, 1, 8)
        self._create_point_box(self.advanced_frame, "上:", self.config_settings['up'], 0, 1, 9)
        self._create_point_box(self.advanced_frame, "下:", self.config_settings['down'], 0, 1, 10)
        self._create_point_box(self.advanced_frame, "左:", self.config_settings['left'], 0, 1, 11)
        self._create_point_box(self.advanced_frame, "右:", self.config_settings['right'], 0, 1, 12)
        self._create_point_box(self.advanced_frame, "风:", self.config_settings['wind'], 0, 1, 13)
        self._create_point_box(self.advanced_frame, "火:", self.config_settings['fire'], 0, 1, 14)
        self._create_point_box(self.advanced_frame, "雷:", self.config_settings['thunder'], 0, 1, 15)
        self._create_point_box(self.advanced_frame, "电:", self.config_settings['electricity'], 0, 1, 16)
        self._create_point_box(self.advanced_frame, "鱼饵切换:", self.config_settings['switch'], 0, 1, 17)

    def toggle_donate(self):
        if hasattr(self, 'donate_frame') and self.donate_frame.winfo_ismapped():
            # If donate frame is shown, hide it and show basic settings
            self.donate_frame.pack_forget()
            self.basic_frame.pack(fill="both", expand=True)
            self.donate_btn.config(text="捐赠")
        else:
            # If donate frame is not shown, hide other frames and show donate frame
            if hasattr(self, 'basic_frame'):
                self.basic_frame.pack_forget()
            if hasattr(self, 'advanced_frame'):
                self.advanced_frame.pack_forget()
            self._create_donate()
            self.donate_btn.config(text="返回")

    def toggle_advanced_settings(self):
        """切换显示/隐藏高级参数"""
        if hasattr(self, 'advanced_frame') and self.advanced_frame.winfo_ismapped():
            # 如果高级参数已显示，则隐藏
            self.advanced_frame.pack_forget()
            self.basic_frame.pack(fill="both", expand=True)
            self.advanced_btn.config(text="显示高级参数")
        else:
            # 如果高级参数未显示，则显示
            if hasattr(self, 'basic_frame'):
                self.basic_frame.pack_forget()
            if hasattr(self, 'donate_frame'):
                self.donate_frame.pack_forget()
            self._create_advanced_settings()
            self.advanced_btn.config(text="隐藏高级参数")

        # 调整窗口大小以适应内容

    # 其余方法保持不变...
    def _create_entry(self, parent, label_text, variable, row):
        """创建文本输入框"""
        frame = tb.Frame(parent)
        frame.pack(fill="x", pady=5)

        tb.Label(frame,font=self.font, text=label_text, width=15).pack(side="left", padx=(0, 10))

        entry = tb.Entry(frame, textvariable=variable,font=self.font)
        entry.pack(side="right", fill="x", expand=True)

    def _create_spinbox(self, parent, label_text, variable, from_, to, row):
        """创建数字输入框"""
        frame = tb.Frame(parent)
        frame.pack(fill="x", pady=5)

        tb.Label(frame, font=self.font,text=label_text, width=15).pack(side="left", padx=(0, 10))

        spinbox = tb.Spinbox(frame, from_=from_, to=to, textvariable=variable,font=self.font)
        spinbox.pack(side="right", fill="x", expand=True)

    def _create_point_box(self, parent, label_text, variable, from_, to, row):
        """创建数字输入框"""
        frame = tb.Frame(parent)
        frame.pack(fill="x", pady=5)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        tb.Label(frame,font=self.font, text=label_text, width=15).grid(row=0, column=0, sticky="w", padx=(0, 10))
        spinbox1 = tb.Spinbox(frame, from_=from_, to=to, textvariable=variable[0],font=self.font)
        spinbox1.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        spinbox2 = tb.Spinbox(frame, from_=from_, to=to, textvariable=variable[1],font=self.font)
        spinbox2.grid(row=0, column=2, sticky="ew")

    def _create_slider(self, parent, label_text, variable, from_, to, row):
        """创建滑块控件"""
        frame = tb.Frame(parent)
        frame.pack(fill="x", pady=10)

        # 标签和值显示
        top_frame = tb.Frame(frame)
        top_frame.pack(fill="x")

        tb.Label(top_frame,font=self.font, text=label_text, width=15).pack(side="left")

        value_label = tb.Label(top_frame, textvariable=variable, width=5,font=self.font,
                               bootstyle="info")
        value_label.pack(side="right")

        # 滑块
        slider = tb.Scale(frame, from_=from_, to=to, variable=variable,
                          command=lambda v: variable.set(round(float(v), 2)),
                          bootstyle="info")
        slider.pack(fill="x")
    def _create_switch(self, parent, label_text, variable,row):
        frame = tb.Frame(parent)
        frame.pack(fill="x", pady=5)

        tb.Label(frame, font=self.font, text=label_text, width=15).pack(side="left", padx=(0, 10))

        check = tb.Checkbutton(frame, variable=variable,bootstyle="success-round-toggle")
        check.pack(side="right", fill="x")
    def load_settings(self):
        """从YAML文件加载配置"""
        try:
            # 尝试从默认配置文件路径加载
            if not os.path.exists(self.config_path):
                messagebox.showwarning("警告", "配置文件不存在，将使用默认配置")
                return
            with open(self.config_path, 'r', encoding='utf-8') as f:
                yaml_settings = yaml.safe_load(f)
            if not yaml_settings:
                messagebox.showwarning("警告", "配置文件为空，将使用默认配置")
                return
            def update_coords(var, coords):
                if coords and len(coords) == 2:
                    var[0].set(coords[0])
                    var[1].set(coords[1])
            # 更新所有变量
            for key,value in yaml_settings.items():
                if type(value)!=list:
                    self.config_settings[key].set(value)
                else:
                    update_coords(self.config_settings[key],value)
            messagebox.showinfo("成功", "配置已成功加载！")

        except Exception as e:
            messagebox.showerror("错误", f"加载配置时出错: {str(e)}")

    def save_settings(self):
        """将当前配置保存到YAML文件"""
        try:
            self.config_to_settings()
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.settings, f, allow_unicode=True, sort_keys=False)
            messagebox.showinfo("成功", f"配置已成功保存到 {self.config_path}")
            self.master.deiconify()
        except Exception as e:
            messagebox.showerror("错误", f"保存配置时出错: {str(e)}")
            self.master.deiconify()
    def config_to_settings(self):
        for key,value in self.config_settings.items():
            if type(value)!=list:
                self.settings[key]=value.get()
            else:
                self.settings[key]=[i.get() for i in value]
    def close_window(self):
        self.config_to_settings()
        self.master.destroy()
if __name__=='__main__':
    root = tk.Tk()
    app = FishingSettingsWindow(root)
    # 运行主循环，等待用户操作
    root.mainloop()

    try:
        if get_system_scale() != 1.0:
            ConfigFail("系统缩放非100%")
        # GameOperator([settings['window_title']], settings)
        # GameCoordinate()
    except ConfigFail as e:
        messagebox.showerror(str(e))
    print(app.settings)