"""Entrypoint for a step running on EMR on EKS."""
import os
import pickle
import sys

import boto3
from dagster.core.execution.plan.external_step import run_step_from_ref
from dagster.core.instance import DagsterInstance

CODE_ZIP_NAME = "code.zip"


def main(s3_bucket_step_run_ref: str, s3_key_step_run_ref: str) -> None:
    session = boto3.client("s3")

    # This must be called before any of our packages is imported so that
    # they can take precedence over any packages installed on the EMR docker and
    # that imports do not fail.
    _adjust_pythonpath_for_staged_assets()

    from dagster_aws.s3.file_manager import S3FileHandle, S3FileManager

    # Read the step description
    file_manager = S3FileManager(session, s3_bucket_step_run_ref, "")
    file_handle = S3FileHandle(s3_bucket_step_run_ref, s3_key_step_run_ref)

    step_run_ref_data = file_manager.read_data(file_handle)
    step_run_ref = pickle.loads(step_run_ref_data)

    print(f"Running the following step: {step_run_ref}")

    from dagster_aws.emr.dagster_event_serde import dump_event

    # Run the Dagster job. The plan process should tail the job
    # logs in order to extract events.
    with DagsterInstance.ephemeral() as instance:
        for event in run_step_from_ref(step_run_ref, instance):
            dump_event(event)

    print("Job is over")


def _adjust_pythonpath_for_staged_assets():
    """
    Adjust Python path for Python packages in staged code.

    When staging code through S3 instead of using code baked in the
    docker image, packages are still picked up from the docker image
    by default, as they are not directly in the path.

    This function adds Python packages in the staged code to the path
    explicitly so that they are picked up.
    """
    code_subpaths_str = os.getenv("ENV_PATHS")
    if code_subpaths_str is None:
        return

    code_subpaths = code_subpaths_str.split(",")

    code_entries = [
        filename for filename in sys.path if os.path.basename(filename) == CODE_ZIP_NAME
    ]

    if not code_entries:
        print("`code.zip` is not in the Python path, code was not staged")
        return

    code_path = code_entries[0]

    for subpath in code_subpaths:
        path_to_add = os.path.join(code_path, subpath)

        print(f"Adding {path_to_add} to Python path")
        sys.path.insert(0, path_to_add)


if __name__ == "__main__":
    assert len(sys.argv) == 3
    main(sys.argv[1], sys.argv[2])
