# Day 1: MongoDB Performance Metrics & Technical Notes

This document provides a comprehensive technical reference for the performance metrics, execution plans, profiling logs, and indexing experiments captured during Day 1 practicals.

---

## 1. Key Performance Metrics Explained

| Metric | Source Field in Explain | Technical Meaning |
| :--- | :--- | :--- |
| **Execution Time** | `executionStats.executionTimeMillis` | Total elapsed time in milliseconds for the query execution on the server engine. Fast in-memory queries on small datasets typically report `0 ms` due to sub-millisecond execution. |
| **Documents Examined** | `executionStats.totalDocsExamined` | Number of physical collection documents scanned and evaluated by the query engine during execution. |
| **Index Keys Examined** | `executionStats.totalKeysExamined` | Number of entries scanned in the B-Tree index structure. In a collection scan (`COLLSCAN`), this is always `0`. |
| **Returned Documents** | `executionStats.nReturned` | Actual number of documents matching the filter criteria and returned to the client cursor. |
| **Execution Stage** | `queryPlanner.winningPlan.stage` | The root operation stage selected by MongoDB's query optimizer (e.g., `COLLSCAN`, `FETCH`, `IXSCAN`, `SORT`). |

---

## 2. Execution Stages: COLLSCAN vs. IXSCAN

- **`COLLSCAN` (Collection Scan)**:
  - MongoDB reads every document in the collection sequentially from disk or cache.
  - Time complexity: $\mathcal{O}(N)$, where $N$ is the total document count.
  - Inefficient for selective queries on large collections, consuming unnecessary I/O, cache space, and CPU cycles.
- **`IXSCAN` (Index Scan)**:
  - MongoDB searches an ordered B-Tree index structure based on the query filter bounds.
  - Time complexity: $\mathcal{O}(\log N) + \mathcal{O}(K)$, where $K$ is the number of matching keys.
  - Highly efficient because non-matching ranges are skipped entirely.
- **`FETCH`**:
  - Retrieves full documents from storage using the Record IDs (DiskLoc / RecordId) provided by `IXSCAN`.
  - When all requested fields are contained in the index, MongoDB performs a **Covered Query** (`PROJECTION_COVERED`), completely eliminating the `FETCH` stage.
- **`SORT` (In-Memory Sort)**:
  - When no suitable index supports the sort order, MongoDB sorts documents in RAM.
  - Limited to a 100 MB memory threshold by default unless `allowDiskUse: true` is specified. An index matching the sort order avoids this stage entirely.

---

## 3. Baseline Query Execution Metrics (Before Indexing)

Baseline execution stats executed on `ecommerce.products` (Total documents = 12, default `_id_` index only):

| # | Query Pattern | Filter / Sort Specification | Matching Docs (`nReturned`) | Time (`ms`) | Docs Examined (`totalDocsExamined`) | Keys Examined (`totalKeysExamined`) | Root Stage | Input Stage |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **1** | Category Filter | `{ category: "Electronics" }` | 7 | 0 | 12 | 0 | `COLLSCAN` | *None* |
| **2** | Price Range | `{ price: { $gt: 5000 } }` | 4 | 0 | 12 | 0 | `COLLSCAN` | *None* |
| **3** | Stock Range | `{ stock: { $lt: 15 } }` | 5 | 0 | 12 | 0 | `COLLSCAN` | *None* |
| **4** | Category + Price | `{ category: "Electronics", price: { $gt: 1000 } }` | 5 | 0 | 12 | 0 | `COLLSCAN` | *None* |
| **5** | Category + Sort | `{ category: "Electronics" }`, sort: `{ price: -1 }` | 7 | 0 | 12 | 0 | `SORT` | `COLLSCAN` |

### Key Baseline Observations:
1. Every query without an index evaluated all **12 documents** (`totalDocsExamined: 12`), regardless of how few documents matched.
2. Query 5 required an in-memory `SORT` stage on top of a full collection scan (`COLLSCAN`).

---

## 4. Index Optimization Experiments

### Experiment A: Single Field Index on Category
- **Target Query**: `db.products.find({ category: "Electronics" })`
- **Created Index**: `db.products.createIndex({ category: 1 })` -> Index Name: `category_1`
- **Comparison**:
  - Before: Stage `COLLSCAN`, `totalDocsExamined: 12`, `totalKeysExamined: 0`
  - After: Stage `FETCH` (input: `IXSCAN`), `totalDocsExamined: 7`, `totalKeysExamined: 7`
- **Document Reduction Formula**:
  $$\text{Reduction (\%)} = \frac{\text{Before} - \text{After}}{\text{Before}} \times 100 = \frac{12 - 7}{12} \times 100 = \frac{5}{12} \times 100 \approx 41.67\%$$

### Experiment B: Compound Index on Category and Price
- **Target Query**: `db.products.find({ category: "Electronics", price: { $gt: 1000 } })`
- **Created Index**: `db.products.createIndex({ category: 1, price: 1 })` -> Index Name: `category_1_price_1`
- **Comparison**:
  - Baseline (No index): Stage `COLLSCAN`, `totalDocsExamined: 12`, `totalKeysExamined: 0`
  - With Single Index `{ category: 1 }`: Stage `FETCH` (input: `IXSCAN`), `totalDocsExamined: 7`, `totalKeysExamined: 7`
  - With Compound Index `{ category: 1, price: 1 }`: Stage `FETCH` (input: `IXSCAN`), `totalDocsExamined: 5`, `totalKeysExamined: 5`
- **Document Reduction Formula (Baseline vs. Compound Index)**:
  $$\text{Reduction (\%)} = \frac{12 - 5}{12} \times 100 = \frac{7}{12} \times 100 \approx 58.33\%$$

### ESR Rule (Equality, Sort, Range)
In Experiment B, the compound index `{ category: 1, price: 1 }` strictly adheres to the **ESR Rule**:
1. **Equality (`category`)**: Filters documents down to the `Electronics` partition in the B-tree.
2. **Sort**: None requested in Query 4.
3. **Range (`price: { $gt: 1000 }`)**: Traverses only the subset of the index where price exceeds 1000.
Result: Exactly 5 keys examined, exactly 5 documents fetched, 0 false-positive reads.

---

## 5. Profiling Configuration & Findings

### Profiling Commands:
```javascript
// 1. Verify profiler is initially off
db.getProfilingStatus(); // { was: 0, slowms: 100, sampleRate: 1, ok: 1 }

// 2. Enable level 1 profiler with 0ms threshold for comprehensive capture
db.setProfilingLevel(1, { slowms: 0 }); // { was: 0, slowms: 0, sampleRate: 1, ok: 1 }

// 3. Inspect operations targeting ecommerce.products
db.system.profile.find(
  { ns: "ecommerce.products" },
  { millis: 1, docsExamined: 1, keysExamined: 1, nreturned: 1, planSummary: 1, command: 1 }
).sort({ ts: -1 }).limit(5);

// 4. Disable profiling post-investigation
db.setProfilingLevel(0); // { was: 1, slowms: 0, sampleRate: 1, ok: 1 }
```

### Profiler Observations:
- In unindexed queries, `planSummary` logged `COLLSCAN`, with `docsExamined: 12` and `keysExamined: 0`.
- Even with `millis: 0`, the profiler flagged high scan ratios (`docsExamined > nreturned`).
- Disabling profiling is essential because profiling level 1 with `slowms: 0` writes every single operation to `system.profile` (a capped collection), adding write overhead in production environments.

---

## 6. Server Health Snapshot Reference

- **Host**: `LAPTOP-9H9SEP3P`
- **MongoDB Version**: `8.2.4`
- **Uptime**: `887,308 seconds` (~10.27 days continuous operation)
- **Connections**:
  - `current`: 12
  - `available`: 201,074
  - `totalCreated`: 106
  - `rejected`: 0
  - `active`: 3
- **Memory**:
  - Architecture: 64-bit
  - `resident`: 47 MB
  - `virtual`: 4488 MB
- **Global Lock Queue**: `readers: 0`, `writers: 0` (no blocking queue)
- **Active Operations**:
  - Background checkpointing (`Checkpointer`) and journaling (`JournalFlusher`) active.
  - Active client connection (`mongosh 2.1.4`) executing `db.currentOp()`.
