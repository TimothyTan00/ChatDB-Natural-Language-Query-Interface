# ChatDB: Natural Language Query Interface

## 📌 Overview
ChatDB is an AI-powered database interface that allows users to interact with relational databases using natural language. Instead of writing complex SQL queries, users can simply type questions like "Show me all female employees in the HR department who placed at least 2 orders", and ChatDB will convert it into a SQL query and retrieve the results.

## 🔹 Key Features
- **Query Execution**: Convert natural language into SQL and fetch results.
- **Schema Exploration**: Ask about database tables, columns, and relationships.
- **Data Modification**: Insert, update, or delete records using conversational English.
- **Multi-Table Queries**: Support for JOIN operations and complex queries.

## 🛠 Tech Stack
- **Backend**: Python
- **Database**: MySQL
- **NLP Processing**: OpenAI GPT-4o-mini via API
- **Interface**: Command-Line Interface.

## 🚀 Future Improvements
- Develop a web-based interface with Flask.
- Enhance query accuracy with prompt engineering.
- Create an automated CSV loading script.
- Introduce session-based memory.
- Add support for NoSQL databases.

# 🔧 Setup Instructions
Before running ChatDB, complete the following steps:

1. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure you have the required software:
```bash
pip list
```

4. Add your personal 🔑 OpenAI API key to the following line in ```chatdb_main.py```:
```bash
client = openai.OpenAI(api_key="")
```

### Required Software

- Python 3.10 or higher
- MySQL Server (recommended: MySQL 8.0+)
- pip (Python package manager)

## SQL Schema Loading Instructions
1. Start MySQL:
```bash
mysql -u root -p --local-infile=1
```

2. Load SQL schema and data:
```bash
SOURCE /Users/timothytan/PycharmProjects/DSCI 551 Data Management/ChatDB_Project/main.sql;

LOAD DATA LOCAL INFILE '/Users/timothytan/PycharmProjects/DSCI 551 Data Management/ChatDB_Project/employee_with_customerid.csv' INTO TABLE Employees FIELDS TERMINATED BY ',' IGNORE 1 ROWS;
LOAD DATA LOCAL INFILE '/Users/timothytan/PycharmProjects/DSCI 551 Data Management/ChatDB_Project/orders_mapped.csv' INTO TABLE Orders FIELDS TERMINATED BY ',' ENCLOSED BY '"' IGNORE 1 ROWS (@InvoiceNo, @StockCode, @Description, @Quantity, @InvoiceDate, @UnitPrice, @CustomerID, @Country) SET InvoiceNo = @InvoiceNo, StockCode = @StockCode, Description = @Description, Quantity = @Quantity, InvoiceDate = STR_TO_DATE(@InvoiceDate, '%c/%e/%Y %k:%i'), UnitPrice = @UnitPrice, CustomerID = @CustomerID, Country = @Country;
LOAD DATA LOCAL INFILE '/Users/timothytan/PycharmProjects/DSCI 551 Data Management/ChatDB_Project/patients_with_customerid.csv' INTO TABLE Patients FIELDS TERMINATED BY ','  ENCLOSED BY '"'  IGNORE 1 ROWS;
```

3. Exit SQL and run:
```bash
python chatdb_main.py
```





