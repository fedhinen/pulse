import asyncio
from aio_pika import DeliveryMode, Message, connect_robust
from aio_pika.pool import Pool
import json
from typing import Any, Dict


class Worker:
    def __init__(self, url: str):
        self.url = url
        self.connection = None
        self.channel_pool = None
        self._connect_lock = asyncio.Lock()

    async def connect(self):
        if self.connection and not self.connection.is_closed:
            return

        async with self._connect_lock:
            if self.connection and not self.connection.is_closed:
                return

            print("Establishing connection to message broker...")
            self.connection = await connect_robust(self.url)

            async def get_channel():
                if self.connection is None:
                    raise Exception("Connection not established")

                return await self.connection.channel()

            self.channel_pool = Pool(get_channel, max_size=10)

    async def close(self):
        if self.channel_pool:
            await self.channel_pool.close()
        if self.connection:
            await self.connection.close()

    async def worker(self):
        if self.connection is None:
            raise Exception("Connection not established")

        return await self.connection.channel()

    async def publish(self, message: Dict[str, Any], key: str):
        if self.channel_pool is None or self.connection is None or self.connection.is_closed:
            await self.connect()

        if self.channel_pool is None:
            raise Exception("Channel pool not established")

        async with self.channel_pool.acquire() as channel:
            await channel.default_exchange.publish(
                Message(
                    body=json.dumps(message).encode(),
                    content_type="application/json",
                    delivery_mode=DeliveryMode.PERSISTENT,
                ),
                routing_key=key,
            )


broker = Worker("amqp://pulse:pulse@127.0.0.1")
