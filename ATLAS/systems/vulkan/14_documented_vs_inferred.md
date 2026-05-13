---
atlas_package: system
system_slug: vulkan
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Documented vs inferred

## DOCUMENTED

**Khronos** **registry** **spec** **+** **vulkan.org** **landing** **+** **SPIR-V** **consumption** **for** **shader** **modules**.

## INFERRED

- **Host** **OS** **integration** **(Linux** **/** **Windows)** **—** **loader** **/** **ICD** **pattern** **without** **per**-**package** **kernel** **claims** **here**.

## Open questions

1. **Which** **extensions** **(ray** **tracing,** **mesh** **shaders,** **…)** **are** **load**-**bearing** **for** **your** **deployment?**  
2. **Add** **Metal** **/** **Direct3D** **packages** **if** **ION** **wants** **explicit** **`competes_with`** **edges** **(not** **modeled** **here** **yet).**
