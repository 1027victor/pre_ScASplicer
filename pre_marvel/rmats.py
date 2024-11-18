#!/usr/bin/env python3
import click
import pandas as pd
import sys
import os

# Define functions to process different event types

def Preprocess_rMATS(file_dict, GTF, EventTypes):
    results = {}
    for EventType in EventTypes:
        df = file_dict[EventType]
        if EventType == "SE":
            results['SE'] = Preprocess_rMATS_SE(df, GTF)
        elif EventType == "MXE":
            results['MXE'] = Preprocess_rMATS_MXE(df, GTF)
        elif EventType == "RI":
            results['RI'] = Preprocess_rMATS_RI(df, GTF)
        elif EventType == "A5SS":
            results['A5SS'] = Preprocess_rMATS_A5SS(df, GTF)
        elif EventType == "A3SS":
            results['A3SS'] = Preprocess_rMATS_A3SS(df, GTF)
        else:
            print(f"Unknown event type: {EventType}")
    return results

# Below are the processing functions for each event type (e.g., SE). Others are similar.

def Preprocess_rMATS_SE(df, GTF):
    df = df.copy()

    # Remove "X" prefix from column names
    df.columns = df.columns.str.replace('^X', '', regex=True)

    # Positive strand
    df_pos = df[df['strand'] == '+'].copy()

    # Adjust coordinates
    df_pos['exonStart_0base'] += 1
    df_pos['upstreamES'] += 1
    df_pos['downstreamES'] += 1

    # Create tran_id
    df_pos['tran_id'] = (
        df_pos['chr'] + ":" + df_pos['upstreamES'].astype(str) + ":" + df_pos['upstreamEE'].astype(str) + ":+@" +
        df_pos['chr'] + ":" + df_pos['exonStart_0base'].astype(str) + ":" + df_pos['exonEnd'].astype(str) + ":+@" +
        df_pos['chr'] + ":" + df_pos['downstreamES'].astype(str) + ":" + df_pos['downstreamEE'].astype(str)
    )

    # Negative strand
    df_neg = df[df['strand'] == '-'].copy()

    # Adjust coordinates
    df_neg['exonStart_0base'] += 1
    df_neg['upstreamES'] += 1
    df_neg['downstreamES'] += 1

    # Create tran_id
    df_neg['tran_id'] = (
        df_neg['chr'] + ":" + df_neg['downstreamES'].astype(str) + ":" + df_neg['downstreamEE'].astype(str) + ":-@" +
        df_neg['chr'] + ":" + df_neg['exonStart_0base'].astype(str) + ":" + df_neg['exonEnd'].astype(str) + ":-@" +
        df_neg['chr'] + ":" +
        df_neg['upstreamES'].astype(str) + ":" +
        df_neg['upstreamEE'].astype(str)
    )

    # Merge
    df = pd.concat([df_pos, df_neg], ignore_index=True)

    # Extract relevant columns
    df = df[['tran_id', 'GeneID', 'geneSymbol']]
    df.columns = ['tran_id', 'gene_id', 'gene_short_name']

    # Remove duplicates
    df = df.drop_duplicates()

    # Annotate gene_type
    ref = GTF[GTF.iloc[:, 2] == 'gene'].copy()
    ref['gene_id'] = ref.iloc[:, 8].str.extract('gene_id "([^"]+)"')
    ref['gene_type'] = ref.iloc[:, 8].str.extract('gene_type "([^"]+)"')
    ref = ref[['gene_id', 'gene_type']].drop_duplicates()
    df = df.merge(ref, on='gene_id', how='left')

    # Collapse duplicate entries
    df = collapse_duplicates(df)

    # Check for missing annotations
    check_missing_annotations(df)

    return df

def Preprocess_rMATS_MXE(df, GTF):
    df = df.copy()

    # Remove "X" prefix from column names
    df.columns = df.columns.str.replace('^X', '', regex=True)

    # Positive strand
    df_pos = df[df['strand'] == '+'].copy()

    # Adjust coordinates
    df_pos['1stExonStart_0base'] += 1
    df_pos['2ndExonStart_0base'] += 1
    df_pos['upstreamES'] += 1
    df_pos['downstreamES'] += 1

    # Create tran_id
    df_pos['tran_id'] = (
        df_pos['chr'] + ":" + df_pos['upstreamES'].astype(str) + ":" + df_pos['upstreamEE'].astype(str) + ":+@" +
        df_pos['chr'] + ":" + df_pos['1stExonStart_0base'].astype(str) + ":" + df_pos['1stExonEnd'].astype(str) + ":+@" +
        df_pos['chr'] + ":" + df_pos['2ndExonStart_0base'].astype(str) + ":" + df_pos['2ndExonEnd'].astype(str) + ":+@" +
        df_pos['chr'] + ":" + df_pos['downstreamES'].astype(str) + ":" + df_pos['downstreamEE'].astype(str)
    )

    # Negative strand
    df_neg = df[df['strand'] == '-'].copy()

    # Adjust coordinates
    df_neg['1stExonStart_0base'] += 1
    df_neg['2ndExonStart_0base'] += 1
    df_neg['upstreamES'] += 1
    df_neg['downstreamES'] += 1

    # Create tran_id
    df_neg['tran_id'] = (
        df_neg['chr'] + ":" + df_neg['downstreamES'].astype(str) + ":" + df_neg['downstreamEE'].astype(str) + ":-@" +
        df_neg['chr'] + ":" + df_neg['2ndExonStart_0base'].astype(str) + ":" + df_neg['2ndExonEnd'].astype(str) + ":-@" +
        df_neg['chr'] + ":" + df_neg['1stExonStart_0base'].astype(str) + ":" + df_neg['1stExonEnd'].astype(str) + ":-@" +
        df_neg['chr'] + ":" + df_neg['upstreamES'].astype(str) + ":" + df_neg['upstreamEE'].astype(str)
    )

    # Merge
    df = pd.concat([df_pos, df_neg], ignore_index=True)

    # Extract relevant columns
    df = df[['tran_id', 'GeneID', 'geneSymbol']]
    df.columns = ['tran_id', 'gene_id', 'gene_short_name']

    # Remove duplicates
    df = df.drop_duplicates()

    # Annotate gene_type
    ref = GTF[GTF.iloc[:, 2] == 'gene'].copy()
    ref['gene_id'] = ref.iloc[:, 8].str.extract('gene_id "([^"]+)"')
    ref['gene_type'] = ref.iloc[:, 8].str.extract('gene_type "([^"]+)"')
    ref = ref[['gene_id', 'gene_type']].drop_duplicates()
    df = df.merge(ref, on='gene_id', how='left')

    # Collapse duplicate entries
    df = collapse_duplicates(df)

    # Check for missing annotations
    check_missing_annotations(df)

    return df

def Preprocess_rMATS_RI(df, GTF):
    df = df.copy()

    # Remove "X" prefix from column names
    df.columns = df.columns.str.replace('^X', '', regex=True)

    # Positive strand
    df_pos = df[df['strand'] == '+'].copy()

    # Adjust coordinates
    df_pos['riExonStart_0base'] += 1
    df_pos['downstreamES'] += 1

    # Create tran_id
    df_pos['tran_id'] = (
        df_pos['chr'] + ":" + df_pos['riExonStart_0base'].astype(str) + ":" + df_pos['upstreamEE'].astype(str) + ":+@" +
        df_pos['chr'] + ":" + df_pos['downstreamES'].astype(str) + ":" + df_pos['riExonEnd'].astype(str)
    )

    # Negative strand
    df_neg = df[df['strand'] == '-'].copy()

    # Adjust coordinates
    df_neg['riExonStart_0base'] += 1
    df_neg['downstreamES'] += 1

    # Create tran_id
    df_neg['tran_id'] = (
        df_neg['chr'] + ":" + df_neg['riExonEnd'].astype(str) + ":" + df_neg['downstreamES'].astype(str) + ":-@" +
        df_neg['chr'] + ":" + df_neg['upstreamEE'].astype(str) + ":" + df_neg['riExonStart_0base'].astype(str)
    )

    # Merge
    df = pd.concat([df_pos, df_neg], ignore_index=True)

    # Extract relevant columns
    df = df[['tran_id', 'GeneID', 'geneSymbol']]
    df.columns = ['tran_id', 'gene_id', 'gene_short_name']

    # Remove duplicates
    df = df.drop_duplicates()

    # Annotate gene_type
    ref = GTF[GTF.iloc[:, 2] == 'gene'].copy()
    ref['gene_id'] = ref.iloc[:, 8].str.extract('gene_id "([^"]+)"')
    ref['gene_type'] = ref.iloc[:, 8].str.extract('gene_type "([^"]+)"')
    ref = ref[['gene_id', 'gene_type']].drop_duplicates()
    df = df.merge(ref, on='gene_id', how='left')

    # Collapse duplicate entries
    df = collapse_duplicates(df)

    # Check for missing annotations
    check_missing_annotations(df)

    return df

def Preprocess_rMATS_A5SS(df, GTF):
    df = df.copy()

    # Remove "X" prefix from column names
    df.columns = df.columns.str.replace('^X', '', regex=True)

    # Positive strand
    df_pos = df[df['strand'] == '+'].copy()

    # Adjust coordinates
    df_pos['longExonStart_0base'] += 1
    df_pos['flankingES'] += 1

    # Create tran_id
    df_pos['tran_id'] = (
        df_pos['chr'] + ":" + df_pos['longExonStart_0base'].astype(str) + ":" +
        df_pos['shortEE'].astype(str) + "|" +
        df_pos['longExonEnd'].astype(str) + ":+@" +
        df_pos['chr'] + ":" + df_pos['flankingES'].astype(str) + ":" +
        df_pos['flankingEE'].astype(str)
    )

    # Negative strand
    df_neg = df[df['strand'] == '-'].copy()

    # Adjust coordinates
    df_neg['longExonStart_0base'] += 1
    df_neg['shortES'] += 1
    df_neg['flankingES'] += 1

    # Create tran_id
    df_neg['tran_id'] = (
        df_neg['chr'] + ":" + df_neg['longExonEnd'].astype(str) + ":" +
        df_neg['longExonStart_0base'].astype(str) + "|" +
        df_neg['shortES'].astype(str) + ":-@" +
        df_neg['chr'] + ":" + df_neg['flankingES'].astype(str) + ":" +
        df_neg['flankingEE'].astype(str)
    )

    # Merge
    df = pd.concat([df_pos, df_neg], ignore_index=True)

    # Extract relevant columns
    df = df[['tran_id', 'GeneID', 'geneSymbol']]
    df.columns = ['tran_id', 'gene_id', 'gene_short_name']

    # Remove duplicates
    df = df.drop_duplicates()

    # Annotate gene_type
    ref = GTF[GTF.iloc[:, 2] == 'gene'].copy()
    ref['gene_id'] = ref.iloc[:, 8].str.extract('gene_id "([^"]+)"')
    ref['gene_type'] = ref.iloc[:, 8].str.extract('gene_type "([^"]+)"')
    ref = ref[['gene_id', 'gene_type']].drop_duplicates()
    df = df.merge(ref, on='gene_id', how='left')

    # Collapse duplicate entries
    df = collapse_duplicates(df)

    # Check for missing annotations
    check_missing_annotations(df)

    return df

def Preprocess_rMATS_A3SS(df, GTF):
    df = df.copy()

    # Remove "X" prefix from column names
    df.columns = df.columns.str.replace('^X', '', regex=True)

    # Positive strand
    df_pos = df[df['strand'] == '+'].copy()

    # Adjust coordinates
    df_pos['longExonStart_0base'] += 1
    df_pos['shortES'] += 1
    df_pos['flankingES'] += 1

    # Create tran_id
    df_pos['tran_id'] = (
        df_pos['chr'] + ":" + df_pos['flankingES'].astype(str) + ":" +
        df_pos['flankingEE'].astype(str) + ":+@" +
        df_pos['chr'] + ":" + df_pos['longExonStart_0base'].astype(str) + "|" +
        df_pos['shortES'].astype(str) + ":" +
        df_pos['longExonEnd'].astype(str)
    )

    # Negative strand
    df_neg = df[df['strand'] == '-'].copy()

    # Adjust coordinates
    df_neg['longExonStart_0base'] += 1
    df_neg['flankingES'] += 1

    # Create tran_id
    df_neg['tran_id'] = (
        df_neg['chr'] + ":" + df_neg['flankingES'].astype(str) + ":" +
        df_neg['flankingEE'].astype(str) + ":-@" +
        df_neg['chr'] + ":" + df_neg['shortEE'].astype(str) + "|" +
        df_neg['longExonEnd'].astype(str) + ":" +
        df_neg['longExonStart_0base'].astype(str)
    )

    # Merge
    df = pd.concat([df_pos, df_neg], ignore_index=True)

    # Extract relevant columns
    df = df[['tran_id', 'GeneID', 'geneSymbol']]
    df.columns = ['tran_id', 'gene_id', 'gene_short_name']

    # Remove duplicates
    df = df.drop_duplicates()

    # Annotate gene_type
    ref = GTF[GTF.iloc[:, 2] == 'gene'].copy()
    ref['gene_id'] = ref.iloc[:, 8].str.extract('gene_id "([^"]+)"')
    ref['gene_type'] = ref.iloc[:, 8].str.extract('gene_type "([^"]+)"')
    ref = ref[['gene_id', 'gene_type']].drop_duplicates()
    df = df.merge(ref, on='gene_id', how='left')

    # Collapse duplicate entries
    df = collapse_duplicates(df)

    # Check for missing annotations
    check_missing_annotations(df)

    return df

# Function to collapse duplicates

def collapse_duplicates(df):
    # Collapse duplicate tran_ids
    tran_id_counts = df['tran_id'].value_counts()
    tran_id_dup = tran_id_counts[tran_id_counts > 1].index.tolist()

    if len(tran_id_dup) != 0:
        df_unique = df[~df['tran_id'].isin(tran_id_dup)].copy()
        df_dup = df[df['tran_id'].isin(tran_id_dup)].copy()

        df_dup = df_dup.groupby('tran_id').agg({
            'gene_id': lambda x: '|'.join(x.astype(str).unique()),
            'gene_short_name': lambda x: '|'.join(x.astype(str).unique()),
            'gene_type': lambda x: '|'.join(x.astype(str).unique())
        }).reset_index()

        df = pd.concat([df_unique, df_dup], ignore_index=True)
    return df

# Function to check for missing annotations

def check_missing_annotations(df):
    if df['gene_type'].isna().sum() != 0:
        print("Warning: Not all genes were successfully annotated with gene_type from the GTF file. Please ensure the provided GTF file is the same version used in the rMATS step.")

# Main function using click

@click.command()
@click.option('--event-types', multiple=True, type=click.Choice(['SE', 'MXE', 'RI', 'A5SS', 'A3SS']), help='Splicing event types to process; multiple can be specified.')
@click.option('--files', multiple=True, type=click.Path(exists=True), help='Input file paths corresponding to event types; multiple can be specified, matching the event types one-to-one.')
@click.option('--gtf', type=click.Path(exists=True), required=True, help='Path to the GTF file used in rMATS.')
@click.option('--output-dir', type=click.Path(), required=True, help='Directory path to save the output results.')
def preprocess_rmats(event_types, files, gtf, output_dir):
    """
    Process rMATS output files to extract splicing event coordinates and annotations.
    """
    if len(event_types) != len(files):
        print("Error: The number of event types does not match the number of files.")
        sys.exit(1)

    # Read GTF file
    GTF_df = pd.read_csv(gtf, sep='\t', header=None, comment='#', low_memory=False)

    # Read files for each event type
    file_dict = {}
    for etype, fpath in zip(event_types, files):
        df = pd.read_csv(fpath, sep='\t', header=0)
        file_dict[etype] = df

    # Process events
    results = Preprocess_rMATS(file_dict, GTF_df, event_types)

    # Check if output directory exists; create if not
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save results
    for etype, result_df in results.items():
        output_file = os.path.join(output_dir, f"{etype}_processed_events.txt")
        result_df.to_csv(output_file, sep='\t', index=False)
        print(f"{etype} event processing complete, results saved to {output_file}")

if __name__ == '__main__':
    preprocess_rmats()





# python rmats.py   --event-types SE --event-types MXE --event-types RI --event-types A5SS --event-types A3SS   --files fromGTF.SE.txt --files fromGTF.MXE.txt --files fromGTF.RI.txt --files fromGTF.A5SS.txt --files fromGTF.A3SS.txt   --gtf gencode.v44.basic.annotation.gtf   --output-dir ./processed_events
