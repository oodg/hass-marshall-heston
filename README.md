# Marshall Heston für Home Assistant

Custom Integration (HACS) zur **lokalen** Steuerung einer Marshall Heston Soundbar (Heston 60 / 100 / 120) über deren HTTPS-API auf **Port 4430**.

Lautstärke, Stummschaltung und Casting werden bewusst **nicht** von dieser Integration übernommen – dafür ist die in Home Assistant integrierte **Google-Cast-Integration** (`cast`) zuständig, die die Heston automatisch als `media_player` erkennt.

## Funktionen

- **Quelle** wählen (`select`): HDMI eARC, HDMI, RCA, Optical, AUX, Bluetooth, Wi-Fi
- **Sound-Modus** wählen (`select`): Music, Movie, Night, Voice
- **Bass / Höhen** (`number`, -6 bis +6) des aktiven Sound-Modus
- **Presets 1–3** auslösen (`button`, in der Marshall-App konfiguriert)
- **Pause** des Players (`button`)
- **Player-Status** inkl. Titel/Interpret/Album (`sensor`)
- Automatische Erkennung im Netzwerk (mDNS `_googlecast._tcp`, Gerätename enthält „Heston“/„Marshall“) oder manuelle Eingabe der IP-Adresse

## Installation

### HACS (empfohlen)

1. HACS → ⋮ → „Benutzerdefinierte Repositories“ → `https://github.com/oodg/hass-marshall-heston` hinzufügen, Kategorie **Integration**
2. „Marshall Heston“ herunterladen, Home Assistant neu starten

### Manuell

Das Verzeichnis `custom_components/marshall_heston/` in das `custom_components/`-Verzeichnis der Home-Assistant-Konfiguration kopieren und neu starten.

## Einrichtung

Einstellungen → Geräte & Dienste → „Integration hinzufügen“ → **Marshall Heston**. Die Soundbar wird automatisch gefunden, wenn sie im selben Netzwerk mit „Heston“ im Gerätenamen erreichbar ist; alternativ die IP-Adresse manuell eingeben.

## Technische Basis

Die Soundbar stellt eine lokale HTTPS-API mit selbstsigniertem Zertifikat auf Port 4430 bereit:

- `GET /api/getData?path=<pfad>&roles=value` → Wert aus dem „zappa"-Baum lesen
- `POST /api/setData` mit `{"path": ..., "role": "value"|"activate", "value": {...}}` → Wert setzen

Verwendete Pfade:

| Funktion | Pfad |
|---|---|
| Quelle lesen/setzen | `settings:/zappa/physicalSource` |
| Sound-Modus lesen | `zappa:soundMode` |
| Sound-Modus setzen | `zappa:soundMode/request` (role `activate`) |
| EQ pro Modus | `settings:/zappa/audio/eqMusic` / `eqMovie` / `eqNight` / `eqVoice` (`value1` = Bass, `value5` = Höhen; negative Gerätewerte = 2× UI-Wert) |
| Player-Status | `player:player/data` |
| Player steuern | `player:player/control` (role `activate`) |
| Preset abspielen | `zappa:presets/play?id=1..3` (role `activate`) |

Referenz-Implementierung: [andreasvikke/marshall-speaker](https://github.com/andreasvikke/marshall-speaker) (Homey-App, `managers/heston-api-manager.js`).

## Hinweise

- Es gibt keinen echten Power-Off; die Heston wechselt nach dem Idle-Timeout in den Netzwerk-Standby und wacht z. B. per TV (HDMI-CEC), Cast oder Marshall-App auf.
- Presets benötigen eine Internetverbindung der Soundbar.
- Die 4430-API ist undokumentiert und kann sich mit Firmware-Updates ändern.
- Inoffizielles Projekt; keine Verbindung zu Marshall PLC.

## Entwicklung

```bash
pip install -r tests/requirements_test.txt
pytest tests/
```
