#!/bin/bash
  
# Specify the genomic file and BED file for bedtools
genome_file="/www/hpw/data/rstudio/PRJEB30442_human/all_bam/chrNameLength.txt"
bed_file="/www/hpw/data/rstudio/PRJEB30442_human/all_bam/unsortbam/rmats/ri.coordinates.bed"

# Check if bedtools is already installed
if ! command -v bedtools &> /dev/null
then
    echo "bedtools could not be found"
    exit
fi

# Iterate through all the eligible .bam files
for bam_file in *.Aligned.sortedByCoord.out.bam
do
    # Generate the name of the output file
    output_file="./bed/${bam_file%.Aligned.sortedByCoord.out.bam}.txt"

    echo "Processing $bam_file -> $output_file"

    # Execute the bedtools coverage command
    bedtools coverage \
        -g "$genome_file" \
        -split \
        -sorted \
        -a "$bed_file" \
        -b "$bam_file" > "$output_file" \
        -d
done

echo "Processing complete."
