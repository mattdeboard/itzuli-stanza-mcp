import { useEffect, useRef, useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import type { SentencePair, Alignment } from '../types/alignment'

interface TokenPosition {
  id: string
  x: number
  y: number
  width: number
  height: number
}

interface AlignmentVisualizerProps {
  sentencePair: SentencePair
}

export function AlignmentVisualizer({ sentencePair }: AlignmentVisualizerProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [sourcePositions, setSourcePositions] = useState<TokenPosition[]>([])
  const [targetPositions, setTargetPositions] = useState<TokenPosition[]>([])
  const [hoveredTokens, setHoveredTokens] = useState<Set<string>>(new Set())
  const [highlightedAlignments, setHighlightedAlignments] = useState<Set<number>>(new Set())

  const updateTokenPositions = useCallback(() => {
    if (!containerRef.current) return

    const container = containerRef.current
    const containerRect = container.getBoundingClientRect()

    // Get source token positions
    const sourceTokens = container.querySelectorAll('[data-token-type="source"]')
    const newSourcePositions: TokenPosition[] = []
    sourceTokens.forEach((token) => {
      const rect = token.getBoundingClientRect()
      const id = token.getAttribute('data-token-id')
      if (id) {
        // Calculate position relative to ribbon space instead of main container
        const ribbonSpace = containerRef.current?.querySelector('.ribbon-space') as HTMLElement
        const ribbonRect = ribbonSpace?.getBoundingClientRect()
        const tokenCenterX = ribbonRect 
          ? rect.left - ribbonRect.left + rect.width / 2
          : rect.left - containerRect.left + rect.width / 2
        newSourcePositions.push({
          id,
          x: tokenCenterX,
          y: rect.bottom - containerRect.top,
          width: rect.width,
          height: rect.height,
        })
      }
    })

    // Get target token positions
    const targetTokens = container.querySelectorAll('[data-token-type="target"]')
    const newTargetPositions: TokenPosition[] = []
    targetTokens.forEach((token) => {
      const rect = token.getBoundingClientRect()
      const id = token.getAttribute('data-token-id')
      if (id) {
        // Calculate position relative to ribbon space instead of main container
        const ribbonSpace = containerRef.current?.querySelector('.ribbon-space') as HTMLElement
        const ribbonRect = ribbonSpace?.getBoundingClientRect()
        const tokenCenterX = ribbonRect 
          ? rect.left - ribbonRect.left + rect.width / 2
          : rect.left - containerRect.left + rect.width / 2
        newTargetPositions.push({
          id,
          x: tokenCenterX,
          y: rect.top - containerRect.top,
          width: rect.width,
          height: rect.height,
        })
      }
    })

    setSourcePositions(newSourcePositions)
    setTargetPositions(newTargetPositions)
  }, [])

  useEffect(() => {
    updateTokenPositions()

    const handleResize = () => updateTokenPositions()
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [updateTokenPositions, sentencePair])

  const handleTokenHover = useCallback((tokenId: string, isSource: boolean) => {
    const newHoveredTokens = new Set([tokenId])
    const newHighlightedAlignments = new Set<number>()

    sentencePair.layers.lexical.forEach((alignment, index) => {
      const isConnected = isSource
        ? alignment.source.includes(tokenId)
        : alignment.target.includes(tokenId)

      if (isConnected) {
        newHighlightedAlignments.add(index)
        // Add connected tokens
        alignment.source.forEach(id => newHoveredTokens.add(id))
        alignment.target.forEach(id => newHoveredTokens.add(id))
      }
    })

    setHoveredTokens(newHoveredTokens)
    setHighlightedAlignments(newHighlightedAlignments)
  }, [sentencePair.layers.lexical, sourcePositions, targetPositions])

  const handleTokenLeave = useCallback(() => {
    setHoveredTokens(new Set())
    setHighlightedAlignments(new Set())
  }, [])

  const createRibbonPath = (alignment: Alignment, index: number) => {
    // Find positions for source and target tokens
    const alignmentSourcePositions = alignment.source
      .map(id => sourcePositions.find(pos => pos.id === id))
      .filter(Boolean) as TokenPosition[]

    const alignmentTargetPositions = alignment.target
      .map(id => targetPositions.find(pos => pos.id === id))
      .filter(Boolean) as TokenPosition[]

    if (alignmentSourcePositions.length === 0 || alignmentTargetPositions.length === 0) {
      return null
    }

    if (!containerRef.current) return null

    // Find the ribbon space div to get proper coordinate system
    const ribbonSpace = containerRef.current.querySelector('.ribbon-space') as HTMLElement
    if (!ribbonSpace) return null

    const ribbonRect = ribbonSpace.getBoundingClientRect()

    // Get the main container rect for proper coordinate conversion
    const containerRect = containerRef.current.getBoundingClientRect()

    // Use the stored positions directly - they're already calculated as centers
    const sourceX = alignmentSourcePositions.length === 1 
      ? alignmentSourcePositions[0].x
      : (Math.min(...alignmentSourcePositions.map(pos => pos.x)) +
         Math.max(...alignmentSourcePositions.map(pos => pos.x))) / 2
    const targetX = alignmentTargetPositions.length === 1
      ? alignmentTargetPositions[0].x  
      : (Math.min(...alignmentTargetPositions.map(pos => pos.x)) +
         Math.max(...alignmentTargetPositions.map(pos => pos.x))) / 2

    console.log(`Ribbon ${index} positioning:`, {
      alignment: alignment.label,
      sourceTokens: alignmentSourcePositions.map(p => ({id: p.id, x: p.x})),
      targetTokens: alignmentTargetPositions.map(p => ({id: p.id, x: p.x})),
      calculatedSourceX: sourceX,
      calculatedTargetX: targetX
    })

    // Connection points
    const sourceDotX = sourceX
    const sourceDotY = -8
    const targetDotX = targetX
    const targetDotY = ribbonRect.height + 8

    // Smooth bezier curve
    const curveHeight = targetDotY - sourceDotY
    const controlOffset = Math.min(curveHeight * 0.3, 50)

    const ribbonPath = `M ${sourceDotX} ${sourceDotY}
                       C ${sourceDotX} ${sourceDotY + controlOffset}, ${targetDotX} ${targetDotY - controlOffset}, ${targetDotX} ${targetDotY}`

    const isHighlighted = highlightedAlignments.has(index)
    const isDimmed = highlightedAlignments.size > 0 && !isHighlighted
    const opacity = isHighlighted ? 1 : (isDimmed ? 0.15 : 0.6)

    return (
      <g key={`ribbon-group-${index}`}>
        {/* Single ribbon curve */}
        <path
          d={ribbonPath}
          fill="none"
          stroke="#3b82f6"
          strokeWidth="3"
          opacity={opacity}
          className="transition-opacity duration-300"
        />

        {/* Source connection dot */}
        <circle
          cx={sourceDotX}
          cy={sourceDotY}
          r="4"
          fill="#3b82f6"
          opacity={opacity}
          className="transition-opacity duration-300"
        />

        {/* Target connection dot */}
        <circle
          cx={targetDotX}
          cy={targetDotY}
          r="4"
          fill="#3b82f6"
          opacity={opacity}
          className="transition-opacity duration-300"
        />

      </g>
    )
  }

  return (
    <div ref={containerRef} className="relative">
      {/* Source Sentence */}
      <div className="px-8 pt-6 pb-0 bg-gray-50 rounded-t-lg mx-8">
        <div className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">
          {sentencePair.source.lang.toUpperCase()}
        </div>
        <div className="text-lg text-slate-800 mb-4 italic">
          {sentencePair.source.text}
        </div>
        <div className="flex flex-wrap gap-3 items-center">
          {sentencePair.source.tokens.map((token) => {
            const isHovered = hoveredTokens.has(token.id)
            const isDimmed = hoveredTokens.size > 0 && !isHovered
            const isConnected = sentencePair.layers.lexical.some(alignment =>
              alignment.source.includes(token.id)
            )

            return (
              <span
                key={token.id}
                className={`token ${isHovered ? 'token--highlighted' : ''} ${isDimmed ? 'token--dimmed' : ''} ${isConnected ? 'token--connected token--source' : ''}`}
                data-token-id={token.id}
                data-token-type="source"
                onMouseEnter={() => handleTokenHover(token.id, true)}
                onMouseLeave={handleTokenLeave}
              >
                {token.form}
              </span>
            )
          })}
        </div>
      </div>

      {/* Ribbon Space */}
      <div
        className="h-ribbon-space relative flex items-center justify-center mx-8 ribbon-space"
        style={{
          background: 'linear-gradient(to bottom, #f8fafc 0%, #ffffff 50%, #f8fafc 100%)'
        }}
      >
        {/* SVG Ribbons */}
        <svg
          className="absolute inset-0 w-full h-full pointer-events-none"
          style={{ zIndex: 1 }}
        >
          {sourcePositions.length > 0 && targetPositions.length > 0 && sentencePair.layers.lexical.map((alignment, index) =>
            createRibbonPath(alignment, index)
          )}
        </svg>
      </div>

      {/* Target Sentence */}
      <div className="px-8 pt-0 pb-6 bg-gray-50 rounded-b-lg mx-8">
        <div className="flex flex-wrap gap-3 items-center mb-2">
          {sentencePair.target.tokens.map((token) => {
            const isHovered = hoveredTokens.has(token.id)
            const isDimmed = hoveredTokens.size > 0 && !isHovered
            const isConnected = sentencePair.layers.lexical.some(alignment =>
              alignment.target.includes(token.id)
            )

            return (
              <span
                key={token.id}
                className={`token ${isHovered ? 'token--highlighted' : ''} ${isDimmed ? 'token--dimmed' : ''} ${isConnected ? 'token--connected token--target' : ''}`}
                data-token-id={token.id}
                data-token-type="target"
                onMouseEnter={() => handleTokenHover(token.id, false)}
                onMouseLeave={handleTokenLeave}
              >
                {token.form}
              </span>
            )
          })}
        </div>
        <div className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-2">
          {sentencePair.target.lang.toUpperCase()}
        </div>
        <div className="text-lg text-slate-800 italic">
          {sentencePair.target.text}
        </div>
      </div>
    </div>
  )
}