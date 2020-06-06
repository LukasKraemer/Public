# Installieren und Starten

### - Als Exe ausführen

- Gehen Sie nun in den Ordner in den die Dateien entpackt wurden und wählen Sie hier die Ordner uploader\gui\gui aus.
- Führen Sie die Datei gui.exe aus.

### - Als Skript ausführen:
#### - Python Installieren

Öffnen Sie den heruntergeladenen Python Installer und wählen Sie die Punkte Install for all Users und Add Python 
to Path dannach wählen Sie Costomize installation aus, und dannach klicken Sie
auf Next. Wählen Sie hier noch zusätzlich den Punkt Install for all Users aus und Add Python to environment 
variables und klicken Sie dannach auf Intstall. Warte Sie bis das Programm installiert ist. Dannach bitte alle weitern Bibliotheken mit pip installieren
- Powershell öffnen Sie indem Sie die Windows Taste + R drücken, und in dem Erscheinenden Eingabefenster Powershell eingeben, und ihre Eingabe dannach mit Enter bestätitigen.
- Linux: Über das Terminal die Befehle ausführen

#### - pip install pandas
#### - pip install sqlalchemy
#### - pip install pymysql
#### - pip install pillow



### Config.ini
- Öffnen Sie die Datei config.ini

- Geben Sie bei path= den Pfad an unter dem Sie ihre exportierten txt-Dateien aus dem Hyrbrid Reporter abspeichern.
Hinweis: Sie müssen bei ihrem kopierten Dateipfad aus dem Explorer noch am Ende \ Ergänzen da sonst Ihre Dateien 
nicht gefunden werden.

- Wählen Sie ihre Farbprofil aus (1 oder 2), oder legen Sie ihre eignene Schriftfarbe und Hintergrundfarbe in einem der beiden Profile an( in RGB Farbcode).

- Speichern Sie diese Änderung in dem Sie Strg + S drücken. Dannach könnnen Sie dieses Fenster schließen.

### Einrichten von XAMPP
Öffnen Sie das XAMPP Control Panel, es erreicht ein Sicherheitshinweis, klicken Sie hier alle Kästchen an, und wählen Sie
Zugriff zulassen aus. Starten Sie Apache, MYSQL und FileZilla und machen wählen Sie hier die selben Einstellungen im 
erscheinenden Fenster. 

### Einrichten des Datenbank
- Drücken Sie bei MYSQL auf Admin. Wählen Sie auf der Erscheinenden Seite Benutzerkonten aus, und drücken Sie auf 
  Benutzerkonto hinzufügen, bei phpmyadmin. 

- Für das Programm und Skript sollte man aus Sicherheitsgründen einen weiteren Datenbanknutzer mit eingeschränkten Rechten erstellen. Ich würde Einfachkeitshalber ein Schema(es empfielt sich "car") erstellen und ihm auf dem gesamten Schema folgende Rechte geben : select, insert, create) meines Wissens sind des genug Rechte, sollte das Programm auf einem Lokalen Rechner ohne externen Zugriff laufen, können Sie dem Nutzer globale Adminrechte geben - wir raten davon aber ab.

Ein Schema kann man je nach Oberfläche unterschiedlich erstellen, der SQL Befel "create schema user;" geht bei den gängisten Datenbanksystemen
