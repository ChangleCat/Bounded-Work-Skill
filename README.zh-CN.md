# Bounded Work Skill

[English](README.md) | [简体中文](README.zh-CN.md)

Bounded Work 是一个与具体 Agent harness 解耦的 Skill，用于规划、执行、恢复或审计高风险、跨组件、跨负责人或跨会话的复杂工作。

它把复杂任务拆成范围明确、可独立验证的工作卡，并通过依赖状态、持久授权、证据、恢复边界和审批 Gate 控制执行。Migration 是其中的专业子流程，而不是这个 Skill 唯一支持的任务类型。

## 适用场景

当工作跨越多个会话、负责人、组件或环境，或者依赖顺序、失败恢复和可审计验收很重要时，适合使用 Bounded Work。

对于很小、可逆的一次性修改，Skill 会自动退化成轻量的目标、范围和验证清单，不会为了使用框架而建立完整控制面。

## 主要能力

- Frame、Bootstrap、Execute 和 Audit 四种模式。
- 原子工作卡，以及唯一权威的任务状态来源。
- 将持久授权与自动化验证严格分离。
- Claim → Card → Evidence → Gate 的完整追踪链路。
- 证据有效期、状态和 SHA-256 输入绑定。
- 重试预算、有限并发、写入所有权和合并负责人。
- 不依赖历史对话的冷恢复。
- 将外部不可信证据与持久控制指令分离。
- 可选的控制文件认证与篡改检测。
- 内置 Migration 与 Cutover 专业流程。

## 安装

### 推荐：把仓库地址交给 Agent

如果你的 Agent 支持从 Git 仓库安装 Skill，最简单的方式是直接把仓库地址发给它。可以原样发送下面这段话：

```text
请从下面的仓库安装 bounded-work Skill：
https://github.com/ChangleCat/Bounded-Work-Skill

请以仓库根目录作为 Skill 来源，使用规范名称 bounded-work 安装；
安装后确认 SKILL.md 能被发现。暂时不要开始执行任何具体项目任务。
```

在 Codex 中，如果内置 Skill Installer 可用，Agent 可以使用它完成安装；其他 harness 可能使用自己的安装器。Agent 请求网络或文件写入权限时，请先核对目标目录和仓库地址再批准。

安装完成后，新建一个任务并发送：

```text
使用 $bounded-work 说明这个 Skill 应该在什么情况下使用，以及什么情况下不应使用。
```

正常情况下，Agent 应识别出 `bounded-work`，并能区分完整的 Bounded Work 流程和普通的一次性修改。

### Codex 手动安装

macOS 或 Linux 使用默认配置时，将仓库克隆到个人 Skills 目录，并确保目录名是规范名称 `bounded-work`：

```bash
git clone https://github.com/ChangleCat/Bounded-Work-Skill.git ~/.codex/skills/bounded-work
```

如果设置了 `CODEX_HOME`，目标目录应改为 `<CODEX_HOME>/skills/bounded-work`。

Windows PowerShell 默认安装路径：

```powershell
git clone https://github.com/ChangleCat/Bounded-Work-Skill.git "$env:USERPROFILE\.codex\skills\bounded-work"
```

更新已有的手动安装：

```bash
git -C ~/.codex/skills/bounded-work pull --ff-only
```

安装后确认 `~/.codex/skills/bounded-work/SKILL.md` 存在，然后新建任务并通过 `$bounded-work` 调用。

### 其他 Agent harness

使用对应 harness 提供的 Skill 或 Agent Skills 安装机制。安装后的 Skill 根目录必须包含 [SKILL.md](SKILL.md)，规范名称为 `bounded-work`。

如果 harness 没有安装器，可以：

1. 将仓库克隆到该 harness 文档规定的个人 Skill 目录；或
2. 在任务中把仓库地址或本地仓库路径交给 Agent，并明确要求其读取根目录下的 `SKILL.md`。

核心指令与 harness 无关，不需要运行时依赖。不同 harness 的调用方式、审批能力和生命周期适配要求见[可移植性说明](references/portability.md)。

### 可选工具依赖

初始化、校验、冷恢复和认证脚本不是使用核心 Skill 的必要条件。这些确定性工具需要 Python 3.11+ 和 PyYAML 6.x：

```bash
python -m pip install -r scripts/requirements.txt
```

## 使用方式

显式调用示例：

```text
使用 $bounded-work 评估这个跨服务认证改造，只制定方案，不修改文件。

使用 $bounded-work 为这个跨会话可靠性项目建立可恢复的协作控制面。

使用 $bounded-work 继续唯一符合条件的工作卡，并更新证据。

使用 $bounded-work 审计这个发布是否就绪，只报告问题，不进行修复。
```

Skill 会自动推断当前请求允许的最窄模式，并用普通语言说明本轮边界。Bootstrap 只建立协调工件，不会自动授予 Execute 权限。

## 可选工具

参考工具可以初始化、校验、恢复和认证文件化控制面：

```bash
python scripts/init_work.py <work-root> \
  --title "<结果导向的标题>" \
  --owner "<负责人>" \
  --authority-ref "<请求或决策来源>" \
  --claim "<可观察的成功声明>"

python scripts/validate_work.py <work-root>
python scripts/resume_work.py <work-root>
python scripts/attest_control.py <work-root> verify
```

完整命令和安全边界见[工具说明](references/tooling.md)。

## 仓库结构

```text
SKILL.md       核心路由与运行契约
agents/        可选的 OpenAI 界面元数据
references/    按需加载的流程与维护资料
assets/        控制面和 Migration 模板
scripts/       可选的确定性参考工具
evals/         行为与自动发现评测定义
tests/         结构和工具回归测试
```

## 验证

安装 Python 3.11+ 和 PyYAML 后运行：

```bash
python -m unittest discover -s tests -v
```

行为场景定义在 [evals/evals.json](evals/evals.json)。结构测试通过并不等同于已经证明所有 Agent harness 上的行为兼容性。

## 许可证

本项目使用 [Apache License 2.0](LICENSE)。
