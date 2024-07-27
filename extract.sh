#!/bin/bash

# Change to the directory where the files are stored
cd /path/to/your/files

# Create or empty the existing file list before starting
> file_names.txt

# Loop through all .gz files in the directory
for file in *.gz
do
  # Extract the part before the underscore and append it to the file
  echo "${file%%_*}" >> file_names.txt
done
