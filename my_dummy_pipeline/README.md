my_dummy_pipeline
=================

## Overview
This pipeline automates a basic BLAST (Basic Local Alignment Search Tool) analysis using Python, Pandas, NumPy, R, and ggplot2. It:

    Takes a FASTA file as input.
    Creates a BLAST database from the sequences.
    Runs BLAST to find similar sequences.
    Parses the BLAST results (TSV format) using Python.
    Processes the data (e.g., log-transforming bit scores).
    Generates a scatter plot using R and ggplot2 to visualize BLAST hit scores against percent identity.

---

## How to run

```sh
python3 main.py \
		--reference-fasta-gz "./_test_data/input_data/reference_proteomes/7165.fasta.gz" \
		--blast-db-output-dir "./_test_data/output_data/blast_db_7165/" \
		--target-fasta-path "./_test_data/input_data/target_proteomes/0.7165.reduced.faa" \
		--blast-result-tsv-path "./_test_data/output_data/blast_result_0.7165.reduced.tsv" \
		--plot-output  "./_test_data/output_data/8.7165.res.png"
```

---

