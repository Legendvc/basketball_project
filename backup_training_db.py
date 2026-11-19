"""Back up the local training database and verify the result."""

import argparse
import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path


def backup_database(source: Path, destination_dir: Path) -> Path:
    source = source.resolve(strict=True)
    destination_dir = destination_dir.resolve()
    destination_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    target = destination_dir / f"{source.stem}-{timestamp}.db"
    with target.open("xb"):
        pass

    try:
        with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as original:
            with closing(sqlite3.connect(target)) as backup:
                original.backup(backup)
                if backup.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
                    raise RuntimeError("备份未通过 SQLite 完整性检查")
                if backup.execute("PRAGMA foreign_key_check").fetchone() is not None:
                    raise RuntimeError("备份未通过外键检查")
    except BaseException:
        target.unlink(missing_ok=True)
        raise

    return target


def main() -> None:
    project = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="备份并验证 SQLite 训练数据库")
    parser.add_argument("--source", type=Path, default=project / "basketball_live.db")
    parser.add_argument("--destination", type=Path, default=project.parent / "basketball_backups")
    args = parser.parse_args()
    print("已验证的备份：", backup_database(args.source, args.destination))


if __name__ == "__main__":
    main()
