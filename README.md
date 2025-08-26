# Final Project -- Project Based Internship (Rakamin Academy x ID/X Partners) 
This portfolio is the final project of the **Project Based Internship Program** organized by **Rakamin Academy in collaboration with ID/X Partners**
**Project Stages**
**1. Data Warehouse Design**
Created a database with dimension and fact tables:
  - DimAccount, DimCustomer, DimBranch, DimDate, and DimTime 
  - FactTransaction
**2. ETL Job with Apache Hop**
- Loaded DimAccount, DimBranch, and DimCustomer tables from the data lake ("sample" database in SQL Server) into the data warehouse ("DWH" database in SQL Server).
- Consolidated transaction data (CSV, Excel, and transaction_db) into a single transaction_db table in the "sample" database using _insert/update_.
- Transferred data from transaction_db into the FactTransaction table in DWH using _insert/update_.
**3. Stored Procedure (SQL)**
- Daily Transaction -> filtered by _start date, end date, and branch name_.
- Balance per Customer → filterable by _customer name_.
**4. Data Export & Integration with SQLite**
- Exported all tables from the DWH database into CSV format.
- Created a local SQLite database (bank_simulasi.db) containing these exported tables.
- Connected the Streamlit application to bank_simulasi.db for querying and visualization.
**5. Streamlit Web Application**
- Landing Page with sidebar navigation.
- Daily Transaction:
  - Recap table (downloadable as CSV).
  - Bar chart of daily transactions (downloadable as PNG).
  - Line chart of daily total amount (downloadable as PNG).
- Balance per Customer:
  - Recap table (downloadable as CSV).
  - Bar chart comparing Initial Balance vs Current Balance (downloadable as PNG).
