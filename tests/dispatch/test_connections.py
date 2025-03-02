import pytest

from httpx import HTTPConnection, exceptions


async def test_get(server, backend):
    async with HTTPConnection(origin=server.url, backend=backend) as conn:
        response = await conn.request("GET", server.url)
        await response.read()
        assert response.status_code == 200
        assert response.content == b"Hello, world!"


async def test_post(server, backend):
    async with HTTPConnection(origin=server.url, backend=backend) as conn:
        response = await conn.request("GET", server.url, data=b"Hello, world!")
        assert response.status_code == 200


async def test_premature_close(server, backend):
    with pytest.raises(exceptions.ConnectionClosed):
        async with HTTPConnection(origin=server.url, backend=backend) as conn:
            response = await conn.request(
                "GET", server.url.copy_with(path="/premature_close")
            )
            await response.read()


async def test_https_get_with_ssl_defaults(https_server, ca_cert_pem_file, backend):
    """
    An HTTPS request, with default SSL configuration set on the client.
    """
    async with HTTPConnection(
        origin=https_server.url, verify=ca_cert_pem_file, backend=backend
    ) as conn:
        response = await conn.request("GET", https_server.url)
        await response.read()
        assert response.status_code == 200
        assert response.content == b"Hello, world!"


async def test_https_get_with_sll_overrides(https_server, ca_cert_pem_file, backend):
    """
    An HTTPS request, with SSL configuration set on the request.
    """
    async with HTTPConnection(origin=https_server.url, backend=backend) as conn:
        response = await conn.request("GET", https_server.url, verify=ca_cert_pem_file)
        await response.read()
        assert response.status_code == 200
        assert response.content == b"Hello, world!"
