# 写作任务

> 最后更新：第X章 | 用途：按章节/场景追踪任务状态、门禁和下一步。

## 任务矩阵

| 场景任务ID | 章节 | 场景/段落 | 情节线ID | 目标字数 | 当前状态 | 门禁 | 下一步 | 负责人 |
|---|---|---|---|---:|---|---|---|---|
| WT-001 | 第X章 | 开场冲突 | PL-001 | 1200 | planned | outline_ready | 等作者确认细纲 | 作者/AI |

> 一个任务只能有一个当前状态，不要把多个状态合写进同一格。

## 状态定义

| 状态 | 含义 | 是否需要人审 |
|---|---|---|
| planned | 已有细纲和章节元数据 | 是 |
| drafting | AI 起草/协写中 | 否 |
| self_checked | AI 自检通过，等待作者审 | 否 |
| human_review | 作者正在审 | 是 |
| finalized | 作者确认定稿 | 是 |
| kb_reviewed | 知识库与追踪更新已审 | 是 |

## 状态转移表

planned -> drafting -> self_checked -> human_review -> finalized -> kb_reviewed

| 当前状态 | 对应门禁 | 可由 AI 建议 | 需要作者确认 | 下一状态 |
|---|---|---|---|---|
| planned | outline_ready | 否 | 是 | drafting |
| drafting | draft_ready | 是 | 否 | self_checked |
| self_checked | self_check_passed | 是 | 否 | human_review |
| human_review | human_finalized | 否 | 是 | finalized |
| finalized | knowledge_reviewed | 否 | 是 | kb_reviewed |

## 阻塞项

| 场景任务ID | 阻塞原因 | 需要作者决定 | 解除条件 |
|---|---|---|---|
| | | | |
