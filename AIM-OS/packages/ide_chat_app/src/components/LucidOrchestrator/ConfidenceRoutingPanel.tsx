import React from 'react'
import { Shield, Target, GitBranch, HelpCircle } from 'lucide-react'
import { ConfidenceRoutingSnapshot } from '@/services/confidenceRoutingService'

interface ConfidenceRoutingPanelProps {
  snapshot: ConfidenceRoutingSnapshot | null
  loading?: boolean
  error?: string | null
  onRefresh?: () => void
}

const tierColors = ['emerald', 'blue', 'amber', 'orange', 'rose', 'slate']

export const ConfidenceRoutingPanel: React.FC<ConfidenceRoutingPanelProps> = ({
  snapshot,
  loading = false,
  error = null,
  onRefresh,
}) => {
  return (
    <div className="p-4 space-y-4">
      <header className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Shield className="w-5 h-5 text-emerald-400" />
            Confidence Routing System
          </h3>
          <p className="text-sm text-gray-400">
            Source: {snapshot?.source ?? 'knowledge_architecture/.../confidence_routing.md'}
          </p>
        </div>
        <button
          className="px-3 py-1.5 rounded-lg bg-white/10 text-sm text-white hover:bg-white/20 transition"
          onClick={onRefresh}
          disabled={loading}
        >
          {loading ? 'Refreshing…' : 'Refresh'}
        </button>
      </header>

      {error && (
        <div className="text-amber-300 bg-amber-500/10 border border-amber-500/30 rounded-lg px-3 py-2 text-sm">
          {error}
        </div>
      )}

      <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {(snapshot?.tiers ?? []).map((tier, index) => (
          <article
            key={tier.label}
            className="bg-white/5 rounded-2xl border border-white/10 p-4 space-y-3 shadow-lg shadow-black/20"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-wide text-gray-400">{tier.range}</p>
                <h4 className="text-lg font-semibold text-white">{tier.label}</h4>
              </div>
              <div className={`px-2 py-1 rounded-lg bg-${tierColors[index % tierColors.length]}-500/20 text-xs text-${tierColors[index % tierColors.length]}-200`}>
                {tier.risk}
              </div>
            </div>
            <p className="text-sm text-gray-300">{tier.description}</p>
            <div className="text-sm text-gray-200 space-y-1">
              <p><span className="text-gray-400">Strategy:</span> {tier.strategy}</p>
              <p><span className="text-gray-400">Validation:</span> {tier.validation}</p>
            </div>
            <div>
              <p className="text-xs text-gray-400 mb-1">Examples</p>
              <div className="flex flex-wrap gap-2">
                {tier.examples.map((example) => (
                  <span key={example} className="text-xs text-gray-200 bg-white/10 px-2 py-1 rounded-full">
                    {example}
                  </span>
                ))}
              </div>
            </div>
          </article>
        ))}
      </section>

      <section className="space-y-2">
        <div className="flex items-center gap-2">
          <GitBranch className="w-4 h-4 text-blue-300" />
          <h4 className="text-white font-semibold text-sm">Git Operation Risk Matrix</h4>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {(snapshot?.gitLevels ?? []).map((level) => (
            <article key={level.level} className="bg-white/5 rounded-2xl border border-white/10 p-3 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-white font-semibold">{level.level}</span>
                <span className="text-xs text-gray-400">{level.confidence_threshold}</span>
              </div>
              <p className="text-xs text-gray-300">Strategy: {level.strategy}</p>
              <p className="text-xs text-gray-300">Validation: {level.validation}</p>
              <p className="text-xs text-gray-500">Risk: {level.risk}</p>
              {level.notes && (
                <p className="text-xs text-amber-300 flex items-center gap-1">
                  <HelpCircle className="w-3 h-3" /> {level.notes}
                </p>
              )}
              <div className="flex flex-wrap gap-1">
                {level.examples.map((example) => (
                  <span key={example} className="text-xs text-gray-200 bg-white/10 px-2 py-0.5 rounded-full">
                    {example}
                  </span>
                ))}
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}
