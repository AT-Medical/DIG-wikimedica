---
# =============================================================================
# Wikimedica — Entlassbrief-Vorlage (Discharge Module Template)
# =============================================================================
# Patientenfreundliche Entlassinformationen nach medizinischem Eingriff
# oder Krankenhausaufenthalt.
# =============================================================================

title: ""                        # (required) Titel des Entlassbriefs
procedure: ""                    # Durchgeführter Eingriff / Diagnose (optional)
specialty: ""                    # (required) Kanonisches Fachgebiet
module_type: "discharge"         # (required) Festgelegt: discharge

version: "1.0.0"
status: "draft"

language: "de"

clinic_brandable: true
clinic_name: ""
clinic_address: ""
clinic_phone: ""
clinic_logo_url: ""

qr_media_url: ""                 # Optional: URL zu weiterführenden Medien

wikimedica_credit: true
licence: "CC BY-SA 4.0"

authors:
  - name: ""
    email: ""

reviewers: []

icd10: []
ops: []

created: ""
updated: ""
next_review: ""

ai_assisted: false
---

<!-- =========================================================================
     KLINIK-BRIEFKOPF (durch Klinik auszufüllen)
     ========================================================================= -->

| | |
|---|---|
| **Klinik:** | {{ clinic_name }} |
| **Adresse:** | {{ clinic_address }} |
| **Telefon:** | {{ clinic_phone }} |
| **Entlassdatum:** | _____________ |
| **Patient/in:** | _____________ |
| **Geburtsdatum:** | _____________ |

---

# Entlassinformation: {{ title }}

*Wir freuen uns, dass Sie sich gut erholt haben. Bitte lesen Sie diese Informationen sorgfältig, damit Ihre Genesung zu Hause gut verläuft. Bei Fragen wenden Sie sich jederzeit an uns.*

---

## Ihre Diagnose

<!-- Ihre Erkrankung / Ihr Befund, verständlich erklärt.
     Kurz, klar, ohne Fachjargon.
-->

**Diagnose:** _______________________________________________

---

## Was wurde bei Ihnen durchgeführt?

<!-- Kurze Beschreibung des durchgeführten Eingriffs oder der Behandlung
     in Patientensprache.
     Beispiel: "Bei Ihnen wurde eine Magenspiegelung (Gastroskopie) durchgeführt.
     Dabei wurde ein kleines Polyp entfernt, der ins Labor geschickt wurde."
-->

---

## Ihre Medikamente

*Bitte nehmen Sie alle unten aufgeführten Medikamente wie angegeben ein.*

| Medikament | Dosierung | Einnahme | Dauer | Hinweis |
|---|---|---|---|---|
| <!-- z.B. Ibuprofen 400 mg --> | | <!-- z.B. 1-0-1 --> | <!-- z.B. 5 Tage --> | <!-- z.B. mit Mahlzeit --> |
| | | | | |
| | | | | |

**Bestehende Medikamente:**

- [ ] Alle bisherigen Medikamente weiter nehmen wie gewohnt.
- [ ] Folgende Medikamente vorübergehend pausieren: ________________________
- [ ] Folgende Medikamente dauerhaft absetzen: ________________________

---

## Verhaltenshinweise

<!-- Konkrete, alltagstaugliche Anweisungen:
     Was darf ich? Was sollte ich vermeiden?
     Wann kann ich wieder arbeiten? Sport treiben? Auto fahren?
     Ernährungshinweise?
-->

### In den ersten 24 Stunden

- [ ] Bitte ruhen Sie sich aus.
- [ ] Kein Autofahren (besonders nach Narkose oder Sedierung).
- [ ] Kein Alkohol.
- [ ] Kein Heben schwerer Gegenstände.

### In den nächsten Tagen / Wochen

<!-- Spezifische Hinweise je nach Eingriff -->

- [ ] <!-- Hinweis 1 -->
- [ ] <!-- Hinweis 2 -->

### Ernährung

<!-- Falls relevant — z.B. nach Magenspiegelung, Darmeingriff etc. -->

---

## Wunden und Verbände

<!-- Wundversorgungsanweisungen:
     - Wie lange Verband belassen?
     - Wie oft wechseln?
     - Darf die Wunde nass werden?
     - Wann Fäden gezogen? (Datum oder bei wem)
-->

### Wundversorgung

| Frage | Antwort |
|---|---|
| Verband belassen bis | _____________ |
| Wunde trocken halten bis | _____________ |
| Fadenentfernung | _____________ |
| Durchführung durch | _____________ |

### Wundsymptome, die Sie beachten sollten

*Kontaktieren Sie uns, wenn Sie an der Wunde folgendes bemerken:*

- [ ] Zunehmende Rötung, Schwellung oder Wärme
- [ ] Eiternde oder übel riechende Wundsekretion
- [ ] Wundöffnung / Nahtdehiszenz
- [ ] Blutung aus der Wunde, die nicht aufhört

---

## Nachsorge

<!-- Folgetermine, Kontrolluntersuchungen:
     Wann? Bei wem? Was wird kontrolliert?
-->

| Termin | Bei wem? | Zweck |
|---|---|---|
| _____________ | Hausarzt | Allgemeine Nachsorge |
| _____________ | _________________________ | _________________________ |
| _____________ | _________________________ | _________________________ |

Bitte vereinbaren Sie bei Ihrem Hausarzt einen Nachsorgetermin innerhalb von **___ Tagen**.

---

## Notfallkontakt

**Wann sollten Sie sofort den Notarzt (112) rufen oder die Notaufnahme aufsuchen?**

- [ ] Starke, plötzlich auftretende Schmerzen
- [ ] Atemnot oder Brustschmerzen
- [ ] Hohes Fieber (> 38,5 °C)
- [ ] Starke Blutung (Wunde oder innere Blutung)
- [ ] Plötzliche Bewusstlosigkeit, Verwirrtheit, Krampfanfall
- [ ] Starke Schwellung eines Beins (Thromboseverdacht)
- [ ] <!-- Eingriffsspezifisches Warnsymptom -->

**Unsere Notaufnahme:** {{ clinic_phone }}

---

## Weiterführende Informationen

<!-- Optional: QR-Code zu weiterführendem Video / Animationsmaterial -->

{{ qr_media_url }}

---

<!-- =========================================================================
     WIKIMEDICA-CREDIT-FOOTER
     ========================================================================= -->

*Erstellt auf Basis von Wikimedica (wikimedica.de) — AT Medical Digital Solutions · Lizenz: CC BY-SA 4.0 · Version: {{ version }} · Aktualisiert: {{ updated }}*
