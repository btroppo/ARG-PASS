"""Wrapper around `foldseek easy-search`.

The search settings here must match those used to generate the stored training
distributions, otherwise candidate TM-scores are not comparable with the
training points the SVM was fitted on.
"""

import glob
import os
import shutil
import subprocess
import tempfile

# Must match COLUMNS in features.py.
FORMAT_OUTPUT = "query,target,alntmscore,qtmscore,ttmscore,pident,qlen,alnlen,tlen"

ALIGNMENT_TYPE = "1"  # TM-align


def find_foldseek(binary=None):
    """Locate the foldseek executable."""
    path = binary or os.environ.get("FOLDSEEK_BIN") or shutil.which("foldseek")
    if path is None:
        raise FileNotFoundError(
            "foldseek not found. Install it (conda install -c conda-forge -c bioconda "
            "foldseek), pass --foldseek-bin, or set FOLDSEEK_BIN."
        )
    return path


def search(input_dir, database, out_path, binary=None, exhaustive=True, threads=None):
    """Run foldseek easy-search of every .pdb in input_dir against database.

    database is the path prefix of the Foldseek database, e.g.
    databases/v2.0/AAC_1/conserved_ARPs.
    """
    foldseek = find_foldseek(binary)

    structures = sorted(glob.glob(os.path.join(input_dir, "*.pdb")))
    if not structures:
        raise FileNotFoundError(f"No .pdb files found in {input_dir}")

    with tempfile.TemporaryDirectory(prefix="argpass_foldseek_") as tmp:
        cmd = [foldseek, "easy-search", *structures, database, out_path, tmp,
               "--alignment-type", ALIGNMENT_TYPE,
               "--format-output", FORMAT_OUTPUT]
        if exhaustive:
            cmd.append("--exhaustive-search")
        if threads:
            cmd += ["--threads", str(threads)]

        result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(
            f"foldseek failed (exit {result.returncode})\n{result.stderr[-2000:]}"
        )

    return out_path
