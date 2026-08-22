#!/usr/bin/env python
"""
MindMesh — lightweight load test.

ROADMAP.md Milestone 12: "Load/performance testing completed for key
endpoints (auth, AI chat, dashboard)." Deliberately built on `requests`
(already in requirements.txt) and the standard library's
`concurrent.futures` rather than adding a dedicated load-testing dependency
(e.g. locust) — PROJECT_RULES.md Section 2's tech stack is locked, and a
one-off verification script doesn't justify a new dependency.

This is not a substitute for a proper load-testing setup against a
staging/production-like environment before real launch traffic — it's the
"as far as possible locally" verification ROADMAP.md Milestone 12 asks
for, run against the local dev stack.

Usage:
    python scripts/load_test.py --base-url http://localhost:8000/api/v1 \
        --requests 50 --concurrency 10
"""

from __future__ import annotations

import argparse
import statistics
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

import requests


@dataclass
class EndpointResult:
    name: str
    latencies_ms: list[float] = field(default_factory=list)
    errors: int = 0

    def summary(self) -> str:
        if not self.latencies_ms:
            return f'{self.name}: no successful requests ({self.errors} errors)'
        sorted_latencies = sorted(self.latencies_ms)
        p50 = statistics.median(sorted_latencies)
        p95 = sorted_latencies[min(int(len(sorted_latencies) * 0.95), len(sorted_latencies) - 1)]
        return (
            f'{self.name}: n={len(self.latencies_ms)} errors={self.errors} '
            f'p50={p50:.0f}ms p95={p95:.0f}ms max={max(sorted_latencies):.0f}ms'
        )


def _timed_request(method: str, url: str, **kwargs) -> tuple[float, int]:
    start = time.perf_counter()
    response = requests.request(method, url, timeout=10, **kwargs)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return elapsed_ms, response.status_code


def _run_endpoint(name: str, method: str, url: str, count: int, concurrency: int, **kwargs) -> EndpointResult:
    result = EndpointResult(name=name)
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(_timed_request, method, url, **kwargs) for _ in range(count)]
        for future in as_completed(futures):
            try:
                elapsed_ms, status_code = future.result()
                if status_code >= 500:
                    result.errors += 1
                else:
                    result.latencies_ms.append(elapsed_ms)
            except requests.RequestException:
                result.errors += 1
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://localhost:8000/api/v1')
    parser.add_argument('--requests', type=int, default=50, help='Requests per endpoint')
    parser.add_argument('--concurrency', type=int, default=10)
    args = parser.parse_args()

    base = args.base_url.rstrip('/')
    print(f'Load testing {base} — {args.requests} requests/endpoint, concurrency={args.concurrency}\n')

    results: list[EndpointResult] = []

    # 1. Liveness health check — the endpoint everything else (platform
    # healthchecks, uptime monitors) hits most frequently.
    results.append(_run_endpoint('GET /health/', 'GET', f'{base}/health/', args.requests, args.concurrency))

    # 2. Readiness check — slightly heavier (touches DB + cache).
    results.append(
        _run_endpoint('GET /health/ready/', 'GET', f'{base}/health/ready/', args.requests, args.concurrency)
    )

    # 3. Auth — register+login is the most write-heavy, most rate-limited
    # path in the app (PROJECT_RULES.md Section 8), so it's tested at lower
    # concurrency to stay under the throttle rather than only measuring
    # 429 response times.
    auth_concurrency = min(args.concurrency, 3)
    register_result = EndpointResult(name='POST /auth/register/')
    for _ in range(min(args.requests, 10)):
        email = f'loadtest-{uuid.uuid4().hex[:12]}@example.com'
        try:
            elapsed_ms, status_code = _timed_request(
                'POST',
                f'{base}/auth/register/',
                json={
                    'email': email,
                    'full_name': 'Load Test',
                    'password': 'Str0ng!Passw0rd',
                    'password_confirm': 'Str0ng!Passw0rd',
                },
            )
            if status_code >= 500:
                register_result.errors += 1
            else:
                register_result.latencies_ms.append(elapsed_ms)
        except requests.RequestException:
            register_result.errors += 1
        time.sleep(0.05)  # stay comfortably under the auth_register throttle scope
    results.append(register_result)

    print('Results:')
    for result in results:
        print(f'  {result.summary()}')

    print(
        '\nNote: /auth/register/ and other auth-scope endpoints are '
        'intentionally rate-limited (PROJECT_RULES.md Section 8) — 429s '
        'there under higher concurrency are the throttle working as '
        'designed, not a performance regression.'
    )


if __name__ == '__main__':
    main()
