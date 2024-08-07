import pandas as pd
import os
import ray
import click
@ray.remote
# 整合gene_counts文件
def merge_data_files(path, quantitative_indicators):
    data_frames = []
    for file in os.listdir(path):
        if file.endswith('.genes.results'):
            data = pd.read_table(os.path.join(path, file), index_col=0)
            selected_data = data[[quantitative_indicators]]
            data_frames.append(selected_data)
    merged_data = pd.concat(data_frames, axis=1)
    merged_data.columns = [file.split('.')[0] for file in os.listdir(path) if file.endswith('.genes.results')]
    merged_data.index.name = 'gene_id'
    output_filename = f'{quantitative_indicators}.txt'
    merged_data.to_csv(output_filename, sep='\t')
    return output_filename

@ray.remote
# 从gtf文件中提取基因元信息
def extract_gene_metadata(gtf_path, species='mouse'):
    gene_metadata = {'gene_id': [], 'gene_short_name': []}
    with open(gtf_path, 'r') as file:
        for line in file:
            if line.startswith('#') or line.strip() == '':
                continue
            fields = line.strip().split('\t')
            if fields[2] == 'gene':
                attributes = {attr.strip().split(' ')[0]: attr.strip().split(' ')[1].strip('"') for attr in fields[8].split(';') if attr.strip()}
                gene_metadata['gene_id'].append(attributes.get('gene_id'))
                gene_metadata['gene_short_name'].append(attributes.get('gene_name'))
    metadata_df = pd.DataFrame(gene_metadata)
    output_filename = f'{species}_Gene_metadata.txt'
    metadata_df.to_csv(output_filename, sep='\t', index=False)
    return output_filename

@ray.remote
def process_and_filter_data(merged_data_file, metadata_file):
    data = pd.read_table(merged_data_file, sep='\t', index_col=0)
    metadata = pd.read_csv(metadata_file, sep='\t', index_col='gene_id')
    metadata = metadata.sort_index(axis=0)
    full_data = pd.concat([metadata, data], axis=1)
    full_data['mean_expression'] = full_data.iloc[:, 1:].mean(axis=1)
    max_expression = full_data.groupby('gene_short_name')['mean_expression'].transform(max)
    filtered_data = full_data[full_data['mean_expression'] == max_expression]
    filtered_data = filtered_data.drop_duplicates(subset=['gene_short_name'], keep='first')
    filtered_data.drop(columns=['mean_expression']).to_csv("final_filtered_counts.txt", sep='\t', index=False)
    return "final_filtered_counts.txt"

# @click.command()
# @click.option('--path_to_data','-p',default="martix/gene_level", help='Path to gene data files.')
# @click.option('--quantitative_indicator','-q',default="expected_count", help='Quantitative indicator to use.')
# @click.option('--species', default="mouse", help='species')
# @click.option('--gtf_file_path', '-g',default="/www/hpw/mouse_gencode/gencode.vM33.chr_patch_hapl_scaff.annotation.gtf", help='Path to GTF file.')
# def run_pipeline(path_to_data, quantitative_indicator, gtf_file_path,species):
#     ray.init()
#     merged_data_future = merge_data_files.remote(path_to_data, quantitative_indicator)
#     metadata_future = extract_gene_metadata.remote(gtf_file_path,species=species)
#     final_data_future = process_and_filter_data.remote(merged_data_future, metadata_future)
#     final_result = ray.get(final_data_future)
#     click.echo(f"Processing complete. Output saved to: {final_result}")


@click.command()
@click.option('--path_to_data', '-p', default="martix/gene_level", help='Path to gene data files.')
@click.option('--quantitative_indicator', '-q', default="expected_count", help='Quantitative indicator to use.')
@click.option('--species', default="mouse", help='species')
@click.option('--gtf_file_path', '-g', default="/www/hpw/mouse_gencode/gencode.vM33.chr_patch_hapl_scaff.annotation.gtf", help='Path to GTF file.')
@click.option('--metadata', '-m', default=None, help='gene metadata.')
def run_pipeline(path_to_data, quantitative_indicator, gtf_file_path, species, metadata_path):
    ray.init()
    merged_data_future = merge_data_files.remote(path_to_data, quantitative_indicator)
    
    if metadata:
        # Use pre-extracted metadata if provided
        metadata_future = ray.put(metadata)
    else:
        # Extract metadata if not provided
        metadata_future = extract_gene_metadata.remote(gtf_file_path, species=species)
    
    final_data_future = process_and_filter_data.remote(merged_data_future, metadata_future)
    final_result = ray.get(final_data_future)
    click.echo(f"Processing complete. Output saved to: {final_result}")

if __name__ == '__main__':
    run_pipeline()



