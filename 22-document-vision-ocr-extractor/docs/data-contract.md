# Data contract

## Accepted input

- One JPEG or PNG image, or one single-page PDF.
- Maximum upload size: 8 MiB by default.
- Maximum decoded image area: 8,000,000 pixels.
- Content type and file signature must agree.

PDF signatures and page count are validated, but PDF rasterization is intentionally absent
from the release candidate. A validated PDF receives an explicit capability error rather
than a fabricated extraction.

## Qualification data

`data/manifests/qualification.json` lists four generated receipt images and their sealed
annotations. They exercise two locales, four business fields, spatial evidence and a
controlled OCR error. They are repository-authored fixtures and must never be described as
SROIE or as an external benchmark.

`data/raw/` remains empty. Official SROIE data must not be committed before its terms,
integrity and official train/test split are recorded.
