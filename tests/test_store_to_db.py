from unittest.mock import patch
from src.spacextracker.services import store_to_db


def test_update_launches_in_db():
    # Mock data
    launches = [{"id": "l1", "name": "Test Launch"}]
    rockets = [{"id": "r1", "name": "Falcon 9"}]
    launchpads = [{"id": "lp1", "name": "LC-39A"}]

    with patch(
        "src.spacextracker.services.store_to_db.get_data_from_api",
        return_value=(launches, rockets, launchpads),
    ), patch(
        "src.spacextracker.services.store_to_db.launches_collection"
    ) as mock_launches_col, patch(
        "src.spacextracker.services.store_to_db.rockets_collection"
    ) as mock_rockets_col, patch(
        "src.spacextracker.services.store_to_db.launchpads_collection"
    ) as mock_lps_col:

        # Mock update_one to do nothing
        mock_launches_col.update_one.return_value = None
        mock_rockets_col.update_one.return_value = None
        mock_lps_col.update_one.return_value = None

        result = store_to_db.update_launches_in_db()

        assert result == len(launches)
        mock_launches_col.update_one.assert_called_once_with(
            {"_id": "l1"}, {"$set": launches[0]}, upsert=True
        )
        mock_rockets_col.update_one.assert_called_once_with(
            {"_id": "r1"}, {"$set": rockets[0]}, upsert=True
        )
        mock_lps_col.update_one.assert_called_once_with(
            {"_id": "lp1"}, {"$set": launchpads[0]}, upsert=True
        )


# Optional: test empty lists
def test_update_launches_in_db_empty():
    with patch(
        "src.spacextracker.services.store_to_db.get_data_from_api",
        return_value=([], [], []),
    ), patch("src.spacextracker.services.store_to_db.launches_collection"), patch(
        "src.spacextracker.services.store_to_db.rockets_collection"
    ), patch(
        "src.spacextracker.services.store_to_db.launchpads_collection"
    ):
        result = store_to_db.update_launches_in_db()
        assert result == 0
