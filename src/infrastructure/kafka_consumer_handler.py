import logging
import uuid
from typing import Dict
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import OperationalError, IntegrityError
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception_type
from src.exceptions import BadValueError, BaseTempError
from src.schemas import IncomingEnrichPayload
from src.db import new_session
from src.shares.models import UserSharesMessages
from src.shares.repository import UserSharesRepository
from src.shares.use_cases import CreateUserInfoUseCase


logger = logging.getLogger('consumer.kafka_consumer_handler')

class KafkaConsumerHandler:

    @retry(
        stop=stop_after_attempt(max_attempt_number=3),
        wait=wait_exponential_jitter(initial=1, max=5),
        retry=retry_if_exception_type((OperationalError, BaseTempError)),
        reraise=True
    )
    async def process_one_message(self, payload: Dict, partition: int, offset: int) -> None:
        try:
            valid_payload = IncomingEnrichPayload.model_validate(payload)

        except ValidationError as valid_error:
            logger.error(f"Невалидный payload из Кафки: {valid_error}")
            raise BadValueError(field_name="Kafka_Payload")

        message_id = str(valid_payload.event_id)
        username = valid_payload.username
        email = valid_payload.email
        shares_broker = valid_payload.shares_broker

        async with new_session() as session:
            query = (
                select(UserSharesMessages)
                .where(UserSharesMessages.message_id == message_id)
            )
            result = await session.execute(query)
            processed_msg = result.scalar_one_or_none()

            if processed_msg:
                logger.warning(f"Сообщение с id={message_id} уже было обработано. Партиция - {partition}, оффсет - {offset}")
                return

            use_case = CreateUserInfoUseCase(repo=UserSharesRepository(session=session))
            await use_case.create_user_commission(username=username, email=email, shares_broker=shares_broker)

            session.add(UserSharesMessages(message_id=uuid.UUID(message_id)))

            try:
                await session.commit()
                logger.info(f"Сообщение с id={message_id} успешно обработано. Партиция - {partition}, оффсет - {offset}")

            except IntegrityError:
                await session.rollback()
                logger.warning(f"Сообщение с id={message_id} только что уже было обработано")
                return