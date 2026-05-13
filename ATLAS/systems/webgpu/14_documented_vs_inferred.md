---
atlas_package: system
system_slug: webgpu
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

**W3C** **WebGPU** **+** **WGSL** **TR** **text.**

## INFERRED

- **Exact** **native** **backend** **(Vulkan** **vs** **Metal** **vs** **D3D12)** **per** **browser** **build.**

## Open questions

1. **Separate** **`wgsl`** **package** **if** **shader** **language** **taxonomy** **needs** **independence** **from** **`webgpu`.**  
2. **`webgl`** **package** **for** **explicit** **legacy** **browser** **GL** **/** **`opengl-es`** **grain.**
