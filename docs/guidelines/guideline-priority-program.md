# Guideline Priority Program — Wikimedica

**Document version:** 1.0
**Owner:** AT Medical Digital Solutions — Editorial Board
**Last updated:** 2025-01-01

---

## 1. Purpose

The Guideline Priority Program ensures that Wikimedica content remains aligned with current evidence-based clinical guidelines. It establishes a systematic registry of tracked guidelines, a prioritisation framework for editorial updates, and automated tooling to alert the editorial team when guidelines are due for re-review or have been updated.

---

## 2. Guideline Registry

The master guideline registry is maintained at `data/registries/guideline-registry.yaml`.

### Registry Structure

Each entry in the registry contains:

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier (e.g., `awmf-019-013`) |
| `title` | string | Full guideline title |
| `specialty` | string | Wikimedica specialty label |
| `issuer` | string | Issuing organisation (AWMF, ESC, DGK, etc.) |
| `year` | integer | Publication / last update year |
| `url` | string | Direct URL to guideline or registry entry |
| `next_review` | ISO 8601 date | Expected next update date |
| `priority` | enum | `high`, `medium`, `low` |
| `status` | enum | `current`, `under-revision`, `superseded`, `withdrawn` |
| `wikimedica_articles` | list | Article filenames referencing this guideline |

---

## 3. Monthly Review Cycle

The guideline review cycle runs on the **1st of each month**, triggered by the GitHub Actions workflow `guideline-review-reminder.yml`. The automated process:

1. Reads `data/registries/guideline-registry.yaml`.
2. Identifies guidelines where `next_review` is within **30 days** of the current date.
3. Identifies guidelines with `status: under-revision` or `status: superseded`.
4. Generates a Markdown report via `scripts/reporting/monthly-guideline-report.py`.
5. Opens a GitHub Issue with the report as the body, labelled `guideline-review`, `monthly-report`.
6. The report is assigned to the relevant specialty editor for each flagged guideline.

### Priority-Based Review Frequency

| Priority | Review Frequency | Alert Lead Time |
|---|---|---|
| High | Every 12 months | 30 days before `next_review` |
| Medium | Every 18 months | 30 days before `next_review` |
| Low | Every 24 months | 30 days before `next_review` |

---

## 4. Evidence Source Hierarchy

Wikimedica uses the following hierarchy for clinical recommendations, listed from highest to lowest priority:

### Level 1 — S3 / High-Quality Guidelines

| Source | Description |
|---|---|
| **AWMF S3 guidelines** | German-language evidence-based guidelines with systematic reviews and formal consensus process |
| **ESC Guidelines** | European Society of Cardiology; adopted by DGK for German context |
| **SIGN Guidelines** | Scottish Intercollegiate Guidelines Network |
| **NICE Guidelines** | UK National Institute for Health and Care Excellence |

### Level 2 — S2k / Consensus Guidelines

| Source | Description |
|---|---|
| **AWMF S2k guidelines** | Formal consensus without systematic review |
| **S2e guidelines** | Evidence-based without formal consensus |
| **DGHO / DGN / DGP / other Fachgesellschaft guidelines** | Specialty society recommendations |
| **WHO clinical guidelines** | Global relevance, especially for infectious disease / public health |

### Level 3 — S1 / Expert Recommendations

| Source | Description |
|---|---|
| **AWMF S1 guidelines** | Expert consensus with no formal evidence review |
| **Cochrane Reviews** | High-quality systematic reviews (used as supplementary evidence) |
| **Pivotal RCTs** | Landmark randomised controlled trials cited in major guidelines |

### Level 4 — Background Evidence

- Systematic reviews without guideline status
- Observational studies
- Expert opinion / narrative reviews
- Drug prescribing information (Fachinformation)

> **Note**: When AWMF and ESC/NICE recommendations conflict for a clinical scenario, the article must explicitly acknowledge both positions, with the German healthcare context (AWMF) presented first.

---

## 5. AT Medical Publication Impact Score (AMPIS)

The **AT Medical Publication Impact Score** is a composite metric used to prioritise which guideline updates or new publications should trigger article updates in Wikimedica. It is calculated per incoming PubMed surveillance result or guideline notification.

See `data/scoring/README.md` for the full AMPIS specification.

### AMPIS Components

| Dimension | Weight | Description |
|---|---|---|
| Clinical Relevance | 30% | How directly does this affect clinical management? |
| Evidence Quality | 25% | Study design, guideline level (S3 > S2 > S1) |
| Update Urgency | 25% | How much does this change current practice? |
| Specialty Coverage | 20% | Breadth of impact across Wikimedica specialties |

### Priority Action Thresholds

| AMPIS Score | Action |
|---|---|
| ≥ 80 | Immediate editorial alert; article update within 7 days |
| 60–79 | High-priority update; article update within 30 days |
| 40–59 | Standard queue; update in next quarterly review cycle |
| < 40 | Log for review; no immediate action required |

---

## 6. Stale Alert Thresholds

Articles referencing tracked guidelines are cross-checked monthly. An article is flagged as **stale** when:

- The referenced guideline has `next_review` in the past (overdue), **or**
- The guideline `status` has changed to `under-revision` or `superseded`, **or**
- The article's `updated` date is older than the guideline's publication year, **or**
- A new guideline version has been published since the article was last updated.

Stale articles receive the label `needs-guideline-update` in the monthly GitHub Issue report.

---

## 7. Priority Topic List per Specialty

The following topics are designated **high-priority** for guideline tracking and article coverage. This list is reviewed annually by the Editorial Board.

| Specialty | Priority Topics |
|---|---|
| Kardiologie | ACS-Management, Herzinsuffizienz, VHF, Hypertonie |
| Pneumologie | COPD-Exazerbation, Asthma, Lungenkarzinom-Screening |
| Gastroenterologie | CED (Morbus Crohn, Colitis ulcerosa), Leberzirrhose, GI-Blutung |
| Endokrinologie | Typ-2-Diabetes, Schilddrüsenkarzinom, Osteoporose |
| Infektiologie | Sepsis, COVID-19, Antibiotika-Stewardship, HIV |
| Neurologie | Schlaganfall-Akuttherapie, Multiple Sklerose, Epilepsie |
| Psychiatrie | Depression, Schizophrenie, Suizidalität |
| Onkologie | Mammakarzinom, Kolonkarzinom, Lungenkarzinom |
| Pädiatrie | Impfplan, Fieberkrämpfe, Kindliche Pneumonie |
| Gynäkologie | Zervixkarzinom-Screening, Präeklampsie, Geburtshilfe-Notfälle |
| Intensivmedizin | Beatmungsprotokoll, Sepsis-Bundles, Ernährungstherapie |
| Gender-Medizin | Geschlechtsspezifische Pharmakologie, Herzinfarkt bei Frauen, Schmerz |
| Palliativmedizin | Symptomkontrolle, Sterbefasten (VSED), Advance Care Planning |
| Notfallmedizin | Reanimation (ERC), Polytrauma, anaphylaktischer Schock |
