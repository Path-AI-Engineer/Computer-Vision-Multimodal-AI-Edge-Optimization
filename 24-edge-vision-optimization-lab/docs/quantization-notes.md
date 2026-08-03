# Quantization notes

Static PTQ calibration uses train samples only. ONNX preprocessing, calibration reader,
activation/weight dtypes and excluded nodes must be versioned. INT8 is accepted only after
quality, parity and benchmark evidence; reduced size does not guarantee faster kernels or
lower peak memory. QAT remains NOT_RUN until the MobileNet research baseline is qualified.
