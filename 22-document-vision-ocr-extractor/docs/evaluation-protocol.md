# Evaluation protocol

Protocol `p22-qualification-v1` rebuilds all sample images, annotations, metrics, errors and
bundle hashes from `scripts/build_qualification_bundle.py`.

## Metrics

- OCR: character error rate, word error rate and line exact match.
- Localization: precision and recall at IoU 0.5.
- KIE: normalized field exact match and all-fields document exact match.
- Operations: review rate and mean field confidence.
- Propagation: oracle OCR field/document accuracy versus end-to-end predictions.

All four documents participate. Ground truth tokens are used only by the evaluation builder;
the live extractor reads predicted tokens. Localization is perfect by construction because
the controlled OCR error changes text, not the annotated fixture region. This result must not
be generalized to real detector boxes.

The generated report currently records 4 documents, 0.34% CER, 2.08% WER, 93.75% normalized
field exact match, 75% document exact match and 6.25% review rate. The JSON report is the
source of truth if these fixtures change.
