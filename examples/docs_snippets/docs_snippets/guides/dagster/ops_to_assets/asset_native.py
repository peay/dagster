from dagster import AssetGroup, asset, asset_dep, graph, op


@asset(non_argument_deps={"raw_items"})
def items():
    ...


@asset(non_argument_deps={"raw_users"})
def users():
    ...


@op
def build_user_item_matrix(users, items):
    ...


@asset(non_argument_deps={"recommender_model"})
def refresh_recommendations(user_item_matrix):
    ...


@asset
@graph
def recommendations(users, items):
    return refresh_recommendations(build_user_item_matrix(users, items))


@op
def send_promotional_emails(recommendations):
    ...


asset_group = AssetGroup([recommendations, users, items])


@asset_group.job
def refresh_recommendations_and_send_promotions():
    send_promotional_emails(asset_dep("recommendations"))
