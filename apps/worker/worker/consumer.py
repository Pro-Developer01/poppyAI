import json
import pika
from .config import settings
from .ingest import process_document

QUEUE = "ingestion"

def main():
    conn = pika.BlockingConnection(pika.URLParameters(settings.rabbitmq_url))
    ch = conn.channel()
    ch.queue_declare(queue=QUEUE, durable=True)   # broker restart pe queue bache
    ch.basic_qos(prefetch_count=1)                # ek baar mein ek job (fair dispatch)

    def on_message(channel, method, properties, body):
        job = json.loads(body)
        print(f"[worker] got job {job.get('jobId')}")
        try:
            process_document(job)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            # poison message loop avoid: abhi requeue nahi. (Phase 2/3 mein DLQ + retry)
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    ch.basic_consume(queue=QUEUE, on_message_callback=on_message)
    print("[worker] waiting for ingestion jobs...  (Ctrl+C to stop)")
    ch.start_consuming()

if __name__ == "__main__":
    main()