"""isort:skip_file"""

# start_asset_marker
import csv
import requests
from dagster import asset


@asset
def cereals():
    response = requests.get("https://docs.dagster.io/assets/cereal.csv")
    lines = response.text.split("\n")
    cereal_rows = [row for row in csv.DictReader(lines)]

    return cereal_rows


# end_asset_marker

# start_materialize_marker
from dagster import AssetGroup

if __name__ == "__main__":
    AssetGroup.from_current_module().materialize_in_process()

# end_materialize_marker
