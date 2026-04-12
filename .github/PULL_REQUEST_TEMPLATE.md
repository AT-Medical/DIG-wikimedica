# Pull Request

## Type of Change

<!-- Check all that apply -->

- [ ] 📄 New article (professional, patient, consent module, or discharge module)
- [ ] ✏️ Article update (existing content modified)
- [ ] 🏗️ Infrastructure change (Docker, Traefik, deploy scripts)
- [ ] 🤖 Automation / scripts (PubMed pipeline, validation, reporting)
- [ ] 📋 Governance / documentation (policies, guidelines, architecture docs)
- [ ] 🐛 Bug fix
- [ ] 🔧 Maintenance / dependencies

---

## Summary

<!-- Describe the changes in this PR. What does it add/change/fix? -->

---

## Specialty (for content changes)

<!-- Which Wikimedica specialty does this content belong to? -->

**Specialty:** <!-- e.g. Kardiologie | Gender-Medizin | N/A -->

---

## Related Issues

<!-- Link related GitHub Issues. Use "Closes #123" to auto-close on merge. -->

- Closes #
- Related to #

---

## Content Checklist (for article PRs)

<!-- Complete all applicable items before requesting review -->

- [ ] Article uses the correct template (`content/templates/`)
- [ ] YAML frontmatter is complete and valid (run `validate-metadata.py`)
- [ ] `specialty` field matches one of the 26 canonical specialty names
- [ ] `article_type` is set correctly
- [ ] `status` is set to `in-review` (not `draft`)
- [ ] `version` has been set or incremented
- [ ] `updated` date is today
- [ ] At least one source (PMID or guideline) is cited in frontmatter **and** in the References section
- [ ] ICD-10 codes added (if applicable)
- [ ] No TODO markers or placeholder text remain
- [ ] No copyrighted text from third-party sources (DocCheck, UpToDate, etc.)
- [ ] AI assistance declared in frontmatter (`ai_assisted: true`) if applicable
- [ ] `wikimedica_credit: true` is set
- [ ] Reviewer(s) assigned in the PR

---

## Medical Content Checklist (for article PRs)

- [ ] All clinical claims are supported by cited evidence
- [ ] Drug dosing information (if present) is cross-referenced with a pharmacological source
- [ ] Diagnostic criteria match current ICD-10/DSM-5/relevant classification
- [ ] No clinically dangerous advice or overlooked contraindications
- [ ] Guideline alignment confirmed (AWMF/ESC/other, as appropriate)
- [ ] Patient safety: no information that could directly cause patient harm if misapplied
- [ ] For patient articles: language is at B1–B2 level; jargon is explained

---

## Infrastructure / Automation Checklist (for non-content PRs)

- [ ] Changes tested locally
- [ ] No secrets or credentials committed
- [ ] `.env` files updated in `.env.example` if new env vars are added
- [ ] Documentation updated if behaviour changes

---

## Review Assignment

<!-- Tag the appropriate reviewers. For content PRs, tag the specialty editor. -->

**Reviewer(s) requested:** @

**Medical Advisor required:** <!-- Yes / No — if Yes, tag the advisor -->

---

## Screenshots / Additional Context

<!-- Optional: Add screenshots, test output, or additional context here -->
