import pathlib
import zipfile

from dagster_pyspark.utils import DEFAULT_EXCLUSION_LIST, build_pyspark_zip


def test_build_pyspark_zip(tmp_path: pathlib.Path):
    files_dir = tmp_path / "source"
    files_dir.mkdir()
    zip_file = tmp_path / "res.zip"

    (files_dir / "__pycache__").mkdir()
    (files_dir / "__pycache__" / "toskip").touch()
    (files_dir / "toskip.pyc").touch()
    (files_dir / "legit.py").touch()
    (files_dir / ".toskip.py").touch()

    hidden_files_regex = [r"^[\.].+", r".+[\/][\.].+"]

    # We skip the pytest exclusion list as it will likely match the tmp dir path
    build_pyspark_zip(
        zip_file.as_posix(), files_dir.as_posix(), DEFAULT_EXCLUSION_LIST[:-1] + hidden_files_regex
    )
    assert zipfile.ZipFile(zip_file.as_posix()).namelist() == ["legit.py"]
