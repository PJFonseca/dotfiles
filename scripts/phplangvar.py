import os
import re
import sys

def extract_and_generate_ddl(directory):
    # Regular expression to match text that starts with '._' and ends with '.'
    # and only contains letters and underscores, allowing optional spaces around the dots
    pattern = r"\s*\.\s*_\s*([A-Za-z0-9_]+)\s*\.\s*"

    # Set to store unique variable names
    unique_matches = set()

    # Traverse through all files in the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Only process .php files
            if file.endswith(".php"):
                file_path = os.path.join(root, file)

                # Read the file content
                with open(file_path, "r", encoding="utf-8-sig", errors="ignore") as f:
                    content = f.read()

                    # Find all occurrences that match the pattern
                    matches = re.findall(pattern, content)

                    # Add each match to the set (duplicates will be automatically handled)
                    unique_matches.update(matches)

    # Open output file to write DDL statements (append if the file exists)
    with open("output.sql", "a") as output_file:
        # For each unique match, generate an INSERT IGNORE statement
        for match in unique_matches:
            ddl = f"INSERT IGNORE INTO adm_language_vars (variable, pt, en, fr) VALUES('_{match}', NULL, NULL, NULL);\n"
            output_file.write(ddl)

# Get directory path from command-line arguments, or use './' by default
directory_to_scan = sys.argv[1] if len(sys.argv) > 1 else './'

extract_and_generate_ddl(directory_to_scan)
