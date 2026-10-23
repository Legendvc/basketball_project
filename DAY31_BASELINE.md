# Day 31 项目基线

## 当前验证结果

- 工作分支：chore/day31-project-baseline
- 测试命令：python -m pytest -q
- 测试结果：33 passed in 0.52s
- 当前尚未实施 ORM 改造。

## 接口与数据流

| 接口 | 功能 | 数据来源或去向 |
|---|---|---|
| GET / | 项目状态 | 固定内容 |
| GET /player | 球员资料与评价 | JSON |
| GET /training-summary | 最近 N 个有效训练日统计 | JSON |
| POST /training | 新增训练 | 先写 JSON，再写 SQLite |
| GET /training-by-date | 按日期查询 | SQLite |

## 当前数据库

数据库路径：basketball.db，相对于运行命令时的工作目录。

training 表：
- id：INTEGER PRIMARY KEY
- date：TEXT NOT NULL
- shots：INTEGER NOT NULL
- made：INTEGER NOT NULL

当前没有 user_id 字段，也没有数值范围 CHECK 约束。

## 已识别的问题

1. JSON 与 SQLite 分别承担查询，尚未统一训练数据来源。
2. 新增训练的两次写入不是一个事务，中途失败可能造成不一致。
3. 数据库相对路径可能导致从不同目录运行时访问不同文件。
4. 多用户功能需要增加数据归属，并明确旧记录属于谁。
5. API 已校验训练数值，但直接操作数据库可以绕过该校验。

以上是结构性风险，不代表已经确认实际数据损坏。

## 下一阶段待办

- [ ] 设计 User、Training、Report 的最小 ORM 模型。
- [ ] 确定统一训练数据来源及 JSON 的兼容方式。
- [ ] 在数据库副本上验证迁移、旧记录归属与重复导入处理。
- [ ] 重构数据库访问，保留已有统计规则。
- [ ] 增加迁移与数据一致性测试。

## 改造约束

- 保留原始 player.json 结构、数据库和历史备份。
- 不直接覆盖真实数据，迁移先在副本上验证。
- 新增依赖先说明用途并确认。
- 提交前逐项检查文件，不将训练数据和备份混入代码提交。
- 已有测试继续通过，并为新增行为补充测试。