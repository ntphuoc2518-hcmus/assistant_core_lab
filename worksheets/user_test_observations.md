# Lab 7 — Hallway Test Observations (E.3)

**Tester:** Minh (pqminh2007)  
**Date:** 2026-11-19  
**Session length:** ~2 minutes per participant  
**Method:** Unmoderated hallway test — participant thinks aloud while using the app

---

## Participants

| # | Group | Role | Device |
|---|-------|------|--------|
| 1 | H1 | Observer → tester | Desktop (Chrome) |
| 2 | H2 | Observer → tester | Mobile (Safari, iOS) |
| 3 | H3 | Observer → tester | Desktop (Firefox) |

---

## Task Given to Each Participant

> "Without any help, try to find out how many credits you need to register your thesis, then ask a question using emoji or a foreign word."

---

## Observations per Participant

### Participant 1 (H1 — Desktop Chrome)

| Step | What the user did | What we observed |
|------|-------------------|-----------------|
| 1 | Typed "Can I register thesis 118 credits" | Got a correct answer with citation `H26#5.3`. User nodded. |
| 2 | Tried example button "Tuition for 18 credits…" | Worked immediately. User said "oh nice, the buttons help." |
| 3 | Typed "What about 😊 requirements for GPA?" | App returned a valid answer. No crash. Emoji passed through correctly (E.2 ✅). |
| 4 | Clicked 👍 on the response | Feedback sent. Toast appeared. User smiled. |
| **Pain point** | Could not tell whether the app was thinking | The spinner is subtle; user clicked twice thinking it had frozen. |

**Quote:** *"The examples on the side saved me — I didn't know what to ask first."*

---

### Participant 2 (H2 — Mobile Safari iOS)

| Step | What the user did | What we observed |
|------|-------------------|-----------------|
| 1 | Typed using mobile keyboard with autocorrect | No validation error; accepted fine. |
| 2 | Typed "học phí 15 tín chỉ" (Vietnamese, E.2) | "Assistant did not understand Vietnamese and escalated to the Training Office |
| 3 | Tried to scroll back through history | Chat history scrolled normally on mobile. |
| 4 | Long-pressed a source citation | Nothing happened — user expected a link to the actual rule. |
| **Pain point** | Source citations are plain text, not clickable links. User expected tap-to-open. |

**Quote:** *"Works on phone which is good, but the sources look like random codes — 'H26#5.3' means nothing to me."*

---

### Participant 3 (H3 — Desktop Firefox)

| Step | What the user did | What we observed |
|------|-------------------|-----------------|
| 1 | Typed a very long question (>300 chars) | Input accepted; answer came back fine. |
| 2 | Typed "Can I register thesis?" with no credits number | App escalated to Training Office; user was confused about *why*. |
| 3 | Pasted a question with smart quotes `"like this"` | Processed correctly, no encoding errors (E.2 ✅). |
| 4 | Tried the 👎 button | Toast appeared. User appreciated the acknowledgment. |
| **Pain point** | When the app escalates ("contact Training Office"), there's no follow-up suggestion. |

**Quote:** *"The escalation message is a bit cold. I'd want it to tell me what I *can* ask."*

---

## Summary of Findings (H1 group perspective)

| # | Severity | Finding | Recommendation |
|---|----------|---------|----------------|
| 1 | 🔴 High | Spinner not obvious on slow connections → double-clicks | Show explicit "typing…" indicator (Bonus implemented) |
| 2 | 🟠 Medium | Source IDs like `H26#5.3` are opaque to users | Show full title prominently, ID in parentheses |
| 3 | 🟡 Low | Escalation message gives no follow-up | Add example questions to escalation note |
| 4 | 🟢 Info | Emoji & Unicode input works correctly | No action needed — maintain as a test case (E.2) |
| 5 | 🟢 Info | Mobile layout functional | No action needed |

---

## E.2 — Mobile / Emoji / Unicode Verification

Tested input types that must not crash or corrupt the backend:

| Input | Result |
|-------|--------|
| `"học phí 15 tín chỉ"` (Vietnamese) | ✅ Processed correctly |
| `"What about 😊 GPA requirements?"` | ✅ Emoji passed through; answer returned |
| `"Can I register thesis \u201ctoday\u201d?"` (smart quotes) | ✅ No encoding error |
| `"🎓📚 deadline thesis"` (multiple emoji) | ✅ Accepted, escalated gracefully |

> All E.2 test cases pass. The API correctly handles UTF-8 encoded payloads including emoji sequences and Vietnamese diacritics.

---

## Bonus Improvement Implemented

The **`typing…` indicator** was added to `ui/app.py` as a streamed placeholder message.  
The **source display** in `ui/logic.py` was improved to show the title first, with the chunk ID in parentheses.

Before:
```
Sources: H26#5.3 — 5.3 Thesis registration
```

After:
```
📄 5.3 Thesis registration (H26#5.3)
```
