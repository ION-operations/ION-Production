# ION Helixion GNOME panel v5 — evidence

## pytest

```
42 passed in 0.71s
```

## node --check extension.js

```
(no output — exit 0)
```

## metadata version

```json
"version": 5
```

## grep carrier actions (extension.js)

```
573:        this._onCarrierMutation([enabled ? 'carrier-enable' : 'carrier-disable', carrierId]);
583:            ['carrier-mode', carrierId, next],
603:        this._onCarrierMutation(['carrier-limit', carrierId, String(next)]);
```
