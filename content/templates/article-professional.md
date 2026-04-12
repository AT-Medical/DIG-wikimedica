---
# =============================================================================
# Wikimedica — Professional Article Template
# =============================================================================
# Copy this file to content/specialties/<specialty>/<article-slug>.md
# Fill in all fields. Required fields are marked with (required).
# =============================================================================

title: ""                        # (required) Full article title in German
specialty: ""                    # (required) Exact canonical specialty name (see content/specialties/README.md)
secondary_specialties: []        # Optional: additional specialty tags
article_type: "professional"     # (required) Fixed: professional
status: "draft"                  # (required) draft | in-review | advisor-review | approved | published | archived

# Versioning
version: "0.1.0"                 # Semantic version; increment per change type

# Authorship
authors:                         # (required) At least one author
  - name: ""
    email: ""
    orcid: ""                    # Optional: ORCID identifier
    affiliation: ""

reviewers: []                    # Assigned after submission
  # - name: ""
  #   specialty: ""
  #   reviewed_date: ""

medical_advisor: ""              # Required for high-risk content; Medical Advisor name

# Dates
created: ""                      # (required) ISO 8601: YYYY-MM-DD
updated: ""                      # (required) ISO 8601: YYYY-MM-DD; update on every revision
next_review: ""                  # ISO 8601: when this article should be re-reviewed

# Classification
icd10: []                        # ICD-10-GM codes (e.g. ["I50.0", "I50.1"])
ops: []                          # OPS procedure codes if applicable

# Evidence
pubmed_ids: []                   # Supporting PubMed IDs (integers or strings)
  # - 12345678
guidelines: []                   # Referenced guidelines
  # - title: ""
  #   issuer: ""
  #   awmf_register: ""         # e.g. "019-013" (if AWMF)
  #   year: 2023
  #   url: ""

# Content metadata
language: "de"                   # ISO 639-1
language_level: "professional"   # professional | simplified | layperson
ai_assisted: false               # true if AI tools contributed substantially to the draft
safety_hold: false               # true if article is under patient safety review

# Consent / legal
wikimedica_credit: true          # Always true for published Wikimedica content
licence: "CC BY-SA 4.0"

# Optional: correction history
corrections: []
  # - date: ""
  #   description: ""
  #   version_after: ""
---

# {{ title }}

> **Fachgebiet:** {{ specialty }}
> **Status:** {{ status }} · **Version:** {{ version }} · **Zuletzt aktualisiert:** {{ updated }}

---

## Übersicht

<!-- Kurze Zusammenfassung der Erkrankung oder des Themas (3–5 Sätze).
     Enthält: Definition, klinische Relevanz, Einordnung.
     Beispiel: "Die chronische Herzinsuffizienz ist ein klinisches Syndrom..."
-->

---

## Epidemiologie

<!-- Inzidenz, Prävalenz, Geschlechterverteilung, Altersverteilung, geografische Variation.
     Quellen: Bevölkerungsstudien, Register, Bundesgesundheitssurvey, WHO-Daten.
     Geschlechtsspezifische Daten sind, wo vorhanden, anzugeben.
     Beispiel: "In Deutschland leiden ca. 1,8 Millionen Menschen an..."
-->

---

## Ätiologie und Pathophysiologie

<!-- Ursachen, Risikofaktoren, pathophysiologische Mechanismen.
     Unterabschnitte nach Ätiologietypen möglich.
     Geschlechtsunterschiede in der Pathophysiologie explizit aufführen (falls vorhanden).
     Genetische Faktoren, Umweltfaktoren, molekulare Mechanismen.
-->

---

## Klinik

<!-- Leitsymptome, klinische Zeichen, Verlaufsformen.
     Geschlechtsunterschiede in der Symptompräsentation.
     Besonderheiten im Hinblick auf Alter, Komorbiditäten.
-->

---

## Diagnostik

<!-- Diagnostischer Algorithmus:
     1. Anamnese und körperliche Untersuchung
     2. Labordiagnostik (mit Referenzwerten wo sinnvoll)
     3. Bildgebung
     4. Weitere Spezialuntersuchungen
     Leitlinienempfehlungen mit Empfehlungsgrad angeben (A/B/C, Ia/Ib etc.).
     Differenzialdiagnosen.
-->

### Anamnese

### Körperliche Untersuchung

### Labordiagnostik

### Bildgebung

### Weitere Untersuchungen

### Differenzialdiagnosen

---

## Therapie

<!-- Evidenzbasierte Therapieempfehlung:
     - Allgemeinmaßnahmen / nicht-pharmakologische Therapie
     - Pharmakotherapie (mit Dosierungsangaben und Quellen)
     - Interventionelle / operative Verfahren
     - Leitlinienkonformität angeben
     Besonderheiten bei Frauen / Männern / Älteren / Schwangeren.
-->

### Allgemeinmaßnahmen

### Pharmakotherapie

### Interventionelle Therapie

### Therapie in besonderen Situationen

---

## Verlauf und Prognose

<!-- Natürlicher Verlauf, prognostische Faktoren, Komplikationen.
     Überlebensdaten, Remissionsraten, Hospitalisierungsrisiken.
     Unterschiede nach Geschlecht, Alter, Komorbiditäten.
-->

---

## Prävention

<!-- Primärprävention (Risikofaktoren-Modifikation)
     Sekundärprävention (Früherkennung, Screening)
     Tertiärprävention (Verhinderung von Verschlechterung/Komplikationen)
     Nur wenn evidenzbasiert belegt.
-->

---

## Besondere Patientengruppen

<!-- Optional: spezifische Hinweise für Schwangere, Kinder/Jugendliche, ältere Patienten,
     Patienten mit eingeschränkter Nieren-/Leberfunktion, Immunsupprimierte.
     Nur ausfüllen wenn relevant und evidenzbasiert.
-->

---

## Literatur

<!-- Nummerierte Literaturliste.
     Format:
     [1] Nachname V. Titel. *Zeitschrift*. Jahr;Band(Heft):Seiten. PMID: XXXXXXXX.
     [2] Leitlinienorganisation. Leitlinientitel. AWMF-Reg.-Nr. XXX-XXX. Versionsjahr. URL.
-->

1. <!-- Quelle 1 -->
2. <!-- Quelle 2 -->

---

*Dieser Artikel wurde gemäß den redaktionellen Richtlinien von Wikimedica erstellt und peer-reviewed.
Wikimedica / AT Medical Digital Solutions · [wikimedica.de](https://wikimedica.de) · Lizenz: CC BY-SA 4.0*
