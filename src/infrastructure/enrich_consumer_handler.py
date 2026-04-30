import logging
import uuid
from typing import Dict
from sqlalchemy import select
from tenacity import retry, stop_after_attempt, wait_exponential_jitter
from src.exceptions import BadValueError
from src.db import new_session
from src.shares.models import UserSharesMessages
from src.shares.repository import UserSharesRepository
from src.shares.use_cases import CreateUserInfoUseCase


logger = logging.getLogger('consumer.enrich_consumer_handler')

class EnrichConsumerHandler:

    @retry(
        stop=stop_after_attempt(max_attempt_number=3),
        wait=wait_exponential_jitter(initial=1, max=5),
        reraise=True
    )
    async def process_one_message(self, payload: Dict) -> None:
        if not isinstance(payload, dict):
            raise BadValueError(field_name="Payload")

        required_fields = ['event_id', 'username', 'email', 'shares_broker']
        for field in required_fields:
            if field not in payload.keys() or not isinstance(payload[field], str):
                raise BadValueError(field_name=f"Payload_{field}")

        message_id = payload.get('event_id')
        username = payload.get('username')
        email = payload.get('email')
        shares_broker = payload.get('shares_broker')

        async with new_session() as session:
            query = (
                select(UserSharesMessages)
                .where(UserSharesMessages.message_id == message_id)
            )
            result = await session.execute(query)
            processed_msg = result.scalar_one_or_none()

            if processed_msg:
                logger.warning(f"Сообщение с id={message_id} уже было обработано")
                return

            use_case = CreateUserInfoUseCase(repo=UserSharesRepository(session=session))
            await use_case.create_user_commission(username=username, email=email, shares_broker=shares_broker)

            session.add(UserSharesMessages(message_id=uuid.UUID(message_id)))
            await session.commit()
            logger.info(f"Сообщение с id={message_id} успешно обработано ")