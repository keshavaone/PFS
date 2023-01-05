# Personal Finance Analysis
A Python script that analyzes personal finance data and generates various reports and visualizations.

## Features
Import data from CSV or Excel files
Generate reports on income, expenses, and net worth
Visualize trends in income, expenses, and net worth over time
Analyze spending patterns by category
Category vs Category Subtype Analysis can be downloaded including data for PowerBI created from the imported Excel file
## Requirements
Python 3.6 or higher
pandas
matplotlib (optional for visualizations)
## Setup
Install the required packages:
```
pip install pandas matplotlib
```
Prepare a CSV or Excel file with your personal finance data. The file should have the following columns:

Date: the date of the transaction
Description: a description of the transaction
Amount: the amount of the transaction
Category: the category of the transaction (optional)
Set the path to the data file in the script.

## Run the script:
```
python pfa.py
```
## Output
The script will generate a report and optionally create visualizations, depending on the options chosen in the script. The Category vs Category Subtype Analysis can be downloaded, including data for PowerBI created from the imported Excel file.

## Notes
The script assumes that all amounts are in the same currency.
The script may require modification to work with your specific data format.
The visualizations are created using matplotlib and saved as PNG files.
