# Validation record

The release gate regenerates the fixed-seed qualification, verifies hashes and evidence
boundaries, checks formatting/lint, executes unit/integration/contract tests, compiles React
and validates Docker Compose.

Current evidence: 12 validation images (4 defective, 8 clean), Small U-Net Dice `0.947943`,
IoU `0.911008`, piece TP/TN/FP/FN `4/8/0/0`, OpenCV Dice `0.883013` with one false accept, and
always-clean defect recall `0.0`. A matched BCE, Dice and BCE+Dice ablation selected BCE+Dice
by macro Dice. The KSDD2 official test is `LOCKED_NOT_ACQUIRED`.

Cloud deployment and KSDD2 benchmark acceptance are not claimed until separately executed.
