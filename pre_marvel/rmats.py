import click
import pandas as pd
import numpy as np
from tqdm import tqdm
import os
import ray

@ray.remote
def process_counts_file(bed, counts_file_path, counts_file):
    """
    Function to process a single counts file using Ray's remote function for parallelization.
    """
    # Read counts file
    df = pd.read_csv(counts_file_path, sep='\t', header=None)

    # Create coordinates
    df['coord.intron'] = df[1] + df[3]
    df['coord.intron'] = df[0].astype(str) + ':' + df['coord.intron'].astype(str)

    # Extract gene counts
    df = df[['coord.intron', 4]]
    df.columns = ['coord.intron', 'count']

    # Keep unique entries
    df = df.drop_duplicates()

    region_counts_df_list = []

    # Process each region in the BED file
    for i in range(len(bed)):
        # Get information of the current region
        bed_small = bed.iloc[i]
        start = bed_small['upstreamEE'] + 1
        end = bed_small['downstreamES']
        # Generate all coordinates within the range
        positions = np.arange(start, end + 1)
        positions_str = positions.astype(str)
        chr_name = str(bed_small['chr'])

        # Ensure chr_name is broadcasted to the same shape as positions_str
        chr_array = np.full(positions_str.shape, chr_name, dtype=positions_str.dtype)

        # Concatenate strings using numpy.char functions
        coords = np.char.add(np.char.add(chr_array, ':'), positions_str)

        # Calculate total counts
        counts_total = df.loc[df['coord.intron'].isin(coords), 'count'].sum()
        # Save result
        coord_intron = f"{chr_name}:{bed_small['upstreamEE'] + 1}:{bed_small['downstreamES']}"
        region_counts_df_list.append({'coord.intron': coord_intron, 'count': counts_total})

    # Create dataframe for the current sample
    region_counts_df = pd.DataFrame(region_counts_df_list)
    region_counts_df.set_index('coord.intron', inplace=True)

    # Rename the count column to the sample name
    sample_name = counts_file.replace('.txt', '')
    region_counts_df.columns = [sample_name]

    return region_counts_df

@click.command()
@click.option('--bed-file', type=click.Path(exists=True), required=True, help='Path to the BED file.')
@click.option('--counts-dir', type=click.Path(exists=True, file_okay=False, dir_okay=True), required=True, help='Directory path containing counts files.')
@click.option('--output-dir', type=click.Path(), required=True, help='Directory path to save processed counts files.')
@click.option('--combined-output', type=click.Path(), required=True, help='File path to save the combined counts file.')
@click.option('--cpus', type=int, default=32, help='Number of CPUs to use.')
def process_and_combine_counts(bed_file, counts_dir, output_dir, combined_output, cpus):
    """
    Use Ray to process all counts files in the specified directory in parallel, output the results to the specified directory, and then combine the processed counts files into a single file.
    """
    # Initialize Ray
    ray.init(num_cpus=cpus)

    # Read BED file
    bed = pd.read_csv(bed_file, sep='\t', header=0)

    # Get list of counts files
    counts_files = [f for f in os.listdir(counts_dir) if os.path.isfile(os.path.join(counts_dir, f)) and f.endswith('.txt')]

    # Check if output directory exists, if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialize list to store references to processed dataframes
    processed_df_futures = []
    counts_file_names = []

    # Process each counts file in parallel
    for counts_file in counts_files:
        counts_file_path = os.path.join(counts_dir, counts_file)
        print(f"Submitting processing task: {counts_file}")
        # Submit processing task to Ray
        future = process_counts_file.remote(bed, counts_file_path, counts_file)
        processed_df_futures.append(future)
        counts_file_names.append(counts_file)

    # Collect results
    print("Collecting processing results...")
    processed_dfs = ray.get(processed_df_futures)

    # Save processed counts files and prepare for combining
    processed_df_list = []
    for counts_file, region_counts_df in zip(counts_file_names, processed_dfs):
        # Save processed counts file
        output_file = os.path.join(output_dir, counts_file)
        region_counts_df.to_csv(output_file, sep='\t', header=True, index=True)
        print(f"Result saved to {output_file}")
        processed_df_list.append(region_counts_df)

    # Combine all processed counts files
    print("Combining all processed counts files...")
    df_combined = pd.concat(processed_df_list, axis=1)

    # Reset index to convert 'coord.intron' to a column
    df_combined.reset_index(inplace=True)

    # Save the combined counts file
    df_combined.to_csv(combined_output, sep='\t', index=False)
    print(f"Combined counts file saved to {combined_output}")

    # Shutdown Ray
    ray.shutdown()

if __name__ == '__main__':
    process_and_combine_counts()
