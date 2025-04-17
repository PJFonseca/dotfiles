#!/usr/bin/env python3

import sys
import re
import os

def split_sql_by_table(input_file, table_name):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        print("⚠️ UTF-8 decoding failed. Retrying with 'latin1' encoding...")
        with open(input_file, 'r', encoding='latin1') as f:
            lines = f.readlines()

    filtered_sql = []
    table_sql = []

    # Extract header (everything before the first -- Table structure for table)
    header_lines = []
    for line in lines:
        if re.match(r"^-- Table structure for table", line):
            break
        header_lines.append(line)

    # Extract database name from header
    db_name = "filtered_output"
    for line in header_lines:
        match = re.search(r"Database:\s+([^\s]+)", line)
        if match:
            db_name = match.group(1)
            break

    filtered_output = f"{db_name}_filtered.sql"
    table_output = f"{table_name}.sql"

    filtered_sql.extend(header_lines)

    in_table_block = False
    current_block = []

    # Regexes to match the structure and inserts
    structure_start = re.compile(rf"^-- Table structure for table [`\"]?{table_name}[`\"]?")
    insert_into = re.compile(rf"^INSERT INTO [`\"]?{table_name}[`\"]?", re.IGNORECASE)
    next_table_structure = re.compile(r"^-- Table structure for table .*")

    for line in lines:
        if structure_start.match(line):
            in_table_block = True
            if current_block:
                filtered_sql.extend(current_block)
                current_block = []
            current_block.append(line)
        elif in_table_block:
            if next_table_structure.match(line) and not structure_start.match(line):
                in_table_block = False
                table_sql.extend(current_block)
                table_sql.append(line)
                current_block = []
            else:
                current_block.append(line)
        elif insert_into.match(line):
            table_sql.append(line)
        else:
            filtered_sql.append(line)

    # Add any remaining structure block
    if in_table_block:
        table_sql.extend(current_block)
    else:
        filtered_sql.extend(current_block)

    # Output to files
    with open(filtered_output, 'w', encoding='utf-8') as f:
        f.writelines(filtered_sql)

    with open(table_output, 'w', encoding='utf-8') as f:
        f.writelines(table_sql)

    print(f"✅ Filtered SQL without '{table_name}' written to: {filtered_output}")
    print(f"✅ SQL for table '{table_name}' written to: {table_output}")

# === USAGE ===
# python split_sql.py backup.sql documentos

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python split_sql.py input.sql table_name")
        sys.exit(1)

    input_file = sys.argv[1]
    table_name = sys.argv[2]

    if not os.path.isfile(input_file):
        print(f"❌ Error: File '{input_file}' not found.")
        sys.exit(1)

    split_sql_by_table(input_file, table_name)
