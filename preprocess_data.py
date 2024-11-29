import pandas as pd
import numpy as np

# File paths
INPUT_FILE = "healthcare-dataset-stroke-data.csv"
OUTPUT_FILE = "cleaned_stroke_data.csv"

def load_data(file_path):
    """
    Load the dataset from the CSV file.
    """
    try:
        data = pd.read_csv(file_path)
        print(f"Dataset loaded successfully with {data.shape[0]} rows and {data.shape[1]} columns.")
        return data
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None

def handle_missing_values(data):
    """
    Handle missing values in the dataset.
    - Fill missing BMI values with the median.
    """
    if 'bmi' in data.columns:
        missing_bmi = data['bmi'].isnull().sum()
        if missing_bmi > 0:
            median_bmi = data['bmi'].median()
            data['bmi'].fillna(median_bmi, inplace=True)
            print(f"Filled {missing_bmi} missing BMI values with median: {median_bmi:.2f}")
        else:
            print("No missing BMI values found.")
    return data

def clean_data(data):
    """
    Clean the dataset by standardizing column names and values.
    - Convert categorical text data to lowercase.
    """
    data['gender'] = data['gender'].str.lower()
    data['ever_married'] = data['ever_married'].str.lower()
    data['work_type'] = data['work_type'].str.lower()
    data['Residence_type'] = data['Residence_type'].str.lower()
    data['smoking_status'] = data['smoking_status'].str.lower()
    print("Data cleaning completed.")
    return data

def save_data(data, file_path):
    """
    Save the cleaned dataset to a CSV file.
    """
    try:
        data.to_csv(file_path, index=False)
        print(f"Cleaned data saved to '{file_path}'.")
    except Exception as e:
        print(f"Error saving cleaned data: {e}")

def display_data_summary(data):
    """
    Display basic statistics and a summary of the dataset.
    """
    print("\nBasic Statistics:")
    print(data.describe())
    
    print("\nData Info:")
    print(data.info())

    print("\nMissing Values Summary:")
    print(data.isnull().sum())

def main():
    # Step 1: Load the dataset
    data = load_data(INPUT_FILE)
    if data is None:
        return

    # Step 2: Handle missing values
    data = handle_missing_values(data)

    # Step 3: Clean the data
    data = clean_data(data)

    # Step 4: Display data summary
    display_data_summary(data)

    # Step 5: Save the cleaned dataset
    save_data(data, OUTPUT_FILE)

if __name__ == "__main__":
    main()
