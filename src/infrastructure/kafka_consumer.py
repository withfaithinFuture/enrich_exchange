import logging
import asyncio
from typing import Dict
import ujson
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaError
from src.exceptions import BaseAppError, BaseTempError
from src.infrastructure.kafka_consumer_handler import KafkaConsumerHandler
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception
from src.settings import settings


logger = logging.getLogger('consumer.kafka_consumer')

class EnrichConsumer:

    def __init__(self, servers: str, consumer_handler: KafkaConsumerHandler):
        self.main_topic = settings.MAIN_TOPIC
        self.dlq_topic = settings.DLQ_TOPIC
        self.consumer_handler = consumer_handler
        self.created_task: asyncio.Task | None = None
        self.is_started = False
        self.lock = asyncio.Lock()

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


    @staticmethod
    def is_retryable(exc: BaseException) -> bool:
        return isinstance(exc, KafkaError) and exc.retriable


    async def start(self) -> None:
        async with self.lock:
            if self.is_started:
                logger.warning("Consumer и DLQ-Producer из DDD-сервиса уже запущены!")
                return

            await self.consumer.start()
            await self.dlq_producer.start()
            self.is_started = True
            logger.info("Consumer и DLQ-Producer из DDD-сервиса начали работу")
            self.created_task = asyncio.create_task(self.consume_message())


    async def stop(self) -> None:
        async with self.lock:
            if not self.is_started:
                logger.warning("Consumer и DLQ-Producer из DDD-сервиса уже остановлены")
                return

            if self.created_task:
                try:
                    self.created_task.cancel()
                    await self.created_task

                except asyncio.CancelledError:
                    logger.warning("Цикл чтения messages успешно остановлен")

            self.is_started = False
            await self.consumer.stop()
            await self.dlq_producer.stop()
            logger.info("Consumer и DLQ-Produces из DDD-сервиса закончили работу")


    @retry(
        stop=stop_after_attempt(max_attempt_number=3),
        wait=wait_exponential_jitter(initial=1, max=5),
        retry=retry_if_exception(is_retryable),
        reraise=True
    )
    async def send_dlq_messages(self, message, error_message: str) -> None:
        bytes_msg = message.value
        message_id = 'unknown_msg_id'
        payload = None
        deserialize_error = False

        try:
            parsed_data = self.deserializer(data=bytes_msg)
            payload = parsed_data
            message_id = parsed_data.get('event_id', message_id)

        except ValueError as parsing_error:
            logger.error(f"Ошибка парсинга message: {parsing_error}")
            payload = bytes_msg.decode('utf-8', errors='replace')
            deserialize_error = True

        dlq_payload = {
            "event_id": message_id,
            "received_payload": payload,
            "error": error_message,
            "deserialize_error": deserialize_error,
            "failed_partition": message.partition,
            "offset": message.offset
        }

        try:
            await self.dlq_producer.send_and_wait(topic=self.dlq_topic, value=dlq_payload)
            logger.info(f"Сообщение с id={message_id} успешно отправлено в DLQ")

        except Exception as dlq_error:
            logger.error(f"Не удалось отправить сообщение в DLQ - {dlq_error}")
            raise dlq_error


    async def handle_one_message(self, message) -> None:
        try:
            payload_dict = self.deserializer(message.value)
        except ValueError as parsing_error:
            logger.error(f"Ошибка парсинга в топике: {parsing_error}. Кидаем в DLQ")
            await self.send_dlq_messages(message=message, error_message=str(parsing_error))
            await self.consumer.commit()
            return

        try:
            await self.consumer_handler.process_one_message(payload=payload_dict, partition=message.partition, offset=message.offset)
            await self.consumer.commit()

        except BaseAppError as app_error:
            logger.error(f"Бизнес-ошибка - {app_error}. Кидаем в DLQ")
            await self.send_dlq_messages(message=message, error_message=str(app_error))
            await self.consumer.commit()

        except BaseTempError as infr_error:
            logger.error(f"Ошибка в инфраструктуре - {infr_error}")
            raise infr_error

        except KafkaError as kafka_error:
            if kafka_error.retriable:
                logger.warning(f"Временная ошибка кафки - {kafka_error}")
                raise kafka_error
            logger.error(f"Фатальная ошибка кафки - {kafka_error}")
            raise kafka_error


    async def consume_message(self) -> None:
        while self.is_started:
            try:
                async for message in self.consumer:

                    await self.handle_one_message(message=message)

                    if not self.is_started:
                        logger.info("Выход из цикла чтения Кафки по флагу is_started")
                        break

            except asyncio.CancelledError:
                logger.warning("Чтение консьюмера было отменено")
                break

            except Exception as e:
                if self.is_started:
                    logger.warning(f"Перезапуск цикла коньюмера через 5 сек из-за ошибки - {e}")
                    await asyncio.sleep(5)