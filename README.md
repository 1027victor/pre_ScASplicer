# pre_MARVEL(Process upstream data single-cell)
`pre_MARVEL` is a Python package that simplifies and streamlines the generation of  MARVEL input files 
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
## Help
### merge-counts --help
```
Options:
  -p, --path_to_data TEXT         Path to gene data files.
  -q, --quantitative_indicator TEXT Quantitative indicator to use.
  --species TEXT                  species
  -g, --gtf_file_path TEXT        Path to GTF file.

```
### merge-SJ --help
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
