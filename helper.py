# ChatDB Data Safety Checker
import re

def get_next_customer_id(cursor):
    cursor.execute("SELECT MAX(CustomerID) FROM Employees")
    max_emp = cursor.fetchone()[0] or 100000

    cursor.execute("SELECT MAX(CustomerID) FROM Patients")
    max_pat = cursor.fetchone()[0] or 100000

    cursor.execute("SELECT MAX(CustomerID) FROM Orders")
    max_order = cursor.fetchone()[0] or 100000

    return max(max_emp, max_pat, max_order) + 1


def clean_sql_output(sql):
    sql = sql.strip()
    if sql.startswith("```sql"):
        sql = sql.replace("```sql", "").strip()
    if sql.startswith("```"):
        sql = sql.replace("```", "").strip()
    if sql.endswith("```"):
        sql = sql[:-3].strip()
    lines = sql.split('\n')
    cleaned = [line for line in lines if not line.strip().startswith("--")]
    return '\n'.join(cleaned)


def confirm_dangerous_query(sql):
    sql = sql.strip().lower()
    if re.match(r'^(delete|update)\b', sql):
        if "where" not in sql:
            print("\n⚠️ Dangerous query detected (no WHERE clause). Aborting for safety.")
            return False
        confirm = input("\n⚠️ Are you sure you want to execute this query? Type 'yes' to proceed: ")
        return confirm.strip().lower() == "yes"
    return True


def is_valid_sql_start(sql):
    sql = sql.strip().lower()
    return sql.startswith(("select", "insert", "update", "delete", "with"))
