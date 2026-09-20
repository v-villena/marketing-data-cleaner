import pandas as pd

# Load raw advertising platform exports
google_data = pd.read_csv("data/google_ads.csv")
meta_data = pd.read_csv("data/meta_ads.csv")

# Inspect the datasets
print("GOOGLE ADS DATA")
print(google_data.head())

print("\nMETA ADS DATA")
print(meta_data.head())

# Compare column names
print("\nGOOGLE ADS COLUMNS")
print(google_data.columns.tolist())

print("\nMETA ADS COLUMNS")
print(meta_data.columns.tolist())
