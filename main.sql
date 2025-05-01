-- Create Databases
DROP DATABASE IF EXISTS UnifiedDB;
CREATE DATABASE UnifiedDB;
USE UnifiedDB;

-- Create Employees table
DROP TABLE IF EXISTS Employees;
CREATE TABLE Employees (
    Education VARCHAR(20),
    JoiningYear INT,
    City VARCHAR(50),
    PaymentTier INT,
    Age INT,
    Gender VARCHAR(10),
    EverBenched VARCHAR(10),
    ExperienceInCurrentDomain INT,
    LeaveOrNot INT,
    CustomerID INT PRIMARY KEY
);


-- Create ECommerce table
DROP TABLE IF EXISTS Orders;
CREATE TABLE Orders (
    OrderID INT AUTO_INCREMENT PRIMARY KEY, -- InvoiceNo cannot be PK bc an invoice can have many lines/products
    InvoiceNo VARCHAR(10),
    StockCode VARCHAR(20),
    Description VARCHAR(100),
    Quantity INT,
    InvoiceDate DATETIME,
    UnitPrice DECIMAL(10,2),
    CustomerID INT,
    Country VARCHAR(30)
);


-- Create Healthcare table
DROP TABLE IF EXISTS Patients;
CREATE TABLE Patients (
    Name VARCHAR(50),
    Age INT,
    Gender VARCHAR(10),
    BloodType VARCHAR(5),
    MedicalCondition VARCHAR(30),
    DateOfAdmission DATE,
    Doctor VARCHAR(50),
    Hospital VARCHAR(50),
    InsuranceProvider VARCHAR(20),
    BillingAmount DECIMAL(15,2),
    RoomNumber INT,
    AdmissionType VARCHAR(20),
    DischargeDate DATE,
    Medication VARCHAR(20),
    TestResults VARCHAR(20),
    CustomerID INT PRIMARY KEY
);