# 🎰 PyJack – Blackjack Web-Anwendung

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![NiceGUI](https://img.shields.io/badge/NiceGUI-1.4%2B-green)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-red)
![License](https://img.shields.io/badge/Lizenz-MIT-yellow)
![FHNW](https://img.shields.io/badge/FHNW-BSc_WI_OOP_SS26-darkblue)

> Browserbasierende Blackjack-Webanwendung entwickelt im Rahmen des Moduls  
> **Objektorientierte Programmierung (OOP), Sommersemester 2026**  
> BSc Wirtschaftsinformatik – Fachhochschule Nordwestschweiz (FHNW)

---

## Inhaltsverzeichnis

1. [Projektbeschreibung](#projektbeschreibung)
2. [Features](#features)
3. [Architektur](#architektur)
4. [User Stories](#user-stories)
5. [Use Cases](#use-cases)
6. [Datenbankschema](#datenbankschema)
7. [Verwendete Bibliotheken](#verwendete-bibliotheken)
8. [Installation & Setup](#installation--setup)
9. [Projektstruktur](#projektstruktur)
10. [Arbeitsaufteilung](#arbeitsaufteilung)
11. [Bekannte Einschränkungen](#bekannte-einschränkungen)
12. [Spielregeln](#spielregeln)

---

## Projektbeschreibung

PyJack ist eine vollständige Blackjack-Webanwendung, welche die klassischen Spielregeln des Kartenspiels Blackjack in einer modernen, browserbasierenden Oberfläche umsetzt. Die Anwendung folgt dem **3-Schichten-Architekturmodell** (Präsentation – Logik – Persistenz) und demonstriert die Prinzipien der objektorientierten Programmierung in Python.

Das Projekt entstand als Erweiterung des gleichnamigen CLI-Projekts aus dem Vorsemester (Programmieren 1) und wurde für das Modul OOP zu einer vollwertigen Webanwendung mit grafischer Benutzeroberfläche und Datenbankanbindung ausgebaut.

---

## Features

### Spielfunktionen
- ♠ Vollständiges Blackjack-Spiel nach offiziellen Regeln (Hit, Stand, Blackjack-Erkennung)
- 🃏 Realistische Pokerkarten mit Corner-Indizes (J/Q/K mit Figurensymbolen)
- 🎩 Automatischer Dealer-Zug (zieht bis Wert ≥ 17)
- 💡 Optionale Spielhinweise (Hit / Stand Empfehlung)

### Navigationssystem

| Route | Seite | Beschreibung |
|---|---|---|
| `/` | Hauptmenü | Startseite mit Navigation |
| `/game` | Spielseite | Aktives Blackjack-Spiel |
| `/history` | Spielhistorie | Statistiken & Spielverlauf mit Charts |
| `/settings` | Einstellungen | Persönliche Konfiguration |

### Statistiken & Analyse
- 📊 Donut-Chart: Sieg-/Niederlage-Verteilung
- 📈 Liniendiagramm: Kumulative Gewinnrate über alle Spiele
- 📉 Balkendiagramm: Punkte-Vergleich (Spieler vs. Dealer)
- 📁 CSV-Export der Spielhistorie (client-seitig via Blob-API)

### Personalisierung  ---> Allenfalls reduzieren, basierend auf scope
- 5 Tischfarben (Grün, Blau, Burgunder, Mitternacht, Braun)
- 4 Karten-Rückseiten-Farben
- Spielername, Audio-Lautstärke, Animations-Toggle
- Alle Einstellungen werden persistent in SQLite gespeichert

---

## Architektur

PyJack folgt dem vorgegebenen 3-Schichten-Architekturmodell:

```
┌─────────────────────────────────────────────────────────────┐
│                   PRÄSENTATIONSSCHICHT                      │
│           Browser (Thin Client – Vue.js / Quasar)           │
│    Keine Geschäftslogik, kein persistenter App-Zustand      │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP / WebSocket
┌──────────────────────▼──────────────────────────────────────┐
│                    ANWENDUNGSLOGIK                          │
│              Python OOP – NiceGUI (Server-seitig)           │
│                                                             │
│  ┌─────────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐    │
│  │   GameUI    │  │   Game   │  │  Player  │  │ Dealer │    │
│  │  (4 Pages)  │  │Controller│  │  + Hand  │  │+ Hand  │    │
│  └─────────────┘  └──────────┘  └──────────┘  └────────┘    │
│  ┌─────────────┐  ┌──────────┐  ┌──────────┐                │
│  │    Card     │  │   Deck   │  │CardRank/ │                │
│  │  @dataclass │  │ (52 Krt) │  │CardSuit  │                │
│  └─────────────┘  └──────────┘  └──────────┘                │
└──────────────────────┬──────────────────────────────────────┘
                       │ SQLAlchemy ORM
┌──────────────────────▼──────────────────────────────────────┐
│                    PERSISTENZSCHICHT                        │
│                  SQLite (pyjack.db)                         │
│                                                             │
│   ┌──────────────────┐    ┌────────────────────────┐        │
│   │   game_records   │    │     app_settings        │       │
│   │  (Spielhistorie) │    │  (Einstellungen ID=1)   │       │
│   └──────────────────┘    └────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### OOP-Klassenhierarchie

```
Player
  └── Dealer          (erbt von Player, erweitert mit Dealer-Regeln)

Enum: CardRank        (TWO..ACE, mit symbol + base_value)
Enum: CardSuit        (HEARTS/DIAMONDS/CLUBS/SPADES, mit symbol + color)
Enum: GameState       (WAITING / PLAYER_TURN / DEALER_TURN / GAME_OVER)

@dataclass Card       (CardRank + CardSuit)
Deck                  (52 Cards, shuffle, draw)
Hand                  (List[Card], get_value mit Ass-Logik)
Game                  (Controller: new_game, hit, stand, _end)
DatabaseManager       (CRUD: save_game, get_games, get_stats, get/save_settings)
GamePageUI            (Spieloberfläche, refresh, Event-Handler)
```

---

## User Stories

| ID | Als … | möchte ich … | damit … | Eingabe | Ausgabe | Datentyp |
|---|---|---|---|---|---|---|
| US-01 | Spieler | ein neues Blackjack-Spiel starten können | ich eine vollständige Spielrunde durchführen kann | Klick auf „Neues Spiel"-Button | Spielfeld wird angezeigt, je 2 Karten für Spieler und Dealer sichtbar | `Game`, `Deck`, `Hand`, `Card` |
| US-02 | Spieler | eine Karte ziehen (Hit) | ich meinen Punktestand erhöhen kann | Klick auf „Hit"-Button | Neue Karte wird auf der Hand angezeigt, Punktestand aktualisiert sich | `Game`, `Hand`, `Card` |
| US-03 | Spieler | stehen bleiben (Stand) | der Dealer seinen Zug ausführt und ein Ergebnis berechnet wird | Klick auf „Stand"-Button | Dealer deckt auf und zieht automatisch, Gewinner wird angezeigt | `Game`, `Dealer`, `GameState` |
| US-04 | Spieler | den aktuellen Punktestand jederzeit sehen | ich fundierte Spielentscheidungen treffen kann | Spieler schaut auf das Spielfeld | Aktueller Punktestand (z.B. „17 Punkte") ist sichtbar | `int`, `Hand` |
| US-05 | Spieler | eine Spielempfehlung (Hit/Stand) erhalten | ich die Spielstrategie erlernen kann | Klick auf Infosymbol | „Hit empfohlen" oder „Stand empfohlen" wird angezeigt | `bool` | ----> Allenfalls entfernen
| US-06 | Spieler | meine Spielhistorie einsehen | ich meine Leistung über Zeit verfolgen kann | Klick auf „Spielhistorie"-Tab | Liste der bisherigen Spiele + Diagramme mit Gewinn/Verlust-Übersicht | `List[GameRecord]`, `dict` Statistiken |
| US-07 | Spieler | meine Spielhistorie als CSV exportieren | ich die Daten in externen Tools auswerten kann | Klick auf „CSV Export"-Button | CSV-Datei (pyjack_history.csv) wird heruntergeladen | `csv.DictWriter`, `Blob` |

---

## Use Cases

### UC-01: Blackjack-Runde spielen

| Feld | Beschreibung |
|---|---|
| **ID** | UC-01 |
| **Name** | Blackjack-Runde durchführen |
| **Akteur** | Spieler |
| **Vorbedingung** | Anwendung gestartet, Spielseite `/game` geöffnet |
| **Auslöser** | Spieler klickt auf «Neues Spiel» |
| **Normalablauf** | 1. System mischt Deck und teilt je 2 Karten aus (eine Dealer-Karte verdeckt) · 2. Spieler entscheidet: Hit oder Stand · 3. Bei Stand: Dealer deckt auf und zieht bis Wert ≥ 17 · 4. System ermittelt Gewinner, speichert Ergebnis in DB |
| **Alternativer Ablauf** | Spieler überschreitet 21 Punkte → sofortige Niederlage (Bust) |
| **Sonderfall** | Spieler oder Dealer hat mit 2 Karten 21 Punkte → Blackjack |
| **Nachbedingung** | Ergebnis in `game_records` gespeichert, Statistiken aktualisiert |

### UC-02: Spielhistorie und Statistiken einsehen

| Feld | Beschreibung |
|---|---|
| **ID** | UC-02 |
| **Name** | Spielhistorie einsehen |
| **Akteur** | Spieler |
| **Vorbedingung** | Mindestens ein gespeichertes Spiel vorhanden |
| **Auslöser** | Spieler navigiert zu `/history` |
| **Normalablauf** | 1. System lädt Statistiken aus DB · 2. Ein Diagramm wird gerendert (Kreis) · 3. Letzten 10 Spiele werden tabellarisch aufgelistet |
| **Alternativer Ablauf** | Keine Spiele vorhanden → Hinweistext wird angezeigt |
| **Nachbedingung** | Keine Datenveränderung |

### UC-03: Einstellungen konfigurieren

| Feld | Beschreibung |
|---|---|
| **ID** | UC-03 |
| **Name** | Einstellungen anpassen und speichern |
| **Akteur** | Spieler |
| **Vorbedingung** | Einstellungsseite `/settings` geöffnet |
| **Auslöser** | Spieler nimmt Änderungen vor und klickt «Einstellungen speichern» |
| **Normalablauf** | 1. Spieler passt die Tischfarbe oder Gameplay-Optionen an · 2. Klick auf Speichern → `save_settings()` schreibt in SQLite |
| **Nachbedingung** | `app_settings` (ID=1) in DB aktualisiert |

### UC-04: Spielhistorie exportieren

| Feld | Beschreibung |
|---|---|
| **ID** | UC-04 |
| **Name** | CSV-Export der Spielhistorie |
| **Akteur** | Spieler |
| **Vorbedingung** | Spielhistorie-Seite geöffnet |
| **Auslöser** | Klick auf «CSV Export» |
| **Normalablauf** | 1. System lädt alle Spieldatensätze · 2. CSV wird client-seitig via Blob-API generiert · 3. Browser-Download-Dialog öffnet sich |
| **Nachbedingung** | Datei `pyjack_history.csv` lokal gespeichert |

---
## Test Cases

### TC-01 bis TC-05: Spielablauf (UC-01 / US-01–04)

| ID | Beschreibung | Vorbedingung | Eingabe | Erwartetes Ergebnis | Priorität |
|---|---|---|---|---|---|
| TC-01 | Neues Spiel starten | App läuft, `/game` geöffnet | Klick auf „Neues Spiel" | Spielfeld sichtbar, Spieler hat 2 Karten, Dealer hat 1 sichtbare + 1 verdeckte Karte, Punktestand aktualisiert | Hoch |
| TC-02 | Karte ziehen (Hit) | Spiel läuft, `GameState = PLAYER` | Klick auf „Hit" | Neue Karte erscheint auf Spielerhand, Punktestand erhöht sich korrekt | Hoch |
| TC-03 | Stehen bleiben (Stand) | Spiel läuft, `GameState = PLAYER` | Klick auf „Stand" | Dealer deckt auf, zieht bis ≥ 17, Gewinner wird angezeigt, Ergebnis in DB gespeichert | Hoch |
| TC-04 | Bust – Spieler überschreitet 21 | Spieler hat z.B. 15 Punkte | Klick auf „Hit" (Karte bringt >21) | Sofortige Niederlage, Ergebnis = „Dealer", kein weiterer Zug möglich | Hoch |
| TC-05 | Blackjack – Spieler hat 21 mit 2 Karten | Neues Spiel gestartet | – (automatisch erkannt) | „Blackjack!" wird angezeigt, Spiel endet sofort als Sieg, ausser Dealer hat ebenfalls Blackjack | Hoch |

---

### TC-06 bis TC-08: Dealer-Logik

| ID | Beschreibung | Vorbedingung | Eingabe | Erwartetes Ergebnis | Priorität |
|---|---|---|---|---|---|
| TC-06 | Dealer zieht bis ≥ 17 | Spieler hat Stand gedrückt | – (automatisch) | Dealer zieht solange Wert < 17, stoppt bei ≥ 17 | Hoch |
| TC-07 | Dealer Bust | Dealer hat < 17, zieht weiter | – (automatisch) | Dealer überschreitet 21 → Spieler gewinnt | Hoch |
| TC-08 | Dealer Blackjack | Dealer erhält 21 mit 2 Karten | – (automatisch) | Unentschieden wenn Spieler auch Blackjack, sonst Dealer gewinnt | Mittel |

---

### TC-09 bis TC-10: Ass-Logik (Hand-Wertberechnung)

| ID | Beschreibung | Vorbedingung | Eingabe | Erwartetes Ergebnis | Priorität |
|---|---|---|---|---|---|
| TC-09 | Ass zählt als 11 | Hand hat Ass + 7 | – | Wert = 18 | Hoch |
| TC-10 | Ass wechselt zu 1 bei Bust-Risiko | Hand hat Ass + 7 + 6 | – | Wert = 14 (Ass zählt als 1, kein Bust) | Hoch |

---

### TC-11 bis TC-12: Spielhistorie (US-06)

| ID | Beschreibung | Vorbedingung | Eingabe | Erwartetes Ergebnis | Priorität |
|---|---|---|---|---|---|
| TC-11 | Spielhistorie anzeigen | Mind. 1 Spiel gespeichert | Navigation zu `/history` | Liste der letzten Spiele + Diagramme werden korrekt geladen | Mittel |
| TC-12 | Keine Spiele vorhanden | Leere Datenbank | Navigation zu `/history` | Hinweistext wird angezeigt, keine Diagramme, kein Absturz | Mittel |

---

### TC-13: CSV-Export (US-08)

| ID | Beschreibung | Vorbedingung | Eingabe | Erwartetes Ergebnis | Priorität |
|---|---|---|---|---|---|
| TC-13 | CSV-Export der Spielhistorie | Mind. 1 Spiel in DB | Klick auf „CSV Export" | `pyjack_history.csv` wird heruntergeladen, enthält korrekte Spalten und Daten | Mittel |

---

### TC-14: Spielhinweise (US-05)

| ID | Beschreibung | Vorbedingung | Eingabe | Erwartetes Ergebnis | Priorität |
|---|---|---|---|---|---|
| TC-14a | Hinweis „Hit empfohlen" wird angezeigt | Spiel läuft, Spieler hat niedrigen Punktestand (z.B. ≤ 11) | Klick auf Infosymbol | „Hit empfohlen" wird angezeigt | Niedrig |
| TC-14b | Hinweis „Stand empfohlen" wird angezeigt | Spiel läuft, Spieler hat hohen Punktestand (z.B. ≥ 17) | Klick auf Infosymbol | „Stand empfohlen" wird angezeigt | Niedrig |
| TC-14c | Hinweis nicht sichtbar wenn deaktiviert | `show_hints = False` in Einstellungen | Klick auf Infosymbol | Kein Hinweis erscheint | Niedrig |

---


## Datenbankschema

```sql
-- Spielhistorie
CREATE TABLE game_records (
    id           INTEGER     PRIMARY KEY AUTOINCREMENT,
    timestamp    DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    winner       VARCHAR(20) NOT NULL,   -- 'Spieler' | 'Dealer' | 'Unentschieden'
    player_score INTEGER     NOT NULL,
    dealer_score INTEGER     NOT NULL,
    player_cards VARCHAR(100) NOT NULL,  -- z.B. "A♠, K♥"
    dealer_cards VARCHAR(100) NOT NULL
);

-- Einstellungen (Singleton – immer genau 1 Zeile mit ID=1)
CREATE TABLE app_settings (
    id            INTEGER      PRIMARY KEY DEFAULT 1,
    table_color   VARCHAR(30)  DEFAULT 'green',
    show_hints    BOOLEAN      DEFAULT 1,
    auto_stand_21 BOOLEAN      DEFAULT 1
);
```

**Entity-Relationship:**

```
┌──────────────────────┐        ┌──────────────────────┐
│     game_records     │        │     app_settings      │
├──────────────────────┤        ├──────────────────────┤
│ PK id         INT    │        │ PK id = 1     INT    │
│    timestamp DATETIME│        │    music_volume REAL  │
│    winner    VARCHAR │        │    sfx_volume   REAL  │
│    player_score INT  │        │    music_enabled BOOL │
│    dealer_score INT  │        │    sfx_enabled   BOOL │
│    player_cards TEXT │        │    player_name VARCHAR│
│    dealer_cards TEXT │        │    table_color  VARCHAR│
└──────────────────────┘        │    card_back    VARCHAR│
  n Einträge – 1 pro Spiel      │    show_hints   BOOL  │
                                │    animations   BOOL  │
                                │    auto_stand_21 BOOL │
                                └──────────────────────┘
                                  Singleton – immer ID=1
```

---

## Verwendete Bibliotheken

| Bibliothek | Version | Zweck | Lizenz |
|---|---|---|---|
| **NiceGUI** | ≥ 1.4.0 | Web-UI Framework (Vue.js/Quasar wrapper) | MIT |
| **SQLAlchemy** | ≥ 2.0.0 | ORM – Datenbankinteraktion ohne direkte SQL-Statements | MIT |
| **Python Standard Library** | 3.11+ | `random`, `csv`, `io`, `base64`, `datetime`, `dataclasses`, `enum` | PSF |

**Frontend-Technologien (via NiceGUI, keine separate Installation):**

| Technologie | Zweck |
|---|---|
| Vue.js 3 | Reaktive UI-Engine im Browser |
| Quasar Framework | UI-Komponenten (Buttons, Tabs, Slider, Switch) |
| Apache ECharts | Interaktive Diagramme (Donut) |

---

## Installation & Setup

### Voraussetzungen
- Python 3.11 oder höher
- pip (Python Package Manager)
- Internetverbindung beim ersten Start (Google Fonts CDN)

### Installation

```bash
# 1. Repository klonen
git clone https://github.com/[Andri-2]/pyjack.git
cd pyjack

# 2. Virtuelle Umgebung erstellen (empfohlen)
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. Anwendung starten
python main.py
```

### Zugriff
Nach dem Start ist die Anwendung unter [**http://localhost:8080**](http://localhost:8080) erreichbar.  
Die Datenbank `pyjack2.db` wird automatisch beim ersten Start erstellt.

---

## Projektstruktur

```
PyJack-2.0/
│  
├── PyJack2              # Programmordner
  ├── main.py            # Präsentationsschicht (NiceGUI Pages)
  ├── domain.py          # Domänenlogik (Game, Cards, Player...)
  ├── database.py        # Persistenzschicht (SQLAlchemy ORM)
├── requirements.txt     # Python-Abhängigkeiten
├── README.md            # Projektdokumentation
└── .gitignore           # Git-Ausschlüsse
```

> Da NiceGUI eine Single-File-Architektur unterstützt und der Projektumfang dies erlaubt, sind alle Schichten in `pyjack.py` implementiert. Die logische Trennung der Schichten ist durch Klassensegmentierung und Kommentare klar erkennbar.

---

## Arbeitsaufteilung

| Bereich | Beschreibung | Verantwortlich |
|---|---|---|
| **Domain Layer** | Klassen: Card, Deck, Hand, Player, Dealer, Game, Enums | [VORNAME NACHNAME 1] |
| **Persistenzschicht** | DatabaseManager, ORM-Modelle, Migration | [VORNAME NACHNAME 2] |
| **UI & Präsentation** | GameUI, alle 4 Pages, Navigation | [VORNAME NACHNAME 3] |
| **CSS & Design** | Poker-Karten, Farbpaletten, Animationen | [VORNAME NACHNAME 1] |
| **Charts** | ECharts Integration (Kreisdiagram) | [VORNAME NACHNAME 3] |
| **Dokumentation** | README, Use Cases, User Stories | Alle |
| **Testing & Bugfixing** | Manuelle Tests, DB-Migration, Bugfixes | Alle |

---

## Bekannte Einschränkungen

- Die Anwendung ist für Einzelspieler ausgelegt (kein Multiplayer)
- Die Datenbank wird lokal auf dem Server gespeichert (kein Cloud-Backup)
- Mobilgeräte werden unterstützt, sind aber nicht primäres Zielgerät

---

## Spielregeln

| Regel | Wert |
|---|---|
| Kartenanzahl | 52 (Standard-Deck, 1× gemischt) |
| Kartenwerte | 2–10 = Nennwert · J/Q/K = 10 · Ass = 11 (oder 1 bei Bust-Risiko) |
| Dealer-Strategie | Zieht obligatorisch bis Wert ≥ 17 |
| Blackjack | 21 mit 2 Karten → Sofortsieg (ausser Dealer hat ebenfalls Blackjack) |
| Bust | Überschreitung von 21 Punkten = sofortige Niederlage |
| Ziel | Näher an 21 kommen als der Dealer, ohne zu übersteigen |

---

## Lizenz

MIT License – © 2026 [Schwab_Mehmeti], FHNW BSc Wirtschaftsinformatik
