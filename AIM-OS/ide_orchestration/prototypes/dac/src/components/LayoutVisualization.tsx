// Layout Visualization Component - Shows mini UI representation of IDE layout
// Displays panels in their actual spatial positions (left, right, bottom, main)

import React from 'react'
import { PanelPreview } from './PanelPreview'

interface PanelInfo {
  id: string
  name: string
  category: 'left' | 'right' | 'bottom' | 'main' | 'view'
  status: string
  hasErrors: boolean
  errorCount: number
  renderCount: number
  mountCount: number
  estimatedMemoryMB: number
  loadTime?: number
}

interface LayoutVisualizationProps {
  loadedPanels: PanelInfo[]
  // Current layout state
  leftTopPanel?: string | null
  leftBottomPanel?: string | null
  rightTopPanel?: string | null
  rightBottomPanel?: string | null
  bottomLeftPanel?: string | null
  bottomRightPanel?: string | null
  mainView?: string
  leftPanelOpen?: boolean
  rightPanelOpen?: boolean
  bottomPanelOpen?: boolean
  onPanelClick?: (panelId: string) => void
  selectedPanel?: string | null
}

export const LayoutVisualization: React.FC<LayoutVisualizationProps> = ({
  loadedPanels,
  leftTopPanel,
  leftBottomPanel,
  rightTopPanel,
  rightBottomPanel,
  bottomLeftPanel,
  bottomRightPanel,
  mainView,
  leftPanelOpen = true,
  rightPanelOpen = true,
  bottomPanelOpen = true,
  onPanelClick,
  selectedPanel
}) => {
  // Create a map of panel IDs to panel info
  const panelMap = new Map(loadedPanels.map(p => [p.id, p]))
  
  // Helper to get panel info
  const getPanel = (panelId: string | null | undefined) => {
    if (!panelId) return null
    return panelMap.get(panelId) || null
  }
  
  // Determine which panels are actually loaded in each position
  const leftTop = getPanel(leftTopPanel)
  const leftBottom = getPanel(leftBottomPanel)
  const rightTop = getPanel(rightTopPanel)
  const rightBottom = getPanel(rightBottomPanel)
  const bottomLeft = getPanel(bottomLeftPanel)
  const bottomRight = getPanel(bottomRightPanel)
  const main = getPanel(mainView)
  
  const hasLeftSplit = leftTop && leftBottom
  const hasRightSplit = rightTop && rightBottom
  const hasBottomSplit = bottomLeft && bottomRight
  
  return (
    <div className="w-full h-full flex flex-col bg-gray-900 rounded-lg border border-gray-700 p-2">
      {/* Mini IDE Layout */}
      <div className="flex-1 flex gap-1 min-h-0">
        {/* Left Panel Zone */}
        {leftPanelOpen && (leftTop || leftBottom) && (
          <div className={`flex flex-col gap-0.5 ${hasLeftSplit ? 'w-[18%]' : 'w-[15%]'}`}>
            {hasLeftSplit ? (
              <>
                {leftTop && (
                  <div className="flex-1 min-h-0" onClick={() => onPanelClick?.(leftTop.id)}>
                    <PanelPreview
                      panelId={leftTop.id}
                      panelName={leftTop.name}
                      category={leftTop.category}
                      status={leftTop.status}
                      hasErrors={leftTop.hasErrors}
                      errorCount={leftTop.errorCount}
                      renderCount={leftTop.renderCount}
                      mountCount={leftTop.mountCount}
                      estimatedMemoryMB={leftTop.estimatedMemoryMB}
                      loadTime={leftTop.loadTime}
                      onClick={() => onPanelClick?.(leftTop.id)}
                      isSelected={selectedPanel === leftTop.id}
                    />
                  </div>
                )}
                {hasLeftSplit && <div className="h-0.5 bg-gray-700"></div>}
                {leftBottom && (
                  <div className="flex-1 min-h-0" onClick={() => onPanelClick?.(leftBottom.id)}>
                    <PanelPreview
                      panelId={leftBottom.id}
                      panelName={leftBottom.name}
                      category={leftBottom.category}
                      status={leftBottom.status}
                      hasErrors={leftBottom.hasErrors}
                      errorCount={leftBottom.errorCount}
                      renderCount={leftBottom.renderCount}
                      mountCount={leftBottom.mountCount}
                      estimatedMemoryMB={leftBottom.estimatedMemoryMB}
                      loadTime={leftBottom.loadTime}
                      onClick={() => onPanelClick?.(leftBottom.id)}
                      isSelected={selectedPanel === leftBottom.id}
                    />
                  </div>
                )}
              </>
            ) : (
              <div className="flex-1 min-h-0" onClick={() => onPanelClick?.(leftTop?.id || leftBottom?.id || '')}>
                {(leftTop || leftBottom) && (
                  <PanelPreview
                    panelId={(leftTop || leftBottom)!.id}
                    panelName={(leftTop || leftBottom)!.name}
                    category={(leftTop || leftBottom)!.category}
                    status={(leftTop || leftBottom)!.status}
                    hasErrors={(leftTop || leftBottom)!.hasErrors}
                    errorCount={(leftTop || leftBottom)!.errorCount}
                    renderCount={(leftTop || leftBottom)!.renderCount}
                    mountCount={(leftTop || leftBottom)!.mountCount}
                    estimatedMemoryMB={(leftTop || leftBottom)!.estimatedMemoryMB}
                    loadTime={(leftTop || leftBottom)!.loadTime}
                    onClick={() => onPanelClick?.((leftTop || leftBottom)!.id)}
                    isSelected={selectedPanel === (leftTop || leftBottom)?.id}
                  />
                )}
              </div>
            )}
          </div>
        )}
        
        {/* Main Content + Bottom Zone */}
        <div className="flex-1 flex flex-col gap-0.5 min-w-0">
          {/* Main View */}
          {main && (
            <div className={`flex-1 min-h-0 ${bottomPanelOpen && (bottomLeft || bottomRight) ? 'mb-0.5' : ''}`} onClick={() => onPanelClick?.(main.id)}>
              <PanelPreview
                panelId={main.id}
                panelName={main.name}
                category={main.category}
                status={main.status}
                hasErrors={main.hasErrors}
                errorCount={main.errorCount}
                renderCount={main.renderCount}
                mountCount={main.mountCount}
                estimatedMemoryMB={main.estimatedMemoryMB}
                loadTime={main.loadTime}
                onClick={() => onPanelClick?.(main.id)}
                isSelected={selectedPanel === main.id}
              />
            </div>
          )}
          
          {/* Bottom Panel Zone */}
          {bottomPanelOpen && (bottomLeft || bottomRight) && (
            <>
              {main && <div className="h-0.5 bg-gray-700"></div>}
              <div className={`flex gap-0.5 ${hasBottomSplit ? 'h-[30%]' : 'h-[25%]'}`}>
                {hasBottomSplit ? (
                  <>
                    {bottomLeft && (
                      <div className="flex-1 min-h-0" onClick={() => onPanelClick?.(bottomLeft.id)}>
                        <PanelPreview
                          panelId={bottomLeft.id}
                          panelName={bottomLeft.name}
                          category={bottomLeft.category}
                          status={bottomLeft.status}
                          hasErrors={bottomLeft.hasErrors}
                          errorCount={bottomLeft.errorCount}
                          renderCount={bottomLeft.renderCount}
                          mountCount={bottomLeft.mountCount}
                          estimatedMemoryMB={bottomLeft.estimatedMemoryMB}
                          loadTime={bottomLeft.loadTime}
                          onClick={() => onPanelClick?.(bottomLeft.id)}
                          isSelected={selectedPanel === bottomLeft.id}
                        />
                      </div>
                    )}
                    {hasBottomSplit && <div className="w-0.5 bg-gray-700"></div>}
                    {bottomRight && (
                      <div className="flex-1 min-h-0" onClick={() => onPanelClick?.(bottomRight.id)}>
                        <PanelPreview
                          panelId={bottomRight.id}
                          panelName={bottomRight.name}
                          category={bottomRight.category}
                          status={bottomRight.status}
                          hasErrors={bottomRight.hasErrors}
                          errorCount={bottomRight.errorCount}
                          renderCount={bottomRight.renderCount}
                          mountCount={bottomRight.mountCount}
                          estimatedMemoryMB={bottomRight.estimatedMemoryMB}
                          loadTime={bottomRight.loadTime}
                          onClick={() => onPanelClick?.(bottomRight.id)}
                          isSelected={selectedPanel === bottomRight.id}
                        />
                      </div>
                    )}
                  </>
                ) : (
                  <div className="flex-1 min-h-0" onClick={() => onPanelClick?.((bottomLeft || bottomRight)!.id)}>
                    {(bottomLeft || bottomRight) && (
                      <PanelPreview
                        panelId={(bottomLeft || bottomRight)!.id}
                        panelName={(bottomLeft || bottomRight)!.name}
                        category={(bottomLeft || bottomRight)!.category}
                        status={(bottomLeft || bottomRight)!.status}
                        hasErrors={(bottomLeft || bottomRight)!.hasErrors}
                        errorCount={(bottomLeft || bottomRight)!.errorCount}
                        renderCount={(bottomLeft || bottomRight)!.renderCount}
                        mountCount={(bottomLeft || bottomRight)!.mountCount}
                        estimatedMemoryMB={(bottomLeft || bottomRight)!.estimatedMemoryMB}
                        loadTime={(bottomLeft || bottomRight)!.loadTime}
                        onClick={() => onPanelClick?.((bottomLeft || bottomRight)!.id)}
                        isSelected={selectedPanel === (bottomLeft || bottomRight)?.id}
                      />
                    )}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
        
        {/* Right Panel Zone */}
        {rightPanelOpen && (rightTop || rightBottom) && (
          <div className={`flex flex-col gap-0.5 ${hasRightSplit ? 'w-[18%]' : 'w-[15%]'}`}>
            {hasRightSplit ? (
              <>
                {rightTop && (
                  <div className="flex-1 min-h-0" onClick={() => onPanelClick?.(rightTop.id)}>
                    <PanelPreview
                      panelId={rightTop.id}
                      panelName={rightTop.name}
                      category={rightTop.category}
                      status={rightTop.status}
                      hasErrors={rightTop.hasErrors}
                      errorCount={rightTop.errorCount}
                      renderCount={rightTop.renderCount}
                      mountCount={rightTop.mountCount}
                      estimatedMemoryMB={rightTop.estimatedMemoryMB}
                      loadTime={rightTop.loadTime}
                      onClick={() => onPanelClick?.(rightTop.id)}
                      isSelected={selectedPanel === rightTop.id}
                    />
                  </div>
                )}
                {hasRightSplit && <div className="h-0.5 bg-gray-700"></div>}
                {rightBottom && (
                  <div className="flex-1 min-h-0" onClick={() => onPanelClick?.(rightBottom.id)}>
                    <PanelPreview
                      panelId={rightBottom.id}
                      panelName={rightBottom.name}
                      category={rightBottom.category}
                      status={rightBottom.status}
                      hasErrors={rightBottom.hasErrors}
                      errorCount={rightBottom.errorCount}
                      renderCount={rightBottom.renderCount}
                      mountCount={rightBottom.mountCount}
                      estimatedMemoryMB={rightBottom.estimatedMemoryMB}
                      loadTime={rightBottom.loadTime}
                      onClick={() => onPanelClick?.(rightBottom.id)}
                      isSelected={selectedPanel === rightBottom.id}
                    />
                  </div>
                )}
              </>
            ) : (
              <div className="flex-1 min-h-0" onClick={() => onPanelClick?.((rightTop || rightBottom)!.id)}>
                {(rightTop || rightBottom) && (
                  <PanelPreview
                    panelId={(rightTop || rightBottom)!.id}
                    panelName={(rightTop || rightBottom)!.name}
                    category={(rightTop || rightBottom)!.category}
                    status={(rightTop || rightBottom)!.status}
                    hasErrors={(rightTop || rightBottom)!.hasErrors}
                    errorCount={(rightTop || rightBottom)!.errorCount}
                    renderCount={(rightTop || rightBottom)!.renderCount}
                    mountCount={(rightTop || rightBottom)!.mountCount}
                    estimatedMemoryMB={(rightTop || rightBottom)!.estimatedMemoryMB}
                    loadTime={(rightTop || rightBottom)!.loadTime}
                    onClick={() => onPanelClick?.((rightTop || rightBottom)!.id)}
                    isSelected={selectedPanel === (rightTop || rightBottom)?.id}
                  />
                )}
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Legend */}
      <div className="mt-2 pt-2 border-t border-gray-700 flex items-center justify-between text-[9px] text-gray-500">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>Mounted</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
            <span>Cached</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-red-500 rounded-full"></div>
            <span>Error</span>
          </div>
        </div>
        <div className="text-gray-600">
          {loadedPanels.length} panel{loadedPanels.length !== 1 ? 's' : ''} loaded
        </div>
      </div>
    </div>
  )
}

