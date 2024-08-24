import pickle
from datetime import datetime
from time import sleep

from config import paths, settings
from loader.main import post_trip
from shared.utils.queue import consume


def callback(ch, method, properties, body):
    try:
        data = pickle.loads(body)
        post_trip(data["trip"], request_id=data["request"].id)

    except Exception as e:
        print(e)

        failed_path = paths.data_path / "failed"
        failed_path.mkdir(exist_ok=True)

        filename = datetime.now().strftime("%y%m%d_%H%M%S")
        with (failed_path / filename).with_suffix(".p").open("wb") as f:
            pickle.dump(data, f)

        sleep(1)

    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":
    consume(queue=settings.flight_loader_queue, callback=callback)
