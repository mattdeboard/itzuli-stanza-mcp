import { LayerType } from '../types/alignment'
import { useEffect, useRef } from 'react'

type LayerConfig = {
  name: string
  displayName: string
  color: string
}

export const LAYER_CONFIGS: Record<LayerType, LayerConfig> = {
  [LayerType.LEXICAL]: {
    name: LayerType.LEXICAL,
    displayName: 'Lexical',
    color: '#5a9975' // sage-500 (forest green)
  },
  [LayerType.GRAMMATICAL_RELATIONS]: {
    name: LayerType.GRAMMATICAL_RELATIONS,
    displayName: 'Grammatical Relations',
    color: '#8b5fb5' // soft purple/violet
  },
  [LayerType.FEATURES]: {
    name: LayerType.FEATURES,
    displayName: 'Features',
    color: '#c8954d' // tan-600 (warm amber/bronze)
  }
}

const LAYER_TOOLTIPS: Record<LayerType, string> = {
  [LayerType.LEXICAL]: "What words mean — dictionary-level correspondences between English words and their direct Basque equivalents, if applicable",
  [LayerType.GRAMMATICAL_RELATIONS]: "Who does what to whom — how English marks sentence roles through word order while Basque marks them through case suffixes and verb agreement",
  [LayerType.FEATURES]: "Where grammar hides — how tense, negation, definiteness, and agreement that live in one place in English get scattered across Basque words"
}

type LayerPickerProps = {
  currentLayer: LayerType
  setVizLayer: (layer: LayerType) => void
}

export function LayerPicker({ currentLayer, setVizLayer }: LayerPickerProps) {
  const tabListRef = useRef<HTMLDivElement>(null)
  
  // Focus the active tab when currentLayer changes (from external sources)
  useEffect(() => {
    const activeButton = tabListRef.current?.querySelector(`[aria-selected="true"]`) as HTMLButtonElement
    if (activeButton && document.activeElement !== activeButton) {
      activeButton.focus()
    }
  }, [currentLayer])
  
  const handleKeyDown = (e: React.KeyboardEvent, currentLayerKey: string) => {
    const layerEntries = Object.entries(LAYER_CONFIGS)
    const currentIndex = layerEntries.findIndex(([key]) => key === currentLayerKey)
    
    let nextIndex = currentIndex
    
    switch (e.key) {
      case 'ArrowRight':
      case 'ArrowDown':
        e.preventDefault()
        nextIndex = (currentIndex + 1) % layerEntries.length
        break
      case 'ArrowLeft':
      case 'ArrowUp':
        e.preventDefault()
        nextIndex = (currentIndex - 1 + layerEntries.length) % layerEntries.length
        break
      case 'Home':
        e.preventDefault()
        nextIndex = 0
        break
      case 'End':
        e.preventDefault()
        nextIndex = layerEntries.length - 1
        break
      default:
        return
    }
    
    const nextLayer = layerEntries[nextIndex][0] as LayerType
    setVizLayer(nextLayer)
    
    // Focus will be handled by the useEffect above
  }
  return (
    <nav 
      className="px-4 sm:px-6 lg:px-10 pt-4 sm:pt-6 pb-3 sm:pb-4 mx-auto animate-on-load" 
      style={{ animationDelay: '200ms' }}
      role="navigation"
      aria-label="Alignment layer selection"
    >
      <div 
        ref={tabListRef}
        className="flex flex-wrap gap-2 sm:gap-3 justify-center"
        role="tablist"
        aria-label="Choose alignment analysis layer"
      >
        {Object.entries(LAYER_CONFIGS).map(([layerKey, config]) => {
          const isActive = currentLayer === layerKey
          return (
            <button
              key={layerKey}
              onClick={() => setVizLayer(layerKey as LayerType)}
              className={`px-2 sm:px-3 py-1 sm:py-1.5 rounded-full text-xs sm:text-sm font-medium transition-all duration-200 border-2 flex items-center gap-1 sm:gap-2 min-h-10 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sage-400 ${
                isActive
                  ? 'text-white shadow-md'
                  : 'hover:shadow-sm focus:shadow-sm'
              }`}
              role="tab"
              aria-selected={isActive}
              aria-controls="alignment-visualization"
              aria-label={`${config.displayName} layer: ${LAYER_TOOLTIPS[layerKey as LayerType]}`}
              tabIndex={isActive ? 0 : -1}
              onKeyDown={(e) => handleKeyDown(e, layerKey)}
              style={isActive 
                ? { backgroundColor: config.color, borderColor: config.color } 
                : { 
                    backgroundColor: `${config.color}20`, 
                    borderColor: config.color, 
                    color: config.color 
                  }
              }
            >
              <div
                className="w-2.5 sm:w-3 h-2.5 sm:h-3 rounded-full flex-shrink-0"
                style={{ backgroundColor: config.color }}
              />
              <span className="truncate">{config.displayName}</span>
            </button>
          )
        })}
      </div>
    </nav>
  )
}