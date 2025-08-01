"""一些低耦合的方法"""

import os
from loguru import logger  # log modules
import winreg
import json
import clr  # C# dll
from tkinter import messagebox, simpledialog
import sys
import shutil
import json
from tkinter import Tk


def pre_check() -> None:
    """
    运行前检查
    """
    if os.name != "nt":
        messagebox.showerror(
            "WPETool-环境检测", "本软件不支持在非Windows系统上运行, 程序将自动退出"
        )
        sys.exit("Not Windows")
    if not os.path.exists(f"{os.getcwd()}\\config.json"):  # 检查config是否存在
        _create_config()
    if (
        not os.path.exists(f"{os.getcwd()}\\modules\\repkg_dll")
        or len(os.listdir(f"{os.getcwd()}\\modules\\repkg_dll")) != 17
    ):  # 检查repkg.dll等文件是否存在
        ask = messagebox.showerror(
            "WPETool-环境检测",
            "所需的依赖项(RePKG.dll等文件)不完整,解决办法:\n"
            "1.如果您使用源码，请运行repkg_build.bat\n"
            "2.如果您使编译版程序(exe文件)，请重新下载程序",
        )
        sys.exit("RePKG module Not Found")


def _check_config(config: dict[str, dict[str, str | int]]) -> bool:
    """
    检查config完整性,
    Args:
        config: config信息
    """

    if (
        "workshop" not in config["Paths"]
        or not os.path.exists(config["Paths"]["workshop"])
        or "output" not in config["Paths"]
        or not os.path.exists((config["Paths"]["output"]))
        or "width" not in config["UI"]
        or not isinstance(config["UI"]["width"], int)
        or "height" not in config["UI"]
        or not isinstance(config["UI"]["height"], int)
        or "line_sum" not in config["UI"]
        or not isinstance(config["UI"]["line_sum"], int)
    ):
        return False

    else:
        return True


def _create_config() -> None:
    """
    创建config
    """
    workshop_path: str = _workshop_path()
    info: dict[str, dict[str, str | int]] = {
        "Paths": {"workshop": workshop_path, "output": _output_path()},
        "UI": {"width": 970, "height": 500, "line_sum": 9},
    }
    with open(file="config.json", mode="w", encoding="utf-8") as file:
        json.dump(info, file, indent=4)


def _output_path() -> str:
    """
    创建输出目录
    Returns:
        输出目录绝对路径
    """
    path: str = os.path.join(os.getcwd(), "output")
    if os.path.exists(path):
        pass
    else:
        os.mkdir(path)
    return path
def read_config() -> dict[str, dict[str, str | int]]:
    """
    读取config
    Returns:
         config文件信息
    """
    with open(file="config.json", mode="r", encoding="utf-8") as file:
        config: dict[str, dict[str, str | int]] = json.load(file)
        if _check_config(config):
            return config
        else:
            _create_config()
            messagebox.showwarning("WPE-config检查", "config.json出现问题，config信息已重置")
            return read_config()


def _workshop_path() -> str | None:
    """
    获取工坊路径和
    Returns:
         工坊路径
    """
    install_path: str = ""
    try:
        install_path = (  # winreg获取工坊路径
            winreg.QueryValueEx(
                winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SoftWare\Valve\Steam"),
                "SteamPath",
            )[0]
            + "/steamapps/workshop/content/431960"
        )
        install_path = install_path.replace("/", "\\")

    except FileNotFoundError:
        while not os.path.exists(install_path):  # 如果安装路径不存在，询问路径
            install_path = simpledialog.askstring(
                "WPETool-工坊路径获取",
                "对不起，程序无法自动读取工坊路径，请手动输入(留空以退出程序)",
            )
            if install_path is None:
                sys.exit("Workshop Path Do Not Get")
            install_path = install_path.replace("/", "\\")
    else:
        while not os.path.exists(install_path):  # 如果安装路径不存在，询问路径
            install_path = simpledialog.askstring(
                "WPETool-工坊路径获取",
                "对不起，程序自动读取读取到工坊路径不存在，请手动输入(留空以退出程序)",
            )
            if install_path is None:
                sys.exit("Workshop Path Not Found")
            install_path = install_path.replace("/", "\\")
        logger.info(f"WPE Workshop路径: {install_path}")
        return install_path


def _read_json_file(path: list[str]) -> dict[str, dict[str, str]]:
    """
    Args:
        path: 所有壁纸的文件夹
    Returns:
         json文件内的关键信息
    """

    json_file_ls: list[str] = [
        os.path.join(i, "project.json") for i in path
    ]  # 获取Json文件路径
    # logger.info(f"Json文件路径: {json_file_ls}")
    res: dict = {}  # 存储壁纸信息 {'文件夹': {'标题': ___, '类型': ___,}}
    flag: int = 0
    for i in json_file_ls:
        # logger.info(f'正在读取{i}的json文件')
        temp: dict = {}  # 存储读取到的信息
        with open(i, mode="r", encoding="utf-8") as f:
            content = json.load(f)  # 读取json文件

        if "title" in content and "type" in content:
            temp["title"] = content["title"]  # 读取标题
            temp["type"] = content["type"]  # 读取类型
            res[path[flag]] = temp  # 存入存储容器中
        else:
            logger.warning(f"读取{i}时遇到问题, 已跳过")
        flag += 1
    # logger.info(f"读取到的json信息:{res}")
    return res


def _get_files(info: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    """
    获取预览图片和壁纸本体的路径
    Args:
        info: 存储壁纸信息的字典
    Returns:
         更新后的字典
    """
    for folder in info.keys():
        for file in os.listdir(folder):
            if "preview" in file:  # 读取预览图
                info[folder]["preview_img"] = os.path.join(folder, file)
            elif file.endswith(".pkg") or file.endswith(".mp4"):  # 壁纸本体
                info[folder]["wpf_path"] = os.path.join(folder, file)
            # 如果两个都找到了，可以提前退出当前文件夹的遍历
            if "preview_img" in info[folder] and "wpf_path" in info[folder]:
                break
    return info


def get_info(path: str) -> dict[str, dict[str, str]]:
    """
    获取壁纸信息
    Args:
        path: 工坊路径
    Returns:
         存储所有壁纸信息的字典，格式如下
            {文件夹 :{title: 标题,
            type: 类型
            preview_img: 预览图片路径
            wpf_path: 壁纸文件路径}}

    """
    folders: list = [os.path.join(path, i) for i in os.listdir(path)]  # 壁纸文件夹
    # logger.info(f"所有文件夹: {folders}")
    info: dict[str, dict[str, str]] = _read_json_file(folders)  # json中获取到的壁纸信息
    info = _get_files(info)
    return info


def _mkpath(title: str, output_path:str) -> str:
    """
    创建壁纸导出的目录并返回该路径
    Args:
        title: 壁纸名字
    Returns:
        壁纸导出路径
    """
    title = (
        title.replace("|", "_")
        .replace(":", "_")
        .replace("<", "_")
        .replace(">", "_")
        .replace("*", "_")
        .replace(":", "_")
        .replace("?", "_")
        .replace("\\", "_")
        .replace("/", "_")
    )
    path = os.path.join(output_path, title)
    os.mkdir(path)
    return path


def extract_pkg(path: str, title: str, output_path: str) -> None:
    """
    导出scene类型的壁纸
    Args:
        title: 壁纸的名字
        path: 壁纸文件路径
        output_path: 输出目录
    :return:
    """
    # logger.info(f"工作目录:{os.getcwd()}")
    clr.AddReference(f"{os.getcwd()}\\modules\\repkg_dll\\RePKG.dll")  # 引用dll
    from RePKG.Command import (
        Extract,
        ExtractOptions,
    )  # 对不起，但只能这样不遵守PEP导入了，都怪跨语言编程:(

    options = ExtractOptions()  # 导出选项类
    # 设置导出属性
    options.Input = path  # *.pkg文件路径
    options.OutputDirectory = _mkpath(title, output_path)  # 导出路径
    Extract.Action(options)  # 开始导出


def extract_mp4(path: str, title: str, output_path: str) -> None:
    """
    导出视频类壁纸
    Args:
        path: 壁纸文件路径
        title: 壁纸标题
        output_path: 输出目录
    """
    shutil.move(path, _mkpath(title, output_path))  # 看什么看啊, *.mp4直接复制不就行了awa


def set_center(root: Tk, width: int, height: int, office: int = 0) -> None:
    """
    设置窗口居中显示
    Args:
        root: 窗口名
        width: 窗口宽
        height: 窗口高
        office: 窗口偏移值

    """
    root.geometry(
        f"{width}x{height}+{(root.winfo_screenwidth() - width) // 2}+{(root.winfo_screenheight() - height) // 2 + office}"
    )


def about() -> None:
    """
    关于界面
    Returns:

    """
    messagebox.showinfo(
        "WPETool-关于",
        "本程序作者:MicGan\n"
        "贡献者(排名不分先后,包括上一版程序):\n"
        "system-windows\n"
        "CodeCrafter-TL\n"
        "WYT\n"
        "本程序基于Apacha 2.0协议发布,请遵守该协议使用\n"
        "开发者不会对您使用本程序所造成的后果承担责任\n"
        "通过本程序‘导出’功能所得到的数据(或文件)的知识产权归该数据(或文件)的作者所有,请勿侵犯其权利,与‘导出’功能所得到的数据(或文件)有关的法律纠纷与开发者无关",
    )

def save(config: dict[str, dict[str, str | int]]) -> None:
    """
    保存config
    Args:
        config: config文件

    Returns:

    """
    with open("config.json", mode="w", encoding="utf-8") as f:
        pass