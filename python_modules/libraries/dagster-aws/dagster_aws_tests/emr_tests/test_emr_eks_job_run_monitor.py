import base64
import json
import logging
import pickle
import time

import boto3
from dagster._core.execution.plan.objects import StepSuccessData
from dagster.core.events import DagsterEvent, DagsterEventType
from dagster_aws.emr.emr_eks_job_run_monitor import EmrEksJobRunMonitor
from moto import mock_emrcontainers, mock_logs


def test_emr_eks_job_run_monitor():
    with mock_logs(), mock_emrcontainers():
        log_group_name = "test-group"
        log_stream_prefix = "test-stream-"
        log_stream_name = log_stream_prefix + "stdout"
        logs = boto3.client("logs", region_name="eu-central-1")
        logs.create_log_group(logGroupName=log_group_name)
        logs.create_log_stream(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
        )

        region_name = "eu-central-1"

        emr_containers = boto3.client("emr-containers", region_name=region_name)

        print("-" * 100)
        response = emr_containers.create_virtual_cluster(
            name="cluster",
            containerProvider={
                "type": "EKS",
                "id": "cluster_id",
                "info": {"eksInfo": {"namespace": "namespace"}},
            },
            clientToken="string",
            tags={},
        )
        cluster_id = response["id"]
        response = emr_containers.start_job_run(
            name="application",
            virtualClusterId=cluster_id,
            executionRoleArn="arn" * 10,
            releaseLabel="emr-4.1.0-latest",
            jobDriver={},
            configurationOverrides={},
        )
        job_id = response["id"]

        monitor = EmrEksJobRunMonitor(cluster_id=cluster_id, region_name=region_name)

        logs.put_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
            logEvents=[
                {"timestamp": int(time.time() * 1000), "message": "test message"},
                {
                    "timestamp": int(time.time() * 1000),
                    "message": json.dumps(
                        {
                            "message": json.dumps(
                                {
                                    "event": base64.b64encode(
                                        pickle.dumps(
                                            DagsterEvent(
                                                event_type_value=DagsterEventType.STEP_SUCCESS,
                                                pipeline_name="application",
                                                event_specific_data=StepSuccessData(
                                                    duration_ms=2.0
                                                ),
                                            )
                                        )
                                    ).decode("ascii")
                                }
                            )
                        }
                    ),
                },
            ],
            sequenceToken="0",
        )

        e = next(
            monitor.wait_for_completion(
                log=logging.getLogger(__name__),
                job_id=job_id,
                log_group_name=log_group_name,
                log_stream_name_prefix=log_stream_prefix,
                start_timestamp_ms=0,
                wait_interval_secs=1,
                max_wait_after_done_secs=0,
            )
        )

        assert e.event_type == DagsterEventType.STEP_SUCCESS
