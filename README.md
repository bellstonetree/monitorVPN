# VPN Monitor

用于监控指定网络接口状态的 Windows 桌面指示器。

程序会显示一个始终置顶的小圆点：

- 灰色：尚未选择网络接口
- 绿色：所选网络接口已连接
- 红色：所选网络接口未连接、不存在或无法检查

## 运行要求

- Windows
- Python 3.9 或更高版本
- Tkinter
- Windows 系统命令 `netsh`

本项目仅使用 Python 标准库，不需要安装第三方软件包。

程序会在显示指示器前检查上述运行环境。如果缺少一个或多个组件，启动提示会逐项列出缺少的组件名。

## 启动方式

日常启动请使用 `run_hidden.vbs`，`run.bat` 是故障排查入口。

双击 `run_hidden.vbs` 可在不显示或闪现命令行窗口的情况下启动程序。如果隐藏启动失败，程序会显示错误对话框，并将详细信息保存到 `vpn_monitor_error.log`。

如需排查故障，请双击 `run.bat`，或运行：

```powershell
python vpn_monitor.py
```

如果系统中没有可用的 `python`，请从以下地址安装 Python 3：

https://www.python.org/downloads/windows/

安装时请勾选“Add python.exe to PATH”。

## 操作方法

- 按住鼠标左键拖动小圆点，可以调整其位置。
- 双击小圆点会启动 `C:\Program Files (x86)\Anycast\Anycast.exe`。程序不存在或启动失败时不会显示错误提示。
- 右键单击小圆点并选择 `Select interface`，可以选择要监控的网络接口。
- 右键单击小圆点并选择 `Exit`，可以退出程序。
- 小圆点获得焦点时，按 `Esc` 键可以退出程序。

## 配置

所选网络接口会保存到脚本所在目录的 `vpn_monitor_config.json`。下次启动时，程序会自动使用上次选择的网络接口。

如有需要，可以修改 `vpn_monitor.py` 文件开头附近的以下常量：

```python
REFRESH_INTERVAL_MS = 1000
DOT_SIZE = 28
WINDOW_MARGIN_RIGHT = 24
WINDOW_MARGIN_TOP = 80
```

程序通过以下命令读取网络接口名称：

```powershell
netsh interface ipv4 show interfaces
```

## 状态检查

程序主要运行以下命令：

```powershell
netsh interface ipv4 show interfaces
```

只有当所选网络接口所在行的 `State` 为 `connected` 时，程序才会将该接口视为已连接。
