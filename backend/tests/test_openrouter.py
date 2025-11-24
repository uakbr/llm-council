import asyncio

from backend import openrouter


class FakeResponse:
    def __init__(self):
        self.data = {"choices": [{"message": {"content": "ok", "reasoning_details": None}}]}

    def raise_for_status(self):
        return None

    def json(self):
        return self.data


class FakeClient:
    instances = []

    def __init__(self, timeout=None):
        self.timeout = timeout
        self.calls = []
        FakeClient.instances.append(self)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, headers=None, json=None):
        self.calls.append((url, headers, json))
        return FakeResponse()


class FakeClientFail(FakeClient):
    async def post(self, url, headers=None, json=None):
        raise RuntimeError("boom")


def test_query_models_parallel_reuses_single_client():
    original_client = openrouter.httpx.AsyncClient
    openrouter.httpx.AsyncClient = FakeClient
    try:
        results = asyncio.run(
            openrouter.query_models_parallel(
                ["model-a", "model-b"],
                [{"role": "user", "content": "hi"}],
                timeout=5.0,
            )
        )
        assert len(FakeClient.instances) == 1
        assert set(results.keys()) == {"model-a", "model-b"}
        # Each post should be recorded
        assert len(FakeClient.instances[0].calls) == 2
    finally:
        openrouter.httpx.AsyncClient = original_client
        FakeClient.instances.clear()


def test_query_model_uses_provided_client():
    client = FakeClient()

    async def run():
        return await openrouter.query_model(
            "model-a",
            [{"role": "user", "content": "test"}],
            timeout=5.0,
            client=client,
        )

    result = asyncio.run(run())
    assert result["content"] == "ok"
    assert len(client.calls) == 1


def test_query_model_uses_internal_client_and_handles_errors():
    original_client = openrouter.httpx.AsyncClient
    try:
        openrouter.httpx.AsyncClient = FakeClient
        result = asyncio.run(
            openrouter.query_model(
                "model-int",
                [{"role": "user", "content": "test"}],
                timeout=5.0,
            )
        )
        assert result["content"] == "ok"

        # Now force an error path
        openrouter.httpx.AsyncClient = FakeClientFail
        result_fail = asyncio.run(
            openrouter.query_model(
                "model-int",
                [{"role": "user", "content": "test"}],
                timeout=5.0,
            )
        )
        assert result_fail is None
    finally:
        openrouter.httpx.AsyncClient = original_client
