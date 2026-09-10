#!/usr/bin/env python
"""Baidu Unlimited-OCR inference wrapper.
Uso:
  run_ocr.py --image img.png --out dir [--config gundam|base]
  run_ocr.py --pdf doc.pdf --out dir --multi
"""
import argparse, os, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", help="ruta a imagen")
    ap.add_argument("--pdf", help="ruta a PDF (multipagina)")
    ap.add_argument("--out", required=True, help="dir de salida")
    ap.add_argument("--config", default="gundam", choices=["gundam", "base"])
    ap.add_argument("--multi", action="store_true", help="usar infer_multi (pdf)")
    ap.add_argument("--model-dir", default=r"C:\Users\<USER>\AppData\Local\hermes\models\baidu",
                    help="ruta local a pesos (default: models/baidu permanente)")
    args = ap.parse_args()

    from transformers import AutoModel, AutoTokenizer
    model_name = args.model_dir or "baidu/Unlimited-OCR"
    tok = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModel.from_pretrained(
        model_name, trust_remote_code=True, use_safetensors=True, dtype="float32"
    ).eval()

    os.makedirs(args.out, exist_ok=True)

    if args.multi or args.pdf:
        import fitz, tempfile
        doc = fitz.open(args.pdf)
        tmp = tempfile.mkdtemp(prefix="baidu_pdf_")
        paths = []
        for i, page in enumerate(doc):
            p = os.path.join(tmp, f"page_{i+1:04d}.png")
            page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72)).save(p)
            paths.append(p)
        doc.close()
        model.infer_multi(tok, prompt="<image>Multi page parsing.",
                          image_files=paths, output_path=args.out,
                          image_size=1024, max_length=32768,
                          no_repeat_ngram_size=35, ngram_window=1024, save_results=True)
    else:
        crop = args.config == "gundam"
        img_size = 640 if crop else 1024
        model.infer(tok, prompt="<image>document parsing.",
                    image_file=args.image, output_path=args.out,
                    base_size=1024, image_size=img_size, crop_mode=crop,
                    max_length=32768, no_repeat_ngram_size=35, ngram_window=128,
                    save_results=True)
    print("BAIDU_OCR_DONE", args.out)

if __name__ == "__main__":
    main()
