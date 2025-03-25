import json
import pickle

from packages.config import paths
from packages.dataloader.main.dataloader import post_trip
from packages.shared.sql import models, schemas
from packages.shared.sql.database import get_or_add
from tqdm import tqdm


def test_post_trip(session):
    request_folders = list(paths.test_data_path.glob("*"))
    if not request_folders:
        raise FileNotFoundError(f"No journey files found in {paths.test_data_path}")

    for folder in request_folders:
        journey_files = list(folder.rglob("parsed_*.p"))
        if not journey_files:
            raise FileNotFoundError(f"No journey files found in {folder}")

    for folder in tqdm(request_folders):
        request_file = folder / "request.json"

        with request_file.open("r") as f:
            request_dict = json.load(f)

        request_db = get_or_add(session, models.Request, **request_dict)
        request = schemas.Request(**request_db.__dict__)

        for journey in folder.rglob("parsed_*.p"):
            with journey.open("rb") as f:
                data = pickle.load(f)

            assert isinstance(data, schemas.TripBase)
            journeys = post_trip(data, request.id)

            for journey in journeys:
                assert isinstance(journey, models.Journey)
