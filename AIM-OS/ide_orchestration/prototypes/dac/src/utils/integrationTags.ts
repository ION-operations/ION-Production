/**
 * Integration Tag Helpers
 * Converts chat/IDE orchestration metadata into standardized tag payloads.
 */

export type IntegrationPriority =
  | 'critical'
  | 'important'
  | 'routine'
  | 'low_stakes'
  | 'p0'
  | 'p1'
  | string

export interface IntegrationSystem {
  name: string
  priority?: IntegrationPriority
}

export interface IntegrationTagContext {
  system?: IntegrationSystem
  integrationType?: string
  connection?: string
  modality?: string
  /**
   * Action identifier (e.g., "code_generation", "research_query").
   */
  action?: string
  /**
   * Active thinking mode (research, execution, synthesis, planning, etc.).
   */
  mode?: string
  /**
   * Active drawer / agent identity (coding, planning, emotional, etc.).
   */
  agent?: string
  /**
   * Additional raw tags (chat_ide, session ids, etc.).
   */
  extras?: string[]
}

const REQUIRED_BASE_TAG = 'chat_ide'

/**
 * Build the canonical list-based tag payload given orchestration context.
 */
export function buildIntegrationTags(context: IntegrationTagContext): string[] {
  const tags: string[] = []

  if (context.system?.name) {
    const priority = context.system.priority || 'p0'
    tags.push(`system:${context.system.name}:${priority}`)
  }

  if (context.integrationType) {
    tags.push(`integration_type:${context.integrationType}`)
  }

  if (context.connection) {
    tags.push(`connection:${context.connection}`)
  }

  if (context.modality) {
    tags.push(`modality:${context.modality}`)
  }

  // Context tags (lighter weight but always helpful)
  if (context.action) {
    tags.push(`action:${context.action}`)
  }

  if (context.mode) {
    tags.push(`mode:${context.mode}`)
  }

  if (context.agent) {
    tags.push(`agent:${context.agent}`)
  }

  if (context.extras?.length) {
    tags.push(...context.extras.filter(Boolean))
  }

  if (!tags.includes(REQUIRED_BASE_TAG)) {
    tags.push(REQUIRED_BASE_TAG)
  }

  return Array.from(new Set(tags))
}

/**
 * Convert tag list format into CMC weighted dictionary format.
 * Mirrors Atlas' recommendation to weight connections/context slightly lower
 * than system/integration identifiers for HHNI indexing.
 */
export function integrationTagsToDict(tags: string[]): Record<string, number> {
  const weights: Record<string, number> = {}

  for (const tag of tags) {
    let weight = 0.9

    if (tag.startsWith('system:')) {
      weight = 1.0
    } else if (tag.startsWith('integration_type:')) {
      weight = 1.0
    } else if (tag.startsWith('modality:')) {
      weight = 1.0
    } else if (tag.startsWith('connection:')) {
      weight = 0.9
    } else if (tag === REQUIRED_BASE_TAG) {
      weight = 1.0
    } else if (tag.startsWith('action:') || tag.startsWith('mode:') || tag.startsWith('agent:')) {
      weight = 0.85
    } else {
      weight = 0.8
    }

    weights[tag] = weight
  }

  return weights
}

const normalizeExtras = (extras?: string[]): string[] | undefined => {
  if (!extras || !extras.length) return undefined
  const deduped = Array.from(new Set(extras.filter(Boolean)))
  return deduped.length ? deduped : undefined
}

const mergeSystems = (
  base?: IntegrationSystem,
  override?: IntegrationSystem
): IntegrationSystem | undefined => {
  if (!base && !override) {
    return undefined
  }

  return {
    name: override?.name ?? base?.name ?? 'unknown',
    priority: override?.priority ?? base?.priority
  }
}

export function mergeIntegrationContexts(
  base?: IntegrationTagContext | null,
  override?: IntegrationTagContext | null
): IntegrationTagContext | undefined {
  if (!base && !override) {
    return undefined
  }

  const merged: IntegrationTagContext = {
    system: mergeSystems(base?.system, override?.system),
    integrationType: override?.integrationType ?? base?.integrationType,
    connection: override?.connection ?? base?.connection,
    modality: override?.modality ?? base?.modality,
    action: override?.action ?? base?.action,
    mode: override?.mode ?? base?.mode,
    agent: override?.agent ?? base?.agent,
    extras: normalizeExtras([...(base?.extras || []), ...(override?.extras || [])])
  }

  return merged
}

let activeIntegrationContext: IntegrationTagContext | null = null

export function setActiveIntegrationContext(context: IntegrationTagContext | null): void {
  activeIntegrationContext = context
    ? {
        ...context,
        system: context.system ? { ...context.system } : undefined,
        extras: normalizeExtras(context.extras)
      }
    : null
}

export function getActiveIntegrationContext(): IntegrationTagContext | null {
  return activeIntegrationContext
}

/**
 * Merge globally active context, request-specific context, and action overrides.
 */
export function resolveIntegrationContext(
  requestContext?: IntegrationTagContext,
  overrides?: IntegrationTagContext
): IntegrationTagContext | undefined {
  const base = mergeIntegrationContexts(getActiveIntegrationContext(), requestContext)
  return mergeIntegrationContexts(base, overrides)
}
