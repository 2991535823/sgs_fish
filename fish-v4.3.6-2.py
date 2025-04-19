import multiprocessing
import time
import tkinter as tk

from tkinter import messagebox


from control import Direction, TouchController
from coordinate import GameCoordinate
from exit import EscMonitor
from gameexception import ConfigFail,Experiment
from getscale import get_scale,get_real_resolution,get_system_scale
from info import GameInfo,get_path

from setgui import  FishingSettingsWindow
from mouseoperator import GameOperator,WindowNotFound

def delayMsecond(t):
    start, end = 0, 0
    start = time.time_ns()  # 精确至ns级别
    while end - start < t * 1000000:
        end = time.time_ns()

def main(settings):
    try:
        # 初始化定位器
        ss=get_system_scale()
        settings['scale']=ss
        if ss!=1.0:
            raise ConfigFail('系统缩放请设置为100%')
        qm = EscMonitor(settings['esc_ms'])
        qm.start()
        locator = GameOperator([settings['window_title']],settings)
        # 获取窗口位置信息
        left, top, width, height = locator.get_window_rect()
        print(locator.get_window_rect())
        screen_rect = get_real_resolution()
        if left+width>screen_rect[0] or top+height>screen_rect[1]:
            raise ConfigFail('模拟器窗口请勿贴边')
        standard_height=round(width*0.5625)
        if not (standard_height-5<height - settings['title_height']<standard_height+5):
            raise ConfigFail(f'游戏窗口配置出错，先设置模拟器800x450，\n当前模拟器窗口：X={left} Y={top} 宽度={width} 高度={height}\n(尝试)请调整"标题栏高度"让屏幕比率接近0.5625\n当前比率:{(height - settings["title_height"])/width},"标题栏高度"参数尝试设置{round(height-width*0.5625)}附近')
        game_info = GameInfo((left, top, width, height),settings)
        game_info.start()
        switch_lure=time.perf_counter()
        while True:
            delayMsecond(500)
            if not game_info.start_fish:#释放鱼饵与刺鱼
                locator.mouse_click(*settings['fish'])
                delayMsecond(2000)
                locator.drag_relative(*settings['fish'], Direction.UP, 100)
                if time.perf_counter() - switch_lure > 6:
                    print('切换鱼饵')
                    locator.mouse_click(*settings['switch'])
                    switch_lure = time.perf_counter()
                    continue
                else:
                    delayMsecond(settings['delay_ms'])
                    locator.click_relative(*settings['fish'])
                    delayMsecond(800)
            if game_info.start_fish:#钓鱼函数
                bg_time=time.perf_counter()#摆杆计时器
                while True:
                    delayMsecond(max(1.5, round(game_info.click_delay * 1000)))
                    locator.click_relative(*settings['click'], 0.001)
                    bp = game_info.cy_process

                    if game_info.is_baigan and time.perf_counter()-bg_time>1:
                        game_info.is_baigan = False
                        bg_time=time.perf_counter()
                        locator.drag_relative(*settings['baigan_p'], Direction.LEFT)
                        locator.drag_relative(*settings['baigan_p'], Direction.RIGHT)
                    if bp >= 0.99:
                        locator.drag_relative(*settings['click'], Direction.UP)
                        delayMsecond(1000)
                    if not game_info.start_fish:
                        delayMsecond(800)
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
                                    locator.kill(res)
                                    delayMsecond(2000)
                                    game_info.start_cap()
                                    delayMsecond(100)
                                    if game_info.start_kill:
                                        pass
                                        # game_info.down_conf()
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
                                switch_lure = time.perf_counter()
                            break
            delayMsecond(settings['fish_wait'])
    except WindowNotFound as e:
        messagebox.showerror("错误", str(e))
    except ConfigFail as e:
        messagebox.showerror("参数错误",str(e))

if __name__ == "__main__":
    multiprocessing.freeze_support()
    root = tk.Tk()
    app = FishingSettingsWindow(root)
    root.mainloop()
    main(app.settings)


