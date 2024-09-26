# Auto Duolingo

Auto Duolingo 是一个自动化工具，旨在帮助用户在 Duolingo 应用程序中自动完成练习和任务。

目前只支持 Android 设备。

## 安装

1. 克隆仓库：

```bash
git clone https://github.com/chess99/auto-duolingo.git
cd auto-duolingo
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

## 运行

确保您的 Android 设备已启用 USB 调试模式并连接到计算机。

运行主程序：

```bash
python -m auto_duolingo.main
```

## 项目结构

- `auto_duolingo/`: 主要的应用程序代码
  - `DuolingoBot.py`: 机器人的核心逻辑
  - `constants.py`: 常量定义
  - `question_answer.py`: 问题回答逻辑
  - `string_util.py`: 字符串处理工具
  - `translate.py`: 翻译功能
  - `ui_helper/`: UI 交互辅助模块
- `db/`: 数据库相关代码
- `tests/`: 测试文件
- `llm/`: 大语言模型解题相关代码 (未完成)
- `ocr/`: OCR 相关代码 (未完成)
- `requirements.txt`: 项目依赖
- `Makefile`: 包含常用命令
- `.gitignore`: Git 忽略文件配置

## 贡献

欢迎贡献代码、报告问题或提出新功能建议。请遵循以下步骤：

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 免责声明

本项目仅用于教育和研究目的。请遵守 Duolingo 的使用条款和服务条款。作者不对因使用此工具而导致的任何问题负责。
