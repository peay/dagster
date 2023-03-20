import base64
import json
import pickle

from dagster.core.events import DagsterEvent

# Any event whose JSON representation is larger than this
# will be dropped. Otherwise, it can cause EMR to stop
# reporting all logs to Cloudwatch Logs.
_MAX_EVENT_SIZE_BYTES = 64 * 1024


def event_to_str(event: DagsterEvent) -> str:
    """Convert a Dagster event to a string that can be logged."""
    return base64.b64encode(pickle.dumps(event)).decode("ascii")


def dump_event(event: DagsterEvent) -> None:
    """Dump a Dagster event to `stdout`."""
    event_json = json.dumps({"event": event_to_str(event), "eventDescr": str(event)})

    if len(event_json) > _MAX_EVENT_SIZE_BYTES:
        print(f"Dropping event of size {len(event_json)} bytes: '{event_json[:32]}...'")
        return

    print(event_json)


def is_dagster_event(msg: str) -> bool:
    """Check whether the message represent a Dagster event"""
    return msg.startswith("""{"event":""")


def deserialize_dagster_event(msg: str) -> DagsterEvent:
    """Deserialize a Dagster event serialized as pickle string in a JSON object"""
    payload = json.loads(msg)
    event = pickle.loads(base64.b64decode(payload["event"].encode("ascii")))

    if not isinstance(event, DagsterEvent):
        raise RuntimeError(f"Event {event} was not a Dagster event")

    return event
