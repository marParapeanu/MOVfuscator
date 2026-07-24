# x86 Assembly MOVfuscator Engine

> A Python-based source-to-source obfuscator that translates standard x86 Assembly instructions into equivalent code composed purely of single-instruction data transfers (`mov`).

---

## Overview

This project implements a custom **MOVfuscator** engine that parses x86 Assembly input files, locates the `main` entry point, and rewrites individual assembly instructions into functionally equivalent sequences using strictly `mov` operations. 

By utilizing precalculated **256x256 byte-level Look-Up Tables (LUTs)** stored in dedicated memory regions, the engine trades memory usage for execution logic, eliminating traditional arithmetic and branch operations.

---

## Features & Instruction Mapping

* **`add` (Byte-level Look-Up Adder):** 
  Operands are split into 4 bytes and processed sequentially. Registers are cached in dedicated memory locations to allow byte-by-byte extraction. Addition uses a $256 \times 256$ `sum_table` (where `index = row * 256 + col`) and a parallel `carry_table` to propagate carry bits across adjacent bytes.
* **`sub` & `dec`:** 
  Implemented via Two's Complement arithmetic `($A - B = A + (\sim B + 1)$)`. It executes bitwise NOT followed by addition with `$1` using dynamic allocations.
* **`inc`:** 
  Mapped directly to an `add` operation with an immediate operand of `$1`.
* **`mul`:** 
  Iterates through bits 0 to 31 of the smaller operand. If a bit is set, the larger operand value is accumulated into the total sum using repeated lookup additions.
* **`shl` (Shift Left):** 
  Implemented via iterative multiplication by a factor of 2.
* **`and`, `or`, `xor`:** 
  Mapped directly to $256 \times 256$ lookup matrices. Since bitwise operations produce no carry, results are constructed by combining byte results directly.
* **`cmp` & Branching (`jmp`):** 
  Calculates $Op2 - Op1$ byte-by-byte from MSB to LSB using a state machine (`cmp_byte_table` and `transition_table`). 
  * Direct modification of `%eip` via `mov` is unsupported in x86, so control flow is simulated by manipulating the stack pointer (`%esp`) combined with target `ret` instructions.
  * Conditional jumps select target addresses via a `choosing_table` based on the computed boolean flag.
* **`loop`:** 
  Combines register decrement (`ecx`), zero-comparison (`cmp`), and conditional jump (`jne`) logic built from the modules above.
* **`lea`:** 
  Substituted with `mov $operand1, operand2` (used for array base address lookup).
* **`push` & `pop`:** 
  Mapped to stack pointer manipulation (`sub $4, %esp` / `add $4, %esp`) paired with memory assignments.

---

## Known Limitations & Scope

* **Division (`div`) & Shift Right (`shr`):** Excluded due to lookup table complexity; preserved in their original form.
* **System Calls & Library Invocations:** Functions such as `printf` or `fflush` rely on OS kernel interrupts and remain untranslated.
* **Register Dependencies:** Subtraction logic internally utilizes `%edx` for carry calculations; direct subtraction operations involving `%edx` are not supported.

---

## Usage

1. Run the Python translation engine on an assembly source file:
   python final_project.py input.s -o output.s

2. Compile the generated assembly code to produce the output binary:
   gcc -m32 output.s -o binary.out


