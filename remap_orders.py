import pandas as pd
import numpy as np
import os

# Ensure the output file is removed before writing a new one
if os.path.exists("orders_mapped.csv"):
    os.remove("orders_mapped.csv")

# Load Orders
orders_df = pd.read_csv("Trash/ecommerce.csv", encoding="latin1")

# Load CustomerID pool from employees and patients
employees_df = pd.read_csv("employee_with_customerid.csv")
patients_df = pd.read_csv("patients_with_customerid.csv")
customer_pool = pd.concat([employees_df[["CustomerID"]], patients_df[["CustomerID"]]], ignore_index=True)

# Get unique invoices
unique_invoices = orders_df["InvoiceNo"].dropna().unique()

# Randomly assign one CustomerID per invoice
np.random.seed(42)
invoice_to_customer = pd.Series(
    np.random.choice(customer_pool["CustomerID"], size=len(unique_invoices), replace=True),
    index=unique_invoices
)

# Map back to the original orders
orders_df["CustomerID"] = orders_df["InvoiceNo"].map(invoice_to_customer)

# Save final remapped CSV
orders_df.to_csv("orders_mapped.csv", index=False)

print("Orders have been re-mapped successfully!")
