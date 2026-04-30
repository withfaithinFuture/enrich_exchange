import logging
import asyncio
from typing import Dict

import ujson
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from src.infrastructure.enrich_consumer_handler import EnrichConsumerHandler
from tenacity import retry, stop_after_attempt, wait_exponential_jitter


logger = logging.getLogger('consumer.kafka_consumer')

class EnrichConsumer:

    def __init__(self, servers: str, consumer_handler: EnrichConsumerHandler):
        self.main_topic = "enrich_user_shares_data"
        self.dlq_topic = "enrich_user_shares_data_dlq"
        self.consumer_handler = consumer_handler
        self.created_task: asyncio.Task | None = None

        self.consumer = AIOKafkaConsumer(
            self.main_topic,
            bootstrap_servers=servers,
            group_id='DDD_enrich_group',
            enable_auto_commit=False,
            isolation_level='read_committed'
        )

        self.dlq_producer = AIOKafkaProducer(
            bootstrap_servers=servers,
            value_serializer=self.serializer
        )


    @staticmethod
    def serializer(data: str) -> bytes:
        return ujson.dumps(data).encode('utf-8')


    @staticmethod
    def deserializer(data: bytes) -> Dict:
        return ujson.loads(data.decode('utf-8'))


    async def start(self):
        await self.consumer.start()
        await self.dlq_producer.start()
        logger.info("Consumer и DLQ-Produces из DDD-сервиса начали работу")
        self.created_task = asyncio.create_task(self.consume_message())


    async def stop(self):
        if self.created_task:
            try:
                self.created_task.cancel()
                await self.created_task

            except asyncio.CancelledError:
                logger.warning("Цикл чтения messages успешно остановлен")

        await self.consumer.stop()
        await self.dlq_producer.stop()
        logger.info("Consumer и DLQ-Produces из DDD-сервиса закончили работу")


    @retry(
        stop=stop_after_attempt(max_attempt_number=3),
        wait=wait_exponential_jitter(initial=1, max=5),
        reraise=True
    )
    async def send_dlq_messages(self, message, error_message: str):
        bytes_msg = message.value
        message_id = 'unknown_msg_id'
        payload = None

        try:
            parsed_data = self.deserializer(data=bytes_msg)
            payload = parsed_data
            message_id = parsed_data.get('event_id', message_id)

        except Exception as parsing_error:
            logger.error(f"Ошибка парсинга message: {parsing_error}")
            payload = bytes_msg.decode('utf-8', errors='replace')

        dlq_payload = {
            "event_id": message_id,
            "received_payload": payload,
            "error": error_message,
            "failed_partition": message.partition,
            "offset": message.offset
        }
        await self.dlq_producer.send_and_wait(topic=self.dlq_topic, value=dlq_payload)
        logger.info(f"Сообщение с id={message_id} успешно отправлено в DLQ")


    async def consume_message(self):
        while True:
            try:
                async for message in self.consumer:
                    try:
                        payload_dict = self.deserializer(message.value)
                        await self.consumer_handler.process_one_message(payload=payload_dict)
                        await self.consumer.commit()

                    except Exception as e:
                        logger.error(f"Ошибка парсинга или бизнес-логики: {e}. Кидаем в DLQ")
                        await self.send_dlq_messages(message=message, error_message=str(e))
                        await self.consumer.commit()

            except Exception as e:
                logger.warning(f"Перезапуск цикла коньюмера через 5 сек из-за ошибки - {e}")
                await asyncio.sleep(5)