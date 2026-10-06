#!/usr/bin/env python3
"""Summarize a JMeter CSV result file and enforce simple acceptance criteria."""

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


def percentile(values, percentage):
    ordered = sorted(values)
    index = max(0, math.ceil((percentage / 100) * len(ordered)) - 1)
    return ordered[index]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("jtl", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-error-rate", type=float, default=1.0)
    parser.add_argument("--max-p95", type=float, default=2000.0)
    return parser.parse_args()


def main():
    args = parse_args()
    grouped = defaultdict(list)

    with args.jtl.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            grouped[row["label"]].append(row)

    if not grouped:
        raise SystemExit("The JMeter result file contains no samples.")

    summary = {}
    failed = False
    for label, rows in grouped.items():
        elapsed = [int(row["elapsed"]) for row in rows]
        errors = sum(row["success"].lower() != "true" for row in rows)
        started = min(int(row["timeStamp"]) for row in rows)
        finished = max(
            int(row["timeStamp"]) + int(row["elapsed"]) for row in rows
        )
        duration_seconds = max((finished - started) / 1000, 0.001)
        error_rate = errors * 100 / len(rows)
        values = {
            "requests": len(rows),
            "average_ms": round(sum(elapsed) / len(elapsed), 2),
            "p95_ms": percentile(elapsed, 95),
            "throughput_rps": round(len(rows) / duration_seconds, 2),
            "errors": errors,
            "error_rate_percent": round(error_rate, 2),
        }
        summary[label] = values
        failed = failed or error_rate > args.max_error_rate
        failed = failed or values["p95_ms"] > args.max_p95

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if failed:
        raise SystemExit(
            "JMeter acceptance criteria failed: "
            f"error rate <= {args.max_error_rate}% and p95 <= {args.max_p95} ms."
        )


if __name__ == "__main__":
    main()
