# Incident PERF-02: Memory Amplification & Resource Exhaustion at Scale (100k)

## 1. Executive Summary & Incident Classification
* **Incident ID:** `PERF-02-STORE-MEMORY-AMPLIFICATION`
* **Target Volume:** 100,000 charges / 95,000 shipments
* **Classification:** `PERFORMANCE_LIMIT` / `PLATFORM_LIMITATION` on reference host (12 GB RAM)
* **Gate Impact:** **Gate 9S remains OPEN** (not permanently failed, pending controlled profiling and optimization).
* **Observed Consequence:** At 50k, measured Peak RSS reached **5,802.3 MB**. When executing 100k, process memory demand exceeded available host physical RAM (11.9 GB total, ~5.6 GB free at baseline) plus 2.0 GB swap, driving the Linux kernel into swap thrashing and memory pressure (`systemd-journald: Under memory pressure, flushing caches`) resulting in an OS freeze and reboot at 17:05.

---

## 2. Causal Hypotheses (EXPLICITLY MARKED AS HYPOTHESES, NOT VERIFIED FACTS)

> [!WARNING]
> **Methodological Note:** The reboot and memory pressure logs are confirmed physical evidence of resource exhaustion. However, the precise internal stage breakdown that caused the memory spike is **currently a causal hypothesis** that must be rigorously isolated via stage-by-stage profiling (at 10k/20k/30k) rather than assumed as fact by code inspection alone.

### Hypothesis H1: Re-audit Duplication in `Store.save`
In `src/freight_audit/storage.py` (line 113):
```python
if result.engine_version != ENGINE_VERSION or canonical(audit(dataset)) != canonical(result):
    raise IntegrityError("El resultado no corresponde a estos datos y a esta versión del motor.")
```
* **Hypothesis:** Re-running `audit(dataset)` creates a second complete in-memory `AuditResult` tree while the original `result` and `dataset` remain allocated. At 100k, this might temporarily double the finding/trace object count in memory.

### Hypothesis H2: Monolithic Canonical JSON Materialization
* **Hypothesis:** `canonical(audit(dataset))`, `canonical(result)`, and `canonical(dataset)` each produce massive canonical JSON strings (estimated 250–400 MB each for 100k elements) and large intermediate dict/list representations. Having multiple serialized representations coexisting in memory may create a large ephemeral RSS multiplier.

### Hypothesis H3: Object Representation Overhead in Pydantic / Python Dataclasses
* **Hypothesis:** 100k `Charge` records, 95k `Shipment` records, and 100k `Finding` records with full calculation step trees might have an inherent baseline memory footprint in CPython/Pydantic v2 that approaches ~4–6 GB independently of serialization.

---

## 3. Blast Radius Assessment Across Pipeline

| Component / Subsystem | Blast Radius & Observed Behavior | Severity |
| :--- | :--- | :--- |
| **Engine (`audit`)** | Completed 100k charges in **29.55s** with peak RSS of **3,330.9 MB** when measured in isolation. Engine itself scales linearly. | Contained |
| **Normalization / Dataset** | In isolation, 100k dataset creation took **15.17s** with max RSS of **2,422.8 MB**. | Contained |
| **Persistence (`Store.save`)** | High memory amplification suspected when dataset, multiple results, and canonical JSON strings are held simultaneously. | **Critical Blocker for 100k** |
| **Replay (`Store.load` + `audit`)** | Expected to demand similar memory as save/load if monolithic snapshots are deserialized. | Blocked at 100k |
| **JSON Export (`canonical(run)`)** | Monolithic serialization of the entire run object. | High Memory Risk |
| **HTML Export (`html_report`)** | Stream-like HTML generator, relatively low footprint (0.19s on 50k). | Low Risk |
| **Integrity Guarantees** | **CRITICAL REQUIREMENT:** Any future fix must preserve the invariant that `Store.save(dataset, incorrect_result)` is strictly rejected. | Invariant Preserved |

---

## 4. Immediate Protocol
1. **NO RE-EXECUTION OF 100k** on this host until profiling on 10k/20k/30k isolates the exact component breakdown.
2. Complete Gate 9W (Windows Portability) on GitHub Actions without touching production code.
3. Profile stages on safe sizes (10k, 20k, 30k) measuring `RSS_before`, `RSS_peak`, and `RSS_after`.
