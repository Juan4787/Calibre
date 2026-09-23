# Blast Radius Analysis: Incident PERF-01 (XLSX Quadratic Complexity)

## 1. Description & Root Cause

In `src/freight_audit/reporting.py`, the internal `sheet(title, headings, rows)` helper function formats and appends tabular rows to openpyxl worksheets:

```python
    def sheet(title, headings, rows):
        ws = workbook.create_sheet(title=title)
        ws.append(headings)
        for values in rows:
            if ws.max_row >= MAX_XLSX_ROWS or any(len(value) > MAX_XLSX_CELL_CHARS for value in values):
                workbook.close()
                raise ReportLimitError(...)
            ws.append(values)
```

In openpyxl, `ws.max_row` is **not** a stored integer; it is a calculated property implemented as:

```python
max_row = max(self._cells)[0]
```

where `self._cells` is a dictionary holding all cells in the sheet.
Calling `ws.max_row` inside `for values in rows:` forces openpyxl to scan all coordinates in `self._cells` on **every single row iteration**.
This turns an intended $O(R)$ row appending routine into a strictly quadratic $O(R^2)$ nested loop.

Furthermore, lines 87–91 re-iterate over every cell in `ws` to set `cell.alignment` and `cell.data_type`:

```python
        for row in ws:
            for cell in row:
                if cell.value is not None:
                    cell.data_type = "s"
                cell.alignment = Alignment(vertical="top", wrap_text=True)
```

For a 10k dataset with 80k trace rows in the "Cálculos" sheet (~400k cells), pure Python cell iteration adds another substantial overhead.

## 2. Blast Radius Assessment

| Component                                | Impact                                                                                         | Severity             |
| :--------------------------------------- | :--------------------------------------------------------------------------------------------- | :------------------- |
| **Engine (`audit`)**                     | **None**. Runs in pure linear time (2.33s for 10k charges).                                    | No Impact            |
| **Storage (`Store.save`, `Store.load`)** | **None**. SQLite transactions and JSON storage complete in 6.6s and 2.5s respectively for 10k. | No Impact            |
| **Replay**                               | **None**. Identical and deterministic (2.3s for 10k).                                          | No Impact            |
| **Export JSON (`canonical`)**            | **None**. Completes in ~1.5s for 10k.                                                          | No Impact            |
| **Export HTML (`html_report`)**          | **None**. Fast string builder completes in 0.06s for 10k.                                      | No Impact            |
| **Export XLSX (`workbook_bytes`)**       | **CRITICAL**. Froze execution for > 5 minutes on 10k findings; estimated 4.4 hours on 50k.     | P1 Performance Cliff |
| **ZIP Bundle (`bundle_bytes`)**          | **CRITICAL**. Calls `workbook_bytes()` internally, causing bundle export to freeze.            | P1 Performance Cliff |

## 3. Classification

- **Classification**: `PRODUCT_BUG` / `PERFORMANCE_LIMIT`.
- **First Pass Policy**: In accordance with Rule 11 of Phase 9:
  > _"Durante la PRIMERA PASADA de cada bloque no modificar src/freight_audit/ para conseguir resultados verdes. Un fallo de producto debe: preservarse, reducirse, clasificarse, medir blast radius ANTES de cualquier corrección de producción."_

The incident is fully preserved, isolated, and documented with its reproducer script and exact timings.
