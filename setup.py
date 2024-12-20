from setuptools import setup, find_packages

setup(
    name='pre_marvel',
    version='0.1.0',
    packages=find_packages(),
    description='A package that simplifies and streamlines the generation of MARVEL input files',
    author='Pengwei Hu',
    # install_requires=[
    #     'pandas',
    #     'click',
    #     'ray',
    # ],
    # url='https://github.com/1027victor/pre_MARVEL',
    entry_points={
        'console_scripts': [
            'merge-bed=pre_marvel.merge_bed:process_and_combine_counts',
            'merge-counts=pre_marvel.merge_counts:run_pipeline',
            'merge-SJ=pre_marvel.merge_SJ:process_files',
            'PreprocessrMATS=pre_marvel.rmats:preprocess_rmats',
            'PrepareBedfile=pre_marvel.CreateBedFile_RI:prepare_bed_file_ri'
        ]
    },
)
