#!/usr/bin/env python3

import os
import shutil
from uuid import UUID, uuid4
from pathlib import Path
from main import prepare_blastdb


def test_prepare_blastdb() -> None:
    uuid: UUID = uuid4()
    test_reference_fasta_gz: str = (
        "./_test_data/input_data/reference_proteomes/8.7165.faa.gz"
    )
    tmp_test_dir = f"/tmp/{uuid}/output_data/blast_db_8.7165/"
    tmp_test_dir_path = Path(tmp_test_dir)
    tmp_test_dir_path.mkdir(parents=True, exist_ok=True)
    res_blast_db = prepare_blastdb(
        reference_fasta_gz=str(test_reference_fasta_gz),
        db_output=str(tmp_test_dir_path),
    )
    assert res_blast_db == os.path.join(tmp_test_dir, "8.7165.faa")

    assert not os.path.exists(os.path.join(tmp_test_dir, "8.7165.faa.gz"))

    assert os.path.exists(os.path.join(tmp_test_dir, "8.7165.faa"))
    assert os.path.exists(os.path.join(tmp_test_dir, "8.7165.faa.pdb"))
    assert os.path.exists(os.path.join(tmp_test_dir, "8.7165.faa.phr"))
    assert os.path.exists(os.path.join(tmp_test_dir, "8.7165.faa.pin"))
    assert os.path.exists(os.path.join(tmp_test_dir, "8.7165.faa.pjs"))
    assert os.path.exists(os.path.join(tmp_test_dir, "8.7165.faa.pot"))
    assert os.path.exists(os.path.join(tmp_test_dir, "8.7165.faa.psq"))
    assert os.path.exists(os.path.join(tmp_test_dir, "8.7165.faa.ptf"))
    assert os.path.exists(os.path.join(tmp_test_dir, "8.7165.faa.pto"))

    if os.path.exists(tmp_test_dir):
        shutil.rmtree(tmp_test_dir)
