<p align="right">
  <a href="./README.md">EN</a> | <strong>简体中文</strong>
</p>

<p align="center">
  <img src="docs/hero.svg" alt="Pass All Exams" width="760" />
</p>

<h1 align="center">Pass All Exams</h1>

<p align="center">
  <strong>面向课程考试与期末复习的证据化 Agent Skill，覆盖文史社科、经管、定量、编程、语言及记忆密集型课程。</strong>
</p>

<p align="center">
  把课堂笔记、考纲、往年题和老师重点变成一套聚焦的复习流程：拆解考点、逐点讲清、立刻检索、修正错题、安排复盘。
</p>

<p align="center">
  支持 Codex、Claude Code、OpenClaw 和 OpenCode。<a href="#安装">安装 Skill</a> 后，输入 <code>/exam &lt;课程&gt; start</code> 即可开始。
</p>

<p align="center">
  <a href="./CHANGELOG.md"><img src="https://img.shields.io/badge/version-3.1.0-2563EB?style=flat-square&amp;labelColor=111827" alt="版本 3.1.0" /></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-16A34A?style=flat-square&amp;labelColor=111827" alt="MIT 许可证" /></a>
  <img src="https://img.shields.io/badge/Codex-supported-2563EB?style=flat-square&amp;labelColor=111827" alt="支持 Codex" />
  <img src="https://img.shields.io/badge/Claude%20Code-supported-D97706?style=flat-square&amp;labelColor=111827" alt="支持 Claude Code" />
  <img src="https://img.shields.io/badge/OpenClaw-supported-0F766E?style=flat-square&amp;labelColor=111827" alt="支持 OpenClaw" />
  <img src="https://img.shields.io/badge/OpenCode-supported-9333EA?style=flat-square&amp;labelColor=111827" alt="支持 OpenCode" />
</p>

## 目录

- [项目概览](#项目概览) · [为什么选择它](#为什么选择它) · [兼容的智能体](#兼容的智能体)
- [安装](#安装) · [快速开始](#快速开始) · [复习流程](#复习流程) · [证据约束](#证据约束) · [命令](#命令)
- [Token 模式](#token-模式) · [适用课程类型](#适用课程类型) · [本地状态与 CLI](#本地状态与-cli)
- [打包与验证](#打包与验证) · [仓库结构](#仓库结构) · [隐私](#隐私) · [致谢](#致谢) · [许可证](#许可证)

## 项目概览

Pass All Exams 面向需要一套可执行复习流程的学生，而不是再生成一份冗长资料。每次复习都刻意保持小而完整：

```text
一门课 -> 一个高价值考点 -> 一段短讲解 -> 一道检索题 -> 一次修正或一张复盘卡
```

整个流程由职责清晰的组件组成：

| 组件 | 职责 |
|---|---|
| [`SKILL.md`](./SKILL.md) | 供智能体读取的轻量入口。 |
| [`references/`](./references/) | 详细阶段规则，仅在需要时加载。 |
| [`scripts/examctl.py`](./scripts/examctl.py) | 确定性的本地课程状态与进度记录。 |
| [`scripts/ingest_materials.py`](./scripts/ingest_materials.py) | 使用 Microsoft MarkItDown 转换资料并建立索引。 |
| [`scripts/install.sh`](./scripts/install.sh) 和 [`scripts/quick-install.sh`](./scripts/quick-install.sh) | 将 Skill 安装到不同智能体。 |
| [`scripts/package_skill.py`](./scripts/package_skill.py) | 生成可上传的 `.skill` 压缩包。 |

## 为什么选择它

| 常见复习问题 | Pass All Exams 的处理方式 |
|---|---|
| AI 写了很多内容，但你并不知道自己会不会。 | 每讲完一个知识点，都接一次检索练习。 |
| “可能会考”听起来像“老师说会考”。 | 明确区分资料依据、合理推断和待确认内容。 |
| 聊天记录越堆越长，后面越来越费 token。 | 进度写入 `state.json`、`errors.jsonl` 和 `cards.jsonl`。 |
| 很多速成工具只适合文科论述课。 | 流程同时覆盖论述、定量、编程、语言和记忆密集型复习。 |
| 错题只是被原话重讲一遍。 | 先判断错因，再换一种讲法，并从新角度重测。 |

## 兼容的智能体

Pass All Exams 运行在能够加载 `SKILL.md` 文件夹并遵循其中流程的智能体工具里。你只需准备一个兼容的智能体，不需要了解 Agent Skill 的内部实现。

| 智能体 | 简单说明 | 官方资源 |
|---|---|---|
| Codex | OpenAI 的编程智能体，可在 ChatGPT 和本地开发流程中使用。 | [openai.com/codex](https://openai.com/codex/) |
| Claude Code | Anthropic 的智能体编程工具。个人 Skill 放在 `~/.claude/skills`，项目级 Skill 放在 `.claude/skills`。 | [Claude Code 文档](https://code.claude.com/docs/en/overview) |
| OpenClaw | 以 `SKILL.md` 为核心构建 Skill 机制的开放智能体平台。 | [OpenClaw 文档](https://docs.openclaw.ai/) |
| OpenCode | 能从项目目录或全局目录发现 Agent Skills 的编程智能体。 | [OpenCode 文档](https://opencode.ai/docs/) |

## 安装

GitHub 仓库名是 `pass_all_exams`，安装后的 Skill 名是 `pass-all-exams`。以下安装命令请在 Bash 环境中运行。

### 方式一：一键安装（推荐）

快速安装脚本会克隆项目、安装 MarkItDown 文件转换依赖，并把 Skill 复制到所选智能体目录：

```bash
curl -fsSL https://raw.githubusercontent.com/jasonisbrave/pass_all_exams/main/scripts/quick-install.sh | bash -s -- <agent>
```

把 `<agent>` 换成下表中的一个值：

| 智能体 | 范围 | `<agent>` 值 |
|---|---|---|
| Codex | 全局；设置 `CODEX_HOME` 时装到其下 | `codex` |
| Claude Code | 全局 | `claude` |
| Claude Code | 仅当前项目 | `claude-project` |
| OpenClaw | 全局 | `openclaw` |
| OpenCode | 全局 | `opencode` |
| OpenCode | 仅当前项目 | `opencode-project` |

如果要跳过自动安装 Python 依赖，把 `--skip-deps` 放在智能体值之前：

```bash
curl -fsSL https://raw.githubusercontent.com/jasonisbrave/pass_all_exams/main/scripts/quick-install.sh | bash -s -- --skip-deps <agent>
```

### 方式二：从 Git 安装

克隆仓库并进入仓库根目录：

```bash
git clone https://github.com/jasonisbrave/pass_all_exams.git
cd pass_all_exams
```

如果需要转换课程文件，安装这组可选依赖：

```bash
python3 -m pip install -r requirements-markitdown.txt
```

然后运行对应智能体的安装命令：

| 智能体 | 范围 | 命令 |
|---|---|---|
| Codex | 全局；设置 `CODEX_HOME` 时装到其下 | `bash scripts/install.sh codex` |
| Claude Code | 全局 | `bash scripts/install.sh claude` |
| Claude Code | 仅当前项目 | `bash scripts/install.sh claude-project` |
| OpenClaw | 全局 | `bash scripts/install.sh openclaw` |
| OpenCode | 全局 | `bash scripts/install.sh opencode` |
| OpenCode | 仅当前项目 | `bash scripts/install.sh opencode-project` |

使用项目级安装时，请在需要接收该 Skill 的项目根目录运行命令。

### 方式三：直接克隆到 Skill 目录

```bash
# Codex
git clone https://github.com/jasonisbrave/pass_all_exams.git ~/.codex/skills/pass-all-exams

# Codex，使用 CODEX_HOME 时
git clone https://github.com/jasonisbrave/pass_all_exams.git "$CODEX_HOME/skills/pass-all-exams"

# Claude Code，全局
git clone https://github.com/jasonisbrave/pass_all_exams.git ~/.claude/skills/pass-all-exams

# Claude Code，当前项目
git clone https://github.com/jasonisbrave/pass_all_exams.git .claude/skills/pass-all-exams

# OpenClaw
git clone https://github.com/jasonisbrave/pass_all_exams.git ~/.openclaw/skills/pass-all-exams

# OpenCode，全局
git clone https://github.com/jasonisbrave/pass_all_exams.git ~/.config/opencode/skill/pass-all-exams

# OpenCode，当前项目
git clone https://github.com/jasonisbrave/pass_all_exams.git .opencode/skill/pass-all-exams
```

如果你的智能体支持上传 Skill 压缩包，也可以[在本地构建 `.skill` 包](#打包与验证)。

## 快速开始

安装后，直接让智能体开始一门课程：

```text
/exam 组织行为学 start
```

也可以用自然语言一次性说明已知信息：

```text
帮我用 pass-all-exams 复习组织行为学。
考试题型是选择题、简答题和案例分析。
老师强调必考：霍桑实验、期望理论。我会继续粘贴课堂笔记。
```

英文课程的用法相同：

```text
/exam Organizational Behavior start
```

```text
Use pass-all-exams to help me review Organizational Behavior.
The exam has multiple choice, short answer, and case analysis.
My must-know topics are Hawthorne studies and expectancy theory.
```

如果有课程文件，在仓库根目录或已安装的 Skill 目录中运行资料转换脚本：

```bash
python3 scripts/ingest_materials.py \
  --course "组织行为学" \
  ~/Downloads/考纲.pdf \
  ~/Downloads/第1周课件.pptx \
  ~/Downloads/复习笔记.docx
```

转换后的 Markdown 会保存在该课程的本地 `materials/` 目录中，供后续阶段复用。

## 复习流程

| 阶段 | 具体做什么 |
|---|---|
| **建档** | 收集课程、考试日期或时间预算、题型、资料和必考点。 |
| **资料转换** | 使用 Microsoft MarkItDown 把上传文件转成 Markdown，并按 SHA-256 缓存转换后的资料。 |
| **拆解** | 把资料拆成适合考试复习的小知识点，并标注来源可信度。 |
| **讲授** | 一次只讲一个点，先给具体场景，最多拆成三块，再让你自己总结。 |
| **检题** | 按真实题型练习：选择、案例分析、计算、代码追踪、简答等。 |
| **诊断与补漏** | 判断错因，换一种表达方式，从新角度重测，而不是重复原讲解。 |
| **复盘** | 生成当天、次日、三天后和考前一天的检索卡。 |

## 证据约束

每次实质讲解、预测考法或批改答案时，都应说明来源状态：

| 标签 | 含义 |
|---|---|
| **资料依据** | 直接来自笔记、考纲、老师原话、往年题或粘贴的资料。 |
| **合理推断** | 基于课程常识和常见考核方式做出的有用复习判断。 |
| **待确认** | 取决于老师要求、教材版本或本校考试范围，仍需核对的内容。 |

这是主要的幻觉控制层。没有资料时，Skill 会按通用知识模式工作，不能假装知道老师真正的考试范围；在依赖高风险考试预测前，请提供考纲或考点清单。

## 命令

以下命令由智能体解释执行，不是可直接在终端运行的 Shell 命令。

| 命令 | 作用 |
|---|---|
| `/exam <课程> start` | 创建或刷新课程复习计划。 |
| `/cram <课程> start` | 兼容 cram 式复习流程的别名。 |
| `/exam <课程> resume` | 从保存的进度和最近的 JSONL 记录继续。 |
| `/exam <课程> drill` | 检索当前薄弱点，并练习到期内容。 |
| `/exam <课程> retry <知识点>` | 对薄弱点重讲、重测，修正所选错题记录并写入会话日志。 |
| `/exam <课程> summary` | 输出考前清单。 |

## Token 模式

| 模式 | 适合场景 | 行为 |
|---|---|---|
| `compact` | 大多数考前突击 | 一个知识点、一个例子、一道检索题和一次纠错。 |
| `standard` | 正常周复习 | 多一个例子，并关联一个已学知识点。 |
| `deep` | 难课或高风险考试 | 增加推导、边界条件和混合练习。 |

默认使用 `compact`。渐进式加载让 `SKILL.md` 保持简短：`references/` 中的详细规则仅在需要时读取。

## 适用课程类型

| 课程类型 | 示例 | 特别处理 |
|---|---|---|
| 文史社科 | 法学、政治学、社会学、教育学 | 定义、比较和案例分析踩分结构 |
| 经管类 | 组织行为学、市场营销、会计理论 | 框架、陷阱和场景应用 |
| 定量课 | 高等数学、统计学、经济学方法 | 公式条件、例题和计算错误诊断 |
| 编程课 | 数据结构、数据库、操作系统、Python/C/Java | 代码追踪、bug 修复和复杂度解释 |
| 语言和记忆密集课 | 英语、历史、医学基础 | 填空、回忆卡和对比表 |

## 本地状态与 CLI

本节的 Python 命令请在仓库根目录或已安装的 Skill 目录中运行。

### 存储位置与文件

默认情况下，进行中与已归档的课程分别保存在：

```text
~/.pass-all-exams/courses/<course-slug>/
~/.pass-all-exams/archive/<course-slug>/
```

`examctl.py` 提供三种存储位置设置方式：

- 设置环境变量 `PASS_ALL_EXAMS_HOME` 覆盖数据根目录，课程位于 `<数据根目录>/courses`。
- 传入 `--data-home <dir>` 使用 `<dir>/courses`。它优先于环境变量，可放在子命令之前或之后。
- 传入 `--root <courses-dir>` 直接指定包含各课程文件夹的目录。它优先于 `--data-home`，同样可放在子命令之前或之后。不要把数据根目录本身传给 `--root`。

自定义存储位置后，资料转换时也要把同一个课程目录传给 `ingest_materials.py --root <courses-dir>`。

在 `examctl.py` 中，只有 `init` 会创建课程；其他子命令都要求课程目录和 `state.json` 已存在。状态缺失时会清晰报错并以退出码 2 退出，不会静默创建文件。

每门课程可以包含：

| 文件或目录 | 作用 |
|---|---|
| `course.yaml` | 课程配置：题型、资料、必考点和偏好。 |
| `state.json` | 当前阶段、知识点状态和计数。 |
| `materials/` | MarkItDown 转换后的 Markdown 资料。 |
| `materials.jsonl` | 资料索引：来源路径、SHA-256、输出路径、标题、字节数和状态。 |
| `errors.jsonl` | 错题、诊断和修正记录。 |
| `cards.jsonl` | 检索复习卡和到期日期。 |
| `sessions.jsonl` | 由 `log-session` 追加的会话日志。 |

### 课程与会话命令

创建课程、查看进度或输出摘要：

```bash
python3 scripts/examctl.py init --course "组织行为学"
python3 scripts/examctl.py status --course "组织行为学"
python3 scripts/examctl.py summary --course "组织行为学"
```

记录一次会话，不改动知识点状态：

```bash
python3 scripts/examctl.py log-session \
  --course "组织行为学" \
  --action drill \
  --topic "期望理论" \
  --result pass \
  --errors-corrected 1 \
  --cards-added 2
```

将筛选后最新一条 open 或 stubborn 错题标记为已修正，并记录修正方式：

```bash
python3 scripts/examctl.py resolve-error \
  --course "组织行为学" \
  --point "期望理论" \
  --repair "用对比表重新讲解，并换一个新场景重测"

# 可选过滤：--contains "混淆"、--date 2026-11-15，
# 或用 --index N 直接选择 errors.jsonl 中从 1 开始计数的行号。
```

归档已完成的课程，或稍后恢复。两个操作都会移动完整目录，不删除数据，并拒绝覆盖已存在的目标：

```bash
python3 scripts/examctl.py archive-course \
  --course "组织行为学" \
  --reason "已考完收官"
python3 scripts/examctl.py restore-course --course "组织行为学"
```

### 记录进度与错题

记录一个已讲授的知识点：

```bash
python3 scripts/examctl.py record-point \
  --course "组织行为学" \
  --point "期望理论" \
  --level must \
  --status taught \
  --source material
```

也可以记录掌握证据和复盘日期：

```bash
python3 scripts/examctl.py record-point \
  --course "组织行为学" \
  --point "期望理论" \
  --status mastered \
  --verification "不看笔记通过一道检索题" \
  --review-due 2026-12-20
```

记录一次错题：

```bash
python3 scripts/examctl.py record-error \
  --course "组织行为学" \
  --point "期望理论" \
  --reason confusion \
  --question-type "选择题" \
  --must-know
```

### 资料转换

Microsoft [MarkItDown](https://github.com/microsoft/markitdown) 支持把 PDF、Word、PowerPoint、Excel、图片、音频、HTML、CSV、JSON、XML、ZIP、EPub 及其他支持的格式转换成 Markdown，再交给复习流程使用。

```bash
python3 scripts/ingest_materials.py \
  --course "组织行为学" \
  ~/Downloads/考纲.pdf
```

默认只处理本地文件。可信的 HTTP(S) URL 需要显式添加 `--allow-url`，因为 MarkItDown 会以当前进程权限读取资源。音频转写可能需要系统安装 `ffmpeg`；普通 PDF、Office 和文本资料转换不需要。

## 打包与验证

在仓库根目录生成可上传的 `.skill` 压缩包：

```bash
python3 scripts/package_skill.py
```

默认输出到 `dist/pass-all-exams.skill`。如果智能体或界面支持上传 Skill 压缩包，可以直接使用这个文件。

验证包结构并编译检查 Python 脚本：

```bash
python3 scripts/validate_skill.py
python3 -m py_compile scripts/examctl.py scripts/ingest_materials.py scripts/validate_skill.py scripts/package_skill.py
```

## 仓库结构

```text
pass_all_exams/
├── SKILL.md                     # 智能体读取的入口
├── README.md                    # 英文文档
├── README.zh-CN.md              # 中文文档
├── CHANGELOG.md                 # 版本记录
├── PROJECT_CHECK.md             # 验证记录
├── LICENSE                      # MIT 许可证
├── requirements-markitdown.txt  # MarkItDown 依赖
├── agents/
│   └── openai.yaml              # Codex UI 元数据
├── configs/
│   └── example.yaml             # 示例课程配置
├── docs/
│   └── hero.svg                 # README 题图
├── references/
│   ├── pipeline.md              # 详细复习流程
│   ├── prompt-patterns.md       # 可复用提示模板
│   ├── platforms.md             # 智能体安装说明
│   └── comparison.md            # 设计对比说明
├── scripts/
│   ├── examctl.py               # 本地课程状态管理
│   ├── ingest_materials.py      # MarkItDown 资料转换脚本
│   ├── install.sh               # 智能体安装脚本
│   ├── quick-install.sh         # 一键安装脚本
│   ├── package_skill.py         # .skill 打包脚本
│   └── validate_skill.py        # 包结构校验脚本
└── tests/
    └── test_examctl.py          # 基于标准库的 unittest 测试
```

## 隐私

课程状态默认保存在本机。这个 Skill 自身不需要额外的外部服务、数据库或账号；笔记、错题和复习卡会留在所选数据根目录中，除非你主动移动或分享。处理敏感资料前，请检查所用智能体和 MarkItDown 的相关设置。

## 致谢

本项目使用 [Microsoft MarkItDown](https://github.com/microsoft/markitdown) 将课程资料转换为 Markdown，供复习流程使用。MarkItDown 由 Microsoft 开发并维护。

## 许可证

[MIT](./LICENSE)
