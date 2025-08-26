import streamlit as st
import pandas as pd
import altair as alt 
import sqlite3
import io 
from altair_saver import save
import matplotlib.pyplot as plt


# ================= Connect to SQLite ================= #
def get_connection():
    return sqlite3.connect("bank_simulasi.db")

# ================= Daily Transaction Function ================= #
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

    # If branch_name is provided, add it to the filter  
    if branch_name:
        query += " AND db.BranchName = ?"
        params.append(branch_name)
    query += " GROUP BY DATE(ft.TransactionDate) ORDER BY Date"
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    # Convert to dataframe
    df = pd.DataFrame(results, columns=["Date", "TotalTransactions", "TotalAmount"])
    
    return df

# ================= Balance Per Customer Function ================= #
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


# ================= Helper function to start indexing from 1 ================= #
def format_index(df):
    df_reset = df.reset_index(drop=True)   # Reset original index
    df_reset.index = df_reset.index + 1    # Start index from 1 
    df_reset.index.name = "No"             # Give a name to the index column
    return df_reset

# ================= Read query param when first loaded ================= #
query_params = st.query_params
if "page" not in st.session_state:
    st.session_state.page = query_params.get("page", "landing")

# ================= Sidebar nav ================= #
if st.session_state.page != "landing":
    with st.sidebar:
        if st.button("🏠 Kembali ke Beranda"):
            st.session_state.page = "landing"
            st.query_params.page = "landing"
            st.rerun()

# ================= Landing page ================= #
if st.session_state.page == "landing":
    st.title("🏦 Dashboard Bank Simulasi")
    st.write("Selamat datang! Pilih laporan yang ingin Anda lihat:")

    menu = st.selectbox(
        "📑 Pilih Laporan:",
        ["Daily Transaction", "Balance Per Customer"],
        index=None,
        placeholder="-- Laporan --"
    )

    if menu:
        st.session_state.page = menu
        st.query_params.page = menu  # Save to URL
        st.rerun()
    
# ================= Daily Transaction ================= #
elif st.session_state.page == "Daily Transaction":
    st.header("💰 Laporan Keuangan")
    st.write("Laporan ini menampilkan rekap transaksi harian berdasarkan tanggal dan cabang.")

        # Choose date range
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Tanggal Awal")
    with col2:
        end_date = st.date_input("Tanggal Akhir")

        # Choose branch 
    conn = sqlite3.connect("bank_simulasi.db")
    branches = conn.execute("SELECT DISTINCT BranchName FROM DimBranch").fetchall()
    conn.close()
    branch_options = [b[0] for b in branches]
    branch_options.insert(0, "Semua Cabang")  # Option for all branches
    selected_branch = st.selectbox("Pilih Cabang", branch_options)

        # Submit button
    if st.button("Tampilkan Data"):
        if start_date and end_date:
            # Convert to string YYYY-MM-DD
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")

            # If choose all branches, send None to the function 
            branch_name = None if selected_branch == "Semua Cabang" else selected_branch
            
            # For file naming -> replace None with "Seluruh_Cabang"
            branch_label = "Seluruh_Cabang" if branch_name is None else branch_name

            df = get_daily_transaction(start_date_str, end_date_str, branch_name)

            if not df.empty:
                st.subheader("📑 Rekap")
                st.dataframe(format_index(df))   # Show with index starting from 1

                # ================= CSV Download Button ================= #
                csv = df.to_csv(index=False).encode("utf-8")
                filename = f"DailyTransaction_{start_date}_{end_date}_{branch_label}.csv"
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=filename,
                    mime="text/csv",
                )

                # Give some space so it's not too close to chart 2
                st.markdown("<br>", unsafe_allow_html=True)

                # ================= Graph of the number of transactions per day ================= #
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
                        padding={"top": 20}  # Give some space for the tittle 
                    )
                )
                st.altair_chart(chart1, use_container_width=True)

                # ================= Download Chart 1 (Matplotlib) PNG ================= #
                fig, ax = plt.subplots(figsize=(8,4))
                df.groupby("Date")["TotalTransactions"].sum().plot(kind="bar", color="#6baed6" ,ax=ax)
                ax.set_title("Grafik Jumlah Transaksi Harian", color="white", fontsize=16)
                ax.set_xlabel("Tanggal", color="white")
                ax.set_ylabel("Jumlah Transaksi", color="white")
                plt.xticks(rotation=45, color="white")
                plt.yticks(color="white")

                # Dark mode background 
                ax.set_facecolor("#0E1117")
                fig.patch.set_facecolor("#0E1117")
                for spine in ax.spines.values():
                    spine.set_color("white")

                buf1 = io.BytesIO()
                plt.savefig(buf1, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
                buf1.seek(0)
                st.download_button(
                    label="📥 Download Grafik Jumlah Transaksi Harian (PNG)",
                    data=buf1,
                    file_name=f"Jumlah Transaksi Harian_{start_date_str}_{end_date_str}_{branch_label}.png",
                    mime="image/png",
                )
                plt.close(fig) 

                # Give some space so it's not too close to chart 3
                st.markdown("<br>", unsafe_allow_html=True)

                # ================= Graph of nominal transaction amounts ================= #
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
                            fontSize=28,           
                            anchor="start",
                            color="white"
                        ),
                        padding={"top": 20}
                    )
                )
                st.altair_chart(chart2, use_container_width=True)

                # ================= Download Chart 2 (Matplotlib) PNG ================= #
                fig, ax = plt.subplots(figsize=(8,4))
                df.groupby("Date")["TotalAmount"].sum().plot(kind="line", marker="o", color="#6baed6", ax=ax)

                ax.set_title("Grafik Total Amount Harian", fontsize=16, color="white")
                ax.set_xlabel("Tanggal", color="white")
                ax.set_ylabel("Total Nominal Transaksi", color="white")

                plt.xticks(rotation=45, color="white")
                plt.yticks(color="white")

                # Set scientific notation (1e7) to white
                ax.yaxis.get_offset_text().set_color("white")
            
                # Dark mode background 
                ax.set_facecolor("#0E1117")
                fig.patch.set_facecolor("#0E1117")
                for spine in ax.spines.values():
                    spine.set_color("white")

                buf2 = io.BytesIO()
                plt.savefig(buf2, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
                buf2.seek(0)

                st.download_button(
                    label="📥 Download Grafik Total Amount Harian (PNG)",
                    data=buf2,
                    file_name=f"TotalAmountHarian_{start_date_str}_{end_date_str}_{branch_label}.png",
                    mime="image/png",
                )

                plt.close(fig)

            else:
                st.info("Tidak ada data pada rentang tanggal ini.")
        else:
            st.warning("Silakan pilih tanggal terlebih dahulu.")

elif st.session_state.page == "Balance Per Customer":
    st.header("🗂️ Laporan Balance Per Customer")
    st.write("Laporan ini menampilkan saldo awal dan saldo terkini dari setiap akun customer")

    # Input customer name
    name = st.text_input("Masukkan Nama Customer", value="Bobi Rinaldo")

    if st.button("Tampilkan Balance"):
        if name:
            df = get_balance_per_customer(name)

            if not df.empty:
                st.subheader(f"📑 Laporan Saldo – {name}")
                st.dataframe(format_index(df))   # Show with index starting from 1 

                # ================= CSV Download Button ================= #
                csv = df.to_csv(index=False).encode("utf-8")
                filename = f"Balance_{name.replace(' ', '_')}.csv"
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=filename,
                    mime="text/csv",
                )

                # ================= Download Chart Balance vs Current Balance ================= #
                chart_df = df.melt(
                    id_vars=["AccountType"],
                    value_vars=["Balance", "CurrentBalance"],
                    var_name="JenisBalance",
                    value_name="Nilai"
                )

                # ================= Chart to be displayed in Streamlit (use emoji) ================= #
                chart_display = (
                    alt.Chart(chart_df, background="#0E1117")
                    .mark_bar()
                    .encode(
                        x=alt.X("AccountType:N", title="Tipe Akun"),
                        y=alt.Y("Nilai:Q", title="Jumlah Balance"),
                        color= alt.Color(
                            "JenisBalance:N",
                            scale=alt.Scale(range=["#6baed6", "#217b15"]),
                            legend=alt.Legend(title="Jenis Balance", labelColor="white", titleColor="white")
                        ),
                        xOffset="JenisBalance:N"
                    )
                    .properties(
                        width=600,
                        height=400,
                        title=alt.TitleParams(
                            text=f"💳 Laporan Keuangan – {name}",   # Use emoji
                            fontSize=28,
                            anchor="start",
                            color="white"
                        )
                    )
                    .configure_axis(labelColor="white", titleColor="white")
                    .configure_view(strokeWidth=0)
                )

                st.altair_chart(chart_display, use_container_width=True)

                # ================= Chart to download (title without emoji) PNG ================= #
                chart_download = chart_display.properties(
                    title=alt.TitleParams(
                        text=f"Laporan Keuangan – {name}",   # Without emoji
                        fontSize=28,
                        anchor="start",
                        color="white"
                    )
                )

                # Save to PNG buffer
                buf = io.BytesIO()
                chart_download.save(buf, format="png", method="vl-convert")
                buf.seek(0)

                # ================= PNG Download Button ================= #
                st.download_button(
                    label="📥 Download Grafik Balance (PNG)",
                    data=buf,
                    file_name=f"Balance_vs_CurrentBalance_{name.replace(' ', '_')}.png",
                    mime="image/png",
                )


            else:
                st.info("Data tidak ditemukan untuk customer ini.")
        else:
            st.warning("Silakan masukkan nama customer terlebih dahulu.")

# ================== FOOTER ================== #
st.markdown(
    """
    <hr style="margin-top:50px; margin-bottom:10px">
    <p style="text-align: center; font-size: 14px; color: gray;">
        Created by <b>Rakhmadiani ✨</b> (with a LOT of help from ChatGPT 😅)
    </p>
    """,
    unsafe_allow_html=True
)