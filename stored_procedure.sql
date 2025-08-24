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

EXEC DailyTransaction @start_date = '2024-01-18', @end_date = '2024-01-20';

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