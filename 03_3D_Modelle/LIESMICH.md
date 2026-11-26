# 3D-Modelle – nach Epochen sortiert

| Ordner | Epoche |
|---|---|
| `01_Steinzeit/` | Steinzeit (aktuell) – Gebäude (mit Wachturm), Zäune, Figuren, Waffen, Tiere, Natur, Deko, Wasser |
| `02_Antike/` | Antike – Reitstall, Sattelpferd, Zäune, Flöße, Eisenwaffen |
| `03_Mittelalter/` | Mittelalter – Schwerter |
| `04_Neuzeit/` | Neuzeit – Galeone, Osmanen-Figuren (`Osmanen/`) |
| `05_Industriezeit/` | Industriezeit – noch leer |
| `06_Erster_Weltkrieg/` | Erster Weltkrieg – Ausguckturm |
| `07_Zweiter_Weltkrieg/` | Zweiter Weltkrieg – Kommandobunker |
| `08_Kalter_Krieg/` | Kalter Krieg – noch leer |
| `09_Moderne/` | Moderne – Beton-Wachturm |
| `10_Zukunft/` | Zukunft – Zukunftsbunker |
| `99_Reserve/` | passt zu keiner Epoche |

In jedem Epochen-Ordner steht eine `LIESMICH.md` mit allen Modellen.

## Aufbau

- `name.glb` = Spiel-Fassung (verkleinert, so wie im Spiel)
- `Original/name_original.glb` = unverändertes Meshy-Original

## Große Originale (über 95 MB)

GitHub erlaubt höchstens 100 MB pro Datei. Diese Originale sind deshalb in Teile zerlegt: `name_original.glb.teil1von2`, `name_original.glb.teil2von2` usw.

Wieder zusammensetzen:

- **Windows** (Eingabeaufforderung im Ordner):
  `copy /b name_original.glb.teil1von2 + name_original.glb.teil2von2 name_original.glb`
- **Mac/Linux**:
  `cat name_original.glb.teil* > name_original.glb`

Danach ist die Datei wieder genau das Original.
