from win32 import win32api, win32gui, win32print
from win32.lib import win32con

from win32.win32api import GetSystemMetrics
import ctypes


def get_real_resolution():
    """获取真实的分辨率"""
    hDC = win32gui.GetDC(0)
    # 横向分辨率
    w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
    # 纵向分辨率
    h = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
    return w, h
def get_screen_size():
    """获取缩放后的分辨率"""
    hDC = win32gui.GetDC(0)
    # 横向分辨率
    w = win32print.GetDeviceCaps(hDC, win32con.DESKTOPHORZRES)
    # 纵向分辨率
    h = win32print.GetDeviceCaps(hDC, win32con.DESKTOPVERTRES)
    scale=get_system_scale()
    return int(w/scale), int(h/scale)
def get_scale():
    real_resolution = get_real_resolution()
    screen_size = get_screen_size()
    return round(real_resolution[0] / screen_size[0], 2)
def get_system_scale():
    """获取系统缩放比例"""
    try:
        # 对于 Windows 系统
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    except:
        # 对于非 Windows 系统或获取失败的情况
        scale_factor = 1.0
    return scale_factor
if __name__ == '__main__':
    print(get_screen_size())
    print(get_scale())