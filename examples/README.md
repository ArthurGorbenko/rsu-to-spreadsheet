# Examples

This folder contains a synthetic saved sale page and generated outputs.

Files:

- `sample-sale.html`: example Morgan Stanley at Work sale page with an `H` wash-sale row
- `sample-output.csv`: CSV produced from the sample HTML
- `sample-output.xlsx`: accountant-style workbook produced from the same sample HTML

Regenerate them from the repo root with:

```bash
uv run rsu-extract extract --input examples/sample-sale.html --output examples/sample-output.csv
uv run rsu-extract extract --input examples/sample-sale.html --output examples/sample-output.xlsx
```
