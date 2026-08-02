# Field contract

The release extracts exactly four fields:

| Field | Candidate signal | Normalized form |
|---|---|---|
| `company` | first eligible text line in the top region | title-cased text |
| `date` | supported date pattern | ISO `YYYY-MM-DD` |
| `address` | top-region address vocabulary | compact title-cased text |
| `total` | total label plus currency amount | decimal with two places |

Every field resource keeps raw value, normalized value, confidence, review flag, reason
codes, token IDs and boxes. Ground truth is not read during extraction. A normalization
failure or confidence below `0.82` requires review.

Operator edits are a separate export map. They do not change the extraction record and are
explicitly marked as non-predictions.
