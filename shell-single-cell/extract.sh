#!/bin/bash

# Change to the directory where the files are stored
cd ./clean

# Create or empty the existing file list before starting
# > fastq.txt

# Loop through all .gz files in the directory
for file in *.gz
do
  # Extract the part before the underscore and append it to the file
  echo "${file%%_*}" >> ../fastq.txt
done
