// Deployment Modal - Configure and deploy generated backend
// Supports Docker, Kubernetes, Vercel, Railway, and more

import React, { useState } from 'react'
import { 
  X, Cloud, Server, Box, Zap, CheckCircle, Circle, 
  ArrowRight, Loader2, ExternalLink, Copy, Check,
  AlertTriangle, Terminal, Settings, Lock
} from 'lucide-react'
import { DeploymentConfig } from './types'

interface DeploymentModalProps {
  isOpen: boolean
  onClose: () => void
  onDeploy: (config: DeploymentConfig) => Promise<void>
}

type DeploymentTarget = DeploymentConfig['target']
type DeploymentEnvironment = DeploymentConfig['environment']

interface TargetOption {
  id: DeploymentTarget
  name: string
  description: string
  icon: React.ComponentType<{ className?: string }>
  color: string
  popular?: boolean
}

const DEPLOYMENT_TARGETS: TargetOption[] = [
  { id: 'docker', name: 'Docker', description: 'Container on any host', icon: Box, color: 'from-blue-500 to-blue-600' },
  { id: 'kubernetes', name: 'Kubernetes', description: 'Production cluster', icon: Server, color: 'from-blue-400 to-indigo-600', popular: true },
  { id: 'vercel', name: 'Vercel', description: 'Serverless edge', icon: Zap, color: 'from-gray-600 to-gray-800' },
  { id: 'railway', name: 'Railway', description: 'Simple deployment', icon: Cloud, color: 'from-purple-500 to-purple-700', popular: true },
  { id: 'fly', name: 'Fly.io', description: 'Global edge', icon: Cloud, color: 'from-violet-500 to-purple-600' },
  { id: 'aws', name: 'AWS', description: 'ECS / Lambda', icon: Cloud, color: 'from-orange-500 to-orange-600' },
  { id: 'gcp', name: 'Google Cloud', description: 'Cloud Run', icon: Cloud, color: 'from-blue-500 to-red-500' },
  { id: 'azure', name: 'Azure', description: 'Container Apps', icon: Cloud, color: 'from-blue-600 to-cyan-500' },
]

const ENVIRONMENTS: { id: DeploymentEnvironment; name: string; color: string }[] = [
  { id: 'development', name: 'Development', color: 'bg-blue-500' },
  { id: 'staging', name: 'Staging', color: 'bg-yellow-500' },
  { id: 'production', name: 'Production', color: 'bg-green-500' },
]

export const DeploymentModal: React.FC<DeploymentModalProps> = ({
  isOpen,
  onClose,
  onDeploy,
}) => {
  const [step, setStep] = useState<'target' | 'config' | 'deploying' | 'success'>('target')
  const [selectedTarget, setSelectedTarget] = useState<DeploymentTarget | null>(null)
  const [selectedEnvironment, setSelectedEnvironment] = useState<DeploymentEnvironment>('staging')
  const [isDeploying, setIsDeploying] = useState(false)
  const [deploymentUrl, setDeploymentUrl] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  
  // Target-specific settings
  const [targetSettings, setTargetSettings] = useState<Record<string, any>>({
    // Docker
    registry: 'docker.io',
    imageName: 'my-backend',
    tag: 'latest',
    // Kubernetes
    namespace: 'default',
    replicas: 3,
    ingress: true,
    // Vercel
    regions: ['iad1'],
    // Railway
    autoDeploy: true,
  })

  const handleDeploy = async () => {
    if (!selectedTarget) return
    
    setStep('deploying')
    setIsDeploying(true)
    
    try {
      await onDeploy({
        target: selectedTarget,
        environment: selectedEnvironment,
        settings: targetSettings,
      })
      
      // Simulate deployment URL
      setDeploymentUrl(`https://my-backend-${selectedEnvironment}.railway.app`)
      setStep('success')
    } catch (error) {
      console.error('Deployment failed:', error)
      setStep('config')
    } finally {
      setIsDeploying(false)
    }
  }

  const handleCopyUrl = async () => {
    if (deploymentUrl) {
      await navigator.clipboard.writeText(deploymentUrl)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const resetAndClose = () => {
    setStep('target')
    setSelectedTarget(null)
    setDeploymentUrl(null)
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="w-full max-w-2xl bg-gray-900 rounded-2xl border border-gray-800 overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="h-14 flex items-center justify-between px-6 border-b border-gray-800 bg-gray-950/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
              <Cloud className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-100">Deploy Backend</h2>
              <div className="flex items-center gap-2 text-xs text-gray-500">
                <span className={step === 'target' ? 'text-blue-400' : ''}>Target</span>
                <ArrowRight className="w-3 h-3" />
                <span className={step === 'config' ? 'text-blue-400' : ''}>Configure</span>
                <ArrowRight className="w-3 h-3" />
                <span className={step === 'deploying' || step === 'success' ? 'text-blue-400' : ''}>Deploy</span>
              </div>
            </div>
          </div>
          
          <button
            onClick={resetAndClose}
            className="p-2 hover:bg-gray-800 rounded-lg text-gray-400 hover:text-gray-200 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {step === 'target' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-sm font-medium text-gray-200 mb-4">Select Deployment Target</h3>
                <div className="grid grid-cols-2 gap-3">
                  {DEPLOYMENT_TARGETS.map(target => {
                    const Icon = target.icon
                    const isSelected = selectedTarget === target.id
                    return (
                      <button
                        key={target.id}
                        onClick={() => setSelectedTarget(target.id)}
                        className={`p-4 rounded-xl border-2 text-left transition-all ${
                          isSelected
                            ? 'border-blue-500 bg-blue-500/10'
                            : 'border-gray-800 hover:border-gray-700 bg-gray-800/30'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${target.color} flex items-center justify-center`}>
                            <Icon className="w-5 h-5 text-white" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-medium text-gray-200">{target.name}</span>
                              {target.popular && (
                                <span className="px-1.5 py-0.5 rounded text-[10px] bg-green-500/20 text-green-400">Popular</span>
                              )}
                            </div>
                            <p className="text-xs text-gray-500 mt-0.5">{target.description}</p>
                          </div>
                          <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                            isSelected ? 'border-blue-500 bg-blue-500' : 'border-gray-600'
                          }`}>
                            {isSelected && <Check className="w-3 h-3 text-white" />}
                          </div>
                        </div>
                      </button>
                    )
                  })}
                </div>
              </div>

              <div className="flex justify-end">
                <button
                  onClick={() => setStep('config')}
                  disabled={!selectedTarget}
                  className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white text-sm font-medium flex items-center gap-2 transition-colors"
                >
                  Continue
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {step === 'config' && selectedTarget && (
            <div className="space-y-6">
              {/* Environment Selection */}
              <div>
                <h3 className="text-sm font-medium text-gray-200 mb-3">Environment</h3>
                <div className="flex gap-2">
                  {ENVIRONMENTS.map(env => (
                    <button
                      key={env.id}
                      onClick={() => setSelectedEnvironment(env.id)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${
                        selectedEnvironment === env.id
                          ? 'bg-gray-700 text-white'
                          : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                      }`}
                    >
                      <div className={`w-2 h-2 rounded-full ${env.color}`} />
                      {env.name}
                    </button>
                  ))}
                </div>
              </div>

              {/* Target-specific settings */}
              <div>
                <h3 className="text-sm font-medium text-gray-200 mb-3">Configuration</h3>
                <div className="space-y-3">
                  {selectedTarget === 'docker' && (
                    <>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="text-xs text-gray-500 mb-1 block">Registry</label>
                          <input
                            type="text"
                            value={targetSettings.registry}
                            onChange={(e) => setTargetSettings(prev => ({ ...prev, registry: e.target.value }))}
                            className="w-full h-9 px-3 rounded-lg bg-gray-800 border border-gray-700 text-sm text-gray-200 focus:outline-none focus:border-blue-500"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500 mb-1 block">Image Name</label>
                          <input
                            type="text"
                            value={targetSettings.imageName}
                            onChange={(e) => setTargetSettings(prev => ({ ...prev, imageName: e.target.value }))}
                            className="w-full h-9 px-3 rounded-lg bg-gray-800 border border-gray-700 text-sm text-gray-200 focus:outline-none focus:border-blue-500"
                          />
                        </div>
                      </div>
                    </>
                  )}

                  {selectedTarget === 'kubernetes' && (
                    <>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <label className="text-xs text-gray-500 mb-1 block">Namespace</label>
                          <input
                            type="text"
                            value={targetSettings.namespace}
                            onChange={(e) => setTargetSettings(prev => ({ ...prev, namespace: e.target.value }))}
                            className="w-full h-9 px-3 rounded-lg bg-gray-800 border border-gray-700 text-sm text-gray-200 focus:outline-none focus:border-blue-500"
                          />
                        </div>
                        <div>
                          <label className="text-xs text-gray-500 mb-1 block">Replicas</label>
                          <input
                            type="number"
                            value={targetSettings.replicas}
                            onChange={(e) => setTargetSettings(prev => ({ ...prev, replicas: Number(e.target.value) }))}
                            min={1}
                            max={20}
                            className="w-full h-9 px-3 rounded-lg bg-gray-800 border border-gray-700 text-sm text-gray-200 focus:outline-none focus:border-blue-500"
                          />
                        </div>
                      </div>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={targetSettings.ingress}
                          onChange={(e) => setTargetSettings(prev => ({ ...prev, ingress: e.target.checked }))}
                          className="w-4 h-4 rounded border-gray-600 bg-gray-800 text-blue-500 focus:ring-blue-500 focus:ring-offset-gray-900"
                        />
                        <span className="text-sm text-gray-300">Enable Ingress</span>
                      </label>
                    </>
                  )}

                  {(selectedTarget === 'railway' || selectedTarget === 'vercel') && (
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={targetSettings.autoDeploy}
                        onChange={(e) => setTargetSettings(prev => ({ ...prev, autoDeploy: e.target.checked }))}
                        className="w-4 h-4 rounded border-gray-600 bg-gray-800 text-blue-500 focus:ring-blue-500 focus:ring-offset-gray-900"
                      />
                      <span className="text-sm text-gray-300">Enable Auto Deploy on Push</span>
                    </label>
                  )}
                </div>
              </div>

              {/* Warning for production */}
              {selectedEnvironment === 'production' && (
                <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30 flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-yellow-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-yellow-400">Production Deployment</p>
                    <p className="text-xs text-yellow-500/80 mt-1">
                      This will deploy to production. Make sure all tests pass and changes are reviewed.
                    </p>
                  </div>
                </div>
              )}

              <div className="flex justify-between">
                <button
                  onClick={() => setStep('target')}
                  className="px-4 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-300 text-sm font-medium transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={handleDeploy}
                  className="px-4 py-2 rounded-lg bg-green-600 hover:bg-green-500 text-white text-sm font-medium flex items-center gap-2 transition-colors"
                >
                  <Cloud className="w-4 h-4" />
                  Deploy to {DEPLOYMENT_TARGETS.find(t => t.id === selectedTarget)?.name}
                </button>
              </div>
            </div>
          )}

          {step === 'deploying' && (
            <div className="py-12 text-center">
              <Loader2 className="w-16 h-16 text-blue-500 animate-spin mx-auto mb-6" />
              <h3 className="text-xl font-semibold text-gray-100 mb-2">Deploying...</h3>
              <p className="text-sm text-gray-400">
                Building and deploying to {DEPLOYMENT_TARGETS.find(t => t.id === selectedTarget)?.name}
              </p>
              
              <div className="mt-8 p-4 rounded-lg bg-gray-800/50 font-mono text-xs text-left text-gray-400 max-w-md mx-auto">
                <div className="flex items-center gap-2 mb-2">
                  <Terminal className="w-4 h-4" />
                  <span>Deployment Log</span>
                </div>
                <div className="space-y-1 text-[11px]">
                  <p className="text-green-400">✓ Building Docker image...</p>
                  <p className="text-green-400">✓ Pushing to registry...</p>
                  <p className="text-yellow-400 animate-pulse">⟳ Starting containers...</p>
                  <p className="text-gray-600">○ Running health checks...</p>
                  <p className="text-gray-600">○ Configuring ingress...</p>
                </div>
              </div>
            </div>
          )}

          {step === 'success' && (
            <div className="py-12 text-center">
              <div className="w-20 h-20 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="w-10 h-10 text-green-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-100 mb-2">Deployed Successfully!</h3>
              <p className="text-sm text-gray-400 mb-6">
                Your backend is now live on {DEPLOYMENT_TARGETS.find(t => t.id === selectedTarget)?.name}
              </p>
              
              {deploymentUrl && (
                <div className="flex items-center justify-center gap-2 p-3 rounded-lg bg-gray-800 max-w-md mx-auto mb-6">
                  <code className="text-sm text-blue-400 flex-1 truncate">{deploymentUrl}</code>
                  <button
                    onClick={handleCopyUrl}
                    className="p-1.5 hover:bg-gray-700 rounded text-gray-400 hover:text-gray-200 transition-colors"
                  >
                    {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                  </button>
                  <a
                    href={deploymentUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-1.5 hover:bg-gray-700 rounded text-gray-400 hover:text-gray-200 transition-colors"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                </div>
              )}
              
              <button
                onClick={resetAndClose}
                className="px-6 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition-colors"
              >
                Done
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default DeploymentModal

