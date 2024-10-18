import os
import pandas as pd
import click
import ray

@click.command()
@click.option('--directory', type=click.Path(exists=True), required=True, help='Input file path')
@click.option('--output-file', type=click.Path(), required=True, help='Output file')
@click.option('--nums', type=int, required=False, help='numers of core',default=30)
def process_files(directory, output_file,nums):
    # 初始化ray
    ray.init(num_cpus=nums, ignore_reinit_error=True)  # ignore_reinit_error=True允许在ray已初始化的情况下忽略重复初始化的错误

    file_paths = [os.path.join(directory, i) for i in os.listdir(directory) if i.endswith('.txt')]
    
    # 使用ray并行处理文件
    data_frames = ray.get([process_file.remote(file_path) for file_path in file_paths])
    null = pd.concat(data_frames, axis=1)
    null = null.sort_index(axis=1)
    null = null.fillna('NA')
    
    output_dir = os.path.dirname(output_file)
    if output_dir:  # 检查output_dir是否为空
        os.makedirs(output_dir, exist_ok=True)
    null.to_csv(output_file, sep='\t')
    click.echo(f"The output file data has been successfully saved to {output_file}")

@ray.remote
def process_file(file_path):
    data = pd.read_table(file_path, sep='\t', index_col=0)
    return data

if __name__ == '__main__':
    process_files()
