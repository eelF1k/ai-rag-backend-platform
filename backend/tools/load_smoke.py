import argparse
import asyncio
import time

import httpx


async def hit_endpoint(client: httpx.AsyncClient, path: str, idx: int) -> tuple[bool, float]:
    started = time.perf_counter()
    ok = False
    try:
        if path.startswith("/api/v1/search"):
            response = await client.get(path, params={"q": f"invoice {idx}", "limit": 3})
        else:
            response = await client.get(path)
        ok = response.status_code < 500
    except Exception:
        ok = False
    elapsed = time.perf_counter() - started
    return ok, elapsed


async def main() -> None:
    parser = argparse.ArgumentParser(description="Small async load smoke test for API endpoints.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--requests", type=int, default=30)
    parser.add_argument("--concurrency", type=int, default=10)
    args = parser.parse_args()

    semaphore = asyncio.Semaphore(args.concurrency)
    endpoints = ["/api/v1/health", "/api/v1/search", "/api/v1/ready"]

    async with httpx.AsyncClient(base_url=args.base_url, timeout=10.0) as client:
        async def bounded_call(i: int):
            async with semaphore:
                path = endpoints[i % len(endpoints)]
                return await hit_endpoint(client, path, i)

        results = await asyncio.gather(*(bounded_call(i) for i in range(args.requests)))

    successes = sum(1 for ok, _ in results if ok)
    latencies = [elapsed for _, elapsed in results]
    avg_latency = (sum(latencies) / len(latencies)) if latencies else 0.0
    p95_latency = sorted(latencies)[max(0, int(len(latencies) * 0.95) - 1)] if latencies else 0.0

    print(f"Requests: {args.requests}")
    print(f"Successes: {successes}")
    print(f"Failures: {args.requests - successes}")
    print(f"Avg latency: {avg_latency:.3f}s")
    print(f"P95 latency: {p95_latency:.3f}s")


if __name__ == "__main__":
    asyncio.run(main())

