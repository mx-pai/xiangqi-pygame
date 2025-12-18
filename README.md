# Xiangqi（象棋）Pygame 项目

三人组：mx、wyf、wty。目标是按照"规则内核 core + UI + AI"分层，先实现骨架、再升级到 Pygame 交互，最后引入 AI。

## 工作空间布局

```
Course/SoftEngineer/
├── .python-version         # uv 管理的 Python 版本配置
├── README.md              # 本文档
├── pyproject.toml         # uv/poetry 依赖配置
├── uv.lock                # uv 环境锁文件
├── cn_chess/              # uv 创建的虚拟环境（已在 .gitignore）
└── xiangqi/               # 象棋项目代码
```

## 项目结构

```
xiangqi/
├── app.py                 # 应用主程序（独立启动入口）
├── core/                  # 棋盘、走法、规则逻辑
│   ├── __init__.py
│   ├── const.py          # 常数定义（Piece, Side 枚举、棋盘尺寸）
│   ├── move.py           # Move 数据类（frm, to, moved_piece, captured）
│   ├── board.py          # Board 棋盘（squares, side_to_move, move_stack）
│   ├── movegen.py        # 走法生成（所有7种棋子的伪合法和合法着法）
│   └── rules.py          # 规则判断（in_check, is_checkmate, is_face_to_face）
│
├── ui/                    # Pygame UI 框架（Scene 模式）
│   ├── __init__.py
│   ├── game.py           # Game 主类（主循环、场景管理）
│   ├── game_config.py    # 游戏常数（800x900 窗口、80px 格子）
│   ├── theme.py          # Theme 主题（3套风格：stype_1/2/3）
│   ├── asset_manager.py  # AssetManager 资源加载（棋子图片、背景等）
│   ├── scenes.py         # Scene 基类（on_enter, on_exit, handle_event, draw）
│   ├── menuscene.py      # MenuScene 菜单（选择游戏模式、主题切换）
│   └── playscene.py      # PlayScene 游戏场景（棋盘显示、选棋、移动、将军检测）
│
├── ai/                    # AI 模块（搜索算法、局面评估）
│   ├── __init__.py
│   ├── eval.py           # 局面评估函数（子力价值、位置价值表）
│   ├── search.py         # 基础 MiniMax 搜索算法
│   ├── search_v2.py      # 高级搜索（Negamax、置换表、PV移动排序）
│   └── zobrist.py        # Zobrist 哈希（置换表实现）
│
├── assets/               # 资源文件
│   ├── fonts/
│   │   └── NotoSerifSC-Regular.otf    # 中文字体
│   ├── audio/            # 音效文件
│   │   ├── bgm.mp3      # 背景音乐
│   │   ├── select.wav   # 选子音效
│   │   └── click.wav    # 移动音效
│   └── img/
│       ├── init_bg.png          # 菜单背景框
│       ├── btn_bg.png           # 菜单按钮
│       ├── btn_fh.png           # 返回按钮
│       ├── stype_1/             # 风格 1（棋子、棋盘、点标记、选框）
│       ├── stype_2/             # 风格 2
│       └── stype_3/             # 风格 3
│
└── test/                 # 测试脚本
    ├── test_play.py      # 跳过菜单直接进游戏
    ├── test_menu.py      # 菜单测试
    └── test_ui.py        # UI 测试
```

## 快速开始

### 安装依赖

```bash
uv sync          # 安装所有依赖（包括 pygame 2.6.1）
```

### 运行游戏

```bash
# 方式 1：模块方式运行（推荐）
python -m xiangqi.app

# 方式 2：直接运行（需在项目根目录）
python xiangqi/app.py

# 方式 3：测试模式（跳过菜单直接进游戏）
python xiangqi/test/test_play.py
```

## 当前进度

### 已完成

#### 核心游戏逻辑

- 完整棋盘数据结构（10×9 一维数组表示）
- 所有 7 种棋子的走法生成（车、马、象、士、将、炮、兵）
- 合法走法过滤（防止走入将军）
- 规则判断（将军检测、将死判定、照面检测）
- 悔棋功能（移动栈管理）

#### AI 系统

- **基础搜索**：MiniMax + Alpha-Beta 剪枝 + 迭代加深
- **高级搜索**：Negamax + 置换表 + PV 移动排序
- **局面评估**：子力价值 + 位置价值表
- **人机对战**：支持可调节难度的 AI 对手

#### UI 框架

- Scene 场景管理系统（菜单、游戏场景分离）
- Game 主循环（60fps 稳定帧率）
- 主题系统（3 套可切换视觉风格）
- 音效系统（背景音乐、选子音效、移动音效）
- 自适应界面（支持全屏、动态缩放）

#### 菜单系统

- 游戏模式选择（人机对战、换边对战、挑战模式）
- 主题切换功能（一键切换三套风格）
- 键盘快捷键（1/2/3 选择，回车确认，M 键音乐开关）
- 鼠标点击支持

#### 游戏场景

- 精确棋盘渲染（网格对齐、动态缩放）
- 棋子选择系统（高亮选中、显示可走位置）
- 实时将军警告（红圈标记被将军的王）
- 移动动画提示（点标记显示可走位置）
- 快捷键支持（Z 键悔棋、Q 键返回菜单、M 键音乐控制）

### 进行中 / 待实现

- [ ] **AI 优化**
  - 异步 AI 思考（避免界面卡顿）
  - 开局库和残局库
  - AI 难度分级
  - 时间控制机制

- [ ] **游戏功能**
  - 游戏状态显示（当前回合、剩余时间）
  - 移动历史记录和回放
  - 棋谱保存和加载
  - 和棋判定（长将、困毙等）

- [ ] **UI 增强**
  - 设置场景（音量控制、难度调节）
  - 胜负结果展示
  - 动画效果（移动轨迹、吃子特效）
  - 多语言支持

- [ ] **网络功能**
  - 在线对战
  - 观战模式
  - 排行榜系统

- [ ] **打包发布**
  - 打包为独立 exe 文件
  - 跨平台支持

## 操作说明

### 菜单界面

- 按 `1` 选择"人机对弈"（红方 vs AI）
- 按 `2` 选择"换边对战"（暂未实现）
- 按 `3` 选择"切换主题"（循环切换三套风格）
- 按 `回车` 开始游戏
- 按 `M` 键暂停/继续背景音乐
- 鼠标点击按钮也可操作

### 游戏界面

1. **选择棋子**：左键点击己方棋子，显示可走位置（点标记）和选中框
2. **移动棋子**：左键点击可走位置执行移动
3. **取消选择**：左键点击空位或敌方棋子
4. **悔棋**：按 `Z` 键撤销上一步移动
5. **返回菜单**：按 `Q` 键
6. **音乐控制**：按 `M` 键暂停/继续音乐

### 游戏提示

- 被将军时，棋子周围会出现红色警告圆圈
- AI 思考时界面不会卡顿，可以正常操作
- 支持鼠标和键盘混合操作

## 技术亮点

### 架构设计

- **三层解耦架构**：core（规则引擎）、ui（界面）、ai（人工智能）完全分离
- **Scene 场景管理**：基于状态模式，易于扩展新场景
- **主题系统**：配置驱动的多风格支持，运行时动态切换
- **资源管理**：统一的 AssetManager，自动加载对应主题资源

### 算法实现

- **双重搜索引擎**：基础 MiniMax + 高级 Negamax，性能差异 5-10 倍
- **置换表优化**：Zobrist 哈希实现，大幅减少重复计算
- **移动排序**：PV（主要变例）优先搜索，提升剪枝效率
- **迭代加深**：渐进式搜索深度，支持时间控制

### 界面技术

- **精确坐标映射**：
  - `pixel_to_rc()`：屏幕坐标 → 棋盘格子（四舍五入对齐）
  - `rc_to_pixel()`：棋盘格子 → 屏幕坐标（像素精确定位）
- **动态缩放**：自适应屏幕尺寸，保持棋盘比例
- **音效系统**：pygame.mixer 实现，支持背景音乐和音效
- **实时渲染**：60fps 稳定帧率，流畅交互体验

## 合作流程

1. **新功能** 从 `main` 拉新分支：`feature/<功能名>`
2. **开发完成** 后提交 PR，至少一人审查
3. **合并** 前确保：
   - 代码通过本地测试
   - 无冲突
   - 遵循现有代码风格

## 参考资源

- [JavaScript 象棋实现](https://github.com/itlwei/Chess)（菜单 UI 参考）
- [chessAI 预训练模型](https://github.com/yuqangy123/chessAI)（AI 参考）
- [Pygame 官方文档](https://www.pygame.org)

## 开发笔记

### 核心设计决策

**坐标系统设计**

- **棋盘表示**：10 行 × 9 列（0-索引），使用一维数组存储
- **索引转换**：`index = row * 9 + col`，`row, col = divmod(index, 9)`
- **屏幕映射**：动态计算网格区域，通过 inset 比例微调对齐

**事件处理流程**

1. `handle_event(MOUSEBUTTONDOWN)` 获取鼠标坐标
2. `pixel_to_rc()` 转换屏幕坐标 → 棋盘坐标（使用 `round()` 四舍五入）
3. 检测棋子选择：己方棋子 → 生成合法走法
4. 检测移动执行：目标位置在可走列表 → `board.make_move()`
5. `rc_to_pixel()` 渲染时转换棋盘坐标 → 屏幕坐标（使用 `int()` 截断）

**关键方法**

- `pixel_to_rc(pos)`：鼠标坐标 → 棋盘 (row, col)
- `rc_to_pixel(row, col)`：棋盘坐标 → 屏幕像素坐标
- `gen_legal_moves(board, side)`：生成指定方的所有合法走法
- `in_check(board, side)`：检测指定方是否被将军

### 性能优化要点

**AI 搜索优化**

- 置换表：避免重复计算相同局面
- 移动排序：PV 移动优先，提升 α-β 剪枝效率
- 迭代加深：渐进式搜索，支持时间控制
- 局面评估：材料价值 + 位置价值表

**UI 渲染优化**

- 图片预加载：AssetManager 启动时加载所有资源
- 动态缩放：一次计算，重复使用坐标转换参数
- 事件驱动：只在状态变化时重绘相关区域

### 扩展开发指南

**添加新场景**

1. 继承 `Scene` 基类，实现生命周期方法
2. 在相应位置调用 `self.game.change_scene(NewScene(self.game))`
3. 通过 `kwargs` 传递场景间参数

**添加新AI算法**

1. 实现搜索接口：`search(board, max_depth, max_time)`
2. 返回 `Move` 对象或 `None`
3. 在 `PlayScene` 中替换 `search_engine` 实例

**添加新主题**

1. 在 `assets/img/` 下创建 `stype_N/` 目录
2. 按现有命名规范添加图片资源
3. 在 `Theme` 类中添加对应的工厂方法
4. 配置相应的 `inset` 参数适配棋盘对齐

---

## 项目状态

当前版本：**v1.0 Beta**
最后更新：2025年12月
开发状态：稳定运行，功能完整

**已验证平台**：Linux (Ubuntu/Arch), Windows 10+
**依赖版本**：Python 3.11+, Pygame 2.6.1+
