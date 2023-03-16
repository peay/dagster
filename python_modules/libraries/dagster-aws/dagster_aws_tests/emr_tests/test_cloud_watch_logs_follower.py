import logging
import time

import boto3
from moto import mock_logs

from dagster_aws.emr.cloud_watch_logs_follower import CloudWatchLogsFollower


@mock_logs
def test_cw_logs_follower():
    logs = boto3.client("logs", region_name="us-east-1")
    logs.create_log_group(logGroupName="grp")

    for i in {1, 2}:
        logs.create_log_stream(logGroupName="grp", logStreamName=f"stream-{i}")

    ts_ms = int(time.time() * 1000)
    follower = CloudWatchLogsFollower(logs, "grp", "stream-", ts_ms + 500)
    log = logging.getLogger(__name__)

    # No events yet
    events = list(follower.fetch_events(log))
    assert not events

    # Add two events
    logs.put_log_events(
        logGroupName="grp",
        logStreamName="stream-1",
        logEvents=[
            {"timestamp": ts_ms + 1000, "message": "string"},
        ],
    )

    logs.put_log_events(
        logGroupName="grp",
        logStreamName="stream-2",
        logEvents=[
            {"timestamp": ts_ms + 1500, "message": "string"},
        ],
    )

    events = list(follower.fetch_events(log))
    assert len(events) == 2

    # New event should be fetched, not older ones
    logs.put_log_events(
        logGroupName="grp",
        logStreamName="stream-2",
        logEvents=[
            {"timestamp": ts_ms + 1500, "message": "another event"},
        ],
    )

    events = list(follower.fetch_events(log))
    assert len(events) == 1

    # Five new events
    for _ in range(5):
        logs.put_log_events(
            logGroupName="grp",
            logStreamName="stream-1",
            logEvents=[
                {"timestamp": ts_ms + 1650, "message": "another event"},
            ],
        )

    events = list(follower.fetch_events(log))
    assert len(events) == 5

    # No new events
    events = list(follower.fetch_events(log))
    assert not events
