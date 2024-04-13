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

# Unzip all .zip files into CSV directory
for zip_file in *.zip; do
    unzip "$zip_file" -d CSV/
done

# Merge CSV files excluding headers except the first file
cat CSV/*.csv | awk -F',' 'NR == 1 || (FNR > 1 && $1 != "Respondent ID" && $10 != "Response")' > merged.csv

echo "Unzipping, merging, and filtering completed."
