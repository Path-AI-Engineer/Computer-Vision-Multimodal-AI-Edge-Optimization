# Demo script

1. Open **Overview** and state the evidence boundary: generated qualification receipts, not
   SROIE.
2. Open **Extract document**, select **Urban Pantry** and run `deskew-clahe-v1`.
3. Click each colored document region and connect it to the raw and normalized field row.
4. Highlight the low-confidence address (`R0ad`) and its review state.
5. Correct the address in the editable value. Explain that the raw prediction is unchanged.
6. Export JSON and show `predictions`, `operator_edits` and `resolved_values` separately.
7. Open **Reading order** to show line geometry and confidence.
8. Open **Evaluation** to compare oracle OCR with end-to-end extraction.
9. Open **Error gallery** and show the controlled failure, not a curated success only.
10. Close with **Model record** and the unavailable official benchmark/upload OCR boundaries.
