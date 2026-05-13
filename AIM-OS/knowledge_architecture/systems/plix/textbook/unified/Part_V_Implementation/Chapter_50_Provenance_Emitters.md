# Chapter 50: Provenance Emitters: PROV/OpenLineage

**Part:** V - Implementation  
**Chapter:** 50  
**Target Word Count:** 2,000-2,500 words  
**Status:** ✅ **COMPLETE** (Unified Textbook v1.0)

---

## Section 50.1: PROV-JSON Emission

PROV-JSON emission transforms PLIx execution traces into W3C PROV standard format, enabling standardized provenance tracking and interoperability.

**PROV Standard Overview**

W3C PROV provides:

- **Entities:** Things that exist (inputs, outputs, artifacts)
- **Activities:** Actions that occur (execution steps, transformations)
- **Agents:** Actors that perform activities (agents, tools, users)
- **Relations:** How entities relate (used, generated, attributed)

PROV enables standardized provenance representation, supporting interoperability and verification.

**PROV-JSON Structure**

PROV-JSON structure:

```typescript
interface PROVJSON {
  prefix: Record<string, string>;
  entity: Record<string, Entity>;
  activity: Record<string, Activity>;
  agent: Record<string, Agent>;
  wasGeneratedBy: Record<string, string>;
  used: Record<string, string>;
  wasAttributedTo: Record<string, string>;
  wasDerivedFrom: Record<string, string>;
}

interface Entity {
  "prov:type": string;
  "prov:value": any;
  "prov:label"?: string;
}

interface Activity {
  "prov:type": string;
  "prov:startTime"?: string;
  "prov:endTime"?: string;
  "prov:label"?: string;
}
```

PROV-JSON structure enables standardized provenance representation.

**PROV Emission Implementation**

PROV emission from PLIx execution:

```typescript
function emitPROV(
  runId: string,
  nodeId: string,
  action: string,
  inputs: Record<string, any>,
  outputs: Record<string, any>,
  agent: string
): PROVJSON {
  const activityId = `act:${runId}.${nodeId}`;
  const entityInId = `ent:${runId}.${nodeId}.in`;
  const entityOutId = `ent:${runId}.${nodeId}.out`;
  const agentId = `agent:${agent}`;
  
  return {
    prefix: {
      "prov": "http://www.w3.org/ns/prov#",
      "act": `urn:activity:${runId}:`,
      "ent": `urn:entity:${runId}:`,
      "agent": "urn:agent:"
    },
    entity: {
      [entityInId]: {
        "prov:type": "Input",
        "prov:value": inputs,
        "prov:label": `Input for ${action}`
      },
      [entityOutId]: {
        "prov:type": "Output",
        "prov:value": outputs,
        "prov:label": `Output from ${action}`
      }
    },
    activity: {
      [activityId]: {
        "prov:type": action,
        "prov:startTime": new Date().toISOString(),
        "prov:label": `Execute ${action}`
      }
    },
    agent: {
      [agentId]: {
        "prov:type": "SoftwareAgent",
        "prov:label": agent
      }
    },
    wasGeneratedBy: {
      [entityOutId]: activityId
    },
    used: {
      [activityId]: entityInId
    },
    wasAttributedTo: {
      [activityId]: agentId
    }
  };
}
```

PROV emission transforms PLIx execution into PROV-JSON, enabling standardized provenance tracking.

**PROV Chain Building**

PROV chain building for multi-step execution:

```typescript
function buildPROVChain(
  ir: IRPlan,
  executionResults: Record<string, ExecutionResult>
): PROVJSON {
  const prov: PROVJSON = {
    prefix: {
      "prov": "http://www.w3.org/ns/prov#",
      "act": `urn:activity:${ir.intent}:`,
      "ent": `urn:entity:${ir.intent}:`,
      "agent": "urn:agent:"
    },
    entity: {},
    activity: {},
    agent: {},
    wasGeneratedBy: {},
    used: {},
    wasAttributedTo: {},
    wasDerivedFrom: {}
  };
  
  // Emit PROV for each node
  for (const node of ir.nodes) {
    const result = executionResults[node.id];
    const nodePROV = emitPROV(
      ir.intent,
      node.id,
      node.action,
      node.params,
      result.outputs,
      result.agent
    );
    
    // Merge PROV structures
    Object.assign(prov.entity, nodePROV.entity);
    Object.assign(prov.activity, nodePROV.activity);
    Object.assign(prov.agent, nodePROV.agent);
    Object.assign(prov.wasGeneratedBy, nodePROV.wasGeneratedBy);
    Object.assign(prov.used, nodePROV.used);
    Object.assign(prov.wasAttributedTo, nodePROV.wasAttributedTo);
    
    // Add derivation links for dependencies
    for (const dep of node.deps) {
      const depOutputId = `ent:${ir.intent}.${dep}.out`;
      const nodeInputId = `ent:${ir.intent}.${node.id}.in`;
      prov.wasDerivedFrom[nodeInputId] = depOutputId;
    }
  }
  
  return prov;
}
```

PROV chain building creates complete provenance chains, enabling full execution traceability.

**PROV Emission Benefits**

PROV emission provides:

- **Standardized Format:** W3C PROV standard enables interoperability
- **Complete Traces:** Full execution provenance tracking
- **Verification:** Enables provenance verification
- **Interoperability:** Standard format supports tool integration

These benefits enable standardized provenance tracking and verification.

---

## Section 50.2: OpenLineage Events

OpenLineage events provide data lineage tracking for PLIx execution, enabling lineage queries and integration with data platforms.

**OpenLineage Overview**

OpenLineage provides:

- **Job Events:** Job-level lineage (START, COMPLETE, FAIL)
- **Run Events:** Run-level lineage (execution instances)
- **Dataset Events:** Dataset-level lineage (inputs/outputs)
- **Integration:** Integration with data platforms (Spark, Airflow, etc.)

OpenLineage enables data lineage tracking, supporting data governance and compliance.

**OpenLineage Event Structure**

OpenLineage event structure:

```typescript
interface OpenLineageEvent {
  eventType: "START" | "COMPLETE" | "FAIL";
  eventTime: string;
  run: {
    runId: string;
    facets?: Record<string, any>;
  };
  job: {
    namespace: string;
    name: string;
    facets?: Record<string, any>;
  };
  inputs?: Dataset[];
  outputs?: Dataset[];
  producer: string;
}

interface Dataset {
  namespace: string;
  name: string;
  facets?: Record<string, any>;
}
```

OpenLineage event structure enables standardized data lineage tracking.

**OpenLineage Event Emission**

OpenLineage event emission:

```typescript
function emitOpenLineageEvent(
  eventType: "START" | "COMPLETE" | "FAIL",
  jobName: string,
  runId: string,
  inputs?: Dataset[],
  outputs?: Dataset[],
  error?: Error
): OpenLineageEvent {
  return {
    eventType,
    eventTime: new Date().toISOString(),
    run: {
      runId,
      facets: {
        "plix:contract": {
          intent: jobName,
          timestamp: new Date().toISOString()
        }
      }
    },
    job: {
      namespace: "aimos/plix",
      name: jobName,
      facets: {
        "plix:execution": {
          intent: jobName,
          runId
        }
      }
    },
    inputs: inputs || [],
    outputs: outputs || [],
    producer: "plix://v0.1",
    ...(error && {
      run: {
        runId,
        facets: {
          "plix:error": {
            message: error.message,
            stack: error.stack
          }
        }
      }
    })
  };
}

function emitNodeEvent(
  nodeId: string,
  action: string,
  eventType: "START" | "COMPLETE" | "FAIL",
  inputs?: Dataset[],
  outputs?: Dataset[],
  error?: Error
): OpenLineageEvent {
  return emitOpenLineageEvent(
    eventType,
    `${nodeId}:${action}`,
    `${nodeId}_${Date.now()}`,
    inputs,
    outputs,
    error
  );
}
```

OpenLineage event emission provides standardized data lineage events, enabling lineage tracking.

**OpenLineage Integration**

OpenLineage integration with PLIx execution:

```typescript
async function executeWithLineage(
  ir: IRPlan,
  executor: NodeExecutor,
  lineageEmitter: (event: OpenLineageEvent) => Promise<void>
): Promise<ExecutionResult> {
  const runId = `run_${Date.now()}`;
  
  // Emit START event
  await lineageEmitter(emitOpenLineageEvent(
    "START",
    ir.intent,
    runId
  ));
  
  const results: Record<string, any> = {};
  
  try {
    for (const node of ir.nodes) {
      // Emit node START event
      await lineageEmitter(emitNodeEvent(
        node.id,
        node.action,
        "START",
        mapToDatasets(node.params, "input")
      ));
      
      try {
        const output = await executor.exec(node.id, node.action, node.params);
        results[node.id] = output;
        
        // Emit node COMPLETE event
        await lineageEmitter(emitNodeEvent(
          node.id,
          node.action,
          "COMPLETE",
          mapToDatasets(node.params, "input"),
          mapToDatasets(output, "output")
        ));
      } catch (error) {
        // Emit node FAIL event
        await lineageEmitter(emitNodeEvent(
          node.id,
          node.action,
          "FAIL",
          mapToDatasets(node.params, "input"),
          undefined,
          error as Error
        ));
        throw error;
      }
    }
    
    // Emit COMPLETE event
    await lineageEmitter(emitOpenLineageEvent(
      "COMPLETE",
      ir.intent,
      runId,
      mapToDatasets(ir.evidenceRequired, "input"),
      mapToDatasets(ir.evidenceProduce, "output")
    ));
    
    return { results };
  } catch (error) {
    // Emit FAIL event
    await lineageEmitter(emitOpenLineageEvent(
      "FAIL",
      ir.intent,
      runId,
      undefined,
      undefined,
      error as Error
    ));
    throw error;
  }
}

function mapToDatasets(data: any, type: "input" | "output"): Dataset[] {
  // Map data to OpenLineage datasets
  if (typeof data === 'object' && data !== null) {
    return Object.entries(data).map(([key, value]) => ({
      namespace: "aimos/plix",
      name: `${type}:${key}`,
      facets: {
        "dataSchema": {
          fields: [{ name: key, type: typeof value }]
        }
      }
    }));
  }
  return [];
}
```

OpenLineage integration provides complete data lineage tracking for PLIx execution.

**OpenLineage Benefits**

OpenLineage provides:

- **Data Lineage:** Complete data lineage tracking
- **Platform Integration:** Integration with data platforms
- **Governance:** Supports data governance and compliance
- **Standardized Format:** Standard format enables tool integration

These benefits enable comprehensive data lineage tracking and integration.

---

## Section 50.3: SEG Integration

SEG integration stores PROV and OpenLineage events as SEG entities and relations, enabling intent-aware evidence tracking and lineage queries.

**PROV → SEG Integration**

PROV to SEG entity conversion:

```typescript
async function storePROVInSEG(
  prov: PROVJSON,
  seg: SEGraph
): Promise<void> {
  // Store entities as SEG entities
  for (const [entityId, entity] of Object.entries(prov.entity)) {
    const segEntity = new Entity({
      type: "provenance_entity",
      name: entity["prov:label"] || entityId,
      attributes: {
        prov_id: entityId,
        prov_type: entity["prov:type"],
        prov_value: entity["prov:value"]
      }
    });
    
    await seg.add_entity(segEntity);
  }
  
  // Store activities as SEG entities
  for (const [activityId, activity] of Object.entries(prov.activity)) {
    const segEntity = new Entity({
      type: "provenance_activity",
      name: activity["prov:label"] || activityId,
      attributes: {
        prov_id: activityId,
        prov_type: activity["prov:type"],
        prov_start_time: activity["prov:startTime"],
        prov_end_time: activity["prov:endTime"]
      }
    });
    
    await seg.add_entity(segEntity);
  }
  
  // Store relations
  for (const [targetId, sourceId] of Object.entries(prov.wasGeneratedBy)) {
    const sourceEntity = await seg.get_entity_by_attributes({ prov_id: sourceId });
    const targetEntity = await seg.get_entity_by_attributes({ prov_id: targetId });
    
    if (sourceEntity && targetEntity) {
      await seg.add_relation(new Relation({
        source_id: sourceEntity.id,
        target_id: targetEntity.id,
        relation_type: RelationType.DERIVES_FROM,
        attributes: {
          prov_relation: "wasGeneratedBy"
        }
      }));
    }
  }
}
```

PROV to SEG integration stores provenance as SEG entities and relations, enabling graph-based provenance queries.

**OpenLineage → SEG Integration**

OpenLineage to SEG integration:

```typescript
async function storeOpenLineageInSEG(
  event: OpenLineageEvent,
  seg: SEGraph
): Promise<void> {
  // Store job as entity
  const jobEntity = new Entity({
    type: "lineage_job",
    name: event.job.name,
    attributes: {
      namespace: event.job.namespace,
      run_id: event.run.runId,
      event_type: event.eventType,
      event_time: event.eventTime
    }
  });
  
  const jobEntityId = (await seg.add_entity(jobEntity)).id;
  
  // Store datasets as entities
  const datasetEntities: string[] = [];
  
  if (event.inputs) {
    for (const dataset of event.inputs) {
      const datasetEntity = new Entity({
        type: "lineage_dataset",
        name: dataset.name,
        attributes: {
          namespace: dataset.namespace,
          dataset_type: "input"
        }
      });
      
      datasetEntities.push((await seg.add_entity(datasetEntity)).id);
      
      // Link dataset to job
      await seg.add_relation(new Relation({
        source_id: datasetEntity.id,
        target_id: jobEntityId,
        relation_type: RelationType.REFERENCES,
        attributes: {
          lineage_relation: "input"
        }
      }));
    }
  }
  
  if (event.outputs) {
    for (const dataset of event.outputs) {
      const datasetEntity = new Entity({
        type: "lineage_dataset",
        name: dataset.name,
        attributes: {
          namespace: dataset.namespace,
          dataset_type: "output"
        }
      });
      
      const datasetEntityId = (await seg.add_entity(datasetEntity)).id;
      
      // Link job to dataset
      await seg.add_relation(new Relation({
        source_id: jobEntityId,
        target_id: datasetEntityId,
        relation_type: RelationType.DERIVES_FROM,
        attributes: {
          lineage_relation: "output"
        }
      }));
    }
  }
}
```

OpenLineage to SEG integration stores lineage events as SEG entities and relations, enabling lineage queries.

**Intent Lineage Tracking**

Intent lineage tracking in SEG:

```typescript
async function trackIntentLineage(
  contract: PLIxContract,
  executionResult: ExecutionResult,
  prov: PROVJSON,
  seg: SEGraph
): Promise<void> {
  // Store intent as entity
  const intentEntity = new Entity({
    type: "plix_intent",
    name: contract.intent,
    attributes: {
      contract: contract.to_dict(),
      intent_type: "booking"
    }
  });
  
  const intentEntityId = (await seg.add_entity(intentEntity)).id;
  
  // Store outcome as entity
  const outcomeEntity = new Entity({
    type: "plix_outcome",
    name: "Execution Result",
    attributes: {
      results: executionResult.results,
      intent_achieved: executionResult.intent_achieved
    }
  });
  
  const outcomeEntityId = (await seg.add_entity(outcomeEntity)).id;
  
  // Link intent to outcome
  await seg.add_relation(new Relation({
    source_id: intentEntityId,
    target_id: outcomeEntityId,
    relation_type: RelationType.DERIVES_FROM,
    attributes: {
      lineage_type: "intent_to_outcome",
      prov_trace: prov
    }
  }));
  
  // Link PROV activities to intent
  for (const [activityId, activity] of Object.entries(prov.activity)) {
    const activityEntity = await seg.get_entity_by_attributes({ prov_id: activityId });
    if (activityEntity) {
      await seg.add_relation(new Relation({
        source_id: intentEntityId,
        target_id: activityEntity.id,
        relation_type: RelationType.REFERENCES,
        attributes: {
          lineage_type: "intent_to_activity"
        }
      }));
    }
  }
}
```

Intent lineage tracking stores intent-outcome relationships in SEG, enabling intent-driven lineage queries.

**SEG Integration Benefits**

SEG integration provides:

- **Graph-Based Queries:** Graph queries for provenance and lineage
- **Intent Awareness:** Intent-aware evidence tracking
- **Temporal Queries:** Bitemporal queries for evolution tracking
- **Evidence Chains:** Complete evidence chains for verification

These benefits enable comprehensive intent-aware evidence tracking and lineage queries.

---

## Section 50.4: Provenance Queries

Provenance queries enable intent lineage queries, evidence chain queries, and temporal queries, supporting verification and learning.

**Intent Lineage Queries**

Intent lineage queries:

```typescript
async function queryIntentLineage(
  outcomeEntityId: string,
  seg: SEGraph
): Promise<Entity[]> {
  // Find all intents that led to this outcome
  const relations = await seg.query_relations({
    target_id: outcomeEntityId,
    relation_type: RelationType.DERIVES_FROM
  });
  
  const intentEntities: Entity[] = [];
  
  for (const relation of relations) {
    const sourceEntity = await seg.get_entity(relation.source_id);
    if (sourceEntity && sourceEntity.type === "plix_intent") {
      intentEntities.push(sourceEntity);
    }
  }
  
  return intentEntities;
}

async function queryOutcomeLineage(
  intentEntityId: string,
  seg: SEGraph
): Promise<Entity[]> {
  // Find all outcomes from this intent
  const relations = await seg.query_relations({
    source_id: intentEntityId,
    relation_type: RelationType.DERIVES_FROM
  });
  
  const outcomeEntities: Entity[] = [];
  
  for (const relation of relations) {
    const targetEntity = await seg.get_entity(relation.target_id);
    if (targetEntity && targetEntity.type === "plix_outcome") {
      outcomeEntities.push(targetEntity);
    }
  }
  
  return outcomeEntities;
}
```

Intent lineage queries enable tracing outcomes to intents and intents to outcomes, supporting learning.

**Evidence Chain Queries**

Evidence chain queries:

```typescript
async function queryEvidenceChain(
  claimEntityId: string,
  seg: SEGraph
): Promise<Entity[]> {
  // Find all evidence supporting this claim
  const relations = await seg.query_relations({
    target_id: claimEntityId,
    relation_type: RelationType.SUPPORTS
  });
  
  const evidenceEntities: Entity[] = [];
  
  for (const relation of relations) {
    const sourceEntity = await seg.get_entity(relation.source_id);
    if (sourceEntity) {
      evidenceEntities.push(sourceEntity);
      
      // Recursively find evidence for this evidence
      const subEvidence = await queryEvidenceChain(sourceEntity.id, seg);
      evidenceEntities.push(...subEvidence);
    }
  }
  
  return evidenceEntities;
}
```

Evidence chain queries enable complete evidence tracing, supporting verification.

**Temporal Queries**

Temporal queries:

```typescript
async function queryProvenanceAtTime(
  entityId: string,
  timestamp: Date,
  seg: SEGraph
): Promise<Entity | null> {
  // Query entity at specific time
  return await seg.get_entity(entityId, as_of: timestamp);
}

async function queryLineageEvolution(
  intentEntityId: string,
  seg: SEGraph
): Promise<Entity[]> {
  // Query intent evolution over time
  const entities = await seg.query_entities({
    type: "plix_intent",
    attributes_filter: { intent_name: intentEntityId }
  });
  
  // Sort by valid time
  return entities.sort((a, b) => 
    a.vt_start.getTime() - b.vt_start.getTime()
  );
}
```

Temporal queries enable time-travel provenance queries, supporting evolution tracking.

**Provenance Query Benefits**

Provenance queries provide:

- **Intent Lineage:** Trace outcomes to intents
- **Evidence Chains:** Complete evidence tracing
- **Temporal Queries:** Time-travel provenance queries
- **Learning:** Support learning from intent-outcome relationships

These benefits enable comprehensive provenance analysis and learning.

---

## Chapter 50 Summary

Provenance emitters provide PROV-JSON emission, OpenLineage events, SEG integration, and provenance queries. PROV-JSON emission transforms PLIx execution into W3C PROV standard format. OpenLineage events provide data lineage tracking. SEG integration stores provenance as graph entities and relations. Provenance queries enable intent lineage, evidence chains, and temporal queries.

**Next:** Chapter 51 explores policy emission—OPA/Rego integration for constraint enforcement.

---

**Word Count:** ~2,400 words  
**Status:** ✅ **COMPLETE** (Unified Textbook v1.0)

