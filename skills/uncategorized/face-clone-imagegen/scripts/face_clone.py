# -*- coding: utf-8 -*-
"""Face clone por imagen: pega el rostro de SRC sobre el cuerpo de DST.

Uso:
    python face_clone.py SRC DST OUT [mask_w] [mask_h]

    SRC = imagen con el rostro a clonar
    DST = imagen con el cuerpo destino
    OUT = ruta del compuesto (guardar en F:/ComfyUI/input/ para integrar en Krea2)
    mask_w/mask_h (opcionales): factor elíptico sobre el bbox destino (default 0.62 / 0.78)

Requiere: pip install insightface onnx (en el venv de ComfyUI). Pesos buffalo_l
se descargan solos al primer run. Después de esto, integrar con img2img denoise 0.25.
"""
import sys

import cv2
import numpy as np
import insightface


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    src_path, dst_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    fw_f = float(sys.argv[4]) if len(sys.argv) > 4 else 0.62
    fh_f = float(sys.argv[5]) if len(sys.argv) > 5 else 0.78

    app = insightface.app.FaceAnalysis(
        name='buffalo_l',
        providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=(640, 640))

    img_src = cv2.imread(src_path)
    img_dst = cv2.imread(dst_path)
    assert img_src is not None and img_dst is not None, 'no se pudo leer SRC o DST'

    faces_src = app.get(img_src)
    faces_dst = app.get(img_dst)
    assert faces_src and faces_dst, 'no se detectaron caras en SRC o DST'

    def biggest(faces):
        return max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))

    f_src, f_dst = biggest(faces_src), biggest(faces_dst)

    # Alineación por 5 landmarks (2 ojos, nariz, 2 comisuras)
    M, _ = cv2.estimateAffinePartial2D(
        f_src.kps.astype(np.float32), f_dst.kps.astype(np.float32),
        method=cv2.LMEDS)
    h, w = img_dst.shape[:2]
    warped = cv2.warpAffine(img_src, M, (w, h), flags=cv2.INTER_CUBIC,
                            borderMode=cv2.BORDER_CONSTANT, borderValue=0)

    # Máscara elíptica sobre el bbox del rostro destino + feather gaussiano
    bbox = f_dst.bbox
    cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
    fw, fh = (bbox[2] - bbox[0]) * fw_f, (bbox[3] - bbox[1]) * fh_f
    mask = np.zeros((h, w), dtype=np.float32)
    cv2.ellipse(mask, (int(cx), int(cy)), (int(fw / 2), int(fh / 2)),
                0, 0, 360, 1.0, -1)
    k = int(max(fw, fh) * 0.35) | 1
    mask = cv2.GaussianBlur(mask, (k, k), 0)

    # Match de color por canal (media/std) dentro de la máscara
    region = mask > 0.5
    for c in range(3):
        s = warped[:, :, c][region]
        d = img_dst[:, :, c][region]
        warped[:, :, c] = np.clip(
            (warped[:, :, c] - s.mean()) * (d.std() / (s.std() + 1e-5)) + d.mean(),
            0, 255)

    mask3 = np.dstack([mask] * 3)
    comp = (warped.astype(np.float32) * mask3
            + img_dst.astype(np.float32) * (1 - mask3)).astype(np.uint8)

    cv2.imwrite(out_path, comp, [cv2.IMWRITE_JPEG_QUALITY, 97])

    # Verificación: el compuesto debe seguir teniendo cara detectable
    chk = app.get(comp)
    print(f'OK -> {out_path} (caras en compuesto: {len(chk)})')


if __name__ == '__main__':
    main()
