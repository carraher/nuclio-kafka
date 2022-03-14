import json
import os
import time
from kafka import KafkaProducer

# def init_context(context):
def handler(context, event):
    context.logger.info('mutate.handler begin')
    try:
        producer = KafkaProducer(bootstrap_servers=os.getenv('KAFKA'),
                                 value_serializer=lambda x: json.dumps(x).encode('utf-8'),api_version=(2, 2, 0))
        
        payload = json.loads(event.body)
        payload['mutate'] = 'was here'
        time.sleep(int(os.getenv('SLEEP', 3)))
        context.logger.info('mutate.handler sending: ' + str(payload))

        producer.send(os.getenv('KAFKA_TOPIC_OUT'), value=payload)
        producer.flush()
    except Exception as e:
        context.logger.error('mutate.handler Exception: ' + str(e))
        raise

    context.logger.info('mutate.handler end')

    return context.Response(body='Mutate sent message to nuclioevents topic',
                            headers={},
                            content_type='text/plain',
                            status_code=200)