import sqlite3


DB_FILE = "basketball.db"


def get_training_by_date(training_date):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # 设置行工厂为 Row，以便按列名访问数据
    try:
        rows = conn.execute(
            """
            SELECT id, date, shots, made
            FROM training
            WHERE date = ?
            """,
            (training_date,)
        ).fetchall()

        return rows

    finally:
        conn.close()

def save_training_record(training_date, shots, made):
    conn = sqlite3.connect(DB_FILE)

    try:
        cursor = conn.execute(
            """
            INSERT INTO training (date, shots, made)
            VALUES (?, ?, ?)
            """,
            (training_date, shots, made)
        )

        conn.commit()
        return cursor.lastrowid

    finally:
        conn.close()
        