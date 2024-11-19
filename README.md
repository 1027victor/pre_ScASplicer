# pre_MARVEL
`pre_MARVEL` is a Python package that simplifies and streamlines the generation of  MARVEL input files,it mainly processes scRNA-seq datasets generated from the plate-based platforms, e.g. Smart-seq2 or microfluidic-based platforms, e.g. Fluidigm C1 instrument.
# Feature
+ simplifies and streamlines the generation of  [`MARVEL`](https://wenweixiong.github.io/MARVEL_Plate.html) `input files`
# Quick Start
## Installation
###  First install depenced packages then install pre_MARVEL
```
conda create -n ray -c conda-forge python==3.11 pandas click -y
conda activate ray
pip install -U "ray"
pip install  git+https://github.com/1027victor/pre_ScSpliceshiner.git
```

## Tips
+ if above final step failed
```
git clone https://github.com/1027victor/pre_ScSpliceshiner.git
cd pre_MARVEL
pip install .
```
## Use pre_MARVEL
Below are examples of typical pre_MARVEL usage. Using the “--help” option with any bedtools will report a list of all command line options.
+ ### Gene expression matrix
  
#### merge-counts --help
```
Usage: merge-counts [OPTIONS]

Options:
  -p, --path_to_data TEXT         Path to gene data files.
  -q, --quantitative_indicator TEXT
                                  Quantitative indicator to use.
  --species TEXT                  species
  -g, --gtf_file_path TEXT        Path to GTF file.
  -m, --metadata TEXT             gene metadata.
  --help                          Show this message and exit.
```
### Run
```
merge-counts -p data/gene_level --species human -g data/gtf/gencode.v46.annotation.gtf
```

+ ### Splice junction counts matrix
  
#### merge-SJ --help
```
Usage: merge-SJ [OPTIONS]

Options:
  --directory PATH    Input file path  [required]
  --output-file PATH  Output file  [required]
  --nums INTEGER      numers of core
  --help              Show this message and exit.

```
### Run
```
# Extract a specific number of columns from the SJ.out.tab file and merge the coordinate columns
#!/bin/bash
cd data/SJ
mkdir -p output_SJ
# Iterate through all files in the current directory that end with ".SJ.out.tab"
for file in *.SJ.out.tab
do
    #  Use the "basename" command to extract the file name (without the extension)
    filename=$(basename "$file" .SJ.out.tab)

    # First, use the awk command to process the file, add a header and extract the required columns
    # Then, apply a second awk processing to this output to merge the chromosome position information and retain the last column
    # Directly output the final result to a file ending with "_merge.txt
    awk -v OFS='\t' -v colname="$filename" 'BEGIN {print "chr", "start", "end", colname} {print $1, $2, $3, $7}' "$file" | awk -v OFS='\t' 'NR==1{print "coord.intron", $4; next} {print $1":"$2":"$3, $4}' > "./output_SJ/${filename}.txt"
done
merge-SJ --directory ./output_SJ --output-file ./merge_SJ.csv  --nums 32

```
+ ### Intron count matrix

#### PrepareBedfile --help

```
Usage: PrepareBedfile [OPTIONS]

  Processes an rMATS output file for Retained Intron events to extract intron
  coordinates and saves it as a BED file.

Options:
  --input PATH   Input rMATS RI file path.  [required]
  --output PATH  Output BED file path.  [required]
  --help         Show this message and exit.

```
  
#### merge-bed --help
```
Usage: merge-bed [OPTIONS]

  Use Ray to process all counts files in the specified directory in parallel,
  output the results to the specified directory, and then combine the
  processed counts files into a single file.

Options:
  --bed-file PATH         Path to the BED file.  [required]
  --counts-dir DIRECTORY  Directory path containing counts files.  [required]
  --output-dir PATH       Directory path to save processed counts files.
                          [required]
  --combined-output PATH  File path to save the combined counts file.
                          [required]
  --cpus INTEGER          Number of CPUs to use.
  --help                  Show this message and exit.

```
### Run
```
 PrepareBedfile --input data/rmats/fromGTF.RI.txt --output data/rmats/RI_introns.bed
  #!/bin/bash  
  # Specify the genomic file and BED file for bedtools
  genome_file="data/bam/chrNameLength.txt"
  bed_file="data/rmats/RI_introns.bed"
  
  # Check if bedtools is already installed
  if ! command -v bedtools &> /dev/null
  then
      echo "bedtools could not be found"
      exit
  fi
  
  # Iterate through all the eligible .bam files
  cd data/bam
  mkdir -p bed
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
cd bed
merge_bed --bed-file data/rmats/RI_introns.bed --counts-dir ./ --output-dir ./processed_counts/ --combined-output ./Counts_by_Region.txt --cpus 32

```

+ ### Splicing event metadata

#### PreprocessrMATS --help

```
Options:
Usage: PreprocessrMATS [OPTIONS]

  Process rMATS output files to extract splicing event coordinates and
  annotations.

Options:
  --event-types [SE|MXE|RI|A5SS|A3SS]
                                  Splicing event types to process; multiple
                                  can be specified.
  --files PATH                    Input file paths corresponding to event
                                  types; multiple can be specified, matching
                                  the event types one-to-one.
  --gtf PATH                      Path to the GTF file used in rMATS.
                                  [required]
  --output-dir PATH               Directory path to save the output results.
                                  [required]
  --help                          Show this message and exit.
```
### Run
#### two cell types
```
cd data/bam
rmats \
    --b1 sample_1.txt \
    --b2 sample_2.txt \
    --gtf data/gtf/gencode.v46.annotation.gtf \
    --od rMATS/ \
    --tmp rMATS/ \
    -t paired \
    --readLength 125 \
    --variable-read-length \
    --nthread 8 \
    --statoff
cd rMATS
PreprocessrMATS --event-types SE --event-types MXE --event-types RI --event-types A5SS --event-types A3SS   --files fromGTF.SE.txt --files fromGTF.MXE.txt --files fromGTF.RI.txt --files fromGTF.A5SS.txt --files fromGTF.A3SS.txt --gtf data/gtf/gencode.v46.annotation.gtf --output-dir ./processed_events
```
#### Various cell types
```
GTF="data/gtf/gencode.v46.annotation.gtf"  # Path of GTF file
OUTPUT_DIR="rMATS_results"        # Overall output folder
THREADS=32                         # Number of threads
READ_LENGTH=125                   # the length of reads

# Specify the directory where the sample template file will be stored
SAMPLE_DIR="data/Various_cell_type"

# Check if the directory for the sample text file exists
if [ ! -d "$SAMPLE_DIR" ]; then
    echo "Error: Directory $SAMPLE_DIR does not exist."
    exit 1
fi

# Get a list of sample data files
sample_files=($(ls $SAMPLE_DIR/*.txt 2>/dev/null))

# Check if there is a sample template file
if [ ${#sample_files[@]} -eq 0 ]; then
    echo "Error: No .txt files found in directory $SAMPLE_DIR."
    exit 1
fi

# Create the output directory
mkdir -p $OUTPUT_DIR

# pairwise cyclic comparison
for ((i=0; i<${#sample_files[@]}-1; i++)); do
    for ((j=i+1; j<${#sample_files[@]}; j++)); do
        # Obtain sample files
        SAMPLE1=${sample_files[i]}
        SAMPLE2=${sample_files[j]}
        
        # Extract the file name (remove the path and extension for naming the output directory)
        NAME1=$(basename "$SAMPLE1" .txt)
        NAME2=$(basename "$SAMPLE2" .txt)
        
        # Create an output directory for a specific comparison
        COMP_OUTPUT_DIR="$OUTPUT_DIR/${NAME1}_vs_${NAME2}"
        mkdir -p $COMP_OUTPUT_DIR

        #  rMATS
        echo "Running rMATS for $NAME1 vs $NAME2..."
        rmats \
            --b1 $SAMPLE1 \
            --b2 $SAMPLE2 \
            --gtf $GTF \
            --od $COMP_OUTPUT_DIR \
            --tmp $COMP_OUTPUT_DIR/tmp \
            -t paired \
            --readLength $READ_LENGTH \
            --variable-read-length \
            --nthread $THREADS \
            --statoff

        # Check if rMATS was successful
        if [ $? -ne 0 ]; then
            echo "Error: rMATS failed for $NAME1 vs $NAME2. Check input files or parameters."
            exit 1
        fi

        echo "Comparison ${NAME1} vs ${NAME2} completed: Results saved in $COMP_OUTPUT_DIR"
    done
done

echo "All comparisons completed successfully."


# Set input and output directories
RESULTS_DIR="rMATS_results"  # The directory where the rMATS results are stored
MERGED_DIR="merged_results" # The directory where the merged files are stored

# Create the output directory
mkdir -p $MERGED_DIR

# Define the file types that need to be merged
FILES_TO_MERGE=("fromGTF.A3SS.txt" "fromGTF.A5SS.txt" "fromGTF.MXE.txt" "fromGTF.SE.txt" "fromGTF.RI.txt")

# Process each file type in a loop
for file in "${FILES_TO_MERGE[@]}"; do
    OUTPUT_FILE="$MERGED_DIR/$file" # The final merged file path

    # Create a new file and write the header
    echo "Adding header for $file"
    head -n 1 $(find $RESULTS_DIR -type f -name "$file" | head -n 1) > $OUTPUT_FILE

    # Combine all similar files (skip header rows)
    for result_file in $(find $RESULTS_DIR -type f -name "$file"); do
        tail -n +2 "$result_file" >> $OUTPUT_FILE
    done

    echo "$file merged into $OUTPUT_FILE"
done

echo "All files merged successfully into $MERGED_DIR"
cd $MERGED_DIR
PreprocessrMATS --event-types SE --event-types MXE --event-types RI --event-types A5SS --event-types A3SS   --files fromGTF.SE.txt --files fromGTF.MXE.txt --files fromGTF.RI.txt --files fromGTF.A5SS.txt --files fromGTF.A3SS.txt --gtf data/gtf/gencode.v46.annotation.gtf --output-dir ./processed_events


```
+ ### Gene metadata
#### Run
```
merge-counts -p data/gene_level --species human -g data/gtf/gencode.v46.annotation.gtf
```
When running this command, a gene expression matrix and gene metadata will be generated simultaneously in the current working directory, with file names "final_filtered_counts.txt" and "human_Gene_metadata.txt", respectively.

*** The shell scripting languages mentioned above are all located in the "shell-single-cell" folder. ***


