import sqlite3

import db_utils


def test_save_training_record(tmp_path, monkeypatch):
    db_file = tmp_path / "test_basketball.db"
    monkeypatch.setattr(db_utils, "DB_FILE", str(db_file))

    conn = sqlite3.connect(db_file)
    conn.execute("""
        CREATE TABLE training (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            shots INTEGER NOT NULL,
            made INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

    record_id = db_utils.save_training_record(
        "2026-10-20", 10, 7
    )

    rows = db_utils.get_training_by_date("2026-10-20")

    assert record_id == 1
    assert len(rows) == 1
    assert rows[0]["shots"] == 10
    assert rows[0]["made"] == 7