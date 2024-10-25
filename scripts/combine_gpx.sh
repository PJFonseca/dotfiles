#!/bin/bash

# Check if source directory and output directory are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <source_directory> <output_directory>"
    exit 1
fi

source_directory="$1"
output_directory="$2"

# Check if the source directory exists
if [ ! -d "$source_directory" ]; then
    echo "Error: Source directory '$source_directory' not found."
    exit 1
fi

# Check if the output directory exists, if not create it
if [ ! -d "$output_directory" ]; then
    echo "Creating output directory: $output_directory"
    mkdir -p "$output_directory"
fi

# Set the output file name
output_file="$output_directory/combined.gpx"

# Remove the existing output file if it exists
if [ -f "$output_file" ]; then
    echo "Removing existing $output_file"
    rm "$output_file"
fi

# Start the combined GPX file with its header and opening trkseg tag
{
  echo '<?xml version="1.0" encoding="UTF-8"?>'
  echo '<gpx version="1.1" creator="Combined GPX File" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">'
  echo '  <metadata>'
  echo '    <name>Combined GPX File</name>'
  echo '    <time>'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'</time>'
  echo '  </metadata>'
  echo '  <trk>'
  echo '    <trkseg>'
} >> "$output_file"

# Loop through each GPX file in the source directory
for file in "$source_directory"/*.gpx; do
    # Skip the output file itself
    if [ "$file" != "$output_file" ]; then
        echo "Combining $file"
        # Extract <trkpt> elements and append to the output file
        sed -n '/<trkpt/,/<\/trkpt>/p' "$file" >> "$output_file"
    fi
done

# Finish the combined GPX file with closing trkseg and trk tags
{
  echo '    </trkseg>'
  echo '  </trk>'
  echo '</gpx>'
} >> "$output_file"

echo "Combination completed. Output saved to $output_file"
