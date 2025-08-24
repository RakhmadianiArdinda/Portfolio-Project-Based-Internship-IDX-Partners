import sqlite3
from datetime import datetime

# Koneksi ke SQLite
db_path = 'bank_simulasi.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ---- Fungsi bantu untuk convert format tanggal/waktu ----
def format_date(text):
    # Konversi string ke 'YYYY-MM-DD'
    try:
        dt = datetime.strptime(text, '%Y-%m-%d')  # sesuaikan dengan format asli
        return dt.strftime('%Y-%m-%d')
    except:
        return text  # jika gagal, biarkan sama

def format_time(text):
    # Konversi string ke 'HH:MM:SS'
    try:
        t = datetime.strptime(text, '%H:%M:%S')  # sesuaikan dengan format asli
        return t.strftime('%H:%M:%S')
    except:
        return text

def format_datetime(text):
    # Konversi string ke 'YYYY-MM-DD HH:MM:SS'
    try:
        dt = datetime.strptime(text, '%Y-%m-%d %H:%M:%S')  # sesuaikan format asli
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return text

# ---- 1. DimDate ----
cursor.execute("""
CREATE TABLE IF NOT EXISTS DimDate_new (
    date_key INTEGER PRIMARY KEY,
    full_date TEXT,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    month_name TEXT,
    week_of_year INTEGER,
    day_of_month INTEGER,
    day_of_week INTEGER,
    day_name TEXT,
    is_weekend INTEGER
)
""")

cursor.execute("SELECT * FROM DimDate")
rows = cursor.fetchall()
for row in rows:
    new_row = (
        row[0],                # date_key
        format_date(row[1]),   # full_date
        *row[2:]               # kolom lain
    )
    cursor.execute("INSERT INTO DimDate_new VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", new_row)

cursor.execute("DROP TABLE DimDate")
cursor.execute("ALTER TABLE DimDate_new RENAME TO DimDate")

# ---- 2. DimTime ----
cursor.execute("""
CREATE TABLE IF NOT EXISTS DimTime_new (
    time_key INTEGER PRIMARY KEY,
    full_time TEXT,
    hour INTEGER,
    minute INTEGER,
    second INTEGER,
    period TEXT,
    shift TEXT
)
""")

cursor.execute("SELECT * FROM DimTime")
rows = cursor.fetchall()
for row in rows:
    new_row = (
        row[0],               # time_key
        format_time(row[1]),  # full_time
        *row[2:]              # kolom lain
    )
    cursor.execute("INSERT INTO DimTime_new VALUES (?, ?, ?, ?, ?, ?, ?)", new_row)

cursor.execute("DROP TABLE DimTime")
cursor.execute("ALTER TABLE DimTime_new RENAME TO DimTime")

# ---- 3. FactTransaction ----
cursor.execute("""
CREATE TABLE IF NOT EXISTS FactTransaction_new (
    TransactionID INTEGER PRIMARY KEY,
    AccountID INTEGER,
    TransactionDate TEXT,
    Amount INTEGER,
    TransactionType TEXT,
    BranchID INTEGER,
    DateKey INTEGER,
    TimeKey INTEGER
)
""")

cursor.execute("SELECT * FROM FactTransaction")
rows = cursor.fetchall()
for row in rows:
    new_row = (
        row[0],                    # TransactionID
        row[1],                    # AccountID
        format_datetime(row[2]),   # TransactionDate
        *row[3:]                   # kolom lain
    )
    cursor.execute("INSERT INTO FactTransaction_new VALUES (?, ?, ?, ?, ?, ?, ?, ?)", new_row)

cursor.execute("DROP TABLE FactTransaction")
cursor.execute("ALTER TABLE FactTransaction_new RENAME TO FactTransaction")

# Commit dan tutup koneksi
conn.commit()
conn.close()

print("Konversi tipe tanggal/waktu selesai!")
