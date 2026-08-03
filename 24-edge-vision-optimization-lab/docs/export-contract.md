# Export contract

An export is accepted only when model version, preprocessing version, input/output names,
shape, dtype, opset, execution provider and graph optimization level are versioned together.
ONNX checker and shape inference precede parity. Parity records maximum and mean absolute
error, top-1 agreement and individual failures. A file that exports but fails parity remains
ineligible for online inference.
