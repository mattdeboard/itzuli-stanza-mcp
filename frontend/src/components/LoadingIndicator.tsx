import { useState, useEffect } from 'react'

type LoadingIndicatorProps = {
  mode: 'input' | 'examples'
}

type ProgressStep = {
  name: string
  status: 'pending' | 'active' | 'completed'
}

export function LoadingIndicator({ mode }: LoadingIndicatorProps) {
  const [steps, setSteps] = useState<ProgressStep[]>([
    { name: 'Translating with Itzuli API', status: 'pending' },
    { name: 'Analyzing with Stanza NLP', status: 'pending' },
    { name: 'Generating alignments with Claude', status: 'pending' }
  ])

  useEffect(() => {
    if (mode !== 'input') return

    // Simulate realistic progress timing - but never reach 100%
    const intervals = [1500, 4000] // Transition between steps, but stay in progress

    const updateProgress = (stepIndex: number) => {
      setSteps(prev => prev.map((step, i) => ({
        ...step,
        status: i < stepIndex ? 'completed' : i === stepIndex ? 'active' : 'pending'
      })))
    }

    // Start first step immediately
    updateProgress(0)

    const timeouts: NodeJS.Timeout[] = []

    intervals.forEach((delay, index) => {
      const timeout = setTimeout(() => {
        updateProgress(index + 1)
      }, delay)
      timeouts.push(timeout)
    })

    return () => {
      timeouts.forEach(clearTimeout)
    }
  }, [mode])

  return (
    <div className="min-h-screen bg-gradient-to-br from-tan-25 via-tan-50 to-tan-100">
      <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 font-sans">
        <header className="text-center mb-3 sm:mb-4" role="banner">
          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-display font-light mb-2 text-slate-800 tracking-tight">
            Itzuli <span className="font-medium text-sage-600">Stanza</span>
          </h1>
          <h2 className="text-lg sm:text-xl font-light text-slate-500 mb-6 max-w-2xl mx-auto leading-relaxed px-4 sm:px-0">
            Translation Alignment Visualization for English-Basque Translations
          </h2>
        </header>

        <div className="flex flex-col items-center justify-center py-12">
          {/* Progress Spinner */}
          <div className="relative mb-6">
            <div className="w-16 h-16 border-4 border-sage-100 border-t-sage-500 rounded-full animate-spin"></div>
            <div className="absolute inset-0 w-16 h-16 border-4 border-transparent border-r-sage-300 rounded-full animate-spin animate-reverse" style={{ animationDuration: '1.5s' }}></div>
          </div>

          {/* Progress Steps */}
          <div className="bg-white/60 backdrop-blur-sm border border-slate-200/60 rounded-lg p-6 max-w-md mx-auto">
            <div className="text-center mb-4">
              <h3 className="text-lg font-medium text-slate-800 mb-2">
                {mode === 'input' ? 'Analyzing Translation' : 'Loading Alignment Data'}
              </h3>
              <p className="text-sm text-slate-600">
                {mode === 'input'
                  ? 'Processing your text through our AI pipeline...'
                  : 'Loading example sentence data...'}
              </p>
            </div>

            {mode === 'input' && (
              <div className="space-y-3">
                {steps.map((step, index) => (
                  <div key={index} className="flex items-center space-x-3">
                    <div className="flex-shrink-0 w-5 h-5 flex items-center justify-center">
                      {step.status === 'completed' ? (
                        <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      ) : step.status === 'active' ? (
                        <div className="w-3 h-3 bg-sage-500 rounded-full animate-pulse"></div>
                      ) : (
                        <div className="w-3 h-3 bg-slate-300 rounded-full"></div>
                      )}
                    </div>
                    <span className={`text-sm transition-colors duration-300 ${
                      step.status === 'completed' ? 'text-green-700 font-medium' :
                      step.status === 'active' ? 'text-slate-700' :
                      'text-slate-500'
                    }`}>
                      {step.name}
                    </span>
                  </div>
                ))}
              </div>
            )}

          </div>

          <p className="text-xs text-slate-500 mt-4 max-w-sm text-center">
            This may take 10-30 seconds depending on text complexity
          </p>
        </div>
      </div>
    </div>
  )
}