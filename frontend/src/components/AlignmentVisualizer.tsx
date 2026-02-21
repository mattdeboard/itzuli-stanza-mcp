import { useEffect, useRef, useState, useCallback } from 'react'
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
  const [pinnedTokenId, setPinnedTokenId] = useState<string | null>(null)
  const [pinnedIsSource, setPinnedIsSource] = useState<boolean>(false)
  const [animatingRibbons, setAnimatingRibbons] = useState<Set<number>>(new Set())
  const [hasInitiallyLoaded, setHasInitiallyLoaded] = useState<boolean>(false)

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

  // Reset initial load state when sentence pair changes
  useEffect(() => {
    setHasInitiallyLoaded(false)
    setHoveredTokens(new Set())
    setHighlightedAlignments(new Set())
    setAnimatingRibbons(new Set())
    setPinnedTokenId(null)
    setPinnedIsSource(false)
  }, [sentencePair])

  // Trigger initial animations when lexical layer loads
  useEffect(() => {
    if (sourcePositions.length > 0 && targetPositions.length > 0 && !hasInitiallyLoaded) {
      // Mark as initially loaded
      setHasInitiallyLoaded(true)

      // Animate all ribbons on initial load with staggered timing
      const allAlignmentIndices = sentencePair.layers.lexical.map((_, index) => index)

      // Start staggered animations for all ribbons
      allAlignmentIndices.forEach((alignmentIndex, order) => {
        setTimeout(() => {
          setAnimatingRibbons(prev => new Set([...prev, alignmentIndex]))
        }, order * 150 + 50) // 150ms stagger, 50ms initial delay
      })

      // Show all ribbons as highlighted during initial load
      setHighlightedAlignments(new Set(allAlignmentIndices))

      // Clear the highlight after all animations complete
      const totalDuration = allAlignmentIndices.length * 150 + 50 + 400 // stagger + delay + animation duration
      setTimeout(() => {
        setHighlightedAlignments(new Set())
        setAnimatingRibbons(new Set())
      }, totalDuration)
    }
  }, [sourcePositions, targetPositions, sentencePair.layers.lexical, hasInitiallyLoaded])


  // Calculate path length for SVG animation
  const calculatePathLength = useCallback((path: string): number => {
    // Create a temporary SVG element to calculate path length
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
    const pathElement = document.createElementNS('http://www.w3.org/2000/svg', 'path')
    pathElement.setAttribute('d', path)
    svg.appendChild(pathElement)
    document.body.appendChild(svg)
    const length = pathElement.getTotalLength()
    document.body.removeChild(svg)
    return length
  }, [])

  const handleTokenHover = useCallback((tokenId: string, isSource: boolean) => {
    const newHoveredTokens = new Set([tokenId])
    const newHighlightedAlignments = new Set<number>()

    const connectedAlignments: number[] = []
    sentencePair.layers.lexical.forEach((alignment, index) => {
      const isConnected = isSource
        ? alignment.source.includes(tokenId)
        : alignment.target.includes(tokenId)

      if (isConnected) {
        connectedAlignments.push(index)
        newHighlightedAlignments.add(index)
        // Add connected tokens
        alignment.source.forEach(id => newHoveredTokens.add(id))
        alignment.target.forEach(id => newHoveredTokens.add(id))
      }
    })

    // If something is pinned, this becomes a secondary preview
    if (pinnedTokenId) {
      // Merge with pinned tokens but keep them visually distinct
      const pinnedTokens = new Set<string>()
      const pinnedAlignments = new Set<number>()

      sentencePair.layers.lexical.forEach((alignment, index) => {
        const isConnectedToPinned = pinnedIsSource
          ? alignment.source.includes(pinnedTokenId)
          : alignment.target.includes(pinnedTokenId)

        if (isConnectedToPinned) {
          pinnedAlignments.add(index)
          alignment.source.forEach(id => pinnedTokens.add(id))
          alignment.target.forEach(id => pinnedTokens.add(id))
        }
      })

      // Add pinned tokens to hover set with special identifier
      pinnedTokens.forEach(id => newHoveredTokens.add(id))
      pinnedAlignments.forEach(idx => newHighlightedAlignments.add(idx))
    }

    // Start staggered animations for all connected alignments
    // First, clear any existing animations for these ribbons
    setAnimatingRibbons(prev => {
      const newSet = new Set(prev)
      connectedAlignments.forEach(idx => newSet.delete(idx))
      return newSet
    })

    // Then start staggered animations with delays
    connectedAlignments.forEach((alignmentIndex, order) => {
      setTimeout(() => {
        setAnimatingRibbons(prev => new Set([...prev, alignmentIndex]))
      }, order * 100 + 10) // Small delay for stagger
    })

    setHoveredTokens(newHoveredTokens)
    setHighlightedAlignments(newHighlightedAlignments)
  }, [sentencePair.layers.lexical, pinnedTokenId, pinnedIsSource, highlightedAlignments])

  const handleTokenLeave = useCallback(() => {
    if (pinnedTokenId) {
      // Restore to pinned state only
      const pinnedTokens = new Set<string>()
      const pinnedAlignments = new Set<number>()

      sentencePair.layers.lexical.forEach((alignment, index) => {
        const isConnectedToPinned = pinnedIsSource
          ? alignment.source.includes(pinnedTokenId)
          : alignment.target.includes(pinnedTokenId)

        if (isConnectedToPinned) {
          pinnedAlignments.add(index)
          alignment.source.forEach(id => pinnedTokens.add(id))
          alignment.target.forEach(id => pinnedTokens.add(id))
        }
      })

      setHoveredTokens(pinnedTokens)
      setHighlightedAlignments(pinnedAlignments)
      // Keep pinned ribbons animated
      setAnimatingRibbons(pinnedAlignments)
    } else {
      setHoveredTokens(new Set())
      setHighlightedAlignments(new Set())
      setAnimatingRibbons(new Set())
    }
  }, [pinnedTokenId, pinnedIsSource, sentencePair.layers.lexical])

  const handleTokenClick = useCallback((tokenId: string, isSource: boolean) => {
    // Toggle pin state
    if (pinnedTokenId === tokenId) {
      // Unpin
      setPinnedTokenId(null)
      setPinnedIsSource(false)
      setHoveredTokens(new Set())
      setHighlightedAlignments(new Set())
      setAnimatingRibbons(new Set())
    } else {
      // Pin this token
      setPinnedTokenId(tokenId)
      setPinnedIsSource(isSource)

      const newHoveredTokens = new Set([tokenId])
      const newHighlightedAlignments = new Set<number>()

      const connectedAlignments: number[] = []
      sentencePair.layers.lexical.forEach((alignment, index) => {
        const isConnected = isSource
          ? alignment.source.includes(tokenId)
          : alignment.target.includes(tokenId)

        if (isConnected) {
          connectedAlignments.push(index)
          newHighlightedAlignments.add(index)
          alignment.source.forEach(id => newHoveredTokens.add(id))
          alignment.target.forEach(id => newHoveredTokens.add(id))
        }
      })

      // Start staggered animations for pinned state
      // First, clear any existing animations for these ribbons
      setAnimatingRibbons(prev => {
        const newSet = new Set(prev)
        connectedAlignments.forEach(idx => newSet.delete(idx))
        return newSet
      })

      // Then start staggered animations with delays
      connectedAlignments.forEach((alignmentIndex, order) => {
        setTimeout(() => {
          setAnimatingRibbons(prev => new Set([...prev, alignmentIndex]))
        }, order * 100 + 10)
      })

      setHoveredTokens(newHoveredTokens)
      setHighlightedAlignments(newHighlightedAlignments)
    }
  }, [pinnedTokenId, sentencePair.layers.lexical])

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

    // Determine if this is a many-to-many connection
    const isManyToMany = alignmentSourcePositions.length > 1 || alignmentTargetPositions.length > 1

    if (isManyToMany) {
      return createManyToManyRibbon(alignmentSourcePositions, alignmentTargetPositions, ribbonRect, index)
    } else {
      return createSimpleRibbon(alignmentSourcePositions[0], alignmentTargetPositions[0], ribbonRect, index)
    }
  }

  const createSingleRibbon = (sourcePos: TokenPosition, targetPos: TokenPosition, ribbonRect: DOMRect, index: number, options?: {
    strokeWidth?: number
    opacityMultiplier?: number
    pathKey?: string
    sourceDotRadius?: number
    targetDotRadius?: number
    animationDelay?: number
  }) => {
    // Connection points
    const sourceDotX = sourcePos.x
    const sourceDotY = -8
    const targetDotX = targetPos.x
    const targetDotY = ribbonRect.height + 8

    // Smooth bezier curve
    const curveHeight = targetDotY - sourceDotY
    const controlOffset = Math.min(curveHeight * 0.3, 50)

    const ribbonPath = `M ${sourceDotX} ${sourceDotY}
                       C ${sourceDotX} ${sourceDotY + controlOffset}, ${targetDotX} ${targetDotY - controlOffset}, ${targetDotX} ${targetDotY}`

    const isHighlighted = highlightedAlignments.has(index)
    const isDimmed = highlightedAlignments.size > 0 && !isHighlighted
    const isAnimating = animatingRibbons.has(index)

    // Determine if this ribbon is part of the pinned set
    const isPinnedRibbon = pinnedTokenId ? sentencePair.layers.lexical[index] &&
      (pinnedIsSource
        ? sentencePair.layers.lexical[index].source.includes(pinnedTokenId)
        : sentencePair.layers.lexical[index].target.includes(pinnedTokenId)
      ) : false

    // Different opacity for pinned vs hovered ribbons
    const baseOpacity = isHighlighted
      ? (isPinnedRibbon ? 1 : 0.7) // Pinned ribbons at full opacity, hover preview at 70%
      : (isDimmed ? 0.15 : 0.6)
    
    const opacity = baseOpacity * (options?.opacityMultiplier || 1)

    // Calculate path length for animation (using a simpler approach)
    let pathLength: number
    try {
      pathLength = calculatePathLength(ribbonPath)
      // Ensure minimum path length for animation to be visible
      if (pathLength < 50) pathLength = 150
    } catch {
      pathLength = 150 // fallback length
    }

    return {
      path: (
        <path
          key={options?.pathKey || `ribbon-path-${index}`}
          d={ribbonPath}
          fill="none"
          stroke="#3b82f6"
          strokeWidth={options?.strokeWidth || "3"}
          opacity={opacity}
          className="transition-opacity duration-300"
          strokeDasharray={isHighlighted || !hasInitiallyLoaded ? `${pathLength}` : undefined}
          strokeDashoffset={isHighlighted || !hasInitiallyLoaded ? (isAnimating ? '0' : `${pathLength}`) : undefined}
          style={isHighlighted ? {
            transition: 'stroke-dashoffset 400ms ease-out',
            transitionDelay: options?.animationDelay ? `${options.animationDelay}ms` : undefined
          } : undefined}
        />
      ),
      sourceDot: (
        <circle
          key={`source-dot-${options?.pathKey || index}`}
          cx={sourceDotX}
          cy={sourceDotY}
          r={options?.sourceDotRadius || "4"}
          fill="#3b82f6"
          opacity={isHighlighted && isAnimating ? opacity : (isHighlighted ? 0 : opacity)}
          className="transition-all duration-300"
          style={isHighlighted ? {
            transitionDelay: isAnimating ? `${300 + (options?.animationDelay || 0)}ms` : '0ms'
          } : undefined}
        />
      ),
      targetDot: (
        <circle
          key={`target-dot-${options?.pathKey || index}`}
          cx={targetDotX}
          cy={targetDotY}
          r={options?.targetDotRadius || "4"}
          fill="#3b82f6"
          opacity={isHighlighted && isAnimating ? opacity : (isHighlighted ? 0 : opacity)}
          className="transition-all duration-300"
          style={isHighlighted ? {
            transitionDelay: isAnimating ? `${350 + (options?.animationDelay || 0)}ms` : '0ms'
          } : undefined}
        />
      )
    }
  }

  const createSimpleRibbon = (sourcePos: TokenPosition, targetPos: TokenPosition, ribbonRect: DOMRect, index: number) => {
    const ribbon = createSingleRibbon(sourcePos, targetPos, ribbonRect, index)
    
    return (
      <g key={`ribbon-group-${index}`}>
        {ribbon.path}
        {ribbon.sourceDot}
        {ribbon.targetDot}
      </g>
    )
  }

  const createManyToManyRibbon = (sourcePositions: TokenPosition[], targetPositions: TokenPosition[], ribbonRect: DOMRect, index: number) => {
    const ribbonElements: JSX.Element[] = []
    const sourceDots: JSX.Element[] = []
    const targetDots: JSX.Element[] = []

    // Create individual ribbons from each source to each target using createSingleRibbon
    sourcePositions.forEach((sourcePos, sourceIndex) => {
      targetPositions.forEach((targetPos, targetIndex) => {
        const ribbonKey = `${index}-${sourceIndex}-${targetIndex}`
        const animationDelay = (sourceIndex + targetIndex) * 100

        const ribbon = createSingleRibbon(sourcePos, targetPos, ribbonRect, index, {
          strokeWidth: 2.5,
          opacityMultiplier: 0.8,
          pathKey: ribbonKey,
          sourceDotRadius: 3,
          targetDotRadius: 3,
          animationDelay
        })

        ribbonElements.push(ribbon.path)
      })
    })

    // Collect unique source dots
    const processedSourcePositions = new Set<string>()
    sourcePositions.forEach((pos, i) => {
      const posKey = `${pos.x}-${pos.y}`
      if (!processedSourcePositions.has(posKey)) {
        processedSourcePositions.add(posKey)
        const ribbon = createSingleRibbon(pos, targetPositions[0], ribbonRect, index, {
          sourceDotRadius: 3,
          animationDelay: i * 50,
          pathKey: `many-source-${index}-${i}`
        })
        sourceDots.push(ribbon.sourceDot)
      }
    })

    // Collect unique target dots
    const processedTargetPositions = new Set<string>()
    targetPositions.forEach((pos, i) => {
      const posKey = `${pos.x}-${pos.y}`
      if (!processedTargetPositions.has(posKey)) {
        processedTargetPositions.add(posKey)
        const ribbon = createSingleRibbon(sourcePositions[0], pos, ribbonRect, index, {
          targetDotRadius: 3,
          animationDelay: i * 50,
          pathKey: `many-target-${index}-${i}`
        })
        targetDots.push(ribbon.targetDot)
      }
    })

    return (
      <g key={`many-to-many-${index}`}>
        {ribbonElements}
        {sourceDots}
        {targetDots}
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
            const isPinned = pinnedTokenId === token.id
            const isConnected = sentencePair.layers.lexical.some(alignment =>
              alignment.source.includes(token.id)
            )

            return (
              <span
                key={token.id}
                className={`token ${isHovered ? 'token--highlighted' : ''} ${isDimmed ? 'token--dimmed' : ''} ${isConnected ? 'token--connected token--source' : ''} ${isPinned ? 'token--pinned' : ''}`}
                data-token-id={token.id}
                data-token-type="source"
                onMouseEnter={() => handleTokenHover(token.id, true)}
                onMouseLeave={handleTokenLeave}
                onClick={() => handleTokenClick(token.id, true)}
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
            const isPinned = pinnedTokenId === token.id
            const isConnected = sentencePair.layers.lexical.some(alignment =>
              alignment.target.includes(token.id)
            )

            return (
              <span
                key={token.id}
                className={`token ${isHovered ? 'token--highlighted' : ''} ${isDimmed ? 'token--dimmed' : ''} ${isConnected ? 'token--connected token--target' : ''} ${isPinned ? 'token--pinned' : ''}`}
                data-token-id={token.id}
                data-token-type="target"
                onMouseEnter={() => handleTokenHover(token.id, false)}
                onMouseLeave={handleTokenLeave}
                onClick={() => handleTokenClick(token.id, false)}
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