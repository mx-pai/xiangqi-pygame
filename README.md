# Xiangqi Pygame Project

三人组：mx； wyf; wty。目标是按照“规则内核 core + UI + AI”分层，先实现骨架、再升级到 Pygame 交互，最后引入 AI。

## 工作空间布局

```
Course/SoftEngineer/
	.python-version         # uv 管理的 Python 版本配置
	README.md              # 本文档
	pyproject.toml         # uv/poetry 依赖配置
	uv.lock                # uv 环境锁文件
	cn_chess/              # uv 创建的虚拟环境（已经在 .gitignore）
	xiangqi/               # 真正的象棋项目代码
```

控制器层在 `xiangqi/` 下，外层的 `cn_chess/` 由 uv 全权管理，避免多个子目录再独立初始化 git/venv。

## 项目结构

```
xiangqi/
	app.py                 # 启动脚本（当前 CLI 版）
	requirements.txt       # Pygame 依赖
	core/                  # 棋盘、走法、规则骨架
		const.py
		move.py
		board.py
		movegen.py           # 伪合法 & 合法框架
		rules.py             # 将军、生死判断占位
	ai/                    # 估值、搜索、Zobrist（后续）
	ui/                    # Pygame 渲染 + 输入
```

## 快速开始

1. **安装依赖**（首选 `uv`）：
	```bash
	uv env           # 确保当前目录下有 cn_chess/ 环境
	uv sync          # 目前只有 pygame>=2.5）
    uv add ...
	```

2. **运行 CLI 骨架验证**：
	```bash
    cd xiangqi
	uv run python app.py
	```
	输出应为初始棋盘、当前轮到谁、随机走一步后的棋盘。

## 合作流程 & Git 指南

1. 先从 `main` 拉最新（`git fetch origin && git switch feature/<name> && git rebase origin/main` 或 `merge`），每人保留主题分支（例 `feature/cannon`, `feature/ui-draft`）。
2. 功能完成后推送自己的 `feature/...` 分支并在 GitHub 开 PR，目标分支为 `main`。
3. `main` 上禁止直接 `git push`（除非是 CI/受权操作）；所有变更都经 PR 审查合并。合入前先在本地 `git switch main && git pull origin main` 保持同步。

## 约定与提示

- `.gitignore` 已排除虚拟环境（例如 `cn_chess/`），不要将其提交。
- `app.py` 用来验证 movegen 逻辑，UI 与 AI 改成模块后再由入口控制。
- 修改核心文件后运行 `uv run python xiangqi/app.py` 验证基本走法；再进 UI 测试鼠标交互。

## 计划

建议自己写代码；参考仓库：[js实现中国象棋](https://github.com/itlwei/Chess/blob/master/js/common.js)
- 重在练习协作，团队一起推进。
- 具体的 uv 教程/ git 操作可参考官方文档或 AI 工具中的指南；需要时可以在群里共享链接。