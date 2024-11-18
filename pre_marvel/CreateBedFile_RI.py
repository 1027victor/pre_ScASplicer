import click
import pandas as pd

@click.command()
@click.option('--input', type=click.Path(exists=True), required=True, help='Input rMATS RI file path.')
@click.option('--output', type=click.Path(), required=True, help='Output BED file path.')
def prepare_bed_file_ri(input, output):
    """
    Processes an rMATS output file for Retained Intron events to extract intron coordinates and saves it as a BED file.
    """
    # Read the input file
    df = pd.read_csv(input, sep='\t', header=0)

    # Remove "X" prefix from column names
    df.columns = df.columns.str.replace('^X', '', regex=True)

    # Subset intron coordinates: positive strand
    df_pos = df[df['strand'] == '+'].copy()
    df_pos = df_pos[['chr', 'upstreamEE', 'downstreamES']]

    # Subset intron coordinates: negative strand
    df_neg = df[df['strand'] == '-'].copy()
    df_neg = df_neg[['chr', 'upstreamEE', 'downstreamES']]

    # Merge
    df_bed = pd.concat([df_pos, df_neg], ignore_index=True)

    # Adjust coordinates for BED format
    # BED format uses 0-based start and 1-based end coordinates
    df_bed['upstreamEE'] = df_bed['upstreamEE'] - 1  # Convert to 0-based start

    # Reorder chromosomes
    chr_order = [f"chr{i}" for i in range(1, 23)] + ["chrX"]
    df_bed['chr'] = pd.Categorical(df_bed['chr'], categories=chr_order, ordered=True)
    df_bed = df_bed.sort_values(by=['chr', 'upstreamEE'])

    # Check coordinates
    coord_check = (df_bed['downstreamES'] > df_bed['upstreamEE']).value_counts()
    print("Coordinate check (downstreamES > upstreamEE):")
    print(coord_check)

    # Keep unique entries
    df_bed = df_bed.drop_duplicates()

    # Save to BED file
    df_bed[['chr', 'upstreamEE', 'downstreamES']].to_csv(output, sep='\t', header=True, index=False)
    print(f"Processed BED file saved to {output}")

if __name__ == '__main__':
    prepare_bed_file_ri()



# python CreateBedFile_RI.py --input fromGTF.RI.txt --output RI_introns.bed
