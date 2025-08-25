import streamlit as st
import pandas as pd
import altair as alt 
import sqlite3

# --- Koneksi ke SQLite ---
def get_connection():
    return sqlite3.connect("bank_simulasi.db")

# --- Fungsi Daily Transaction (ganti EXEC jadi query manual) ---
def get_daily_transaction(start_date, end_date, branch_name=None):
    conn = sqlite3.connect("bank_simulasi.db")
    cursor = conn.cursor()
    query = """
        SELECT 
            DATE(ft.TransactionDate) AS Date,
            COUNT(*) AS TotalTransactions,
            SUM(ft.Amount) AS TotalAmount
        FROM FactTransaction ft
        INNER JOIN DimBranch db ON ft.BranchID = db.BranchID
        WHERE DATE(ft.TransactionDate) BETWEEN ? AND ?
    """
    params = [start_date, end_date]

    # jika branch_name diberikan, tambahkan ke filter
    if branch_name:
        query += " AND db.BranchName = ?"
        params.append(branch_name)
    query += " GROUP BY DATE(ft.TransactionDate) ORDER BY Date"
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    # ubah ke dataframe
    df = pd.DataFrame(results, columns=["Date", "TotalTransactions", "TotalAmount"])
    
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
    st.title("💰 Laporan Keuangan")

    # Pilih tanggal
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Tanggal Awal")
    with col2:
        end_date = st.date_input("Tanggal Akhir")

    # Pilih branch 
    conn = sqlite3.connect("bank_simulasi.db")
    branches = conn.execute("SELECT DISTINCT BranchName FROM DimBranch").fetchall()
    conn.close()
    branch_options = [b[0] for b in branches]
    branch_options.insert(0, "Semua Cabang")  # opsi untuk semua cabang
    selected_branch = st.selectbox("Pilih Cabang", branch_options)

    # Tombol submit
    if st.button("Tampilkan Data"):
        if start_date and end_date:
            # convert ke string YYYY-MM-DD
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")

            # jika pilih semua branch, kirim None ke fungsi 
            branch_name = None if selected_branch == "Semua Cabang" else selected_branch
            
            df = get_daily_transaction(start_date_str, end_date_str, branch_name)

            if not df.empty:
                st.subheader("📑 Rekap")
                st.dataframe(format_index(df))   # tampilkan dengan index mulai 1

                # --- Tombol Download CSV ---
                csv = df.to_csv(index=False).encode("utf-8")
                filename = f"DailyTransaction_{start_date}_{end_date}_{branch_name}.csv"
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
                        title=alt.TitleParams(
                            text="📊 Grafik Jumlah Transaksi Harian",
                            fontSize=28,
                            anchor="start",
                            color="white"
                        ),
                        padding={"top": 20}  # beri ruang untuk judul
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
                        title=alt.TitleParams(
                            text="📈Grafik Total Amount Harian📉",
                            fontSize=28,           # font size tetap 28
                            anchor="start",
                            color="white"
                        ),
                        padding={"top": 20}
                    )
                )
                st.altair_chart(chart2, use_container_width=True)
            else:
                st.info("Tidak ada data pada rentang tanggal ini.")
        else:
            st.warning("Silakan pilih tanggal terlebih dahulu.")

elif menu == "Balance Per Customer":
    st.title("🗂️ Laporan Balance Per Customer")

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
                        title=f"💳 Laporan Keuangan – {name}"
                    )
                    .configure_title(fontSize=28, anchor="start", color="white")
                )

                st.altair_chart(chart, use_container_width=True)

            else:
                st.info("Data tidak ditemukan untuk customer ini.")
        else:
            st.warning("Silakan masukkan nama customer terlebih dahulu.")