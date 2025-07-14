"""一些低耦合的方法"""

import os
from loguru import logger  # log modules
import winreg
import json
import clr  # C# dll
from tkinter import messagebox
import sys
import shutil


def pre_check() -> None:
    """
    检查依赖
    :return:
    """
    if not os.path.exists(f"{os.getcwd()}\\output"):
        os.mkdir(f"{os.getcwd()}\\output")
    if (
        not os.path.exists(f"{os.getcwd()}\\modules\\repkg_dll")
        or len(os.listdir(f"{os.getcwd()}\\modules\\repkg_dll")) != 17
    ):
        ask = messagebox.showerror(
            "环境检测",
            "所需的依赖项(RePKG.dll等文件)不完整, 如果您使用源码，请运行repkg_build.bat, 如果您是exe文件用户，请重新下载程序",
        )
        sys.exit("RePKG module Not Found")


def get_path() -> str:
    """
    获取工坊路径和工作目录
    :return: 工坊路径
    """

    try:
        install_path: str = (
            winreg.QueryValueEx(
                winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SoftWare\Valve\Steam"),
                "SteamPath",
            )[0]
            + "/steamapps/workshop/content/431960"
        )
        install_path = install_path.replace("/", "\\")
    except FileNotFoundError:
        messagebox.showerror(
            "错误", "未检测到Wallpaper Engine已安装，请检查是否正确安装"
        )
        sys.exit("WPE Not Found")
    else:
        logger.info(f"Steam路径: {install_path}")
        return install_path


def _read_json_file(path: list[str]) -> dict[str, dict[str, str]]:
    """
    读取壁纸json信息
    :param path: 所有壁纸的文件夹
    :return: json文件内的关键信息
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

        try:
            temp["title"] = content["title"]  # 读取标题
            temp["type"] = content["type"]  # 读取类型
        except KeyError:
            logger.warning(f"读取{i}时遇到问题, 已跳过")
            continue
        else:
            # logger.info(f"{i} 中的json信息: {temp}")
            res[path[flag]] = temp  # 存入存储容器中
        flag += 1
    # logger.info(f"读取到的json信息:{res}")
    return res


def _get_files(info: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    """
    获取预览图片和壁纸本体的路径
    :param info: 存储壁纸信息的字典
    :return: 更新后的字典
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
    :param path: 工坊路径
    :return: 存储所有壁纸信息的字典，格式如下
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


def _mkpath(title: str) -> str:
    """
    创建壁纸导出的目录并返回该路径
    :param title: 壁纸名字
    :return: 壁纸导出路径
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
    path = os.getcwd() + "\\output" + f"\\{title}"
    os.mkdir(path)
    return path


def extract_pkg(path: str, title: str) -> None:
    """
    导出scene类型的壁纸
    :param title: 壁纸的名字
    :param path: 壁纸文件路径
    :return:
    """
    # logger.info(f"工作目录:{os.getcwd()}")
    clr.AddReference(os.getcwd() + "\\modules\\repkg_dll\\RePKG.dll")  # 引用dll
    from RePKG.Command import Extract, ExtractOptions

    options = ExtractOptions()  # 导出选项类
    # 设置导出属性
    options.Input = path  # *.pkg文件路径
    options.OutputDirectory = _mkpath(title)  # 导出路径
    Extract.Action(options)  # 开始导出


def extract_mp4(path: str, title: str) -> None:
    """
    导出视频类壁纸
    :param path: 壁纸文件路径
    :param title: 壁纸标题
    :return:
    """
    shutil.move(path, _mkpath(title))  # 看什么看啊, *.mp4直接复制不就行了awa
