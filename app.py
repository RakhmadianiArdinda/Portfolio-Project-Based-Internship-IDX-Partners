import streamlit as st
import pandas as pd
import pyodbc
import altair as alt 

# --- Koneksi ke SQL Server ---
def get_connection():
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"     # ganti dengan server SQL kamu
        "DATABASE=DWH;" # ganti dengan nama database
        "UID=etl_hop;"               # username SQL Server
        "PWD=etlhop;"    # password SQL Server
    )
    return conn

# --- Fungsi panggil Stored Procedure ---
def get_daily_transaction(start_date, end_date):
    conn = get_connection()
    query = """
        EXEC DailyTransaction @start_date=?, @end_date=?
    """
    df = pd.read_sql(query, conn, params=[start_date, end_date])
    conn.close()

    # Format tanggal jadi string biar ga ada jam
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
    
    return df

def get_balance_per_customer(name):
    conn = get_connection()
    query = """
        EXEC BalancePerCustomer @name=?
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
            df = get_daily_transaction(start_date, end_date)

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
                    .configure_title(
                        fontSize=28,
                        anchor="start",
                        color="white"
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
                    .configure_title(
                        fontSize=28,
                        anchor="start",
                        color="white"
                    )
                )
                st.altair_chart(chart2, use_container_width=True)

            else:
                st.info("Tidak ada data pada rentang tanggal ini.")
        else:
            st.warning("Silakan pilih tanggal terlebih dahulu.")

# ================= Balance Per Customer =================
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
                    .configure_title(
                        fontSize=28,
                        anchor="start",
                        color="white"
                    )
                )

                st.altair_chart(chart, use_container_width=True)

            else:
                st.info("Data tidak ditemukan untuk customer ini.")
        else:
            st.warning("Silakan masukkan nama customer terlebih dahulu.")