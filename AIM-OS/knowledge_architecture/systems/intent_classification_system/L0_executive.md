# L0 Executive Summary - Intent Classification System

## Problem Solved
The current `IntentType` enum is misaligned with Aether's capabilities, leading to "code monkey" behavior where Aether assumes every request is execution-phase work. This prevents proper classification of complex missions like "design an entirely new product" or "figure out what this app even is."

## Solution
Multi-axis `MissionIntent` model that classifies intent across multiple dimensions:
- **Primary Category**: 13 categories from `new_system_design` to `research_probe`
- **Lifecycle Stage**: `ideation` → `architecture` → `implementation` → `integration` → `hardening` → `stabilization` → `deprecation`
- **Scope Level**: `local_function` → `single_module` → `multi_service` → `whole_platform`
- **Clarity State**: `exploratory` → `partially_defined` → `fully_defined`
- **Facets**: Contextual tags for targeted L0-L4 documentation loading

## Key Features
- **Behavior Gating**: Determines allowed actions based on mission profile
- **Risk Assessment**: Generates stop conditions and escalation triggers
- **Mission Management**: Tracks status, supersession, and concurrency
- **Timeline Integration**: Creates audit trails and learning opportunities
- **Enforcement Layer**: Prevents unauthorized actions with confidence-gated controls

## Impact
Enables Aether to operate as a conscious, self-governing entity rather than a simple code generator. Provides proper safety controls, audit capabilities, and mission continuity across sessions.

## Status
Architecture phase complete. Ready for implementation planning.
