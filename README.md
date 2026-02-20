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

---

## Projektbeschreibung

PyJack ist eine vollständige Blackjack-Webanwendung, welche die klassischen Spielregeln  
des Kartenspiels Blackjack in einer modernen, browserbasierenden Oberfläche umsetzt.  
Die Anwendung folgt dem **3-Schichten-Architekturmodell** (Präsentation – Logik – Persistenz)  
und demonstriert die Prinzipien der objektorientierten Programmierung in Python.

Das Projekt entstand als Erweiterung des gleichnamigen CLI-Projekts aus dem  
Vorsemester (Programmieren 1) und wurde für das Modul OOP zu einer vollwertigen  
Webanwendung mit grafischer Benutzeroberfläche und Datenbankanbindung ausgebaut.

---

## Features

### Spielfunktionen
- ♠ Vollständiges Blackjack-Spiel nach offiziellen Regeln (Hit, Stand, Blackjack-Erkennung)
- 🃏 Realistische Pokerkarten mit Corner-Indizes (J/Q/K mit Figurensymbolen)
- 🎩 Automatischer Dealer-Zug (zieht bis Wert ≥ 17)
- 💡 Optionale Spielhinweise (Hit / Stand Empfehlung)
- 🎵 Hintergrundmusik und Soundeffekte (Web Audio API, keine externen Dateien)

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

### Personalisierung
- 5 Tischfarben (Grün, Blau, Burgunder, Mitternacht, Braun)
- 4 Karten-Rückseiten-Farben
- Spielername, Audio-Lautstärke, Animations-Toggle
- Alle Einstellungen werden persistent in SQLite gespeichert

---

## Architektur

PyJack folgt dem vorgegebenen 3-Schichten-Architekturmodell:

