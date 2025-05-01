import pandas as pd

# Load datasets
employees_df = pd.read_csv("Trash/employee.csv")
patients_df = pd.read_csv("Trash/healthcare.csv")

# Generate sequential unique CustomerIDs
start_id = 100001
employees_df["CustomerID"] = range(start_id, start_id + len(employees_df))
patients_df["CustomerID"] = range(start_id + len(employees_df), start_id + len(employees_df) + len(patients_df))

# Save new files
employees_df.to_csv("employee_with_customerid.csv", index=False)
patients_df.to_csv("patients_with_customerid.csv", index=False)

print("CustomerIDs successfully assigned!")
