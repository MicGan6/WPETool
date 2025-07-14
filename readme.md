# Wallpaper Engine 第三方工具

```
          _____                    _____                    _____                _____                   _______                  _______                   _____  
         /\    \                  /\    \                  /\    \              /\    \                 /::\    \                /::\    \                 /\    \ 
        /::\____\                /::\    \                /::\    \            /::\    \               /::::\    \              /::::\    \               /::\____\
       /:::/    /               /::::\    \              /::::\    \           \:::\    \             /::::::\    \            /::::::\    \             /:::/    /
      /:::/   _/___            /::::::\    \            /::::::\    \           \:::\    \           /::::::::\    \          /::::::::\    \           /:::/    / 
     /:::/   /\    \          /:::/\:::\    \          /:::/\:::\    \           \:::\    \         /:::/~~\:::\    \        /:::/~~\:::\    \         /:::/    /  
    /:::/   /::\____\        /:::/__\:::\    \        /:::/__\:::\    \           \:::\    \       /:::/    \:::\    \      /:::/    \:::\    \       /:::/    /   
   /:::/   /:::/    /       /::::\   \:::\    \      /::::\   \:::\    \          /::::\    \     /:::/    / \:::\    \    /:::/    / \:::\    \     /:::/    /    
  /:::/   /:::/   _/___    /::::::\   \:::\    \    /::::::\   \:::\    \        /::::::\    \   /:::/____/   \:::\____\  /:::/____/   \:::\____\   /:::/    /     
 /:::/___/:::/   /\    \  /:::/\:::\   \:::\____\  /:::/\:::\   \:::\    \      /:::/\:::\    \ |:::|    |     |:::|    ||:::|    |     |:::|    | /:::/    /      
|:::|   /:::/   /::\____\/:::/  \:::\   \:::|    |/:::/__\:::\   \:::\____\    /:::/  \:::\____\|:::|____|     |:::|    ||:::|____|     |:::|    |/:::/____/       
|:::|__/:::/   /:::/    /\::/    \:::\  /:::|____|\:::\   \:::\   \::/    /   /:::/    \::/    / \:::\    \   /:::/    /  \:::\    \   /:::/    / \:::\    \       
 \:::\/:::/   /:::/    /  \/_____/\:::\/:::/    /  \:::\   \:::\   \/____/   /:::/    / \/____/   \:::\    \ /:::/    /    \:::\    \ /:::/    /   \:::\    \      
  \::::::/   /:::/    /            \::::::/    /    \:::\   \:::\    \      /:::/    /             \:::\    /:::/    /      \:::\    /:::/    /     \:::\    \     
   \::::/___/:::/    /              \::::/    /      \:::\   \:::\____\    /:::/    /               \:::\__/:::/    /        \:::\__/:::/    /       \:::\    \    
    \:::\__/:::/    /                \::/____/        \:::\   \::/    /    \::/    /                 \::::::::/    /          \::::::::/    /         \:::\    \   
     \::::::::/    /                  ~~               \:::\   \/____/      \/____/                   \::::::/    /            \::::::/    /           \:::\    \  
      \::::::/    /                                     \:::\    \                                     \::::/    /              \::::/    /             \:::\    \ 
       \::::/    /                                       \:::\____\                                     \::/____/                \::/____/               \:::\____\
        \::/____/                                         \::/    /                                      ~~                       ~~                      \::/    /
         ~~                                                \/____/                                                                                         \/____/ 
```

## 一、简介
这是一个针对Wallpaper Engine开发的第三方工具，主要功能是帮助用户管理Wallpaper Engine工坊中的壁纸。通过该工具，用户可以方便地查看壁纸的详细信息，包括标题、类型、预览图片等。

## 二、原理概述

### 1. 路径获取
工具首先会尝试从Windows注册表中获取Steam的安装路径，然后根据该路径拼接出Wallpaper Engine工坊的路径。具体代码在`tools.py`文件的`get_path`函数中实现：
```python
def get_path() -> str:
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
        install_path = None
    finally:
        logger.info(f"Steam路径: {install_path}")
        return install_path
```

### 2. 信息读取
获取到工坊路径后，工具会遍历该路径下的所有壁纸文件夹，读取每个文件夹中的`project.json`文件，从中提取壁纸的标题和类型信息。这部分功能由`tools.py`文件的`_read_json_file`函数完成：
```python
def _read_json_file(path: list[str]) -> dict[str, dict[str, str]]:
    json_file_ls: list[str] = [
        os.path.join(i, "project.json") for i in path
    ]
    res: dict = {}
    flag: int = 0
    for i in json_file_ls:
        temp: dict = {}
        with open(i, mode="r", encoding="utf-8") as f:
            content = json.load(f)
        try:
            temp["title"] = content["title"]
            temp["type"] = content["type"]
        except KeyError:
            logger.warning(f"读取{i}时遇到问题, 已跳过")
            continue
        else:
            res[path[flag]] = temp
        flag += 1
    return res
```

### 3. 预览图片和壁纸文件路径获取
工具会继续遍历每个壁纸文件夹，查找包含`preview`的文件作为预览图片，查找以`.pkg`或`.mp4`结尾的文件作为壁纸文件。这两个功能分别由`_get_preview_file`和`_get_wp_file`函数实现：
```python
def _get_preview_file(info: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    for i in info.keys():
        for j in os.listdir(i):
            if "preview" in j:
                info[i]["preview_img"] = os.path.join(i, j)
                break
    return info

def _get_wp_file(info: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    for i in info.keys():
        for j in os.listdir(i):
            if j.endswith(".pkg") or j.endswith(".mp4"):
                info[i]["wpf_path"] = os.path.join(i, j)
                break
    return info
```

### 4. 用户界面
使用Python的`tkinter`库创建用户界面。在主窗口中，会显示所有壁纸的预览图片按钮，用户点击按钮可以查看壁纸的详细信息。具体的界面类和功能在`UI.py`和`wpe.py`文件中实现。

## 三、使用方法
1. **编译**：运行`build.bat`脚本进行编译，该脚本会使用`dotnet`编译`RePKG`模块。
```batch
@off
...
dotnet build RePKG.csproj -c Release /p:OutputType=Library
...
```
2. **运行**：在编译完成后，运行`main.py`文件启动工具。
```python
import modules.tools as tools
import modules.UI as ui
import modules.wpe as wpe

if __name__ == "__main__":
    wpe.WPEApplication()
```

## 四、版权声明
本工具的代码版权归原作者所有。未经作者允许，请勿将代码用于商业用途。协议待定，后续会根据具体情况确定开源协议。

## 五、注意事项
- 本工具依赖于Steam和Wallpaper Engine的安装，确保你的系统中已经正确安装了这两个软件。
- 如果在使用过程中遇到问题，可以查看日志文件获取详细信息。日志功能使用`loguru`库实现。