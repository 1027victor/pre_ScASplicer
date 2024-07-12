# 提取SJ.out.tab文件特定的列数且合并坐标列
#!/bin/bash
mkdir -p SJ
# 遍历当前目录下所有以.SJ.out.tab结尾的文件
for file in *.SJ.out.tab
do
    # 使用basename命令提取文件名（不带扩展名）
    filename=$(basename "$file" .SJ.out.tab)

    # 首先，使用awk命令处理文件，添加标题并提取所需列
    # 然后，对这个输出应用第二次awk处理，合并染色体位置信息并保留最后一列
    # 直接将最终结果输出到以"_merge.txt"结尾的文件中
    awk -v OFS='\t' -v colname="$filename" 'BEGIN {print "chr", "start", "end", colname} {print $1, $2, $3, $7}' "$file" | awk -v OFS='\t' 'NR==1{print "coord.intron", $4; next} {print $1":"$2":"$3, $4}' > "./SJ/${filename}.txt"
done

python marge_SJ.py --directory ./SJ  --output-file result.csv
