------------------------------ DATA WAREHOUSE ------------------------------
CREATE DATABASE DWH

------------------------------ TABEL DIMENSI ------------------------------
-- Tabel Customer 
CREATE TABLE DimCustomer (
	CustomerID INT PRIMARY KEY ,
	CustomerName VARCHAR(50), 
	Address VARCHAR(MAX),
	CityName VARCHAR(50),
	StateName VARCHAR(50),
	Age VARCHAR(3),
	Gender VARCHAR(10),
	Email VARCHAR(50) 
)

-- Tabel Account
CREATE TABLE DimAccount (
	AccountID INT NOT NULL PRIMARY KEY, 
	CustomerID INT FOREIGN KEY REFERENCES DimCustomer(CustomerID),
	AccountType VARCHAR(10),
	Balance INT,
	DateOpened DATETIME2(0),
	Status VARCHAR(10)
)

-- Tabel Branch 
CREATE TABLE DimBranch (
	BranchID INT NOT NULL PRIMARY KEY, 
	BranchName VARCHAR(50),
	BranchLocation VARCHAR(50)
)

------------------------------ TABEL FAKTA ------------------------------
CREATE TABLE FactTransaction ( 
	TransactionID INT NOT NULL PRIMARY KEY,
	AccountID INT NULL FOREIGN KEY REFERENCES DimAccount(AccountID), 
	TransactionDate DATETIME2(0), 
	Amount INT, 
	TransactionType VARCHAR(50), 
	BranchID INT NULL FOREIGN KEY REFERENCES DimBranch(BranchID),
	DateKey INT FOREIGN KEY REFERENCES DimDate(date_key),
	TimeKey INT FOREIGN KEY REFERENCES DimTime(time_key)
)
drop table FactTransaction
select * from transaction_db
select * from FactTransaction
select * from DimAccount
select * from DimBranch
select * from DimCustomer



