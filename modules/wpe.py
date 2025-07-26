"""
Main Process
"""

from tkinter import (
    Toplevel,
    Tk,
    Label,
    Scrollbar,
    X,
    Y,
    LEFT,
    RIGHT,
    VERTICAL,
    Button,
    messagebox,
    Menu,
    Scale,
    Entry
)
from copy import deepcopy
from PIL import Image, ImageTk
from PIL.ImageChops import offset

import modules.tools as tools
from threading import Thread
from loguru import logger
import modules.UI as UI
import time


class SettingWindow(Toplevel):
    def __init__(self, main):
        super().__init__()
        self.title("WPETool-设置")
        self.geometry('700x700')
        self.resizable(False, False)
        self.main = main  # 主窗口信息
        self.config: dict[str, dict[str, str | int]] = deepcopy(self.main.config)
        self.workshop_path_label: Label
        self.workshop_path_entry: Entry
        self.output_path_label: Label
        self.output_path_entry: Entry
        self.save_button: Button
        self.create_widgets()
    def create_widgets(self):
        self.workshop_path_label = Label(master=self, text='工坊路径:  ')
        self.workshop_path_label.grid(row=1, column=1)
        self.workshop_path_entry = Entry(master=self, width=len(self.config['Paths']['workshop']))
        self.workshop_path_entry.insert(0, self.config['Paths']['workshop'].capitalize())
        self.workshop_path_entry.grid(row=1, column=2)

        self.output_path_label = Label(master=self, text='输出目录:  ')
        self.output_path_label.grid(row=2, column=1)
        self.output_path_entry = Entry(master=self, width=len(self.config['Paths']['output']))
        self.output_path_entry.insert(0, self.config['Paths']['output'])
        self.output_path_entry.grid(row=2, column=2)

        self.save_button = Button(master=self,text="保存", command=self.save)
        self.save_button.grid(row=4, column=4)
    def save(self):
        self.config['Paths']['workshop'] = self.workshop_path_entry.get()
        self.config['Paths']['output'] = self.output_path_entry.get()






class DetailWindow(Toplevel):
    """壁纸详细信息窗口"""

    def __init__(self, path: str, info: dict[str, str]):
        """
        Args:
            path: 壁纸所在文件夹
            info: 该壁纸的详细信息
        """
        super().__init__()
        self.resizable(False, False)
        self.path = path
        self.output_path: str
        tools.set_center(self, 400, 400)  # 居中 500 * 400 窗口
        self.preview_img = info["preview_img"]  # 预览图片内存地址
        self.w_title: str = info["title"]  # 壁纸标题
        self.type: str = info["type"]  # 壁纸类型
        self.wpf_path: str = info.get("wpf_path", None)
        self.img_label: Label  # 预览图的标签
        self.title_label: Label
        self.type_label: Label
        self.extract_button: Button
        self.title(f"{self.w_title}")
        self.create_label()

    def create_label(self) -> None:
        """
        创建图片和标题
        """

        # logger.info(f"所选壁纸信息{self.path}")
        self.img_label = Label(master=self, image=self.preview_img)
        self.img_label.grid(row = 1, column=3)
        self.title_lavel = Label(master=self, text=self.w_title)
        self.title_lavel.grid(row=2, column=3)
        self.type_label = Label(master=self, text=f"类型: {self.type}")
        self.type_label.grid(row=3, column=3)
        self.extract_button = Button(master=self, text="导出", command=self.extract)
        self.extract_button.grid(row=4, column=3)

    def extract(self):
        if self.wpf_path != None:
            if self.type == "scene":
                tools.extract_pkg(self.wpf_path, self.w_title, self.output_path)
            elif self.type == "video":
                tools.extract_mp4(self.wpf_path, self.w_title, self.output_path)
        else:
            messagebox.showwarning("WPETool-对不起.....", "还在写呢，不急，好吗~")
            self.wm_attributes("-topmost", True)  # 保持窗口最顶层


class WPEApplication(Tk):
    """主进程"""

    def __init__(self):
        """
        构造函数
        Args:
            width: 窗口宽
            height: 窗口高
            line_sum: 单行显示的壁纸数量
            workshop_path: Workshop路径
            output_path: 输出文件夹
        """
        super().__init__()  # 调用tkinter.TK的构造函数
        self.config: dict[str, dict[str, str | int]] = tools.read_config()
        self.info: dict[str, dict[str, str]]  # 壁纸信息
        self.workshop_path: str
        self.output_path: str
        # 计算Button坐标时要用到的变量
        self.line_sum: int
        self.x: int  # 横坐标
        self.y: int  # 纵坐标
        self.line: int = 0  # Button在第几行
        self.button_canvas: UI.ButtonCanvas  # 按钮的父容器
        self.scrollbar: Scrollbar  # 滑动条
        self.loading_label: Label  # 加载中文字
        self.mainmenu: Menu  # 主菜单容器
        self.optionmenu: Menu  # 选项菜单容器
        self.title("WPETool")
        self.resizable(False, False)
        self.loading_ui()
        # self.after(10, self.setup)
        thr = Thread(target=self.setup)
        thr.start()
        # self.setup()
        self.mainloop()  # 启动！（保持主进程循环）

    def loading_ui(self):
        tools.set_center(
            root=self, width=self.config["UI"]["width"], height=self.config["UI"]["width"], office=-50
        )  # 居中 970 * 700 向上偏移 50 窗口
        self.loading_label = Label(self, text="加载中...", font=("Microsoft YaHei", 20))
        self.loading_label.place(relx=0.5, rely=0.5, anchor="center")
        self.update()
        self.loading_label.update()

    def setup(self):
        """
        实现异步初始化
        """
        """
        INFO存储所有壁纸信息，格式如下
        {文件夹 :{title: 标题,
                type: 类型
                preview_img: 预览图片
                wpf_path: 壁纸文件路径}}
        """
        self.workshop_path = self.config["Paths"]["workshop"]
        self.output_path = self.config["Paths"]["output"]
        self.line_sum = self.config["UI"]["line_sum"]
        self.info: dict[str, dict[str, str]] = tools.get_info(self.workshop_path)
        # logger.info(f"tools info: {self.info}")
        time.sleep(5)
        self.after(1, self.loading_label.destroy)
        self.after(100, self.setup_ui)

    def setup_ui(self):
        self.create_canvas()  # 创建ButtonCanvas
        self.scrollbar.configure(command=self.button_canvas.yview)
        self.set_menu()  # 设置菜单
        self.deal_image()  # 处理图片
        self.create_button()  # 创建按钮

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
        flag: int = 1  # 第几个壁纸
        max_x = 0  # 记录最大x坐标（用于更新scrollregion）
        max_y = 0  # 记录最大y坐标
        for key, value in self.info.items():
            self.calc_xy(flag=flag)
            # logger.info(f"flag:{flag}, x: {self.x}, y: {self.y}")
            # 创建按钮（不在这里放置）
            btn = UI.ImageButton(img=value["preview_img"], path=key, info=value, output_path=self.output_path)
            # 用Canvas的create_window将按钮嵌入Canvas，坐标为(self.x, self.y)
            self.button_canvas.create_window(
                self.x, self.y, window=btn, anchor="nw"  # anchor="nw"表示左上角对齐
            )
            self.info[key]["button"] = btn  # 存储按钮引用
            # 更新最大x和y（按钮大小100x100，所以最大坐标需加100）
            current_max_x = self.x + 100
            current_max_y = self.y + 100
            if current_max_x > max_x:
                max_x = current_max_x
            if current_max_y > max_y:
                max_y = current_max_y
            flag += 1

        # 所有按钮创建后，更新Canvas的scrollregion为包含所有按钮的区域
        self.button_canvas.configure(scrollregion=(0, 0, max_x, max_y))
        self.button_canvas.update_scrollregion()

    def _deal_image(self, img: str) -> ImageTk.PhotoImage:
        """
        处理预览图片(辅助方法)
        Args:
            img: 预览图片路径
        Returns:
            tk格式的预览图地址
        """
        # logger.info(f"识别图片地址：{img}")
        image = Image.open(img)
        image = ImageTk.PhotoImage(
            image.resize((100, 100))
        )  # 将图片类型适应tkinter并设置大小
        return image

    def calc_xy(self, flag: int) -> None:
        """
        计算按钮横纵坐标
        Args:
            flag: 第几个壁纸
        """
        if flag == 1:
            self.x, self.y, self.line = 0, 0, 0
        else:
            if flag // self.line_sum <= self.line or flag % self.line_sum == 0:
                self.x += 100
            elif flag // self.line_sum > self.line:
                self.x = 0
                self.y += 100
                self.line = flag // self.line_sum

    def create_canvas(self):
        """创建Canvas和Scrollbar"""
        self.scrollbar = Scrollbar(master=self, orient=VERTICAL)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        flag = len(self.info.keys())
        # 得到最后一个按钮的位置
        x: int = 9 * 100
        y: int = (flag // 9) * 100
        logger.info(f"Canvas大小: {x,y}")
        self.button_canvas = UI.ButtonCanvas(
            size=(x, y), master=self, scrollbar=self.scrollbar
        )
        self.scrollbar.configure(command=self.button_canvas.yview)

    def set_menu(self):
        """
        设置菜单
        """
        self.mainmenu = Menu(self)  # 主菜单
        self.optionmenu = Menu(self.mainmenu, tearoff=False)
        self.optionmenu.add_command(label="设置", command=self.setting_window)
        self.optionmenu.add_command(label="关于", command=tools.about)
        self.mainmenu.add_cascade(label="选项", menu=self.optionmenu)
        self.configure(menu=self.mainmenu)

    def setting_window(self) -> None:
        """
        创建设置窗口
        Returns:

        """
        SettingWindow(main=self)