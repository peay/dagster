import os
import sys
from unittest import mock

from dagster_aws.emr.emr_eks_step_main import _adjust_pythonpath_for_staged_assets


def test__adjust_pythonpath_for_staged_assets_noop():
    _adjust_pythonpath_for_staged_assets()


@mock.patch("sys.path", ["/tmp/dir/code.zip"])
def test__adjust_pythonpath_for_staged_assets():
    path_to_lib = "path/to/lib"
    os.environ["ENV_PATHS"] = path_to_lib

    _adjust_pythonpath_for_staged_assets()

    assert os.path.join("/tmp/dir/code.zip/", path_to_lib) in sys.path
