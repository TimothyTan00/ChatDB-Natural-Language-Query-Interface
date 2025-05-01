import pandas as pd

# Load CSV files with proper encoding
employee_df = pd.read_csv("Trash/employee.csv")
ecommerce_df = pd.read_csv("Trash/ecommerce.csv", encoding='latin1')  # Specify encoding
healthcare_df = pd.read_csv("Trash/healthcare.csv")

# Assign UserIDs to Employees
employee_df["UserID"] = range(1001, 1001 + len(employee_df))

# Create a mapping for UserID → CustomerID
customer_to_userid = {customer: user for customer, user in zip(ecommerce_df["CustomerID"].unique(), employee_df["UserID"][:len(ecommerce_df["CustomerID"].unique())])}

# Replace CustomerID with UserID in E-commerce data
ecommerce_df["UserID"] = ecommerce_df["CustomerID"].map(customer_to_userid)
ecommerce_df.drop(columns=["CustomerID"], inplace=True)

# Create a new column in healthcare_df for UserID
healthcare_df["UserID"] = pd.NA  # Initialize with NaN (missing values)

# Assign UserIDs to the first N patients, where N is the number of employees
healthcare_df.loc[:len(employee_df) - 1, "UserID"] = employee_df["UserID"].values

# Ensure UserID is an integer
healthcare_df["UserID"] = healthcare_df["UserID"].astype("Int64")

# Save updated CSVs
employee_df.to_csv("employee_updated.csv", index=False)
ecommerce_df.to_csv("ecommerce_updated.csv", index=False)
healthcare_df.to_csv("healthcare_updated.csv", index=False)

print("UserIDs successfully assigned!")