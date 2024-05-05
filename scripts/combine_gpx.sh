#!/bin/bash

combine_gpx() {
    # Check if directory exists
    if [ -d "$1" ]; then
        # Create a new GPX file
        echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" > combined.gpx
        echo "<gpx version=\"1.1\" creator=\"YourAppName\">" >> combined.gpx
        echo "<trk><trkseg>" >> combined.gpx

        # Concatenate all GPX files into one
        for file in "$1"/*.gpx; do
            cat "$file" | grep -v '<?xml\|<gpx\|<trk\|<trkseg\|</trkseg\|</trk\|</gpx\|<metadata\|</wpt\|<rte\|</rtept' >> combined.gpx
        done

        # Close the GPX file
        echo "</trkseg></trk></gpx>" >> combined.gpx

        echo "Combined GPX files into combined.gpx"
    else
        echo "Directory not found."
    fi
}

# Check if argument provided
if [ -z "$1" ]; then
    echo "Usage: $0 directory"
    exit 1
fi

# Call the function with the provided directory
combine_gpx "$1"
