#!/bin/bash

# Create CSV directory if it doesn't exist
if [ ! -d "CSV" ]; then
    mkdir CSV
    echo "CSV directory created."
fi

# Delete PageOrder.csv if it exists inside CSV directory
if [ -f "CSV/PageOrder.csv" ]; then
    rm CSV/PageOrder.csv
    echo "CSV/PageOrder.csv deleted."
fi

# Temporary directory to unzip files
temp_dir="temp_unzip"

# Unzip all .zip files into temporary directory
for zip_file in *.zip; do
    unzip -o "$zip_file" -d "$temp_dir/"
done

# Move all .csv files from temporary directory to main CSV directory
find "$temp_dir" -name "*.csv" -exec mv {} CSV/ \;

# Remove temporary directories
rm -r "$temp_dir"

# Merge CSV files excluding headers except the first file
cat CSV/*.csv | awk -F',' 'NR == 1 || (FNR > 1 && $1 != "Respondent ID" && $10 != "Response")' > merged.csv

echo "Unzipping, merging, and filtering completed."
