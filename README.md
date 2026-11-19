# Basketball Training System

A Python project for managing basketball player training data.

## Features

- Player information management
- Shooting statistics
- Training history recording
- Shooting evaluation system
- Overall shooting percentage for the most recent effective training days

## Recent Effective Training Days

The API calculates the overall shooting percentage for the most recent effective training days from SQLite. It defaults to five days. `training_summary.py` also provides the same calculation for the older `Player` methods.

Rules:

- Training records are sorted by their actual ISO date values.
- Records from the same date are merged before deciding whether that date is effective.
- A training day is effective only when merged `shots >= 5`.
- The overall percentage is calculated as total made shots divided by total shots, then rounded to 1 decimal place.
- If fewer than 5 effective training days exist, available data is used and the result is marked as reference only.
- Missing dates, invalid dates, and illegal shooting data are skipped with user-facing messages.

Related methods:

- `Player.get_recent_effective_training_days(limit=5)`
- `Player.get_recent_effective_training_days_summary(limit=5)`
- `Player.show_recent_effective_training_days(limit=5)`

## Project Structure

```text
basketball_project/
├── main.py              # 命令行入口
├── api.py               # 旧版 API 和 /v2 的挂载入口
├── api_orm_demo.py      # /v2 的训练接口
├── schemas.py           # API 请求和响应模型
├── database.py          # SQLite 路径与 SQLAlchemy Session
├── models.py            # ORM 表结构
├── training_repository.py # 训练记录查询和写入
├── training_service.py  # 从数据库读取记录并计算汇总
├── training_summary.py  # 有效训练日统计规则
├── player.py            # 球员资料、投篮计数和旧统计入口
├── player.json          # 本地球员资料与原始历史
├── migrations/          # Alembic 表结构迁移
├── tests/               # 自动化测试
├── practice/            # 原有 SQLite 学习脚本及使用说明
├── backups/             # 原有 .backup 历史文件及说明
├── requirements.txt
└── README.md
```

## How to Run

使用 Python 3.14。在项目根目录创建虚拟环境并安装依赖。已有 `.venv` 时可以直接执行安装命令。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

将完成迁移的 `basketball_live.db` 放到项目根目录，并确认库中的用户名与 `player.json` 的球员姓名一致。下面两条命令分别在项目根目录的两个 PowerShell 窗口执行。

```powershell
.\.venv\Scripts\python.exe -m uvicorn api:app --port 8003
```

```powershell
.\.venv\Scripts\python.exe main.py
```

API 和命令行默认共用 `basketball_live.db`。需要切到演练副本时，在对应窗口启动程序前设置 `$env:BASKETBALL_DB_FILE = "basketball_api_trial.db"`。使用 `Remove-Item Env:\BASKETBALL_DB_FILE -ErrorAction SilentlyContinue` 恢复默认。

启动 API 后，可打开 [旧版接口文档](http://127.0.0.1:8003/docs)或 [新版接口文档](http://127.0.0.1:8003/v2/docs)。旧版训练接口根据本地球员姓名查找用户，`/v2` 的调用方显式传入 `user_id`。两版 `GET /training-summary` 的 `limit` 默认是 5，最小值为 1。

命令行的选项 6 显示每次训练命中率的平均值。API 汇总按有效训练日计算总命中次数除以总投篮次数。

## Data and Practice Files

- `basketball_live.db` 保存当前训练记录。使用正式库前，请先备份已迁移的数据库。Git 忽略项目根目录的训练数据库及其 SQLite 辅助文件。
- `player.json` 保存球员资料与原始训练历史。缺少日期的旧记录继续保留在 JSON 中。旧结构的 `basketball.db` 可用作迁移来源。
- `practice/` 中的脚本仍按当前工作目录寻找 `basketball.db`，其中包含写入、更新和删除操作。练习前先阅读 [练习说明](practice/README.md)，使用单独的练习目录与数据库。
- 原有备份见 [备份说明](backups/README.md)。

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

测试用临时 SQLite 数据库验证查询、写入、回滚和接口行为。在项目根目录执行，`tests/test_json.py` 会读取当前的 `player.json`。

## Technologies
- Python
- JSON
- Git
- GitHub

## Future Improvements

## Version History

## Author
Richard
