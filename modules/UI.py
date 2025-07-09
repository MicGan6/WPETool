"""
有关UI的类
"""

from loguru import logger
import tkinter as tk

# import modules.tools as tools
from PIL import Image, ImageTk


class ImageButton(tk.Button):
    """图片按钮类，继承自Button类"""

    def __init__(self, img: ImageTk.PhotoImage, x: int = 0, y: int = 0):
        """
        :param img: tk格式图片的内存地址
        :param x: 按钮横坐标
        :param y: 按钮纵坐标
        """
        self.x, self.y = x, y  # 按钮横纵位置
        # logger.info(img)
        tk.Button.__init__(self, image=img)
        self.place(x=self.x, y=self.y)


class MainWindow(tk.Tk):
    """主窗口"""

    def __init__(self, info: dict[str, dict[str, str]]):
        """
        主窗口的构造函数
        :param info: 壁纸信息的字典
        """
        super().__init__()  # 初始化Tkinter.TK
        self.info: dict[str, dict[str, str]] = info  # 壁纸信息
        #self.count = len(self.info.keys())
        #计算Button坐标时要用到的变量
        self.x: int #横坐标
        self.y: int #纵坐标
        self.line: int #Button在第几行
        # self.img_ls: list[ImageTk.PhotoImage] = [] #存储tkinter化的预览图的内存地址
        self.geometry("1000x700")  # 设置窗口大小
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
        flag: int = 1 # 是第几个壁纸
        for key, value in self.info.items():
            # logger.info(value['preview_img'])

            # logger.info(f'Button传参:{self.img_ls[-1]}')
            self.calc_xy(flag=flag)
            logger.info(f'id:{flag}, x: {self.x}, y: {self.y}')
            self.info[key]["button"] = ImageButton(img=value["preview_img"], x=self.x, y=self.y)
            flag += 1

        #logger.info(f"信息字典:\n{self.info}")

    def _deal_image(self, img: str) -> ImageTk.PhotoImage:
        """
        处理预览图片(辅助方法)
        :param img: 预览图片路径
        :return: tk格式的预览图地址
        """
        # logger.info(f"img:{img}")
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
            if flag // 12 == self.line:
                self.x += 100
            elif flag // 12 != self.line:
                self.x = 0
                self.y += 100
                self.line = flag // 12



