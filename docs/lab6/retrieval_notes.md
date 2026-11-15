# Lab 06 - Retrieval Notes

## 1. Configuration

- Knowledge Base: `data/kb/`
- Retrieval method: BM25
- `RETRIEVAL_MIN_SCORE`: 2.0

## 2. Required Retrieval Checks

### Thesis registration

Query: `can I register my thesis with 118 credits`

| Chunk ID | BM25 score |
|---|---:|
| H26#5.3 | 4.914 |
| H26#5.4 | 2.449 |

The top two results match the expected retrieval results.

### Irrelevant query

Query: `what is the capital of France`

Result: No results (`[]`).

This confirms that the query does not retrieve a relevant chunk.

## 3. Borrow vs. Borrowing

### Mini Search

| Query | Document ID | Score |
|---|---|---:|
| how many books can I borrow | D4 | 2 |
| borrowing books | D4 | 1 |

The Mini Search implementation uses exact token matching without stemming. Therefore, `borrow` and `borrowing` are treated as different tokens.

### BM25

| Query | Top chunk ID | Score |
|---|---|---:|
| borrow | S26#1 | 2.299 |
| borrowing | S26#1 | 2.299 |

For the current Knowledge Base and BM25 implementation, both queries return the same top chunk and score. This is an observed result and does not by itself establish that the two words are stemmed to the same token.

## 4. Additional Retrieval Experiments

### Query 1: Tuition per credit

Query: `how much is tuition per credit`

| Chunk ID | BM25 score |
|---|---:|
| F26#1 | 7.763 |
| F26#2 | 1.512 |
| F26#3 | 1.484 |

Top result: `F26#1`.

### Query 2: Lost student card

Query: `where can I replace a lost student card`

| Chunk ID | BM25 score |
|---|---:|
| S26#3 | 9.836 |

Top result: `S26#3`.

### Query 3: Missing a final exam

Query: `what should I do if I miss a final exam because I am sick`

| Chunk ID | BM25 score |
|---|---:|
| H26#7.2 | 5.620 |
| H26#8.3 | 1.789 |
| S26#1 | 1.789 |

Top result: `H26#7.2`.

## 5. Observations

- The thesis query retrieves the expected thesis registration chunks.
- The France query returns no results.
- Mini Search distinguishes `borrow` from `borrowing` because it uses exact token matching.
- BM25 returns the same top result and score for both terms in the current experiment.
- The configured retrieval minimum score is 2.0. The scores recorded above are raw BM25 scores returned by the index.
