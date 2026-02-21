import { LayerType } from '../types/alignment'

type LayerConfig = {
  name: string
  displayName: string
  color: string
}

export const LAYER_CONFIGS: Record<LayerType, LayerConfig> = {
  [LayerType.LEXICAL]: {
    name: LayerType.LEXICAL,
    displayName: 'Lexical',
    color: '#10B981'
  },
  [LayerType.GRAMMATICAL_RELATIONS]: {
    name: LayerType.GRAMMATICAL_RELATIONS,
    displayName: 'Grammatical Relations',
    color: '#E07C3E'
  },
  [LayerType.FEATURES]: {
    name: LayerType.FEATURES,
    displayName: 'Features',
    color: '#8B5CF6'
  }
}

type LayerPickerProps = {
  currentLayer: LayerType
  setVizLayer: (layer: LayerType) => void
}

export function LayerPicker({ currentLayer, setVizLayer }: LayerPickerProps) {
  return (
    <div className="px-8 pt-4 pb-2 mx-8">
      <div className="flex gap-2 justify-center">
        {Object.entries(LAYER_CONFIGS).map(([layerKey, config]) => {
          const isActive = currentLayer === layerKey
          return (
            <button
              key={layerKey}
              onClick={() => setVizLayer(layerKey as LayerType)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200 border-2 flex items-center gap-2 ${
                isActive
                  ? 'border-current text-white shadow-md'
                  : 'border-gray-300 text-gray-600 hover:border-gray-400'
              }`}
              style={isActive ? { backgroundColor: config.color, borderColor: config.color } : {}}
            >
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: config.color }}
              />
              {config.displayName}
            </button>
          )
        })}
      </div>
    </div>
  )
}