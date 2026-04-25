import logging
import asyncio
import ujson
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sqlalchemy import select
from src.shares.repository import UserSharesRepository
from src.shares.use_cases import CreateUserInfoUseCase
from src.db.db import new_session
from src.shares.models import UserSharesMessages


logger = logging.getLogger('workers.kafka_consumer')

class EnrichConsumer:

    def __init__(self, servers: str):
        self.main_topic = "enrich_user_shares_data"
        self.dlq_topic = "enrich_user_shares_data_dlq"

        self.consumer = AIOKafkaConsumer(
            self.main_topic,
            bootstrap_servers=servers,
            group_id='DDD_enrich_group',
            enable_auto_commit=False,
            value_deserializer=self.deserializer
        )

        self.dlq_producer = AIOKafkaProducer(
            bootstrap_servers=servers,
            value_serializer=self.serializer
        )


    @staticmethod
    def serializer(data: str) -> bytes:
        return ujson.dumps(data).encode('utf-8')


    @staticmethod
    def deserializer(data: bytes) -> str:
        return ujson.loads(data.decode('utf-8'))


    async def start(self):
        await self.consumer.start()
        await self.dlq_producer.start()
        logger.info("Consumer и DLQ-Produces из DDD-сервиса начали работу")
        asyncio.create_task(self.consume_message())


    async def stop(self):
        await self.consumer.stop()
        await self.dlq_producer.stop()
        logger.info("Consumer и DLQ-Produces из DDD-сервиса закончили работу")


    async def consume_message(self):
        while True:
            try:
                async for message in self.consumer:
                    payload = message.value
                    message_id = payload.get('event_id')
                    username = payload.get('username')
                    email = payload.get('email')
                    shares_broker = payload.get('shares_broker')

                    try:
                        async with new_session() as session:
                            query = (
                                select(UserSharesMessages)
                                .where(UserSharesMessages.message_id == message_id)
                            )
                            result = await session.execute(query)
                            processed_msg = result.scalar_one_or_none()

                            if processed_msg:
                                logger.warning(f"Сообщение с id={message_id} уже было обработано")
                                continue

                            use_case = CreateUserInfoUseCase(repo=UserSharesRepository(session=session))

                            await use_case.create_user_commission(username=username, email=email, shares_broker=shares_broker)

                            session.add(UserSharesMessages(message_id=message_id))
                            await session.commit()
                            await self.consumer.commit()
                            logger.info(f"Сообщение с id={message_id} успешно обработано обработано")

                    except Exception as e:
                        logger.error(f"Ошибка бизнес-логики id={message_id}: {e}. Кидаем в DLQ")
                        dlq_payload = {
                            "event_id": message_id,
                            "received_payload": payload,
                            "error": str(e),
                            "failed_partition": message.partition,
                            "offset": message.offset
                        }

                        await self.dlq_producer.send_and_wait(topic=self.dlq_topic, value=dlq_payload)
                        await self.consumer.commit()

                        logger.info(f"Сообщение с id={message_id} успешно отправлено в DLQ")

            except Exception as e:
                logger.warning(f"Перезапуск цикла коньюмера через 5 сек из-за ошибки - {e}")
                await asyncio.sleep(5)



