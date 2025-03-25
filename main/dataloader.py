import logging

from packages.shared.sql import database, models, schemas
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


def adapt_logger(logger, request_id: int):
    return schemas.RequestAdapter(logger, {"id": request_id})


def post_trip(trip: schemas.TripBase, request_id: int):
    logger = adapt_logger(LOGGER, request_id=request_id)
    logger.info("Received request")

    with Session(database.engine) as session:
        journey_dbs = []
        for journey in trip.journey_1, trip.journey_2:
            if journey is None:
                continue

            flights = journey.flights
            journey_dict = journey.dict()
            journey_dict.pop("flights")

            journey_db = database.get_or_add(session, models.Journey, **journey_dict)

            if flights is not None:
                flight_dbs = [
                    database.get_or_add(session, models.Flight, **flight.dict())
                    for flight in flights
                ]

                post_journey_flight(
                    journey_id=journey_db.id, flight_dbs=flight_dbs, session=session
                )

            journey_dbs.append(journey_db)

        post_request_journey(
            request_id=request_id,
            journey_dbs=journey_dbs,
            price=trip.price,
            session=session,
        )

    logger.info("Trip posted to database")
    return journey_dbs


def post_journey():
    pass


def post_flight():
    pass


def post_journey_flight(
    journey_id: int, flight_dbs: list[models.Flight], session: Session
):
    for flight_db in flight_dbs:
        association_schema = schemas.JourneyFlightCreate(
            journey_id=journey_id,
            flight_id=flight_db.id,
        )
        _ = database.get_or_add(
            session, models.JourneyFlight, **association_schema.dict()
        )


def post_request_journey(
    request_id: int, journey_dbs: list[models.Journey], price, session: Session
) -> models.RequestJourney:
    journey_id_1 = journey_dbs[0].id
    journey_id_2 = journey_dbs[1].id if len(journey_dbs) > 1 else None

    # Filter by unique columns
    association = (
        session.query(models.RequestJourney)
        .filter_by(
            request_id=request_id, journey_id_1=journey_id_1, journey_id_2=journey_id_2
        )
        .first()
    )

    if association:
        # Updating price if record exists
        association.price = price
    else:
        # Else create new record
        association_schema = schemas.RequestJourneyCreate(
            request_id=request_id,
            journey_id_1=journey_id_1,
            journey_id_2=journey_id_2,
            price=price,
        )
        association = models.RequestJourney(**association_schema.dict())
        session.add(association)

    session.commit()
    session.refresh(association)
    return association
