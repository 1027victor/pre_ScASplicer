from setuptools import setup, find_packages

setup(
    name='pre_marvel',
    version='0.1.0',
    packages=find_packages(),
    description='A package for merging gene data files.',
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
            'merge-SJ=pre_marvel.merge_SJ:process_files'
        ]
    },
)
