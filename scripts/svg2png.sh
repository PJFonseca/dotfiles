#!/bin/bash

# Set the width and height
WIDTH=1024
HEIGHT=1024

# Check if the user specified an output format (png or jpg)
OUTPUT_FORMAT=${1:-png}  # Default to png if no format is provided

# Loop over all SVG files in the current directory
for svgfile in *.svg; do
    # Extract the filename without the extension
    filename=$(basename "$svgfile" .svg)

    # Convert to the desired format
    if [ "$OUTPUT_FORMAT" == "jpg" ]; then
        # Convert to JPG
        inkscape -w "$WIDTH" -h "$HEIGHT" "$svgfile" -o "${filename}.png"
        convert "${filename}.png" -background white -flatten "${filename}.jpg"
        rm "${filename}.png"  # Remove the intermediate PNG file
    else
        # Convert to PNG
        inkscape -w "$WIDTH" -h "$HEIGHT" "$svgfile" -o "${filename}.png"
    fi
done
