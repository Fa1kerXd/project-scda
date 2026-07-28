import sys
import sqlite3
from PySide6.QtWidgets import QApplication

from app_path import DATABASE_FILE
from database.tables import (
    create_table_coordinator,
    create_table_analyst,
    create_table_corrective_patch,
    create_table_logging,
)
from designer.mainwindow import MainWindow
# -------------------------------------------------------


def main_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database(conn: sqlite3.Connection):
    create_table_coordinator(conn)
    create_table_analyst(conn)
    create_table_corrective_patch(conn)
    create_table_logging(conn)


def main():
    db = main_db()
    init_database(db)

    app = QApplication(sys.argv)
    window = MainWindow(db)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()