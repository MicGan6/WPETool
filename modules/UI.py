"""有关UI的类"""

from loguru import logger
import tkinter as tk

import modules.tools as tools
from PIL import Image, ImageTk


class ImageButton(tk.Button):
    """图片按钮类，继承自Button类"""

    def __init__(self, img: ImageTk.PhotoImage, master: tk.Canvas, x: int, y: int):
        """
        :param img: tk格式图片的内存地址
        :param x: 按钮横坐标
        :param y: 按钮纵坐标
        """
        super().__init__(image=img)
        self.x, self.y = x, y  # 按钮横纵位置
        self.master = master
        self.place(x=self.x, y=self.y)


class ButtonCanvas(tk.Canvas):
    """图片按钮所在的父容器, 继承自Canvas类"""

    def __init__(self, size: tuple[int, int], master: tk.Tk, scrollbar: tk.Scrollbar):
        """
        :param size: 画布的大小(x, y)
        :param master: 父容器
        :param scrollbar: 滑动条
        """
        self.x = size[0]
        self.y = size[1]
        self.master = master
        self.scrollbar = scrollbar
        super().__init__(
            master=self.master,
            width=self.x,
            height=self.y,
            highlightthickness=0,
            yscrollcommand=self.scrollbar.set,
            yscrollincrement=10,
            scrollregion=(0, 0, self.x, self.y),
        )
        self.pack(fill="both", expand=True)


class MainWindow(tk.Tk):
    """主窗口"""

    def __init__(self, info: dict[str, dict[str, str]]):
        """
        :param info: 壁纸信息的字典
        """
        super().__init__()  # 调用tkinter.TK的构造函数
        self.info: dict[str, dict[str, str]] = info  # 壁纸信息
        # 计算Button坐标时要用到的变量
        self.x: int  # 横坐标
        self.y: int  # 纵坐标
        self.line: int = 0  # Button在第几行
        self.button_canvas: ButtonCanvas  # 按钮的父容器
        self.scrollbar: tk.Scrollbar # 滑动条
        self.create_canvas()  # 创建ButtonCanvas
        self.scrollbar.configure(command=self.button_canvas.yview)
        self.geometry("930x800")  # 设置窗口大小
        self.title("Wallpaper Engine: 壁纸引擎 第三方工具")
        self.resizable(False, False)
        self.deal_image()  # 处理图片
        self.create_button()  # 创建按钮
        self.mainloop()  # 启动！

    def deal_image(self) -> None:
        """
        处理预览图片
        """
        for key, value in self.info.items():
            self.info[key]["preview_img"] = self._deal_image(value["preview_img"])

    def create_button(self) -> None:
        """
        创建Button
        """

        """
        此处修改info，格式如下
        {文件夹 :{title: 标题,
                type: 类型
                preview_img: 预览图片(tk格式)
                wpf_path: 壁纸文件路径
                button: 按钮组件所在内存地址}}
        """
        flag: int = 1  # 是第几个壁纸
        for key, value in self.info.items():
            self.calc_xy(flag=flag)
            logger.info(f"flag:{flag}, x: {self.x}, y: {self.y}")
            self.info[key]["button"] = ImageButton(
                img=value["preview_img"], master=self.button_canvas, x=self.x, y=self.y
            )
            flag += 1

        # logger.info(f"信息字典:\n{self.info}")

    def _deal_image(self, img: str) -> ImageTk.PhotoImage:
        """
        处理预览图片(辅助方法)
        :param img: 预览图片路径
        :return: tk格式的预览图地址
        """
        image = Image.open(img)
        image = ImageTk.PhotoImage(
            image.resize((100, 100))
        )  # 将图片类型适应tkinter并设置大小
        return image

    def calc_xy(self, flag: int) -> None:
        """
        计算按钮横纵坐标
        :param flag: 第几个壁纸
        """
        if flag == 1:
            self.x, self.y, self.line = 0, 0, 0
        else:
            if flag // 9 <= self.line or flag % 9 == 0:
                self.x += 100
            elif flag // 9 > self.line:
                self.x = 0
                self.y += 100
                self.line = flag // 9

    def create_canvas(self):
        """创建Canvas和Scrollbar"""
        self.scrollbar = tk.Scrollbar(master=self, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        flag = len(self.info.keys())
        # 得到最后一个按钮的位置
        x: int = 9 * 100
        y: int = (flag // 9) * 100
        logger.info(f"Canvas大小: {x,y}")
        self.button_canvas = ButtonCanvas(
            size=(x, y), master=self, scrollbar=self.scrollbar
        )
        self.scrollbar.configure(command=self.button_canvas.yview)
