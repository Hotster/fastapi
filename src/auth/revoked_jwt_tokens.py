from abc import ABC, abstractmethod

from redis.asyncio import Redis

from auth.utils import REFRESH_TOKEN_EXPIRE_MINUTES


class JWTTokenRevocationStorage(ABC):
    @abstractmethod
    async def add_revoked_token(self, token_id: str) -> None:
        pass

    @abstractmethod
    async def is_token_revoked(self, token_id: str) -> bool:
        pass


class JWTTokenRevocationService:
    def __init__(self, token_revocation: JWTTokenRevocationStorage):
        self.token_revocation = token_revocation

    async def add_revoked_token(self, token_id: str):
        await self.token_revocation.add_revoked_token(token_id)

    async def is_token_revoked(self, token_id: str):
        return await self.token_revocation.is_token_revoked(token_id)


class RedisJWTTokenRevocationStorage(JWTTokenRevocationStorage):
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def add_revoked_token(self, token_id: str) -> None:
        await self.redis_client.sadd('revoked_tokens', token_id)
        await self.redis_client.expire(f'revoked_tokens:{token_id}',
                                       REFRESH_TOKEN_EXPIRE_MINUTES)

    async def is_token_revoked(self, token_id: str) -> bool:
        return await self.redis_client.sismember('revoked_tokens', token_id)


class RedisJWTTokenRevocationService(JWTTokenRevocationService):
    def __init__(self, redis_client: Redis):
        super().__init__(RedisJWTTokenRevocationStorage(redis_client=redis_client))
