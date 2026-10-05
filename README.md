## Open-source contributions

**Netflix · VMAF**

Three merged performance PRs removed redundant SpEED filtering and added AArch64 NEON kernels for covariance, ADM decoupling, wavelet transforms, and contrast masking. Together, they delivered **2.10–2.73× full-model throughput (52–63% less elapsed time)** across 1, 2, 4, and 8 threads in an Apple M4 benchmark of the VMAF v1.0.16 3d0h model on repeated 1080p content.

Across the three PRs, **24,443 feature and score comparisons matched exactly**, covering real SD/HD clips, synthetic 8/10/12/16-bit inputs, multiple model configurations, and thread counts.

Merged PRs: [#1653](https://github.com/Netflix/vmaf/pull/1653) · [#1656](https://github.com/Netflix/vmaf/pull/1656) · [#1664](https://github.com/Netflix/vmaf/pull/1664)

<details>
<summary>Combined benchmark: measurements and scope</summary>

Direct comparison of the source before all three changes with the source containing all three.

| Threads | Before | After | Throughput |
|---|---:|---:|---:|
| 1 | 3.394 s | 1.482 s | 2.29× |
| 2 | 1.920 s | 0.765 s | 2.51× |
| 4 | 1.478 s | 0.542 s | 2.73× |
| 8 | 0.898 s | 0.428 s | 2.10× |

Measured October 5, 2026, on Apple M4, macOS 15.6.1, Apple Clang 17, Meson release builds. Medians of seven timed runs per build after warmup, alternating build order. The upstream five-frame 1920×1080 YUV420p8 reference/distorted pair was repeated twenty times to produce 100 frames. Timings include process startup, file reads, feature extraction, prediction, and JSON output; they exclude video decoding. Filesystem cache was warm. This is one repeated sequence on one machine; background load was not controlled, and individual runs varied.

Baseline: `8e7a1ac4eb835a274fb32b2851e6db719fd10c7f`. Candidate: `dd22bc4077128362a260a469bbea86f4ce173ed6`. The revisions differ only by the three PRs. The candidate's final ADM patch has the same stable Git patch ID as the changes merged into Netflix's `b41d2340a881c69682efb08fbffd0856485c57b9`.

All reported JSON feature and score outputs matched in this combined benchmark. The 24,443 exact comparisons above come from the separate PR validation runs: 3,743 + 8,280 + 12,420.

[Raw timings and fixture hashes](benchmarks/vmaf-2026-10-05/results.json) · [Reproduction script and build instructions](benchmarks/vmaf-2026-10-05/benchmark.py)

</details>

**AuthZed · SpiceDB**

Reduced p95 `LookupSubjects` latency from **88.7 ms to 11.4 ms (87% lower)** and server allocation per lookup from **111.5 MB to 3.6 MB (97% lower)** in a PostgreSQL-backed Apple M4 benchmark with 5,000 wildcard exclusions and concurrent writes. Replaced repeated copying of growing exclusion lists with batched subtraction, reducing exclusion construction from quadratic to linear work while preserving conditional permissions and resource provenance.

Measurements are medians across three runs of 60 requests at 10 requests/second on synthetic graphs, with dispatch caches enabled. Allocation includes concurrent writes and background work. Cached-snapshot and concrete-subject controls showed no consistent latency change. All 96 fixture documents returned the exact expected subjects.

[Pull request #3395](https://github.com/authzed/spicedb/pull/3395) · [Merged commit](https://github.com/authzed/spicedb/commit/983ff476ad80c7bc3c44866c1c80b882a1bc8cbf) · [Benchmarks and reproduction](https://github.com/dantrapp/spicedb/tree/5c887488c5aae616a22204541b96a28487617e9d/benchmark-results/wildcard-lookup)

**Meta · Pyrefly**

Fixed workspace symbol search to include instance attributes defined inside methods, with regression tests.

[Pull request #4897](https://github.com/facebook/pyrefly/pull/4897) · [Accepted commit](https://github.com/facebook/pyrefly/commit/4bd953d9adcbaf7e6610d415078848a5fbdfd739)
