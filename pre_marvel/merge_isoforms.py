
import pandas as pd
import os
import ray
import click
@ray.remote
# Merge the gene_counts file
def merge_data_files(path, quantitative_indicators):
    data_frames = []
    for file in os.listdir(path):
        if file.endswith('.genes.results'):
            data = pd.read_table(os.path.join(path, file), index_col=0)
            selected_data = data[[quantitative_indicators]]
            data_frames.append(selected_data)
    merged_data = pd.concat(data_frames, axis=1)
    merged_data.columns = [file.split('.')[0] for file in os.listdir(path) if file.endswith('.isofroms.results')]
    merged_data.index.name = 'isoform_id'
    output_filename = f'{quantitative_indicators}.txt'
    merged_data.to_csv(output_filename, sep='\t')
    return output_filename
  
@click.command()
@click.option('--path_to_data', '-p', default="martix/isoform_level", help='Path to gene data files.')
@click.option('--quantitative_indicator', '-q', default="expected_count", help='Quantitative indicator to use.')
def run_pipeline(path_to_data, quantitative_indicator):
    ray.init()
    merged_data_future = merge_data_files.remote(path_to_data, quantitative_indicator)
    final_result = ray.get(merged_data_future)
    click.echo(f"Processing complete. Output saved to: {final_result}")

if __name__ == '__main__':
    run_pipeline()
