# -*- coding: utf-8 -*-
"""
@Time ： 2024/3/22 19:04
@Auth ： victor
@IDE ：PyCharm
"""
import os
import pandas as pd
import click
import ray

@ray.remote
def process_file_to_intron_matrix(input_path, output_dir):
    data = pd.read_table(input_path)
    df_sum = data.groupby('coord.intron').sum().reset_index()
    output_path = os.path.join(output_dir, os.path.basename(input_path))
    df_sum.to_csv(output_path, index=False, sep='\t')
    return output_path

@ray.remote
def concatenate_dfs(file_path):
    return pd.read_table(file_path, index_col=0)

@click.command()
@click.option('--input-dir', type=click.Path(exists=True), required=True, help='Path to the input directory.')
@click.option('--intermediate-dir', type=click.Path(), required=True, help='Path to the directory for intermediate intron matrices.')
@click.option('--output-file', type=click.Path(), required=True, help='Output file for the concatenated matrix.')
def full_process(input_dir, intermediate_dir, output_file):
    ray.init(num_cpus=30, ignore_reinit_error=True)  # 根据您的系统配置调整num_cpus的值
    output_dir = os.path.dirname(intermediate_dir)
    if output_dir:  # 检查output_dir是否为空
       os.makedirs(intermediate_dir, exist_ok=True)
    output_dir_final = os.path.dirname(output_file)
    if output_dir_final:  # 检查output_dir是否为空
        os.makedirs(output_dir_final, exist_ok=True)
    # Form intron matrices
    file_paths = [os.path.join(input_dir, filename) for filename in os.listdir(input_dir)  if filename.endswith('.txt')]
    formed_files = ray.get([process_file_to_intron_matrix.remote(file_path, intermediate_dir) for file_path in file_paths])
    
    # Merge intron matrices
    data_frames = ray.get([concatenate_dfs.remote(file_path) for file_path in formed_files])
    combined_df = pd.concat(data_frames, axis=1)
    combined_df = combined_df.sort_index(axis=1)
    combined_df = combined_df.fillna('NA')
    combined_df.to_csv(output_file, sep='\t')
    
    click.echo(f"Intron matrices merged and saved to {output_file}")

if __name__ == '__main__':
    full_process()
