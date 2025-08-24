import streamlit as st
import pandas as pd
import altair as alt 
import sqlite3

# --- Koneksi ke SQLite ---
def get_connection():
    return sqlite3.connect("bank_simulasi.db")

# --- Fungsi Daily Transaction (ganti EXEC jadi query manual) ---
def get_daily_transaction(start_date, end_date):
    conn = sqlite3.connect("bank_simulasi.db")
    query = """
        SELECT 
            DATE(TransactionDate) AS Date,
            COUNT(*) AS TotalTransactions,
            SUM(Amount) AS TotalAmount
        FROM FactTransaction
        WHERE DATE(TransactionDate) BETWEEN ? AND ?
        GROUP BY DATE(TransactionDate)
        ORDER BY Date
    """
    df = pd.read_sql(query, conn, params=[start_date, end_date])
    conn.close()
    
    if not df.empty:
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
    
    return df

# --- Fungsi Balance Per Customer (perbaikan SQL) ---
def get_balance_per_customer(name):
    conn = sqlite3.connect("bank_simulasi.db")
    query = """
        SELECT 
            c.CustomerName,
            a.AccountType,
            a.Balance,
            a.Balance + COALESCE(SUM(
                CASE WHEN f.TransactionType='Deposit' THEN f.Amount ELSE -f.Amount END
            ), 0) AS CurrentBalance
        FROM DimCustomer c
        INNER JOIN DimAccount a ON c.CustomerID = a.CustomerID
        LEFT JOIN FactTransaction f ON a.AccountID = f.AccountID
        WHERE UPPER(TRIM(c.CustomerName)) = UPPER(?)
          AND UPPER(TRIM(a.Status)) = 'ACTIVE'
        GROUP BY c.CustomerName, a.AccountType, a.Balance
    """
    df = pd.read_sql(query, conn, params=[name])
    conn.close()
    return df


# --- Fungsi helper untuk format index mulai dari 1 ---
def format_index(df):
    df_reset = df.reset_index(drop=True)   # reset index lama
    df_reset.index = df_reset.index + 1    # mulai dari 1
    df_reset.index.name = "No"             # beri nama kolom index
    return df_reset

# --- UI Sidebar ---
st.sidebar.title("📌 Menu")
menu = st.sidebar.radio("Pilih Laporan:", ["Daily Transaction", "Balance Per Customer"])

# ================= Daily Transaction =================
if menu == "Daily Transaction":
    st.title("📊 Laporan Daily Transaction")

    # Pilih tanggal
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Pilih Tanggal Awal")
    with col2:
        end_date = st.date_input("Pilih Tanggal Akhir")

    # Tombol submit
    if st.button("Tampilkan Data"):
        if start_date and end_date:
            # convert ke string YYYY-MM-DD
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            df = get_daily_transaction(start_date_str, end_date_str)

            if not df.empty:
                st.subheader("📑 Hasil Tabel")
                st.dataframe(format_index(df))   # tampilkan dengan index mulai 1

                # --- Tombol Download CSV ---
                csv = df.to_csv(index=False).encode("utf-8")
                filename = f"DailyTransaction_{start_date}_{end_date}.csv"
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=filename,
                    mime="text/csv",
                )

                # --- Grafik jumlah transaksi per hari ---
                chart1 = (
                    alt.Chart(df)
                    .mark_bar()
                    .encode(
                        x=alt.X("Date:N", title="Tanggal"),
                        y=alt.Y("TotalTransactions:Q", title="Jumlah Transaksi")
                    )
                    .properties(
                        width=600,
                        height=300,
                        title="Grafik Jumlah Transaksi Harian"
                    )
                )
                st.altair_chart(chart1, use_container_width=True)

                # --- Grafik jumlah nominal transaksi ---
                chart2 = (
                    alt.Chart(df)
                    .mark_line(point=True)
                    .encode(
                        x=alt.X("Date:N", title="Tanggal"),
                        y=alt.Y("TotalAmount:Q", title="Total Nominal Transaksi")
                    )
                    .properties(
                        width=600,
                        height=300,
                        title="Grafik Total Amount Harian"
                    )
                )
                st.altair_chart(chart2, use_container_width=True)

            else:
                st.info("Tidak ada data pada rentang tanggal ini.")
        else:
            st.warning("Silakan pilih tanggal terlebih dahulu.")

elif menu == "Balance Per Customer":
    st.title("🏦 Laporan Balance Per Customer")

    # Input nama customer
    name = st.text_input("Masukkan Nama Customer", value="Bobi Rinaldo")

    if st.button("Tampilkan Balance"):
        if name:
            df = get_balance_per_customer(name)

            if not df.empty:
                st.subheader(f"📑 Laporan Saldo – {name}")
                st.dataframe(format_index(df))   # tampilkan dengan index mulai 1

                # --- Tombol Download CSV ---
                csv = df.to_csv(index=False).encode("utf-8")
                filename = f"Balance_{name.replace(' ', '_')}.csv"
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=filename,
                    mime="text/csv",
                )

                # --- Grafik Balance vs CurrentBalance ---
                chart_df = df.melt(
                    id_vars=["AccountType"],
                    value_vars=["Balance", "CurrentBalance"],
                    var_name="JenisBalance",
                    value_name="Nilai"
                )

                chart = (
                    alt.Chart(chart_df)
                    .mark_bar()
                    .encode(
                        x=alt.X("AccountType:N", title="Tipe Akun"),
                        y=alt.Y("Nilai:Q", title="Jumlah Balance"),
                        color="JenisBalance:N",
                        xOffset="JenisBalance:N"
                    )
                    .properties(
                        width=600,
                        height=400,
                        title=f"Laporan Keuangan – {name}"
                    )
                )

                st.altair_chart(chart, use_container_width=True)

            else:
                st.info("Data tidak ditemukan untuk customer ini.")
        else:
            st.warning("Silakan masukkan nama customer terlebih dahulu.")