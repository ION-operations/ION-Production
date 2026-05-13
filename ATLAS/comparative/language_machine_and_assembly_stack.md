# Comparative: Machine languages, assembly, and high-level languages

**Atlas scope:** How **executable intent** is represented from **silicon** through **human-maintained source** — vocabulary for comparing packages like `pl-i`, `fortran`, `c-language`, `cobol`, kernels, and toolchains.  
**Evidence:** Cells reference ATLAS packages where they exist; otherwise tier per footnote.

---

## 1. Machine languages (machine code / object code)

| Concept | Definition (operational) | Typical evidence tier |
|---------|--------------------------|------------------------|
| **Instruction** | Bit pattern the CPU decodes as an operation + operands | DOCUMENTED (ISA manual) |
| **ISA** | Contract between **microarchitecture** and **software** — opcodes, registers, memory model | DOCUMENTED (vendor manual / Vol. 2 for x86) |
| **Object / relocatable** | Machine code + **relocation** metadata for linking | DOCUMENTED (ABI docs) |
| **Position-independent code (PIC)** | Machine + indirection patterns for shared libraries | DOCUMENTED (ABI) |
| **RISC-V (open ISA)** | Modular ISA: base integer profiles + ratified extensions (`I`, `M`, `A`, `F`, `D`, …) | DOCUMENTED (`riscv-isa` package; RISC-V International specs) |

**Atlas packages:** OS kernels (`linux-kernel`, `xnu-macos`, …) **host** machine code; they are not “machine languages” themselves — link at **ISA** boundary.

---

## 2. Assembly languages

| Concept | Definition | Notes |
|---------|------------|-------|
| **Symbolic assembly** | Mnemonics + directives → assembler → machine code | DOCUMENTED (assembler manual) |
| **Macro assemblers** | Textual macros before expansion | DOCUMENTED (e.g. historic mainframe culture) |
| **Inline assembly** | HLL embedding of asm fragments | DOCUMENTED (compiler docs) |

**Relation to HLL:** Assembly is **1:1 region** of the stack closest to **ISA**; compilers for **PL/I**, **C**, **Fortran** **lower** through internal IR to assembly or machine (`INFERRED` pipeline shape; **DOCUMENTED** per compiler).

---

## 3. High-level languages (families)

| Family | Example slugs / notes | Typical design force |
|--------|------------------------|----------------------|
| **Scientific / formula** | **Fortran** (`systems/fortran`) | Arrays, numerics, long ISO lineage |
| **Business / record** | **COBOL** (`systems/cobol`) | Records, reports, decimal arithmetic |
| **Algol family** | **ALGOL** (`systems/algol`) | Blocks, BNF-era specification culture, 60 vs 68 split |
| **Teaching / structured** | **Pascal** (`systems/pascal-language`) | Small language, ISO 7185, Wirth lineage |
| **Algol-like block** | **PL/I** (`systems/pl-i`) | Block structure, exceptions, unified domains |
| **Systems / low-level** | **C** (`systems/c-language`) | Manual memory, ABI, kernel/toolchain anchor |
| **Memory-safe systems** | **Rust** (`systems/rust-language`) | Ownership, LLVM backend, kernel Rust |
| **Safety-critical / embedded HLL** | **Ada** (`systems/ada-language`) | Tasks, strong typing, ISO 8652 |
| **GC + CSP concurrency** | **Go** (`systems/golang`) | Goroutines/channels, cloud-native tooling |
| **Concurrent CSP-flavored** | Limbo (`systems/inferno-os`) | Channels / processes (survey) |
| **Managed / VM** | **JVM** (`jvm`), **ECMA-335 CLI** (`ecma-335-cli`) | Verified bytecode + runtime (CLR / .NET implements CLI) |
| **Portable sandbox module** | **WebAssembly** (`webassembly`) | W3C core binary format; host embeddings (browser, wasmtime, …) |

---

## 4. Compilation and linkage model (cross-cutting)

```
Source (PL/I, C, …) → front-end → IR → code gen → assembly / object → linker → load image → CPU
```

| Stage | Failure mode | Atlas discipline |
|-------|--------------|------------------|
| Lex/parse | Syntax errors | DOCUMENTED grammar |
| Semantic | Type errors | DOCUMENTED typing rules |
| Codegen | Wrong opcode | OBSERVED test or formal verification |
| Link | Missing symbol | DOCUMENTED ABI |

---

## 5. Compiler IR and debug formats

| Artifact | Atlas slug | Role |
|----------|------------|------|
| **LLVM IR** | `llvm-ir` | SSA-style intermediate representation between language front ends and backends ([LLVM LangRef](https://llvm.org/docs/LangRef.html)). |
| **DWARF** | `dwarf` | Debugging information in object files (line tables, types, unwind) ([DWARF committee](https://dwarfstd.org/)). |
| **ELF** | `elf` | Executable / shared object / relocatable **container** on Unix-class systems; carries machine code and (often) DWARF sections ([TIS ELF / gABI via Linux Foundation refspecs](https://refspecs.linuxfoundation.org/)). |
| **GNU Binutils** | `gnu-binutils` | **as** / **ld** / **readelf** / **objdump** / **ar** / **nm** / **objcopy** / **strip** — toolchain that **materializes** and **inspects** ELF (and archives); pairs with **GCC** on typical GNU/Linux flows ([GNU Binutils](https://www.gnu.org/software/binutils/)). |
| **LLVM lld** | `llvm-lld` | LLVM **linker**; **ELF** / **COFF** / **Wasm** (etc.) per build; competes with **GNU ld** in many **clang**/**rustc** stacks ([lld.llvm.org](https://lld.llvm.org/)). |
| **Clang** | `clang` | LLVM **C/C++ frontend** + **`clang`** driver → **LLVM IR** → backend → **as**/**ld** or **lld** ([clang.llvm.org](https://clang.llvm.org/)). |
| **GNU GCC** | `gnu-gcc` | **gcc**/**g++** + **GIMPLE**/RTL pipeline → **GNU as**/**GNU ld** (**`gnu-binutils`**) on typical GNU/Linux ([gcc.gnu.org](https://gcc.gnu.org/)). |
| **GNU GDB** | `gnu-gdb` | **gdb** / **gdbserver** — consumes **DWARF** in **ELF**, **MI** for IDEs; often behind **DAP** adapters ([GNU GDB](https://www.gnu.org/software/gdb/)). |
| **LLDB** | `lldb` | LLVM **debugger**; **Clang**-aligned; **SB API**; **lldb-dap** / adapters — **`competes_with`** **GDB** on Linux ([lldb.llvm.org](https://lldb.llvm.org/)). |
| **GNU C Library** | `glibc` | **C**/**POSIX** **userland** **runtime** + **dynamic** **linker** on **GNU/Linux**; **`competes_with`** **`musl`**, **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`android-bionic`**, **`newlib`**, **`wasi-libc`**, **`uclibc`**, **`dietlibc`** (INFERRED); **`integrates_with`** **`linux-kernel`**, **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`c-language`** ([GNU libc manual](https://www.gnu.org/software/libc/manual/)). |
| **musl libc** | `musl` | **Lightweight** **Linux** **libc**; **`competes_with`** **`glibc`**, **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`android-bionic`**, **`newlib`**, **`wasi-libc`**, **`uclibc`**, **`dietlibc`** (INFERRED); **`integrates_with`** **`linux-kernel`**, **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`c-language`**, **`docker`** (INFERRED) ([musl.libc.org](https://musl.libc.org/)). |
| **FreeBSD libc** | `freebsd-libc` | **FreeBSD** **base** **libc**; **`integrates_with`** **`freebsd`**, **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`c-language`**, **`clang`** (INFERRED); **`competes_with`** **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`android-bionic`**, **`newlib`**, **`wasi-libc`**, **`uclibc`**, **`dietlibc`** (INFERRED) ([FreeBSD Handbook](https://docs.freebsd.org/en/books/handbook/bibliography/)). |
| **OpenBSD libc** | `openbsd-libc` | **OpenBSD** **base** **libc**; **`competes_with`** **`freebsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`android-bionic`**, **`newlib`**, **`wasi-libc`**, **`uclibc`**, **`dietlibc`** (INFERRED); **`integrates_with`** **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`c-language`**, **`clang`** (INFERRED) ([OpenBSD FAQ](https://www.openbsd.org/faq/)). |
| **NetBSD libc** | `netbsd-libc` | **NetBSD** **base** **libc**; **`competes_with`** **`freebsd-libc`**, **`openbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`android-bionic`**, **`newlib`**, **`wasi-libc`**, **`uclibc`**, **`dietlibc`** (INFERRED); **`integrates_with`** **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`c-language`**, **`clang`** (INFERRED) ([NetBSD Guide](https://www.netbsd.org/docs/guide/en/)). |
| **DragonFly libc** | `dragonfly-libc` | **DragonFly** **base** **libc**; **`competes_with`** **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`illumos-libc`**, **`android-bionic`**, **`newlib`**, **`wasi-libc`**, **`uclibc`**, **`dietlibc`** (INFERRED); **`integrates_with`** **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`c-language`**, **`clang`** (INFERRED) ([DragonFly Handbook](https://www.dragonflybsd.org/docs/handbook/)). |
| **illumos libc** | `illumos-libc` | **illumos** **core** **libc** **(Solaris/ON** **lineage)**; **`competes_with`** **`glibc`**, **`musl`**, **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`android-bionic`**, **`newlib`**, **`wasi-libc`**, **`uclibc`**, **`dietlibc`** (INFERRED); **`integrates_with`** **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`c-language`**, **`clang`** (INFERRED) ([illumos developer guide](https://illumos.org/books/dev/intro.html)). |
| **Android Bionic** | `android-bionic` | **Android** **Bionic** **libc**; **`integrates_with`** **`android-aosp`**, **`linux-kernel`**, **`elf`**, **`c-language`**, **`clang`** (INFERRED), **`llvm-libcxx`** (INFERRED); **`competes_with`** **`glibc`**, **`musl`**, **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`newlib`**, **`wasi-libc`**, **`uclibc`**, **`dietlibc`** (INFERRED) ([AOSP platform/bionic](https://android.googlesource.com/platform/bionic/+/refs/heads/main/README.md)). |
| **newlib** | `newlib` | **Embedded** **GCC** **libc**; **`integrates_with`** **`c-language`**, **`elf`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED), **`riscv-isa`** (INFERRED); **`competes_with`** **`glibc`**, **`musl`**, **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`android-bionic`**, **`wasi-libc`**, **`uclibc`**, **`dietlibc`** (INFERRED) ([Sourceware newlib](https://sourceware.org/newlib/)). |
| **wasi-libc** | `wasi-libc` | **WASI** **C** **library** **for** **wasm32-wasi**; **`integrates_with`** **`wasi`**, **`webassembly`**, **`c-language`**, **`clang`**, **`llvm-lld`**, **`wasm-component-model`** (INFERRED); **`competes_with`** **`glibc`**, **`musl`**, **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`android-bionic`**, **`newlib`**, **`uclibc`**, **`dietlibc`** (INFERRED) ([wasi-libc](https://github.com/WebAssembly/wasi-libc)). |
| **uClibc-ng** | `uclibc` | **Small** **Linux** **libc** **(embedded** **GNU/Linux)**; **`integrates_with`** **`linux-kernel`**, **`elf`**, **`c-language`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED); **`competes_with`** **`glibc`**, **`musl`**, **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`android-bionic`**, **`newlib`**, **`wasi-libc`**, **`dietlibc`** (INFERRED) ([uClibc-ng](https://uclibc-ng.org/)). |
| **dietlibc** | `dietlibc` | **Minimal** **Linux** **libc** **(static-friendly)**; **`integrates_with`** **`linux-kernel`**, **`elf`**, **`c-language`**, **`gnu-gcc`**, **`gnu-binutils`**, **`clang`** (INFERRED); **`competes_with`** **`glibc`**, **`musl`**, **`freebsd-libc`**, **`openbsd-libc`**, **`netbsd-libc`**, **`dragonfly-libc`**, **`illumos-libc`**, **`android-bionic`**, **`newlib`**, **`wasi-libc`**, **`uclibc`** (INFERRED) ([dietlibc](https://www.fefe.de/dietlibc/)). |
| **MSVC UCRT / VCRUNTIME** | `msvc-vcruntime` | **Windows** **UCRT** **+** **`VCRUNTIME*.dll`** **hosted** **C** **runtime** **DLLs**; **`integrates_with`** **`windows-nt`**, **`c-language`**, **`clang`** (INFERRED), **`msvcprt`** ([CRT features](https://learn.microsoft.com/en-us/cpp/c-runtime-library/crt-library-features)). |
| **GNU libstdc++** | `gnu-libstdcxx` | **GCC** **C++** **standard** **library**; **`integrates_with`** **`gnu-gcc`**, **`glibc`**, **`musl`** (INFERRED), **`freebsd-libc`** (INFERRED), **`openbsd-libc`** (INFERRED), **`netbsd-libc`** (INFERRED), **`dragonfly-libc`** (INFERRED), **`illumos-libc`** (INFERRED), **`android-bionic`** (INFERRED), **`newlib`** (INFERRED), **`wasi-libc`** (INFERRED), **`uclibc`** (INFERRED), **`dietlibc`** (INFERRED), **`elf`**, **`gnu-binutils`**, **`dwarf`**; **`competes_with`** **`llvm-libcxx`**, **`msvcprt`** (INFERRED) ([libstdc++ manual](https://gcc.gnu.org/onlinedocs/libstdc++/)). |
| **LLVM libc++** | `llvm-libcxx` | **LLVM** **C++** **standard** **library**; **`integrates_with`** **`llvm-libcxxabi`**, **`clang`**, **`llvm-lld`**, **`glibc`**, **`musl`** (INFERRED), **`freebsd-libc`** (INFERRED), **`openbsd-libc`** (INFERRED), **`netbsd-libc`** (INFERRED), **`dragonfly-libc`** (INFERRED), **`illumos-libc`** (INFERRED), **`android-bionic`** (INFERRED), **`newlib`** (INFERRED), **`wasi-libc`** (INFERRED), **`uclibc`** (INFERRED), **`dietlibc`** (INFERRED), **`elf`**, **`gnu-binutils`**, **`dwarf`**, **`lldb`**; **`competes_with`** **`gnu-libstdcxx`**, **`msvcprt`** (INFERRED) ([libc++](https://libcxx.llvm.org/)). |
| **MSVC C++ runtime** | `msvcprt` | **Windows** **`msvcp*.dll`** **C++** **stdlib** **runtime**; **`integrates_with`** **`windows-nt`**, **`msvc-vcruntime`**, **`c-language`**; **`competes_with`** **`gnu-libstdcxx`**, **`llvm-libcxx`** (INFERRED) ([C++ standard library](https://learn.microsoft.com/en-us/cpp/standard-library/cpp-standard-library-reference)). |
| **LLVM libc++abi** | `llvm-libcxxabi` | **Itanium** **C++** **ABI** **runtime** paired **with** **`llvm-libcxx`**; **`integrates_with`** **`llvm-libcxx`**, **`clang`**, **`llvm-lld`**, **`glibc`**, **`musl`** (INFERRED), **`freebsd-libc`** (INFERRED), **`openbsd-libc`** (INFERRED), **`netbsd-libc`** (INFERRED), **`dragonfly-libc`** (INFERRED), **`illumos-libc`** (INFERRED), **`android-bionic`** (INFERRED), **`newlib`** (INFERRED), **`wasi-libc`** (INFERRED), **`uclibc`** (INFERRED), **`dietlibc`** (INFERRED), **`gnu-binutils`**, **`elf`**, **`dwarf`**, **`c-language`** (INFERRED), **`gnu-gdb`** (INFERRED), **`lldb`**, **`riscv-isa`** ([libc++abi](https://libcxxabi.llvm.org/)). |

**GPU-distinct IR / virtual ISAs** (not §1 CPU machine code; not the same linkage model as desktop objects):

| Artifact | Atlas slug | Role |
|----------|------------|------|
| **SPIR-V** | `spir-v` | Khronos binary IR consumed by **Vulkan** (`vulkan`), optional **OpenGL** (`opengl`) 4.6-era ingest, and OpenCL-class pipelines ([registry](https://registry.khronos.org/SPIR-V/)). |
| **NVIDIA PTX** | `nvidia-ptx` | NVIDIA virtual ISA consumed by CUDA toolchains / drivers ([PTX manual](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html)). |

**Typical CPU pipeline:** Source (C, Rust, …) → **LLVM IR** (Clang/rustc paths) → object code + **DWARF** sections → linker → load image.

**Typical GPU paths:** High-level shader or CUDA source → **SPIR-V** and/or **PTX** → driver / proprietary lowering → GPU machine ISA (vendor-specific; out of scope for this comparative unless a package exists).

**Cross-vendor parallel compute API:** **OpenCL** (`opencl`) — Khronos **host** **/** **device** **API** for heterogeneous compute ([OpenCL](https://www.khronos.org/opencl/)); **`integrates_with`** **`spir-v`** (SPIR-V IL in **2.1+** **tracks**); **`competes_with`** **`nvidia-cuda`** (INFERRED); **`integrates_with`** **`amd-rocm`** (AMD OpenCL implementations).

**Khronos C++ heterogeneous model:** **SYCL** (`sycl`) — **single**-**source** **C++** **for** **accelerators** ([SYCL](https://www.khronos.org/sycl/), [registry](https://registry.khronos.org/SYCL/)); **`integrates_with`** **`opencl`** **/** **`llvm-ir`** (INFERRED); **`integrates_with`** **`level-zero`** (INFERRED, Intel GPU stacks); **`competes_with`** **`nvidia-cuda`** (INFERRED); **`spir-v`** **may** **appear** **on** **some** **LLVM** **GPU** **lowerings** (**INFERRED**, **implementation**-**dependent**).

**oneAPI low-level GPU API:** **Level** **Zero** (`level-zero`) — **C** **API** **for** **devices,** **queues,** **and** **modules** ([spec](https://oneapi-src.github.io/level-zero-spec/), [SPIR-V guide](https://oneapi-src.github.io/level-zero-spec/level-zero/latest/core/SPIRV.html)); **`integrates_with`** **`spir-v`** (DOCUMENTED); **`integrates_with`** **`sycl`** (INFERRED); **`linux-kernel`** **/** **`windows-nt`** (INFERRED).

**Cross-vendor graphics + compute API:** **Vulkan** (`vulkan`) — Khronos **GPU** **API** ([Vulkan](https://www.vulkan.org/), [spec registry](https://registry.khronos.org/vulkan/)); **`depends_on`** **`spir-v`** **for** **shader** **modules** (DOCUMENTED).

**Cross-vendor legacy graphics API:** **OpenGL** (`opengl`) — Khronos **state**-**machine** **graphics** **API** ([OpenGL](https://www.khronos.org/opengl/), [registry](https://registry.khronos.org/OpenGL/)); **primary** **shaders** **via** **GLSL;** **`integrates_with`** **`spir-v`** **on** **the** **4.6** **SPIR-V** **extension** **track** (DOCUMENTED); **`competes_with`** **`vulkan`** (INFERRED).

**Embedded** **/** **mobile** **GL** **profile:** **OpenGL** **ES** (`opengl-es`) — **Khronos** **subset** **for** **constrained** **devices** ([OpenGL ES](https://www.khronos.org/opengles/), [ES 3.2 registry](https://registry.khronos.org/OpenGL/specs/es/3.2/)); **`integrates_with`** **`opengl`** **/** **`webgl`** (INFERRED); **`competes_with`** **`vulkan`** (INFERRED).

**Apple platform GPU API:** **Metal** (`metal`) — **graphics** **+** **compute** **on** **Apple** **GPUs** ([Metal](https://developer.apple.com/metal/)); **`integrates_with`** **`xnu-macos`** (DOCUMENTED); **`competes_with`** **`vulkan`** **/** **`opengl`** (INFERRED); **native** **shaders** **via** **MSL** **(not** **SPIR-V** **as** **the** **primary** **documented** **IR** **surface).**

**Windows platform GPU API:** **Direct3D** (`direct3d`) — **Microsoft** **graphics** **/** **compute** **API** **family** **(Direct3D** **12** **grain)** ([Direct3D 12](https://learn.microsoft.com/en-us/windows/win32/direct3d12/)); **`integrates_with`** **`windows-nt`** (DOCUMENTED); **`competes_with`** **`vulkan`** **/** **`opengl`** **/** **`metal`** (INFERRED); **shaders** **via** **HLSL** **→** **DXIL** **on** **documented** **D3D12** **paths** **(not** **SPIR-V**-**native).**

**GPU vendor compute stacks** (ecosystem grain — not the same as IR rows above):

| Stack | Atlas slug | Role |
|-------|------------|------|
| **NVIDIA PTX (ISA doc)** | `nvidia-ptx` | Virtual ISA / assembly-level IR ([PTX manual](https://docs.nvidia.com/cuda/parallel-thread-execution/index.html)); **`integrates_with`** **`nvidia-cuda`**. |
| **NVIDIA CUDA (platform)** | `nvidia-cuda` | Toolkit, runtime, libraries ([CUDA docs](https://docs.nvidia.com/cuda/)); **`integrates_with`** **`nvidia-ptx`**; **`competes_with`** **`amd-rocm`** (INFERRED). |
| **AMD ROCm** | `amd-rocm` | Open **HIP** + **ROCm** **libraries** + **Linux** **tooling** ([ROCm docs](https://rocm.docs.amd.com/)); **`competes_with`** **`nvidia-cuda`** (INFERRED). |

**Note:** **`nvidia-ptx`** **≠** **`nvidia-cuda`** **(IR** **spec** **vs** **full** **platform)**; **`amd-rocm`** **is** **the** **AMD** **stack** **peer** **to** **`nvidia-cuda`**, **not** **to** **PTX** **alone**. **§8** **still** **tracks** **undocumented** **vendor** **machine** **ISA** **encoding** **(e.g.** **SASS)**.

---

## 6. Managed VMs and portable modules (Java / .NET / Wasm)

| Platform | Atlas slug | Role |
|----------|------------|------|
| **JVM** | `jvm` | Java **bytecode**, **class** **files**, **JVM** **specification** ([Oracle JVM spec](https://docs.oracle.com/javase/specs/jvms/se21/html/index.html)). |
| **ECMA-335 CLI** | `ecma-335-cli` | **CIL**, **metadata**, **assemblies**; **CLR** **implements** **the** **CLI** **on** **.NET** ([ECMA-335](https://www.ecma-international.org/publications-and-standards/standards/ecma-335/)). |
| **WebAssembly** | `webassembly` | **Sandboxed** **binary** **module** **format** **(W3C** **core** **spec)** ([W3C Wasm Core 2](https://www.w3.org/TR/wasm-core-2/)); often produced via **LLVM**-based toolchains (`INFERRED` edge to `llvm-ir`). |

**Relation:** `jvm` **`competes_with`** `ecma-335-cli` at **ecosystem** **level** (INFERRED — many substitutable server/desktop stacks); **not** equivalent instruction sets. **WebAssembly** **differs** **from** **both** **(linear** **memory,** **module** **imports/exports,** **browser/edge** **hosts).**

### Wasm host extensions (beyond core Wasm)

| Extension | Atlas slug | Role |
|-----------|------------|------|
| **WASI** | `wasi` | **System** **imports** (files, clocks, sockets, …) — [wasi.dev](https://wasi.dev/) / [WebAssembly/WASI](https://github.com/WebAssembly/WASI). **`depends_on`** **`webassembly`**. |
| **Component Model** | `wasm-component-model` | **WIT**, **packages**, **typed** **composition** — [Bytecode Alliance book](https://component-model.bytecodealliance.org/). **`depends_on`** **`webassembly`**; **`integrates_with`** **`wasi`** (INFERRED). |

**Web** **platform** **GPU** **(browser):** **WebGPU** (`webgpu`) — **W3C** **GPU** **API** **+** **WGSL** ([WebGPU](https://www.w3.org/TR/webgpu/), [WGSL](https://www.w3.org/TR/WGSL/)); **`integrates_with`** **`webassembly`** (INFERRED); **`integrates_with`** **`vulkan`** **/** **`metal`** **/** **`direct3d`** **/** **`spir-v`** **on** **native** **backends** (**INFERRED**, **implementation**-**dependent**).

**Legacy** **browser** **GPU** **(Khronos):** **WebGL** (`webgl`) — **OpenGL** **ES**-**class** **API** **for** **canvas** **/** **JavaScript** ([WebGL](https://www.khronos.org/webgl/), [WebGL 2.0 spec](https://registry.khronos.org/webgl/specs/latest/2.0/)); **`integrates_with`** **`opengl`** **/** **`webassembly`** (INFERRED); **`competes_with`** **`webgpu`** (INFERRED).

---

## 7. PL/I in this stack

**PL/I** (`systems/pl-i`) is a **large** **HLL** aimed at **unifying** scientific and commercial programming on **System/360-class** systems (`HISTORICAL`, `src-wiki-pl-i`). It is **not** machine language; it **targets** machine code via **vendor compilers**.

| Dimension | PL/I |
|-----------|------|
| **Distance from ISA** | High — programmer rarely writes asm |
| **Memory model** | Language + implementation (`UNKNOWN` per platform without manual) |
| **I/O** | Language-level stream/record (`DOCUMENTED` summaries) |

---

## 8. Open gaps (honest)

- **Vendor** **GPU** **machine** **ISAs** **(e.g.** **NVIDIA** **SASS,** **AMD** **RDNA/CDNA** **machine** **encoding)** — **proprietary** **/** **incompletely** **public**; **distinct** **from** **`spir-v`**, **`nvidia-ptx`,** **and** **`amd-rocm`** **(IR** **/** **virtual** **ISA** **/** **software** **stack** **surfaces)**.

---

## Forbidden merges

- Calling **PL/I** “assembly” because it is old.  
- Treating **one** vendor’s codegen as **the** language semantics without standard text.
