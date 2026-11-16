import pandas as pd
import os

file_path = "C:/Users/micha/OneDrive/Desktop/magda/VSC/Project_15/data/raw/data_hse/ridfatal.xlsx"

# List all sheets
excel = pd.ExcelFile(file_path)

print(excel.sheet_names)