## Open-source contributions

**Netflix · VMAF**

Fused SpEED filtering and downsampling to skip discarded samples, and added an AArch64 NEON covariance kernel. On Apple M4, the PR's repeated 1080p clips ran 8.30–8.65× faster for SpEED and 1.76× faster for VMAF with the v1.0.16 3d0h model. Compared outputs were bit-for-bit identical.

[Pull request #1653](https://github.com/Netflix/vmaf/pull/1653) · [Merged commit](https://github.com/Netflix/vmaf/commit/cea2b4d832a105116a3f16f56d6f5d953421952c)

**Meta · Pyrefly**

Fixed workspace symbol search to include instance attributes defined inside methods, with regression tests.

[Pull request #4897](https://github.com/facebook/pyrefly/pull/4897) · [Accepted commit](https://github.com/facebook/pyrefly/commit/4bd953d9adcbaf7e6610d415078848a5fbdfd739)
