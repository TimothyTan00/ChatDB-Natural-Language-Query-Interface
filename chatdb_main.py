import openai
import mysql.connector
from helper import (
    clean_sql_output,
    confirm_dangerous_query,
    get_next_customer_id,
    is_valid_sql_start
)

# Set up OpenAI Client here
client = openai.OpenAI(api_key="")

# ---- Prompt Template ----
SQL_PROMPT = """
You are a MySQL SQL query generator. The database has three tables:

Employees(Education, JoiningYear, City, PaymentTier, Age, Gender, EverBenched, ExperienceInCurrentDomain, LeaveOrNot, CustomerID)
Patients(Name, Age, Gender, BloodType, MedicalCondition, DateOfAdmission, Doctor, Hospital, InsuranceProvider, 
BillingAmount, RoomNumber, AdmissionType, DischargeDate, Medication, TestResults, CustomerID)
Orders(InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country)

---
Your task is to generate clean, correct MySQL queries based on the user instruction below.

Instruction: {instruction}

---
Schema exploration rules:
- If the user asks to "list", "show", or "describe" something about the schema, return the appropriate SQL for schema exploration (e.g., `SHOW TABLES`, `DESCRIBE table_name`).
- For example:
  - "What tables are in the database?" → "SHOW TABLES;"
  - "Describe the Employees table." → "DESCRIBE Employees;"
  - "Give me a few rows from Patients" → "SELECT * FROM Patients LIMIT 5;"

Prompt Rules:
- Return a valid SQL query.
- Don't wrap the SQL in markdown-style triple backticks (```sql).
- Do not use SELECT * unless explicitly asked.
- Avoid using DISTINCT unless necessary for the logic.
- Use table aliases (e.g., p, o, e) for clarity in joins.
- Always join tables using shared keys (e.g., CustomerID) where applicable. 
- When grouping, group by unique identifiers like CustomerID or PatientID where appropriate.
- If the output only requests names, it is okay to omit IDs from the SELECT clause.
- Order results by relevant columns when the instruction implies ranking or sorting.
- Only use date fields like InvoiceDate from the Orders table.
- When filtering by year or month, use the appropriate MySQL functions: YEAR(), MONTH(), etc.
- Employees and Patients have unique CustomerIDs.
- When comparing Patients and Employees, use UNION ALL across separate queries.
- If comparing employees and patients, use `UNION ALL` and label rows using `'Employee'` or `'Patient'`.
- Do not use unrelated columns like PaymentTier or BillingAmount to represent spending — always calculate it from Orders using SUM(Quantity * UnitPrice).
- When aggregating over groups (e.g., hospital, city), include the aggregate value (e.g., SUM or COUNT) in the SELECT clause.
- Do not invent new tables. Always check columns in the existing three tables and use those for the answer, if applicable.
- When matching product descriptions, use `LIKE '%keyword%'` for partial matches.
- Use `DISTINCT` to avoid duplicate IDs unless aggregation is needed.
- Do not query 'Name' from Employees table.
- If the instruction asks for the name of a product, it is referring to the Description column
- Do not assume there is a `Customers` table. Use `CustomerID` and `Country` from the `Orders` table for customer details.
---

Prompt Logic for Cost:
- To calculate the cost, use `SUM(Quantity * UnitPrice)` in your SELECT statement for cost.
- If the instruction mentions "cost," replace with `SUM(o.Quantity * o.UnitPrice)` for accurate computation.
- When calculating order costs, use `SUM(Quantity * UnitPrice)` grouped by `InvoiceNo`.
- If selecting non-aggregated fields (like Description, Country, or CustomerID) along with SUM(Quantity * UnitPrice), group by all non-aggregated fields or use a subquery that performs the aggregation, then filter or sort in the outer query.
- MySQL uses ONLY_FULL_GROUP_BY mode. If a column is not aggregated or in the GROUP BY clause, wrap the aggregation in a subquery and select from that.
---

The assistant should also support SQL data modification commands: INSERT, UPDATE, DELETE.

Examples:
- Insert a new employee named John Doe who is 28, male, lives in Pune, in payment tier 2, with 3 years of experience.
- Update the age of employee with CustomerID 1050 to 30.
- Delete the employee who lives in Bangalore and has CustomerID 1122.

If an INSERT or UPDATE is requested, ensure all required fields are provided.
Always use explicit column names in INSERT statements.

Prompt Rules:
- The Employees table does NOT include a 'Name' column. Do NOT generate queries using Employee names.Use CustomerID as the identifier instead.
- For INSERT queries, always use CustomerID = 9999 as a placeholder. It will be replaced with a unique ID.
- Valid values for Education are: 'Bachelors', 'Masters', 'PHD'. Do not use phrases like 'Bachelor's degree'.
- LeaveOrNot must be 0 (still with company) or 1 (left the company).
- EverBenched must be 'Yes' or 'No'.
- CustomerID must be a unique integer.
- Always use numeric values for integers and avoid putting strings in number fields.
- Do not include quotes around CustomerID.
- Use NULL for any unknown optional field.
"""

def generate_sql(instruction):
    prompt = SQL_PROMPT.format(instruction=instruction)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=200
    )
    content = response.choices[0].message.content
    return content.strip() if content else ""

def run_sql_query(sql, conn, cursor):
    try:
        cursor.execute(sql)
        if sql.strip().lower().startswith("show tables"):
            tables = cursor.fetchall()
            print("\n📦 Available Tables:")
            for table in tables:
                print("-", table[0])
        elif sql.strip().lower().startswith("describe"):
            columns = cursor.fetchall()
            print("\n📋 Column Attributes:")
            print([col[0] for col in columns])
        elif sql.strip().lower().startswith("select"):
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            print("\nQuery Results:")
            print(columns)
            for row in rows:
                print([str(item) for item in row])
        else:
            conn.commit()
            if cursor.rowcount == 0:
                print("\nResults: \n⚠️ Your query was valid but did not affect any rows.")
            else:
                print(f"✅ Query executed successfully. Rows affected: {cursor.rowcount}")
    except Exception as e:
        print(f"❌ SQL execution error: {e}")

def main():
    print("\nWelcome to ChatDB, your Natural Language SQL Assistant!\n")
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="E6741586F",
            database="UnifiedDB",
            allow_local_infile=True
        )
        cursor = conn.cursor()
    except mysql.connector.Error as err:
        print("❌ Could not connect to the database:", err)
        return

    while True:
        user_input = input("\nPlease ask something (or type 'exit'): \n> ").strip()
        if user_input.lower() == "exit":
            break
        if not user_input:
            continue  # skip empty prompts

        if any(kw in user_input.lower() for kw in ["what tables", "show tables", "list tables"]):
            run_sql_query("SHOW TABLES;", conn, cursor)
            continue

        if "describe" in user_input.lower() or "attributes" in user_input.lower():
            for table_name in ["employees", "patients", "orders"]:
                if table_name in user_input.lower():
                    run_sql_query(f"DESCRIBE {table_name.capitalize()};", conn, cursor)
                    break
            continue

        if "sample query" in user_input.lower():
            sample_prompt = "Generate a creative sample SQL query that uses multiple tables or advanced features."
            sample_sql = generate_sql(sample_prompt)
            print("\n📄 Sample Query:")
            print(sample_sql)
            confirmation = input("\n⚠️ Run this query? Type 'yes' to proceed: ").strip().lower()
            if confirmation == "yes":
                run_sql_query(sample_sql, conn, cursor)
            continue

        if not user_input or user_input.lower() in ["hello", "quit", "goodbye"]:
            print("⚠️ Please provide a valid query.")
            continue

        raw_sql = generate_sql(user_input)
        sql_query = clean_sql_output(raw_sql)

        if ";" in sql_query.strip(";"):
            print("⚠️ Please only provide one SQL statement at a time.")
            continue

        if sql_query.strip().lower().endswith(("and", "or", "where")):
            print("⚠️ Detected an incomplete SQL query. Skipping execution.")
            continue

        if not is_valid_sql_start(sql_query):
            print("⚠️ ChatDB could not return a valid answer. Please rephrase your question.")
            continue

        if not confirm_dangerous_query(sql_query):
            continue

        if ("insert into employees" in sql_query.lower() or "insert into patients" in sql_query.lower()) and "customerid" in sql_query.lower():
            next_id = get_next_customer_id(cursor)
            sql_query = sql_query.replace("9999", str(next_id))
            print(f"\nResults:\n {sql_query}")

        print(f"\n📄 Executing SQL Query:\n{sql_query}")
        run_sql_query(sql_query, conn, cursor)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
