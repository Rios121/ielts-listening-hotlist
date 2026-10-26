---
name: ielts-listening-hotlist
description: Fetch an IELTS listening hot-list (Part 1/2/3/4, 20 passages each) from an IELTS computer-based test platform's API and generate a study-reference doc (Markdown + Word) with per-passage transcript summary, answer words, signal words, traps, and per-question answers (with Chinese stems). Use when the user asks to 抓取/整理/生成 雅思听力热榜、听力备考速查、听力真题答案、听力答案词、听力场景、热榜文档 等.
---

# 雅思听力热榜备考速查生成器

从一个雅思机考平台的听力热榜（Part 1 / Part 2 / Part 3 / Part 4 各 20 篇，共 80 篇）生成备考速查文档。**听力按 Part 类型用不同格式**：P1 答案词、P2/P3 信号词+坑、P4 题干+原句精听。

## 版权与合规（重要，先读）

- 本 skill **只提供「方法 + 工具」**，仓库内**不含任何第三方版权内容**——录音原文、题目、答案、解析等一概不打包、不分发。
- 数据由**使用者本人**，从**自己安装、并已合法获得使用授权**的 App 中即时获取，仅供个人学习之用。
- 使用者应自行确认其使用方式符合**所在地法律**及**数据源提供方的服务条款与版权规定**，责任自负。
- MIT 许可证仅适用于本仓库的代码与文档，**不延伸至任何第三方内容**。

## 工作流（按顺序执行）

设工作目录 `WD`（默认当前目录，脚本自动建 `WD/input`、`WD/summaries` 等子目录）。

1. **抓取**：`python ${CLAUDE_SKILL_DIR}/scripts/fetch_listening.py --workdir WD`
   产出 `WD/listening_data.json`（80 篇录音原文 + 笔记题干 + 题目 + 答案解析）。默认内置数据源，无需配置。

2. **生成中间输入**：`python ${CLAUDE_SKILL_DIR}/scripts/build_input.py --workdir WD`
   产出 `WD/input/batch_01.md` ~ `batch_08.md`（每批 10 篇，含 transcript + 笔记题干 + 题目解析）。

3. **LLM 总结**（核心）：派 8 个子代理，每个读一个 `batch_XX.md`，按下方「Agent 总结 prompt 模板」生成总结；把每个子代理返回的 markdown 原样写入 `WD/summaries/batch_XX.md`。

4. **合并**：`python ${CLAUDE_SKILL_DIR}/scripts/merge_to_md.py --workdir WD`
   产出最终 `WD/听力7天热榜_备考速查_<当天日期>.md`（含**可点击跳转的超链接目录**）。

5. **（可选）转 Word**：`python ${CLAUDE_SKILL_DIR}/scripts/md2docx.py --md <md文件> --out <docx文件>`

## Agent 总结 prompt 模板

批次与 Part 对应：batch_01=Part1 #1-10，batch_02=Part1 #11-20，batch_03=Part2 #1-10，batch_04=Part2 #11-20，batch_05=Part3 #1-10，batch_06=Part3 #11-20，batch_07=Part4 #1-10，batch_08=Part4 #11-20。（每个 batch 只含单一 Part，便于统一格式。）

对每个批次派一个子代理，prompt 如下（把 `<文件绝对路径>`、`<Part 号>`、`<排名范围>` 替换为实际值）：

> 读文件 `<文件绝对路径>`（UTF-8）。里面有 10 篇雅思听力真题（Part `<Part 号>`，排名 `<排名范围>`），每篇含：录音原文 transcript（按 [0][1]… 分段）、笔记题干（填空，空格用【题号】标出）、题目（题干+选项）和中文答案解析（解析含"题目理解+定位+答案"，以及听力原句）。
>
> 为每篇生成备考总结，**按 Part 类型用对应格式**（答案一律从「解析」提取，未明确的写「（未明确）」不要猜）：
>
> **Part 1（填空）——用「答案词速查」格式：**
> ```
> ### [P1 #N] 标题（中文标题）
> **答案词速查**：
> | 题 | 答案词 | 一句提示 |
> | --- | --- | --- |
> | 1 | birds | large numbers of ↔ huge flock of |
> ...
> **滚动词表**：word1 · word2 · ...（所有答案词连起来）
> ```
> 提示要写"定位/同义替换/陷阱"（如"but 后 heading for ↔ final destination"）。
>
> **Part 2/3（选择+匹配）——用「信号词+坑」格式：**
> ```
> ### [P2 #N] 标题（中文标题）
> **一句话**：谁在什么场合对谁讲什么
> **大意**：2-3 句概括
> **选择题**：
> | 题 | 中文题干 | 答案 | 信号词 |
> | --- | --- | --- | --- |
> | 11 | Claire 认为酒店吸引人的是什么？ | C | expensive fabrics / antique carpets |
> ...
> **匹配题**：
> | 项 | 配对 | 答案 | 信号词 |
> ...
> **坑**：① ...（时间线/否定/偷换概念等，可迁移的规律）
> **同义替换**：A↔B · C↔D · ...
> ```
> 选择题的"中文题干"要忠实翻译，"信号词"写录音里听到就选的原词；匹配题同理；"坑"要提炼成可迁移规律。
>
> **Part 4（填空）——用「题干+原句精听」格式：**
> ```
> ### [P4 #N] 标题（中文标题）
> **一句话**：讲什么的 lecture
> **大意**：2-3 句概括
> **逐题精听**：
> | 题 | 题干（笔记空格） | 答案词 | 听力原句 |
> | --- | --- | --- | --- |
> | 31 | Cup made of a ___ shell | coconut | ...a coconut shell... |
> ...
> **关键词滚动**：word1 · word2 · ...
> **坑**：① ...（题干已给词别重复填 / 听清复数 / 比较级 / first 不是 later 等）
> **同义替换**：A↔B · ...
> ```
> "题干"从笔记题干（【题号】标记）提取空格前后文；"听力原句"从解析的"句子/原文"里提取含答案词的那句。
>
> 输出就是这 10 篇的完整 markdown，从第 1 篇到第 10 篇，不要遗漏任何一篇、任何一题。不要写任何额外说明，直接输出 markdown。

## 脚本

- `scripts/fetch_listening.py` — 抓取听力热榜 + transcript + 笔记题干 + 答案（含 token 降级）
- `scripts/build_input.py` — 生成 LLM 总结的中间输入（batch 文件）
- `scripts/merge_to_md.py` — 合并 batch 成最终 markdown（含超链接目录）
- `scripts/md2docx.py` — markdown → Word（含表格）

## 备注

- 填空题的题干在 `contentHtml`（笔记表格），空格用 `<input placeholder="题号">` 标记，`fetch_listening.py` 已提取为【题号】。
- 所有脚本幂等、无副作用，可重复运行覆盖旧文件。
