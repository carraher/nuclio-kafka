import json
import os
import time
from kafka import KafkaProducer

# def init_context(context):
def handler(context, event):
    context.logger.info('rest-ingest.handler begin')
    try:
        producer = KafkaProducer(bootstrap_servers=os.getenv('KAFKA'),
                                 value_serializer=lambda x: json.dumps(x).encode('utf-8'),api_version=(2, 2, 0))

        time.sleep(int(os.getenv('SLEEP', 1)))
        context.logger.info('rest-ingest.handler sending: ' + str(event.body))

        producer.send(os.getenv('KAFKA_TOPIC_OUT'), value=event.body)
        producer.flush()
    except Exception as e:
        context.logger.error('rest-ingest.handler Exception: ' + str(e))
        raise

    context.logger.info('rest-ingest.handler end')

    return context.Response(body='Ingest sent message to nuclioevents topic',
                            headers={},
                            content_type='text/plain',
                            status_code=200)