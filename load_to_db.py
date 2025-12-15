import pandas as pd
import sqlite3

# Replace with your exact CSV filename if different
df = pd.read_csv('hk_property_data.csv')

# Clean: drop rows missing key columns
df = df.dropna(subset=['price', 'saleable_area(ft^2)', 'date', 'district'])

# Rename the weird area column to something clean (optional but makes life easier)
df = df.rename(columns={'saleable_area(ft^2)': 'saleable_area'})

# If 'unit_rate' is already price per sqft, we can use it directly
# Otherwise calculate it (in case unit_rate is missing or weird)
if 'unit_rate' not in df.columns or df['unit_rate'].isnull().all():
    df['price_per_sqft'] = df['price'] / df['saleable_area']
else:
    df['price_per_sqft'] = df['unit_rate']  # use the existing one

# Convert date to proper datetime
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Save to SQLite
conn = sqlite3.connect('hk_property.db')
df.to_sql('transactions', conn, if_exists='replace', index=False)

print(f"Database created! Rows loaded: {len(df)}")
conn.close()