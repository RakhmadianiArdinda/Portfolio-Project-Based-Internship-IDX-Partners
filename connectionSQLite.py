import pandas as pd
import sqlite3

# Buat koneksi SQLite
conn = sqlite3.connect("bank_simulasi.db")

# Import CSV jadi tabel
pd.read_csv("DimCustomer.csv").to_sql("DimCustomer", conn, if_exists="replace", index=False)
pd.read_csv("DimAccount.csv").to_sql("DimAccount", conn, if_exists="replace", index=False)
pd.read_csv("DimBranch.csv").to_sql("DimBranch", conn, if_exists="replace", index=False)
pd.read_csv("FactTransaction.csv").to_sql("FactTransaction", conn, if_exists="replace", index=False)

conn.close()
print("Database SQLite berhasil dibuat: bank_simulasi.db")
