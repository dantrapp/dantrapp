## Open-source contributions

**Netflix · VMAF**

Added an AArch64 NEON implementation of ADM scale-zero decoupling. On Apple M4, the full v1.0.16 3d0h model ran 5.4–7.5% faster across 1, 2, 4, and 8 threads on the PR's repeated 1080p fixture. All 8,280 feature and score comparisons matched exactly.

[Pull request #1656](https://github.com/Netflix/vmaf/pull/1656) · [Merged commit](https://github.com/Netflix/vmaf/commit/9e48141bd1eb8d2329e09d3744e7c24af53017ca)

Fused SpEED filtering and downsampling to skip discarded samples, and added an AArch64 NEON covariance kernel. On Apple M4, the PR's repeated 1080p clips ran 8.30–8.65× faster for SpEED and 1.76× faster for VMAF with the v1.0.16 3d0h model. Compared outputs were bit-for-bit identical.

[Pull request #1653](https://github.com/Netflix/vmaf/pull/1653) · [Merged commit](https://github.com/Netflix/vmaf/commit/cea2b4d832a105116a3f16f56d6f5d953421952c)

**Meta · Pyrefly**

Fixed workspace symbol search to include instance attributes defined inside methods, with regression tests.

[Pull request #4897](https://github.com/facebook/pyrefly/pull/4897) · [Accepted commit](https://github.com/facebook/pyrefly/commit/4bd953d9adcbaf7e6610d415078848a5fbdfd739)
