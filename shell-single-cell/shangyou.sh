#single-end sequence
#Quality control
mkdir -p fastqc
#fastqc
fastqc -t 24 -o ./fastqc/ -q ./*.gz
mkdir -p ./STAR_index
#Establishing an index
STAR --runThreadN 24 --runMode genomeGenerate \
--genomeDir ./STAR_index \
--genomeFastaFiles /www/hpw/human_gencode/GRCh38.p14.genome.fa \
--sjdbGTFfile /www/hpw/human_gencode/gencode.v44.basic.annotation.gtf \
--sjdbOverhang 42
#24-1(reads-1)

mkdir -p ./rsem_index
#RSEM index                                 
rsem-prepare-reference \
--gtf  /www/hpw/human_gencode/gencode.v44.basic.annotation.gtf  -p 24 /www/hpw/human_gencode/GRCh38.p14.genome.fa \
./rsem_index/human_v44 


mkdir -p ./clean
# The number of base pairs that can be tolerated for overlapping adapter sequences at the 5' and 3' ends is 3
#filter
cat fastq.txt | while read id
do
    trim_galore --quality 20 --phred33 \
    --length 20 -j 16 \
    --stringency 3 \
    -o ./clean \
    ${id}.fastq.gz
done 

mkdir -p ./SJ
#aligment
# STAR in 1st pass mode
cat fastq.txt | while read id
do
    STAR --runThreadN 10 \
     --genomeDir ./STAR_index \
     --readFilesCommand zcat \
     --readFilesIn ./clean/${id}_trimmed.fq.gz \
     --outFileNamePrefix ./SJ/${id}. \
     --outSAMtype None
done

mkdir -p ./bam
#STAR in 2nd pass mode
cat fastq.txt | while read id
do
   STAR --runThreadN 12 \
     --genomeDir ./STAR_index \
     --readFilesCommand zcat \
     --readFilesIn ./clean/${id}_trimmed.fq.gz \
     --outFileNamePrefix ./bam/${id}. \
     --sjdbFileChrStartEnd ./SJ/*SJ.out.tab \
     --outSAMtype BAM SortedByCoordinate \
     --outSAMattributes NH HI AS nM XS \
     --quantMode TranscriptomeSAM
done

mkdir -p ./martix
#counts
cat fastq.txt | while read id
do
    rsem-calculate-expression --bam \
                          -p 12 \
                          ./bam/${id}.Aligned.toTranscriptome.out.bam \
                          ./rsem_index/human_v44 \
                          ./martix/${id}
done
