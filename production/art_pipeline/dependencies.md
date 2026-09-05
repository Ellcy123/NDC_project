# 美术脚本依赖与换机安装

这份清单覆盖 `skill_sources.json` 登记的 17 个主 Skill 使用的 Python 图像、审核和 H3 视频处理脚本，以及仓库中的公共美术工具。自有脚本随所属仓库交付；Python、第三方包和 FFmpeg 在每台电脑单独安装。工程侧三个 H3 Skill 也使用同一份依赖清单。

## 从策划仓库根目录创建环境

推荐安装 64 位 Python 3.11。以下 PowerShell 命令在本仓库根目录执行，不依赖原作者的用户名、磁盘目录或个人 Hermes 环境：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r production/art_pipeline/requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -c "import PIL,numpy,cv2; print(PIL.__version__,numpy.__version__,cv2.__version__)"
```

未安装 Windows `py` 启动器时，用已确认版本的 `python` 代替第一条命令的 `py -3.11`。macOS/Linux 可使用 `python3.11 -m venv .venv`，随后将命令中的解释器替换为 `.venv/bin/python`。本次实测平台是 Windows x64；其他平台须准备对应平台和 Python 版本的 wheel，并运行同样的检查。

`.venv/` 是本机环境，不入 Git，也不要从另一台电脑复制虚拟环境。运行自有脚本时使用这里创建的解释器，脚本路径按主 Skill 所属仓库解析。Skill 中的 `uv run --with ... python` 示例表示包依赖；团队环境已经安装锁定清单后，可直接用该虚拟环境的 Python 执行对应脚本及原参数，避免另建一个依赖版本不同的临时环境。

离线机器需要事先取得这三个精确版本及对应平台的 wheel。准备好后执行：

```powershell
.\.venv\Scripts\python.exe -m pip install --no-index --find-links <团队离线wheel目录> -r production/art_pipeline/requirements.txt
```

仓库内的 requirements 文件不会自动包含 wheel；个人 uv 缓存也不是团队交付物。本次没有执行联网下载或安装。

## 锁定版本与验证依据

| 包 | 锁定版本 | 用途与约束 |
|---|---|---|
| Pillow | 12.1.1 | PNG、Alpha、裁切、合成和审核图；基础安装没有必需的外部 Python 包依赖 |
| NumPy | 2.4.6 | 像素数组、蒙版、音频数值分析；包元数据要求 Python >= 3.11 |
| opencv-python | 5.0.0.93 | H3 视频处理；Python >= 3.9 时要求 NumPy >= 2，本清单满足该条件 |

只安装 `opencv-python`。不要在同一环境叠装 `opencv-python-headless`、`opencv-contrib-python` 等同样提供 `cv2` 的发行包。包发行版本 `5.0.0.93` 对应本次导入时报告的 `cv2.__version__ == 5.0.0`。

2026-09-05 的离线检查使用 Windows x64 / Python 3.11.3，读取已有 Pillow 和 uv 缓存中的 NumPy、OpenCV 包元数据及 wheel 标签。NumPy/Pillow 为 CPython 3.11 Windows x64 wheel，OpenCV 为 Windows x64 ABI3 wheel。通过 `-I -S -B` 隔离启动，显式加载选中的包目录，排除默认 site-packages 中混装的 OpenCV。实测结果：

- 三个包导入成功，版本与清单一致。
- Pillow RGBA 图像转 NumPy、OpenCV 缩放和 RGBA/BGRA 转换通过。
- 工程主实现 `ndc-h3-avatar-delivery/scripts/prepare_delivery.py` 导入通过。
- 主线程在确认这三个精确版本及 NumPy/OpenCV 的实际加载来源后，使用已有测试验证：29 项人物入景测试、7 项表情测试全部通过；测试子进程继承选定包的环境。

这次验证没有安装包、生成视频、访问生成 API 或改写资产。完整依赖组合尚未经过 pip/uv 安装验收：离线 uv 尝试因 Pillow 未缓存而无法解析，随后使用已有包运行上述验证。因此，本次结果证明选定包可兼容运行这些现有测试，不等同于已经交付完整离线安装包或通过全流程视频验收。版本升级后应重新检查依赖元数据，并运行相应脚本的现有验证。

## FFmpeg 与 Node

H3 的音频 QA、视频准备和交付核验还需要单独安装 FFmpeg，安装包必须同时包含 `ffmpeg` 和 `ffprobe`。将其 `bin` 目录加入当前用户或系统的 `PATH`，重新打开终端检查：

```powershell
ffmpeg -version
ffprobe -version
```

本机实测两者均为 8.0.1。Python 的 requirements 不会安装它们，也不要将本机可执行文件和 DLL 复制进 Skill 仓库。`audio_reference_qa.py` 支持 `--ffmpeg` 指定位置；`prepare_delivery.py` 与 `stage_delivery.py` 通过 PATH 查找，因此仍应配置 PATH。

Node.js 仅用于 Skill 看板相关脚本，不是这些 Python 美术脚本的运行依赖；本机可查询版本为 24.11.0。Midjourney 浏览器会话、图像生成工具、Photoshop MCP 和 RunningHub 凭据属于各自工具或服务的配置，不能通过复制 Python 环境替代。密钥不得写入依赖清单或 Git。

## Git 交付与参考素材

自有 `.py`、`.ps1`、`.js` 等脚本，以及运行时必需的模板、规则和数据，必须纳入所属仓库的 Git；不能只留在个人 Skills、临时目录或被 ignore 的位置。兼容入口应定位已跟踪的主实现，不能复制出新的独立实现。共同依赖本仓库 `scripts/art_pipeline/` 的工程流程，需要同时检出策划仓库，并按公共路径配置连接两个仓库。

本次只读审计时，17 个主 Skill 内的 71 个脚本文件（含测试）已被当前 Git 索引收录；公共路径/任务工具、三个视觉校验器和道具 Skill 的三张锁定模板也已收录。索引收录不代表已完成 commit/push；交付前仍需由提交负责人确认最终提交范围。虚拟环境、字节码、下载缓存、候选和过程产物不属于这些自有源码。

四个同事维护的道具 Skill 保持原目录内容；旧外部校验器地址按公共工作区文档映射至本仓库实现。`evidence_delivery.py` 的 Unity 禁写检查仍含固定旧工程路径，且没有可覆盖该检查根目录的 CLI 参数；必须由公共任务入口核实 `--output-dir` 位于受管 `payload`，不能将可配置输出误认为已经修复这个保护边界。

缺失的 PMH 原始头像、历史表情、UI 遮挡参考和旧角色风格库属于素材待恢复，不属于 pip 安装问题。应恢复原始授权素材，或记录用户明确选择的替代来源；不能拿同名角色卡默认为已批准头像。新任务的候选与过程图仍写入公共工具返回的项目外 `payload`，现有活跃任务素材保留原位。
