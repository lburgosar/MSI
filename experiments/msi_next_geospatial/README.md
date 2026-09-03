# MSI NEXT Map-first Operator Preview

Experimento aislado: no reemplaza Mission Studio ni modifica Mission Runtime.

Ejecutar desde la raíz:

```powershell
manager\mission_studio\.venv\Scripts\python.exe -m experiments.msi_next_geospatial.prototype
```

Controles: arrastre izquierdo o touch para pintar, click derecho para quitar, rueda para zoom, `C` para limpiar y `E` para exportar `selection.geojson`.

- El botón verde principal avanza por preflight, reconocimiento, corrección, autorización y ejecución.
- `SIMULAR VIENTO ↑` o `W` inyecta viento de 8.4 m/s; durante ejecución MSI pausa y explica la decisión.
- `DETALLES / PRECISIÓN` revela coordenadas WGS84 y parámetros avanzados.

La base agrícola es simulada y está rotulada. La iteración valida interacción, grid adaptativo, flujo guiado y exportación geográfica; no finge cartografía real, Runtime conectado ni control de vehículos.
