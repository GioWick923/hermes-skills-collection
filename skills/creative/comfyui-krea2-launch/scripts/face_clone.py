# -*- coding: utf-8 -*-
"""Face clone pipeline - corrected version.
Use when you have a real face reference (photo) and want to composite it onto a body image.
Only works when BOTH images have detectable real faces (fails on anime/illustration).
"""
import cv2, os, numpy as np
from PIL import Image

def face_clone(src_path, dst_path, output_path, mask_expansion=0.70):
    """
    Clone face from src_image onto dst_image using InsightFace landmarks.
    
    Args:
        src_path: Path to image with face to clone (source)
        dst_path: Path to image with body (destination)
        output_path: Where to save result
        mask_expansion: How much larger the elliptical mask is (0.70 = 70% of bbox)
    """
    # Load and scale images
    im_dst = Image.open(dst_path).convert('RGB')
    # Scale to standard size for processing
    if im_dst.size[0] > 1024:
        ratio = 1024 / im_dst.size[0]
        new_size = (1024, int(im_dst.size[1] * ratio))
        im_dst = im_dst.resize(new_size, Image.LANCZOS)
    cv_dst = cv2.cvtColor(np.array(im_dst), cv2.COLOR_RGB2BGR)
    
    im_src = Image.open(src_path).convert('RGB')
    # Crop to square center for face focus
    dim = min(im_src.size)
    left = (im_src.size[0] - dim) // 2
    top = (im_src.size[1] - dim) // 2
    im_src = im_src.crop((left, top, left + dim, top + dim))
    im_src = im_src.resize((512, 512), Image.LANCZOS)
    cv_src = cv2.cvtColor(np.array(im_src), cv2.COLOR_RGB2BGR)
    
    # Load face analysis
    try:
        import insightface
        app = insightface.app.FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
        app.prepare(ctx_id=0, det_size=(640, 640))
    except ImportError:
        print("ERROR: insightface not installed")
        Image.fromarray(cv_dst).save(output_path, quality=95)
        return False
    
    faces_src = app.get(cv_src)
    faces_dst = app.get(cv_dst)
    
    if not faces_src or not faces_dst:
        print(f"INFO: No faces detected (src: {len(faces_src) if faces_src else 0}, dst: {len(faces_dst) if faces_dst else 0})")
        print("       This may be an illustration/anime image - face clone will not work.")
        Image.fromarray(cv_dst).save(output_path, quality=95)
        return False
    
    # Get largest face from each
    f_src = max(faces_src, key=lambda x: (x.bbox[2]-x.bbox[0])*(x.bbox[3]-x.bbox[1]))
    f_dst = max(faces_dst, key=lambda x: (x.bbox[2]-x.bbox[0])*(x.bbox[3]-x.bbox[1]))
    
    # Align faces
    lm_src = f_src.kps.astype(np.float32)
    lm_dst = f_dst.kps.astype(np.float32)
    M, _ = cv2.estimateAffinePartial2D(lm_src, lm_dst, method=cv2.LMEDS)
    
    h, w = cv_dst.shape[:2]
    warped = cv2.warpAffine(cv_src, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    
    # Create elliptical mask
    bbox = f_dst.bbox
    cx, cy = int((bbox[0]+bbox[2])/2), int((bbox[1]+bbox[3])/2)
    fw, fh = int((bbox[2]-bbox[0])*mask_expansion), int((bbox[3]-bbox[1])*mask_expansion*1.2)
    mask = np.zeros((h, w), dtype=np.float32)
    cv2.ellipse(mask, (cx, cy), (fw, fh), 0, 0, 360, 255, -1)
    mask = cv2.GaussianBlur(mask, (31, 31), 0)
    mask = mask[:, :, np.newaxis]
    
    # Color correction
    src_mean = cv_src.astype(np.float32).mean(axis=(0, 1))
    dst_mean = cv_dst.astype(np.float32).mean(axis=(0, 1))
    diff = src_mean - dst_mean
    warped = warped.astype(np.float32) + diff
    warped = np.clip(warped, 0, 255).astype(np.uint8)
    
    # Blend
    result = cv_dst.astype(np.float32) * (1 - mask) + warped * mask
    result = np.clip(result, 0, 255).astype(np.uint8)
    
    # Save
    Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB)).save(output_path, quality=95)
    print(f"✓ Composite saved: {output_path} ({os.path.getsize(output_path)//1024}KB)")
    return True

if __name__ == '__main__':
    import sys
    if len(sys.argv) >= 4:
        success = face_clone(sys.argv[1], sys.argv[2], sys.argv[3])
        sys.exit(0 if success else 1)
    else:
        print("Usage: face_clone.py <src_face> <dst_body> <output>")
        print("Example: face_clone.py sadie_ref.jpg base.jpg output.jpg")
