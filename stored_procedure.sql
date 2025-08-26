CREATE PROCEDURE DailyTransaction
    @start_date DATE,
    @end_date DATE
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        CAST(TransactionDate AS DATE) AS [Date],
        COUNT(*) AS TotalTransactions,
        SUM(Amount) AS TotalAmount
    FROM FactTransaction  
    WHERE CAST(TransactionDate AS DATE) BETWEEN @start_date AND @end_date
    GROUP BY CAST(TransactionDate AS DATE)
    ORDER BY [Date];
END;
GO

EXEC DailyTransaction @start_date = '2024-01-01', @end_date = '2024-01-31';

CREATE PROCEDURE BalancePerCustomer
    @name NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        c.CustomerName,
        a.AccountType,
        a.Balance,
        a.Balance 
            + COALESCE(SUM(CASE 
                               WHEN f.TransactionType = 'Deposit' THEN f.Amount
                               ELSE -f.Amount 
                           END), 0) AS CurrentBalance
    FROM DimCustomer c
    INNER JOIN DimAccount a 
        ON c.CustomerID = a.CustomerID
    LEFT JOIN FactTransaction f 
        ON a.AccountID = f.AccountID
    WHERE c.CustomerName = @name
      AND a.Status = 'Active'
    GROUP BY c.CustomerName, a.AccountType, a.Balance;
END;
GO
    

EXEC BalancePerCustomer @name = "Shelly Juwita"

select * from DimCustomer
select * from DimAccount
select * from FactTransaction

drop procedure DailyTransaction

CREATE PROCEDURE DailyTransaction
    @start_date DATE,
    @end_date DATE,
    @BranchName NVARCHAR(100) = NULL  -- default NULL supaya opsional
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        CAST(ft.TransactionDate AS DATE) AS [Date],
        COUNT(*) AS TotalTransactions,
        SUM(ft.Amount) AS TotalAmount
    FROM FactTransaction ft
    INNER JOIN DimBranch db ON ft.BranchID = db.BranchID
    WHERE CAST(ft.TransactionDate AS DATE) BETWEEN @start_date AND @end_date
      AND (@BranchName IS NULL OR db.BranchName = @BranchName)  -- filter branch jika diisi
    GROUP BY CAST(ft.TransactionDate AS DATE)
    ORDER BY [Date];
END;
GO

EXEC DailyTransaction @start_date = '2024-01-01', @end_date = '2024-01-31', @BranchName = 'KC Bekas';
EXEC DailyTransaction @start_date = '2024-01-01', @end_date = '2025-08-26', @BranchName = 'KC Jakarta';
EXEC DailyTransaction @start_date = '2024-01-01', @end_date = '2024-01-31', @BranchName = 'KC Tangerang';
EXEC DailyTransaction @start_date = '2024-01-01', @end_date = '2024-01-31', @BranchName = 'KC Depok';
EXEC DailyTransaction @start_date = '2024-01-01', @end_date = '2024-01-31', @BranchName = 'KC Bogor';