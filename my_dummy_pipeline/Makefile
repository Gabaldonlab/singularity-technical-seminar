.PHONY: \
	test-data-run

test-data-run:
	@python3 main.py \
		--reference-fasta-gz "./_test_data/input_data/reference_proteomes/7165.fasta.gz" \
		--blast-db-output-dir "./_test_data/output_data/blast_db_7165/" \
		--target-fasta-path "./_test_data/input_data/target_proteomes/0.7165.reduced.faa" \
		--blast-result-tsv-path "./_test_data/output_data/blast_result_0.7165.reduced.tsv" \
		--plot-output  "./_test_data/output_data/0.7165.res.png"

unit-tests-run:
	@python3 -m pytest ./tests

