# Buzz Solutions Assignment

## Introduction

This is my solution to Buzz Solutions coding challenge

Problem 1 is in the Problem 1 Notebook

Problem 2 is in ScrapeGoogle.py

## Installation Instructions 

1. Ensure conda is installed
2. create the `Buzz_Solutions` conda environment via  `conda env create -f Buzz_Solutions.yml`
3. Install the ipykernel to run the jupyter notebook via `python -m ipykernel install --user --name Buzz_Solutions --display-name "Python (Buzz_Solutions)"`

## Usage Instructions

To use the Problem 1 Notebook, simply run the cells in descending order.

To use ScrapeGoogle.py, simply provide it a `--query`, a `--num_images`, and a `--data_dir` (the root directory of where to store your scrapped images).
### Example
`python ScrapeGoogle.py --query bananas --num_images 5 --data_dir ./data`
