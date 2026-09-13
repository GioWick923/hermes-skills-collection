# Face clone por imagen — parámetros y ajustes finos

Validado con insightface buffalo_l + Krea2 img2img, imágenes 2048x3072.

## Qué hace scripts/face_clone.py

1. Detecta caras en SRC y DST (buffalo_l, det_size 640; toma la de mayor bbox si hay varias).
2. Alinea por 5 landmarks (`kps`: 2 ojos, nariz, 2 comisuras) con `estimateAffinePartial2D(..., method=cv2.LMEDS)`.
3. Máscara elíptica sobre el bbox del rostro DESTINO: 0.62 del ancho, 0.78 del alto — cubre frente/mentón sin comerse el cabello del contorno.
4. Feather gaussiano: kernel = 0.35 * max(ancho, alto) de la elipse.
5. Match de color por canal (media/std) dentro de la máscara ANTES de mezclar — adapta el tono de piel al ambiente destino; sin esto el rostro se ve "recortado".
6. Mezcla y verifica: re-detección en el compuesto (debe reportar 1 cara).

## Tabla de ajustes

| Síntoma | Ajuste |
|---|---|
| Borde duro / rostro "pegado" | feather 0.35→0.5, o elipse más grande: `face_clone.py SRC DST OUT 0.70 0.85` |
| Rostro deformado tras integrar | denoise 0.25→0.15 en el pase final |
| Identidad se pierde tras integrar | denoise más bajo o cambiar seed |
| Tono de piel desigual | verificar match de color dentro de la máscara (`region = mask > 0.5`, máscara 2D, no 3D) |

## Notas

- insightface devuelve varias caras en escenas multi-persona: el script toma la mayor. Verificar manualmente si importa cuál.
- El compuesto intermedio se guarda JPEG q97 — suficiente para el pase de integración.
- Copiar la imagen de referencia del usuario a `F:/ComfyUI/input/` antes de cualquier LoadImage.