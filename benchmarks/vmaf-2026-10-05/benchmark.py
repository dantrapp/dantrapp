#!/usr/bin/env python3
"""Compare release builds on the same 100-frame 1080p YUV420p8 pair.

Baseline: 8e7a1ac4eb835a274fb32b2851e6db719fd10c7f
Candidate: dd22bc4077128362a260a469bbea86f4ce173ed6
Obtain both source trees from https://github.com/dantrapp/vmaf. In each tree, run:
    meson setup build libvmaf --buildtype=release -Ddefault_library=both \
        -Denable_docs=false -Denable_checkasm=true
    ninja -C build -j2

From https://github.com/Netflix/vmaf_resource/tree/master/python/test/resource/yuv, obtain:
    src01_hrc00_1920x1080_5frames.yuv
    src01_hrc01_1920x1080_5frames.yuv
Concatenate twenty copies of each into reference.yuv and distorted.yuv.
Run this script with --baseline and --candidate pointing to those source trees,
--reference reference.yuv --distorted distorted.yuv --output runs.
The recorded fixture hashes in results.json identify the repeated inputs.
"""
import argparse
import hashlib
import json
import platform
import statistics
import subprocess
import time
from pathlib import Path


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--baseline", type=Path, required=True)
parser.add_argument("--candidate", type=Path, required=True)
parser.add_argument("--reference", type=Path, required=True)
parser.add_argument("--distorted", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
expected_bytes = 1920 * 1080 * 3 // 2 * 100
for path in (args.reference, args.distorted):
    if path.stat().st_size != expected_bytes:
        parser.error(f"Expected 100 frames of 1920x1080 YUV420p8: {path}")

report = {
    "baseline_revision": "8e7a1ac4eb835a274fb32b2851e6db719fd10c7f",
    "candidate_revision": "dd22bc4077128362a260a469bbea86f4ce173ed6",
    "platform": platform.platform(),
    "cpu": subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip(),
    "compiler": subprocess.check_output(["cc", "--version"], text=True).strip(),
    "build": "Meson release, -O3, default_library=both, enable_docs=false, enable_checkasm=true; ninja -j2",
    "method": "One warmup per build, seven timed runs per build, alternating order, sequential processes; median wall time",
    "fixture": "Upstream five-frame 1920x1080 YUV420p8 pair repeated twenty times (100 frames)",
    "reference_sha256": digest(args.reference),
    "distorted_sha256": digest(args.distorted),
    "timing_scope": "CLI startup, file reads, feature extraction, prediction for full-model cases, JSON output; warm filesystem cache; no decoding",
    "limitations": "One repeated short sequence on one Apple M4; background load not controlled; JSON comparisons use reported precision",
    "cases": [],
}
for mode, threads in [("full", n) for n in (1, 2, 4, 8)] + [("speed_chroma", 1), ("speed_temporal", 1)]:
    commands, times = {}, {"baseline": [], "candidate": []}
    for label in times:
        tree = getattr(args, label).resolve()
        command = [str(tree / "build/tools/vmaf"), "-r", str(args.reference.resolve()),
                   "-d", str(args.distorted.resolve()), "-w", "1920", "-h", "1080",
                   "-p", "420", "-b", "8", "--threads", str(threads), "--quiet",
                   "--json", "-o", str(args.output / f"{mode}-{threads}-{label}.json")]
        if mode == "full":
            command += ["-m", f"path={tree}/model/vmaf_v1.0.16/vmaf_v1.0.16_3d0h.json"]
        else:
            command += ["--no_prediction", "--feature", mode]
        commands[label] = command
    for iteration in range(8):
        for label in (list(times) if iteration % 2 == 0 else list(reversed(times))):
            start = time.perf_counter()
            subprocess.run(commands[label], capture_output=True, check=True)
            elapsed = time.perf_counter() - start
            if iteration:
                times[label].append(elapsed)
    outputs = []
    for label in times:
        result = json.loads((args.output / f"{mode}-{threads}-{label}.json").read_text())
        if len(result["frames"]) != 100:
            raise RuntimeError("Unexpected frame count")
        result.pop("fps", None)
        result.pop("version", None)
        outputs.append(result)
    if outputs[0] != outputs[1]:
        raise RuntimeError(f"Reported outputs differ: {mode}, threads={threads}")
    medians = {label: statistics.median(values) for label, values in times.items()}
    case = {"mode": mode, "threads": threads, "seconds": times,
            "median_seconds": medians, "speedup": medians["baseline"] / medians["candidate"],
            "wall_time_reduction_percent": 100 * (1 - medians["candidate"] / medians["baseline"]),
            "reported_outputs_identical": True}
    report["cases"].append(case)
    (args.output / "results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"{mode}/{threads}: {medians['baseline']:.6f}s -> {medians['candidate']:.6f}s; {case['speedup']:.3f}x", flush=True)
