import sqlite3
from tabulate import tabulate

DB_PATH = "clarity/data/clarity.db"

def view_logs():
    """Display all pillar logs in a table format."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, date, pillar, hours FROM pillar_logs ORDER BY date DESC;")
    rows = c.fetchall()
    conn.close()

    if not rows:
        print("⚠ No logs found.")
        return

    headers = ["ID", "Date", "Pillar", "Hours"]
    print(tabulate(rows, headers, tablefmt="fancy_grid"))

if __name__ == "__main__":
    view_logs()
