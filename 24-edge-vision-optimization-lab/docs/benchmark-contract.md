# Benchmark contract

- Benchmark one environment at a time; never merge machines into one comparison.
- Record CPU identity, architecture, OS, Python/runtime, provider, threads and power mode.
- Record batch, input shape, dtype, warmup and measured iterations.
- Report raw samples plus p50, p90, p95, mean and throughput.
- Synchronize asynchronous runtimes before stopping a timer.
- Recalculate quality for every artifact.
- Energy is `NOT_MEASURED` unless a trustworthy meter exists.
- `edge_proxy` means CPU constrained configuration, not physical edge hardware.

The included measurements execute NumPy qualification adapters on the current host. They
validate the harness and product flow, not MobileNetV3 or ONNX Runtime performance.
