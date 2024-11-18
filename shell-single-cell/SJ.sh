# Extract a specific number of columns from the SJ.out.tab file and merge the coordinate columns
#!/bin/bash
mkdir -p SJ
# Iterate through all files in the current directory that end with ".SJ.out.tab"
for file in *.SJ.out.tab
do
    #  Use the "basename" command to extract the file name (without the extension)
    filename=$(basename "$file" .SJ.out.tab)

    # First, use the awk command to process the file, add a header and extract the required columns
    # Then, apply a second awk processing to this output to merge the chromosome position information and retain the last column
    # Directly output the final result to a file ending with "_merge.txt
    awk -v OFS='\t' -v colname="$filename" 'BEGIN {print "chr", "start", "end", colname} {print $1, $2, $3, $7}' "$file" | awk -v OFS='\t' 'NR==1{print "coord.intron", $4; next} {print $1":"$2":"$3, $4}' > "./SJ/${filename}.txt"
done

python merge_SJ.py --directory ./SJ  --output-file result.csv
