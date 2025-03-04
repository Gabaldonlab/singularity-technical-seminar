#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from subprocess import getstatusoutput
from uuid import UUID, uuid4

import numpy as np
import pandas as pd


@dataclass
class CliArguments:
    reference_fasta_gz: str
    blast_db_output_dir: str
    target_fasta_path: str
    blast_result_tsv_path: str
    plot_output: str

    @classmethod
    def get_arguments(cls) -> CliArguments:
        parser = ArgumentParser()
        parser.add_argument(
            "--reference-fasta-gz",
            required=True,
            type=str,
            help="Path to the reference fasta file compressed as .gz.",
        )
        parser.add_argument(
            "--blast-db-output-dir",
            type=str,
            help="Output directory path to the generated Blast database.",
            default=os.path.join(os.getcwd(), "output", "blastdb"),
        )
        parser.add_argument(
            "--blast-result-tsv-path",
            type=str,
            help="Output path of the Blast result .tsv file.",
            default=os.path.join(os.getcwd(), "output", "blast_result.tsv"),
        )
        parser.add_argument(
            "--target-fasta-path",
            required=True,
            type=str,
            help="Path to the target fasta file to be queried by Blast.",
        )
        parser.add_argument(
            "--plot-output",
            required=True,
            type=str,
            help="Output path to the generated plot.",
        )
        return CliArguments(**vars(parser.parse_args()))


def _exec_shell(cmd: str) -> str:
    exit_code, output = getstatusoutput(cmd)
    if exit_code != 0:
        raise ChildProcessError(f"[ERROR] Failed cmd: [{cmd}]!\n" f"OUTPUT:\n{output}")
    return output


def prepare_blastdb(reference_fasta_gz: str, db_output: str) -> str:
    if os.path.exists(db_output):
        shutil.rmtree(db_output)

    reference_gz = Path(reference_fasta_gz)
    reference_file_name: str = reference_gz.name
    reference_gz_parent_dir: Path = reference_gz.parent

    resolved_reference_parent: Path = reference_gz_parent_dir.resolve()
    db_output_path = Path(db_output)
    resolved_db_output: Path = db_output_path.resolve()
    if resolved_reference_parent != resolved_db_output:
        db_output_path.mkdir(parents=True, exist_ok=True)
        reference_gz = db_output_path / reference_file_name
        shutil.copyfile(reference_fasta_gz, str(reference_gz))

    title_uuid: UUID = uuid4()
    decompressed_fasta = reference_gz.with_suffix("")
    decompress_cmd = f"zcat {reference_gz} > {decompressed_fasta}"
    _exec_shell(decompress_cmd)

    makeblastdb_cmd = (
        f"makeblastdb -in {decompressed_fasta} -dbtype 'prot' -title {title_uuid}"
    )
    _exec_shell(makeblastdb_cmd)
    reference_gz.unlink()
    return str(decompressed_fasta)


def generate_blast_result_tsv(
    target_fasta_path: str | Path,
    blastdb_path: str | Path,
    result_tsv_output_path: str | Path,
) -> Path:
    blast_cmd = (
        f'blastp -task "blastp-fast" '
        f"-query {target_fasta_path} "
        f"-db {blastdb_path} "
        "-outfmt '6 qseqid sseqid pident length bitscore' "
        f"-out {result_tsv_output_path}"
    )
    _exec_shell(blast_cmd)
    return Path(result_tsv_output_path)


def run_create_result_plot(blast_results_tsv: str | Path, plot_output_path: str | Path) -> None:
    create_plots_script_path: Path = Path(__file__).parent / "create_result_plot.R"
    create_plots_cmd: str = f"Rscript {create_plots_script_path} {blast_results_tsv} {plot_output_path}"
    _exec_shell(create_plots_cmd)


def main() -> int:
    print("LALA")
    args = CliArguments.get_arguments()
    blast_db = prepare_blastdb(
        reference_fasta_gz=args.reference_fasta_gz, db_output=args.blast_db_output_dir
    )
    blast_result_tsv = generate_blast_result_tsv(
        target_fasta_path=args.target_fasta_path,
        blastdb_path=blast_db,
        result_tsv_output_path=args.blast_result_tsv_path,
    )

    blast_output: pd.DataFrame = pd.read_csv(
        blast_result_tsv,
        sep="\t",
        header=None,
        names=["qseqid", "sseqid", "pident", "length", "bitscore"],
    )

    # Normalize bitscores
    blast_output["norm_bitscore"] = np.log1p(blast_output["bitscore"])

    # Save processed data for R
    processed_blast_result_tsv = blast_result_tsv.with_suffix(".processed.tsv")
    blast_output.to_csv(processed_blast_result_tsv, sep="\t", index=False)

    run_create_result_plot(processed_blast_result_tsv, args.plot_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
