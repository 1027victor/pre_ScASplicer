#!/bin/bash
  
# 指定bedtools的基因组文件和BED文件
genome_file="/www/hpw/data/rstudio/PRJEB30442_human/all_bam/chrNameLength.txt"
bed_file="/www/hpw/data/rstudio/PRJEB30442_human/all_bam/unsortbam/rmats/ri.coordinates.bed"

# 检查bedtools是否已安装
if ! command -v bedtools &> /dev/null
then
    echo "bedtools could not be found"
    exit
fi

# 循环处理所有符合条件的.bam文件
for bam_file in *.Aligned.sortedByCoord.out.bam
do
    # 生成输出文件的名称
    output_file="./bed/${bam_file%.Aligned.sortedByCoord.out.bam}.txt"

    echo "Processing $bam_file -> $output_file"

    # 执行bedtools coverage命令
    bedtools coverage \
        -g "$genome_file" \
        -split \
        -sorted \
        -a "$bed_file" \
        -b "$bam_file" > "$output_file" \
        -d
done

echo "Processing complete."
