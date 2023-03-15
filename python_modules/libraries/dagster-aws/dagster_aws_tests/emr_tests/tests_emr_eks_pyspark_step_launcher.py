from unittest import mock
from dagster_aws.emr.emr_eks_pyspark_step_launcher import (
    EmrEksPySparkResource,
    emr_eks_pyspark_resource,
)
from dagster.core.events import DagsterEvent, DagsterEventType
from dagster import build_init_resource_context
import pytest
import os


@mock.patch(
    "dagster_aws.emr.emr_eks_pyspark_step_launcher.EmrEksJobRunMonitor.__post_init__",
)
@mock.patch(
    "dagster_aws.emr.emr_eks_pyspark_step_launcher.EmrEksJobRunMonitor.wait_for_completion",
    side_effect=[
        iter(
            [
                DagsterEvent(
                    event_type_value=DagsterEventType.LOGS_CAPTURED, pipeline_name="pipeline"
                ),
                DagsterEvent(
                    event_type_value=DagsterEventType.STEP_START, pipeline_name="pipeline"
                ),
            ]
        )
    ],
)
def test_wait_for_completion(mock_monitor, mock_wait):
    launcher = EmrEksPySparkResource(
        cluster_id="",
        container_image="",
        deploy_local_job_package=False,
        emr_release_label="",
        job_role_arn="",
        log_group_name="",
        log4j_conf="",
        region_name="",
        staging_bucket="",
        staging_prefix="",
        spark_config={},
        ephemeral_instance="",
        additional_relative_paths=[],
    )

    mock_context = mock.MagicMock()
    mock_context.step.key = "key"
    mock_context.dagster_run.pipeline_name = "pipeline"

    yielded_events = list(
        launcher.wait_for_completion_and_log(job_id="", step_context=mock_context)
    )
    assert len(yielded_events) == 2


def test_emr_pyspark_step_launcher_legacy_arguments():
    mock_config = {
        "spark_config": {},
        "cluster_id": "",
        "region_name": "",
        "staging_bucket": "",
        "staging_prefix": "",
        "deploy_local_job_package": "",
        "emr_release_label": "",
        "container_image": "",
        "job_role_arn": "",
        "log_group_name": "",
    }

    with pytest.raises(Exception):
        emr_eks_pyspark_resource(
            build_init_resource_context(
                config={
                    **mock_config,
                    "spark_config": "config",
                }
            )
        )

    with pytest.raises(Exception):
        emr_eks_pyspark_resource(
            build_init_resource_context(
                config={
                    **mock_config,
                    "additional_relative_paths": paths,
                }
            )
        )

    assert emr_eks_pyspark_resource(
        build_init_resource_context(
            config={
                **mock_config,
                "deploy_local_job_package": True,
            }
        )
    )
