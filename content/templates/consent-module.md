---
# =============================================================================
# Wikimedica — Einwilligungsbogen-Vorlage (Consent Module Template)
# =============================================================================
# Modularer Aufklärungsbogen für medizinische Eingriffe.
# Klinik-brandbar: Kliniklogo und -adresse im Kopfbereich eintragbar.
# =============================================================================

title: ""                        # (required) Titel des Aufklärungsbogens
procedure: ""                    # (required) Name des Eingriffs / der Maßnahme
specialty: ""                    # (required) Kanonisches Fachgebiet
module_type: "consent"           # (required) Festgelegt: consent

version: "1.0.0"
status: "draft"                  # draft | in-review | approved | published | archived

# Sprache
language: "de"

# Klinik-Branding (wird durch die Klinik befüllt — NICHT durch Wikimedica)
clinic_brandable: true
clinic_name: ""                  # Klinikname (durch Klinik einzutragen)
clinic_address: ""               # Klinikadresse
clinic_logo_url: ""              # URL zum Kliniklogo

# QR-Medium
qr_media_url: ""                 # URL zu Animationsvideo / Erklärungsgraphik

# Wikimedica-Metadaten (Pflichtfelder)
wikimedica_credit: true          # Pflichtfeld — darf nicht entfernt werden
licence: "CC BY-SA 4.0"

# Autorenschaft
authors:
  - name: ""
    email: ""
    specialty: ""

reviewers: []

# ICD-10 / OPS
icd10: []
ops: []

# Quellen
pubmed_ids: []
guidelines: []

# Datum
created: ""
updated: ""
next_review: ""

# KI-Nutzung
ai_assisted: false
---

<!-- =========================================================================
     KLINIK-BRIEFKOPF (durch Klinik auszufüllen)
     ========================================================================= -->

| | |
|---|---|
| **Klinik:** | {{ clinic_name }} |
| **Adresse:** | {{ clinic_address }} |
| **Datum:** | _____________ |
| **Patient/in:** | _____________ |
| **Geburtsdatum:** | _____________ |
| **Aufklärender Arzt:** | _____________ |

---

# Aufklärungsbogen: {{ procedure }}

*Dieser Aufklärungsbogen informiert Sie über den geplanten Eingriff, mögliche Risiken und Alternativen. Bitte lesen Sie ihn sorgfältig durch. Sprechen Sie Fragen offen mit Ihrem Arzt an.*

---

## Einleitung

<!-- Kurze, patientenfreundliche Einführung (3–5 Sätze).
     Wer führt den Eingriff durch? Wann? In welchem Kontext?
     Warum ist dieses Gespräch wichtig?
-->

---

## Was wird durchgeführt?

<!-- Beschreibung des Eingriffs in einfacher Sprache:
     - Vorbereitung (Nüchternheit, Medikamentenpause, etc.)
     - Ablauf des Eingriffs (Schritt für Schritt, kurz und klar)
     - Dauer
     - Anästhesieverfahren (Lokal-/Regionalanästhesie/Narkose)
     Optional: QR-Code zum Erklärungsvideo
-->

---

## Warum ist der Eingriff notwendig?

<!-- Medizinische Begründung in Patientensprache:
     - Diagnose / Indikation
     - Was passiert, wenn nicht behandelt wird?
     - Nutzen des Eingriffs
-->

---

## Mögliche Risiken und Komplikationen

*Alle medizinischen Eingriffe können Risiken mit sich bringen. Ihr Arzt wird diese mit Ihnen besprechen und kann erklären, wie groß das Risiko in Ihrem individuellen Fall ist.*

### Allgemeine Risiken (bei fast allen Eingriffen möglich)

- [ ] Blutung / Nachblutung
- [ ] Infektion / Wundinfektion
- [ ] Thrombose (Blutgerinnsel) / Lungenembolie
- [ ] Allergische Reaktion (auf Medikamente, Narkosemittel, Materialien)
- [ ] Verletzung umliegender Strukturen (Blutgefäße, Nerven, Organe)
- [ ] Narbenentstehung / Wundheilungsstörung

### Eingriffsspezifische Risiken

<!-- Hier die spezifischen Risiken des Eingriffs auflisten.
     Format: - [ ] Beschreibung (Häufigkeitsangabe, falls belegt)
     Beispiel: - [ ] Stimmveränderung (ca. 1 von 200 Patienten)
-->

- [ ] <!-- Risiko 1 -->
- [ ] <!-- Risiko 2 -->
- [ ] <!-- Risiko 3 -->

### Sehr seltene, schwerwiegende Risiken

<!-- Risiken, die selten auftreten, aber schwerwiegende Folgen haben können. -->

- [ ] <!-- Seltenes schwerwiegendes Risiko -->

---

## Alternativen

<!-- Welche Behandlungsalternativen gibt es?
     - Konservative Therapie
     - Andere operative Verfahren
     - Abwarten / Beobachten
     Was sind Vor- und Nachteile der Alternativen?
-->

---

## Verhalten nach dem Eingriff

<!-- Kurze Hinweise für die unmittelbare Nachsorge.
     Details im Entlassbrief / Discharge Module.
-->

---

## Ihre Fragen

*Haben Sie noch Fragen? Ihr Arzt steht Ihnen gerne zur Verfügung.*

Meine Fragen / Notizen:

_______________________________________________________________________________

_______________________________________________________________________________

---

## Einwilligung

Ich erkläre, dass mir der Inhalt dieses Aufklärungsbogens erläutert wurde. Ich hatte Gelegenheit, Fragen zu stellen, und habe ausreichend Zeit zum Nachdenken erhalten. Ich willige in die Durchführung des oben beschriebenen Eingriffs ein.

| | |
|---|---|
| **Ort, Datum:** | _________________________ |
| **Unterschrift Patient/in:** | _________________________ |
| **Unterschrift aufklärender Arzt:** | _________________________ |
| **Unterschrift gesetzl. Vertreter (falls zutreffend):** | _________________________ |

---

<!-- =========================================================================
     WIKIMEDICA-CREDIT-FOOTER (Pflichtfeld — darf nicht entfernt werden)
     ========================================================================= -->

*Erstellt auf Basis von Wikimedica (wikimedica.de) — AT Medical Digital Solutions · Lizenz: CC BY-SA 4.0 · Version: {{ version }} · Aktualisiert: {{ updated }}*
