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
Options:
  -p, --path_to_data TEXT         Path to gene data files.
  -q, --quantitative_indicator TEXT Quantitative indicator to use.
  --species TEXT                  species
  -g, --gtf_file_path TEXT        Path to GTF file.

```
+ Splice junction counts matrix  
merge-SJ --help
```
Options:
  --directory PATH     Input file path  [required]
  --output-file PATH   Output file  [required]
  --nums INTEGER       numers of core

```
### merge-bed --help
```
Options:
  --input-dir PATH         Path to the input directory.  [required]
  --intermediate-dir PATH  Path to the directory for intermediate intron
                           matrices.  [required]
  --output-file PATH       Output file for the concatenated matrix.
                           [required]

```
## Run
```
merge-counts -p xxx -q xxx --species xxx -g xxx
merge-SJ --directory xxx --output-file xxx  --nums xxx
merge-bed --input-dir xxx --intermediate-dir xxx --output-file xxx
```
