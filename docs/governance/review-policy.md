# Review Policy — Wikimedica

**Document version:** 1.0
**Owner:** AT Medical Digital Solutions — Editorial Board
**Last updated:** 2025-01-01

---

## 1. Purpose

This document defines the mandatory peer review requirements, reviewer qualifications, turnaround standards, escalation procedures, and retraction processes for all Wikimedica content.

---

## 2. Mandatory Peer Review

All articles submitted to Wikimedica — regardless of type (professional, patient, consent module, discharge module) — **must** undergo at least one peer review before publication. There are no exceptions.

### Minimum Review Requirements by Article Type

| Article Type | Minimum Reviewers | Medical Advisor Required |
|---|---|---|
| Professional (standard) | 1 specialty reviewer | No |
| Professional (high-risk: drug dosing, emergency, oncology) | 1 specialty reviewer + 1 Medical Advisor | Yes |
| Patient Article | 1 specialty reviewer | No |
| Consent Module | 1 specialty reviewer + 1 medical/legal reviewer | Recommended |
| Discharge Module | 1 specialty reviewer | No |
| Pharmaka | 1 pharmacist reviewer + 1 specialty physician reviewer | Recommended |
| Therapy Protocol | 1 specialty reviewer + 1 Medical Advisor | Yes |

### Self-Review Prohibition

An author may **not** serve as the sole reviewer for their own article or for any article where they have a declared conflict of interest (see editorial governance document).

---

## 3. Specialty Reviewer Requirements

Reviewers must declare their specialty qualifications at onboarding (see `docs/authors/author-onboarding-model.md`). Review assignments are restricted to declared specialties.

A reviewer is considered **specialty-qualified** for a given article if:

1. They hold a board certification (Facharzt) or equivalent academic qualification in the relevant specialty, **or**
2. They hold a senior academic position (Oberarzt, Habilitation, or equivalent) in the specialty area, **or**
3. For cross-specialty articles (e.g., Gender-Medizin, Palliativmedizin): they hold qualification in at least one contributing specialty AND have documented experience in the cross-specialty area.

---

## 4. Turnaround Times

### Standard Targets

| Priority Level | Trigger | Target Turnaround |
|---|---|---|
| Standard | Normal new article or update | 14 calendar days |
| Elevated | New or updated guideline (AWMF/ESC/etc.) triggers content revision | 7 calendar days |
| Urgent | Patient safety concern identified | 48 hours |
| Emergency | Active safety recall / drug warning | 24 hours |

### Escalation on Timeout

If a review has not been completed within the target turnaround:

1. **Day +3 past deadline**: Automated GitHub comment on the PR notifying the assigned reviewer.
2. **Day +5 past deadline**: Editor notified via email; reviewer may be re-assigned.
3. **Day +7 past deadline**: Editor may assign a substitute reviewer and log the delay.

For **urgent and emergency** reviews: escalation to the Medical Director occurs at hour 24 (urgent) or hour 12 (emergency) if no reviewer has engaged.

---

## 5. Escalation Paths

### Clinical Uncertainty

If a reviewer identifies a clinical question that cannot be resolved with available evidence, they must:

1. Flag the specific question in the PR review comments.
2. Set article status to `in-review` (not approve).
3. Tag the relevant Medical Advisor in the PR.

The Medical Advisor has authority to:
- Resolve the question and approve.
- Request additional evidence.
- Recommend the article not be published in its current form.

### Disagreement Between Reviewers

If two reviewers disagree on a clinical point:

1. Both positions are documented in the PR comments.
2. The Editor escalates to the Medical Director.
3. The Medical Director's decision is final and documented in the PR.

### Urgent Patient Safety Concerns

If any reviewer or editor identifies a published article that may present a patient safety risk:

1. The article is immediately flagged in frontmatter with `safety_hold: true`.
2. The Editor notifies the Medical Director within 4 hours.
3. The Medical Director decides within 24 hours whether to retract, restrict access, or add a safety notice.
4. If retracted: see Section 8 (Retraction Process).

---

## 6. Appeal Process

### Author Appeal

An author who disagrees with a rejection decision may appeal by:

1. Submitting a written appeal to the Editorial Board (editorial@wikimedica.de) within **14 days** of the rejection notification.
2. Clearly stating the grounds for appeal and providing supporting evidence.

The Editorial Board will review the appeal within **21 days** and issue a final decision. The Medical Director may be consulted for clinical appeals.

### Reviewer Appeal

A reviewer who believes a decision was made improperly (e.g., their review was overridden without justification) may raise the matter with the Medical Director within **14 days**.

---

## 7. Stale Content Policy

Articles are considered **stale** when:

- They have not been reviewed within **12 months** of their `updated` date, **or**
- A guideline referenced in the article has been superseded, **or**
- A PubMed surveillance alert of **high relevance** has been logged against the article topic and not actioned within **30 days**.

### Stale Content Process

1. **Automated detection**: `scripts/review/generate-review-report.py` flags stale articles monthly.
2. **GitHub Issue created**: An issue is opened with label `stale-content` and assigned to the article's original author.
3. **Author response**: The author must either update the article or confirm it remains current within **30 days**.
4. **No response**: The Editor assigns a new reviewer; article is flagged as `needs-update` in frontmatter.
5. **Unresolvable staleness**: Article is archived with a notice explaining the circumstances.

---

## 8. Retraction Process

Retraction is a serious editorial action reserved for articles where:

- Clinically significant factual errors were published.
- A conflict of interest was concealed by the author.
- The content presents a patient safety risk that cannot be corrected in place.
- Plagiarism or copyright violation is confirmed.

### Steps

1. **Decision**: Medical Director issues written retraction order.
2. **Immediate action**: Article `status` is set to `retracted`; a retraction notice is added to the frontmatter.
3. **MediaWiki**: The page is replaced with a retraction notice that explains the reason without identifying patients or confidential information.
4. **Archive**: The original content is archived in a branch (not deleted) for audit purposes.
5. **Notification**: Authors and reviewers of the retracted article are notified in writing.
6. **Public notice**: A retraction notice is published on the Wikimedica editorial blog (future).
7. **Registry**: The retraction is logged in the internal editorial registry (Nextcloud).

Retracted articles are **never** republished without a complete re-authoring and full review cycle.
