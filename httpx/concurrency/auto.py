import ssl
import typing

import sniffio

from ..config import PoolLimits, TimeoutConfig
from .base import (
    BaseBackgroundManager,
    BaseEvent,
    BasePoolSemaphore,
    BaseSocketStream,
    ConcurrencyBackend,
    lookup_backend,
)


class AutoBackend(ConcurrencyBackend):
    @property
    def backend(self) -> ConcurrencyBackend:
        if not hasattr(self, "_backend_implementation"):
            backend = sniffio.current_async_library()
            if backend not in ("asyncio", "trio"):
                raise RuntimeError(f"Unsupported concurrency backend {backend!r}")
            self._backend_implementation = lookup_backend(backend)
        return self._backend_implementation

    async def open_tcp_stream(
        self,
        hostname: str,
        port: int,
        ssl_context: typing.Optional[ssl.SSLContext],
        timeout: TimeoutConfig,
    ) -> BaseSocketStream:
        return await self.backend.open_tcp_stream(hostname, port, ssl_context, timeout)

    async def open_uds_stream(
        self,
        path: str,
        hostname: typing.Optional[str],
        ssl_context: typing.Optional[ssl.SSLContext],
        timeout: TimeoutConfig,
    ) -> BaseSocketStream:
        return await self.backend.open_uds_stream(path, hostname, ssl_context, timeout)

    def get_semaphore(self, limits: PoolLimits) -> BasePoolSemaphore:
        return self.backend.get_semaphore(limits)

    async def run_in_threadpool(
        self, func: typing.Callable, *args: typing.Any, **kwargs: typing.Any
    ) -> typing.Any:
        return await self.backend.run_in_threadpool(func, *args, **kwargs)

    def create_event(self) -> BaseEvent:
        return self.backend.create_event()

    def background_manager(
        self, coroutine: typing.Callable, *args: typing.Any
    ) -> BaseBackgroundManager:
        return self.backend.background_manager(coroutine, *args)
