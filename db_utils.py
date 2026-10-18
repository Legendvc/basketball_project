import sqlite3


DB_FILE = "basketball.db"


def get_training_by_date(training_date):
    conn = sqlite3.connect(DB_FILE)

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