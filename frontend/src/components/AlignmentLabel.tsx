import { LayerType } from '../types/alignment'
import { LAYER_CONFIGS } from './LayerPicker'

type AlignmentLabelProps = {
  label: string
  currentLayer: LayerType
  index?: number
  visible?: boolean
}

export function AlignmentLabel({ label, currentLayer, index, visible = false }: AlignmentLabelProps) {
  if (!visible) {
    return null
  }

  return (
    <div
      className="flex items-start gap-3 p-3 rounded-md transition-all duration-200"
      style={{ backgroundColor: `${LAYER_CONFIGS[currentLayer].color}10` }}
    >
      <div
        className="w-3 h-3 rounded-full flex-shrink-0 mt-0.5"
        style={{ backgroundColor: LAYER_CONFIGS[currentLayer].color }}
      />
      <div className="text-sm text-gray-700 leading-relaxed">
        {label}
      </div>
    </div>
  )
}