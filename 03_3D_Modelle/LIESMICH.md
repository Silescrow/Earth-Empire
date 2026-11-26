# 3D-Modelle – nach Epochen sortiert

| Ordner | Epoche |
|---|---|
| `1_Steinzeit/` | Steinzeit (aktuelle Epoche) – Gebäude, Zäune, Figuren, Waffen, Tiere, Natur, Deko, Wasser |
| `2_Antike/` | Antike – Reitstall, Sattelpferd, Weidezäune, Flöße, Eisenwaffen |
| `3_Mittelalter/` | Mittelalter – Schwerter |
| `4_Neuzeit/` | Neuzeit – Galeone |
| `9_Reserve/` | passt zu keiner Epoche |

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
