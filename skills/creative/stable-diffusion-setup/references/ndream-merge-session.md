# Sesión: cadena de merges NDREAM (28-29 ago 2026)

Modelos en `F:/Modelos/checkpoints/`. Cadena de merges ponderados que hizo Gio
(todos safetensors SDXL/Illustrious, 2515 tensores + 248 VAE = 2765).

## Lineage
```
illustriousxl12GBFP32_v10  (base grande fp32, 13.8GB, id Civitai 1190200, Ene 2025)
+ nexusdreamINFINITY_infinityULTRAAIO / _NDREAM (pequeños ~7.2GB)
+ reijality_v30, illustrijGEN_3, maturaVyron_v5RosE, nexusdreamultra_ndreamultraV2

INFINITY_x_illustriousXL_fp32     (INFINITY 0.4 + ilxl 0.6)
INFINITY_MIX_TRIO_fp32            (INFINITY .50 + INFINITY_x_ilxl .25 + reijality .25)
NDREAM_x_TRIO_x_ULTRA_fp32        (NDREAM .40 + TRIO .30 + ULTRAAIO .30)
NDREAM_v2_45_30_25_fp32           (NDREAM .45 + TRIO_nuevo .30 + ULTRA .25)
NDREAM_v3_sdxlvae_fp32            (NDREAM .45 + V2 .30 + ULTRA .25 + VAE SDXL bake)
NDREAM_FINAL_60_20_20_sdxlvae_fp32(NDREAM_v3 .60 + TRIO .20 + ULTRAAIO .20 + VAE) ★ el que Gio aprobó "espectacular"
NDREAM_TRI_ULTRA_GEN_50_25_25     (TRINITY .50 + ULTRAAIO .25 + Gen_Vyron .25)
NDREAM_TRINITY_333_sdxlvae_fp32   (FINAL + Gen_Vyron + V3, cada uno 1/3)
NDREAM_TUG_FINAL_50_50_sdxlvae_fp32(TRI_ULTRA_GEN .50 + FINAL .50)
NDREAM_ULTRA.safetensors = NDREAM_FINAL_60_20_20 convertido a fp16 (7.27GB, VAE horneado) ← publicado/nombre final
```

## Scripts
Cada merge se hizo con un script dedicado en `F:/Modelos/checkpoints/merge_*.py`
(patrón: load 2-3 modelos, suma ponderada de tensores coincidentes por shape,
conservar first_stage_model.* de la base, `st.save_file`). El script genérico
`merge_checkpoints.py` del skill cubre el mismo patrón.

## Pitfalls confirmados esta sesión
- **Disco se llena**: cada merge fp32 ~14GB. `os error 112 Espacio en disco insuficiente`
  ocurre al guardar si `df -h /f` muestra <14GB libres. Liberar merges intermedios
  (los que ya se integraron a uno mayor) antes de seguir encadenando.
- **fp32 → fp16**: para un modelo que ya solo se genera (no se mergea más), reducir a
  la mitad con `{k: (v if k.startswith('first_stage_model') else v.half())}`. Resultado
  `NDREAM_ULTRA.safetensors` 7.27GB, VAE conservado fp32.
- **Nombres**: Gio a veces da nombres aproximados; SIEMPRE confirmar con `ls *.safetensors`
  antes de asumir qué archivo existe (ej. "ULTRA AIO" vs "infinityULTRAAIO" era el mismo).
- **"ULTRA AIO" / "infinityULTRAAIO"** eran el mismo archivo — preguntar al usuario
  cuando la lista parezca duplicada.
