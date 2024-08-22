#!/bin/bash

# Set the width and height
WIDTH=1024
HEIGHT=1024

# Loop over all SVG files in the current directory
for svgfile in *.svg; do
    # Extract the filename without the extension
    filename=$(basename "$svgfile" .svg)
    # Convert to PNG
    inkscape -w "$WIDTH" -h "$HEIGHT" "$svgfile" -o "${filename}.png"
done
