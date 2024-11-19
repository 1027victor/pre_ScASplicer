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
+ Gene expression matrix
  
merge-counts --help
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
+ Splice junction counts matrix
  
merge-SJ --help
```
Usage: merge-SJ [OPTIONS]

Options:
  --directory PATH    Input file path  [required]
  --output-file PATH  Output file  [required]
  --nums INTEGER      numers of core
  --help              Show this message and exit.

```
+ Intron count matrix

PrepareBedfile --help

```
Usage: PrepareBedfile [OPTIONS]

  Processes an rMATS output file for Retained Intron events to extract intron
  coordinates and saves it as a BED file.

Options:
  --input PATH   Input rMATS RI file path.  [required]
  --output PATH  Output BED file path.  [required]
  --help         Show this message and exit.

```
  
merge-bed --help
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

+ Splicing event metadata

PreprocessrMATS --help

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
+ Gene metadata
## Run
```
merge-counts -p xxx -q xxx --species xxx -g xxx
merge-SJ --directory xxx --output-file xxx  --nums xxx
merge-bed --input-dir xxx --intermediate-dir xxx --output-file xxx
```
