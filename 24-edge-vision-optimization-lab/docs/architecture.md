# Architecture

Project 24 separates offline experimentation from online evidence serving.

Offline: dataset contract -> baseline protocol -> pruning/quantization/export adapters ->
quality evaluation -> paired benchmark -> parity -> Pareto report -> immutable registry.

Online: registry validation -> selected qualification predictor -> FastAPI resources -> React
console. The API never constructs an unregistered variant and the frontend never invents a
metric. Research MobileNet, ONNX and INT8 artifacts can replace qualification adapters only
after producing compatible manifests and passing the same gates.
