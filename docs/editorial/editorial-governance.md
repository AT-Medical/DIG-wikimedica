# Editorial Governance — Wikimedica

**Document version:** 1.0
**Owner:** AT Medical Digital Solutions — Editorial Board
**Last updated:** 2025-01-01

---

## 1. Purpose

This document defines the editorial governance framework for Wikimedica. It describes the roles, workflows, quality standards, and policies that ensure all published content meets the highest standards of medical accuracy, patient safety, and editorial integrity.

---

## 2. Editorial Roles

### 2.1 Contributor (Author)

A **Contributor** creates initial article drafts, proposes new topics, and submits content via GitHub Pull Requests.

**Requirements:**
- Medical degree (MD, DO, or equivalent) or equivalent qualification (pharmacist, nurse practitioner, medical scientist) appropriate to the content area.
- Specialty qualification for articles classified within a clinical specialty.
- Signed author agreement and declaration of conflicts of interest.
- AT Medical contributor account (email: `firstname.lastname@wikimedica.de`).

**Permissions:**
- Create and edit articles in `content/` via PR.
- Propose new topics via GitHub Issues.
- Access Nextcloud collaboration workspace (read/write).

### 2.2 Reviewer

A **Reviewer** performs peer review of submitted articles within their declared specialty area.

**Requirements:**
- Meets all Contributor requirements.
- Minimum 3 years of post-qualification clinical or academic experience in the specialty.
- Approved by the Editorial Board.

**Permissions:**
- All Contributor permissions.
- Approve PRs in their designated specialty area (CODEOWNERS enforcement).
- Assign labels (`reviewed`, `needs-revision`) on PRs.

### 2.3 Editor

An **Editor** manages the editorial pipeline, coordinates reviewers, and has final approval authority for content readiness.

**Requirements:**
- Meets all Reviewer requirements.
- Demonstrated editorial experience (academic publishing, clinical guideline committees, or equivalent).
- Appointed by the Medical Director / AT Medical Editorial Board.

**Permissions:**
- All Reviewer permissions.
- Merge approved PRs to `main`.
- Assign and manage reviewer assignments.
- Archive or retract published content.
- Modify editorial governance documents (with Medical Director co-approval).

### 2.4 Medical Advisor

A **Medical Advisor** provides final sign-off for high-risk content categories: medication dosing, emergency protocols, oncology treatment, surgical procedures, and any content directly guiding clinical decision-making.

**Requirements:**
- Board-certified physician (Facharzt) in the relevant specialty.
- Active clinical or academic practice.
- Formal advisory agreement with AT Medical Digital Solutions.

**Permissions:**
- All Editor permissions in their specialty.
- Mandatory co-reviewer on high-risk articles (enforced via CODEOWNERS).
- Authority to place a clinical hold on any article pending safety review.

### 2.5 Medical Director

The **Medical Director** has ultimate editorial authority across the platform. Responsible for the editorial governance framework, advisor appointments, and final escalation decisions.

---

## 3. Content Workflow Stages

All content passes through the following stages, tracked via the `status` field in article frontmatter.

```
┌────────┐    ┌───────────┐    ┌──────────────────┐    ┌──────────┐    ┌───────────┐
│ draft  │───►│ in-review │───►│ advisor-review   │───►│ approved │───►│ published │
└────────┘    └───────────┘    │ (high-risk only) │    └──────────┘    └───────────┘
     ▲              │           └──────────────────┘         │
     │              │                                        │
     └──────────────┘ (revision requested)          ┌────────▼────────┐
                                                     │    archived     │
                                                     └─────────────────┘
```

### Stage Descriptions

| Stage | Status Value | Responsible | Entry Criteria | Exit Criteria |
|---|---|---|---|---|
| Drafting | `draft` | Contributor | PR opened | Author marks ready for review |
| Peer Review | `in-review` | Reviewer | PR assigned to reviewer | Reviewer approval or revision request |
| Medical Advisor Review | `advisor-review` | Medical Advisor | High-risk category flagged | Advisor sign-off |
| Approved | `approved` | Editor | All reviews passed | Editor merges PR |
| Published | `published` | Editor | Merged to main | Import to MediaWiki completed |
| Archived | `archived` | Editor | Content superseded or retracted | — |

### Review Turnaround Targets

| Priority | Target Turnaround |
|---|---|
| Standard | 14 calendar days |
| Elevated (new guideline triggers update) | 7 calendar days |
| Urgent (patient safety concern) | 48 hours |

---

## 4. Quality Standards

### 4.1 Medical Accuracy

- All clinical claims must be supported by at least one of: peer-reviewed publication (PMID), named clinical guideline (AWMF, ESC, DGK, DGN, etc.), or textbook reference with edition and page number.
- Unsupported statements, speculation, and anecdote are not permitted.
- Drug dosing information requires a secondary pharmacological reference cross-check.

### 4.2 Currency

- Articles must reflect the most current available evidence and guidelines.
- A "last reviewed" date is mandatory in frontmatter.
- Articles not reviewed within **12 months** of publication are flagged as `stale` by automated tooling.
- Articles referencing guidelines that have been superseded must be updated within **30 days** of guideline publication.

### 4.3 Language and Readability

- Professional articles: written in clear medical German, targeting a physician/healthcare professional audience.
- Patient articles: written at a maximum *Leichte Sprache* B2 level; jargon must be explained or avoided.
- No colloquialisms or ambiguous language in clinical instruction sections.

### 4.4 Structural Completeness

Professional articles must include all mandatory sections as defined in `content/templates/article-professional.md`. Patient articles must follow `content/templates/article-patient.md`. Missing mandatory sections block publication.

---

## 5. Conflict of Interest Policy

- All contributors, reviewers, and editors must declare conflicts of interest (financial relationships with pharmaceutical companies, device manufacturers, or other commercial entities) at the time of author application and update their declaration annually.
- Declarations are stored in the author registry (Nextcloud, access-controlled).
- A contributor with a declared conflict in the product or therapy covered by an article **may not serve as the sole author or sole reviewer** for that article.
- Undisclosed conflicts of interest discovered post-publication result in article retraction pending re-review.

---

## 6. Corrections Policy

### Minor Corrections

Typographical errors, formatting issues, and non-clinical corrections may be corrected by Editors without triggering a full review cycle. A `patch` version bump is applied.

### Substantive Corrections

Changes to clinical content, diagnoses, dosing, or therapeutic recommendations require a new peer review cycle. A `minor` or `major` version bump is applied depending on scope.

### Post-Publication Corrections

A correction notice is appended to the article frontmatter and displayed on the published page. The nature of the correction and the date are recorded.

---

## 7. AI Usage Policy

### Permitted Uses

- AI-assisted drafting (e.g., GPT-based tools) for initial structuring, outline generation, or language polishing.
- AI-assisted PubMed abstract screening (relevance classification in `scripts/pubmed/`).
- AI-assisted translation between languages (requires full human medical review of the translated output).

### Mandatory Declarations

- Any article where AI tools contributed substantially to the initial draft must declare this in the YAML frontmatter field `ai_assisted: true`.
- AI-generated content is **not** publishable without full human review and revision by a qualified author.
- AI tools may **not** be used to generate reference lists, PMID citations, or guideline references — these must be manually verified.

### Prohibited Uses

- Using AI to fabricate or invent clinical data, study results, or statistics.
- Using AI to generate drug dosing information without cross-checking against a pharmacological reference.
- Using AI-generated content as a substitute for peer review.
