import os
import re
import zipfile

import dagster._check as check

DEFAULT_EXCLUSION_LIST = [r".*\.pyc$", r".*\/__pycache__\/.*", r".*pytest.*"]


def build_pyspark_zip(zip_file, path, exclusion_regexes=DEFAULT_EXCLUSION_LIST):
    """Archives the current path into a file named `zip_file`."""
    check.str_param(zip_file, "zip_file")
    check.str_param(path, "path")

    joined_regex = "|".join([f"({r})" for r in exclusion_regexes])

    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(path, followlinks=True):
            for fname in files:
                abs_fname = os.path.join(root, fname)

                if re.match(joined_regex, abs_fname):
                    continue

                zf.write(abs_fname, os.path.relpath(os.path.join(root, fname), path))
