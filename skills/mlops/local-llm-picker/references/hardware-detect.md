# Hardware detection commands (for local LLM sizing)

Run in terminal, then read GPU name + RAM to pick model/quant.

## Windows (git-bash / MSYS)
```bash
# GPU(s)
wmic path win32_VideoController get name,AdapterRAM
# CPU
wmic cpu get name
# Total RAM (GB)
powershell -NoProfile -Command "(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB"
```
Note: `wmic computersystem get TotalPhysicalMemory` often returns blank in git-bash — use the powershell one-liner.

## Linux
```bash
lspci | grep -i vga
nproc
free -h
```

## macOS
```bash
system_profiler SPHardwareDataType | grep -E "Chip|Memory"
system_profiler SPDisplaysDataType | grep -i "chipset"
```

## Sizing rules
- Dedicated GPU -> check VRAM; pick quant that fits with headroom for KV cache.
- Integrated GPU (Intel Iris Xe / AMD iGPU / Apple) -> model + OS + context all share system RAM. Keep 6-8 GB free for OS.
- Quick fit table (shared RAM, assume 16 GB total, leave 8 GB for OS -> ~8 GB for model+context):
  - 3B Q4 (~2 GB) + 16k ctx -> fine, fast
  - 7B Q4_K_M (~4.5 GB) + 16-32k ctx -> fine, usable
  - 7B Q4 + 128k ctx -> risks OOM on 16 GB
  - 30B MoE Q4 (~18 GB) -> does NOT fit 16 GB shared; needs Q3 + CPU offload (slow) or 24 GB+
