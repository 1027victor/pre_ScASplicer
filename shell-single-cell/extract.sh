#!/bin/bash

# Change to the directory where the files are stored
cd ./clean

# Create or empty the existing file list before starting
# > fastq.txt

# Loop through all .gz files in the directory
# pair-end
for file in *.gz
do
  # 提取下划线前的部分并输出到 fastq.txt
  echo "${file%%_*}"
done | sort | uniq > ../fastq.txt


# single-end
for file in *.gz
do
  # 提取下划线前的部分并输出到 fastq.txt
  echo "${file%%.*}"
done | sort | uniq > ../fastq.txt

