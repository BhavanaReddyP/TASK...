import pandas as pd
import re

# Load the dataset
data = pd.read_csv('transactions.csv')

# Function to clean up the amount column
def clean_amount(amount):
    # Remove non-numeric characters
    cleaned_amount = re.sub(r'[^\d.]+', '', str(amount))
    return float(cleaned_amount)

# Apply the clean_amount function to the amount column
data['amount'] = data['amount'].apply(clean_amount)

# Handling missing values (if any)
data.dropna(inplace=True)

# Standardizing the data (ensuring all amounts are floats)
data['amount'] = data['amount'].astype(float)

# Print the cleaned data
# print("Cleaned Data:")
# print(data)

# Calculate basic statistical metrics
stats = data.groupby('category')['amount'].agg(['mean', 'median', 'std', 'count', 'min', 'max', lambda x: x.quantile(0.25), lambda x: x.quantile(0.75)]).reset_index()
stats.columns = ['category', 'mean', 'median', 'std', 'count', 'min', 'max', '25%', '75%']

# Print the statistics
# print("Statistics by Category:")
# print(stats)

# Function to detect anomalies based on Z-score and IQR
def detect_anomalies(row, stats):
    category_stats = stats.loc[stats['category'] == row['category']].iloc[0]
    mean = category_stats['mean']
    std_dev = category_stats['std']
    lower_bound = category_stats['25%']
    upper_bound = category_stats['75%']
    
    # Calculate Z-score
    z_score = (row['amount'] - mean) / std_dev if std_dev > 0 else 0
    if abs(z_score) > 3:
        return f"Z-score of {z_score:.2f} exceeds threshold"
    
    # Check IQR bounds
    if row['amount'] < lower_bound or row['amount'] > upper_bound:
        return f"Amount {row['amount']} is outside IQR bounds ({lower_bound}, {upper_bound})"
    
    return None

# Apply the anomaly detection function
data['reason_for_anomaly'] = data.apply(detect_anomalies, axis=1, stats=stats)

# Print the data with anomalies detected
print("Data with Anomalies Detected:")
print(data)

# Filter out the anomalies
anomalies = data[data['reason_for_anomaly'].notnull()]

# Generate anomaly report
anomaly_report = anomalies[['transaction_id', 'date', 'category', 'amount', 'reason_for_anomaly']]
print("Anomaly Report:")
print(anomaly_report)

# Save the anomaly report to a CSV file
anomaly_report.to_csv('anomaly_report.csv', index=False)
