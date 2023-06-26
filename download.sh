#!/bin/bash

rm -rfv pdf
# Create the pdf directory if it doesn't exist
mkdir -p pdf

# Read each link from the input file
while read -r link; do
    # Extract the filename from the link
    filename=$(basename "$link")
    # Extract the nct_id from the link
    nct_id=$(dirname "$link" | awk -F/ '{print $(NF)}')
    # Extract the prefix and suffix from the filename
    prefix="${filename}"
    
    # Construct the new filename
    new_filename="${nct_id}_${prefix}"

    # Download the file and save it with the new filename in the pdf directory
    wget tries=10 -q -c --wait=5 "$link" -O "pdf/$new_filename" 

    echo "Downloaded: $link, renamed to $new_filename"
    # break

    # Introduce a delay of 1 second before the next download
    sleep 5
done < url.txt
