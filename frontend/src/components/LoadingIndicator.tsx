import classNames from 'classnames'
import { useEffect, useState } from 'react'
import { useI18n } from '../i18n'
import type { LoadingStage } from '../services/alignmentApi'

type LoadingIndicatorProps = {
  mode: 'input' | 'examples'
  loadingStage?: LoadingStage | null
}

type ProgressStep = {
  name: string
  status: 'pending' | 'active' | 'completed'
}

const STAGE_INDEX: Record<LoadingStage, number> = {
  itzuli: 0,
  stanza: 1,
  claude: 2,
}

export function LoadingIndicator({ mode, loadingStage }: LoadingIndicatorProps) {
  const { t } = useI18n()
  const [steps, setSteps] = useState<ProgressStep[]>([])

  // Initialize steps with translations
  useEffect(() => {
    setSteps([
      { name: t('loading.step_translating'), status: 'pending' },
      { name: t('loading.step_analyzing'), status: 'pending' },
      { name: t('loading.step_generating_alignments'), status: 'pending' },
    ])
  }, [t])

  // Drive steps from real SSE stage events when available
  useEffect(() => {
    if (mode !== 'input') return
    if (loadingStage == null) return

    const activeIndex = STAGE_INDEX[loadingStage]
    setSteps((prev) =>
      prev.map((step, i) => ({
        ...step,
        status: i < activeIndex ? 'completed' : i === activeIndex ? 'active' : 'pending',
      }))
    )
  }, [mode, loadingStage])

  // Fallback timer-based progress when loadingStage is not provided
  useEffect(() => {
    if (mode !== 'input') return
    if (loadingStage != null) return

    const updateProgress = (stepIndex: number) => {
      setSteps((prev) =>
        prev.map((step, i) => ({
          ...step,
          status: i < stepIndex ? 'completed' : i === stepIndex ? 'active' : 'pending',
        }))
      )
    }

    updateProgress(0)

    const timeouts = [
      setTimeout(() => updateProgress(1), 1500),
      setTimeout(() => updateProgress(2), 4000),
    ]

    return () => {
      timeouts.forEach(clearTimeout)
    }
  }, [mode, loadingStage])

  return (
    <div
      className={classNames(
        'min-h-screen',
        'bg-gradient-to-br',
        'from-tan-25',
        'via-tan-50',
        'to-tan-100'
      )}
    >
      <div className={classNames('max-w-7xl', 'mx-auto', 'p-4', 'sm:p-6', 'lg:p-8', 'font-sans')}>
        <header className={classNames('text-center', 'mb-3', 'sm:mb-4')}>
          <h1
            className={classNames(
              'text-3xl',
              'sm:text-4xl',
              'lg:text-5xl',
              'font-display',
              'font-light',
              'mb-2',
              'text-slate-800',
              'tracking-tight'
            )}
          >
            Xingolak
          </h1>
          <h2
            className={classNames(
              'text-lg',
              'sm:text-xl',
              'font-light',
              'text-slate-500',
              'mb-6',
              'max-w-2xl',
              'mx-auto',
              'leading-relaxed',
              'px-4',
              'sm:px-0'
            )}
          >
            {t('app.loading.subtitle')}
          </h2>
        </header>

        <div className={classNames('flex', 'flex-col', 'items-center', 'justify-center', 'py-12')}>
          {/* Progress Spinner */}
          <div className={classNames('relative', 'mb-6')}>
            <div
              className={classNames(
                'w-16',
                'h-16',
                'border-4',
                'border-teal-100',
                'border-t-teal-700',
                'rounded-full',
                'animate-spin'
              )}
            ></div>
            <div
              className={classNames(
                'absolute',
                'inset-0',
                'w-16',
                'h-16',
                'border-4',
                'border-transparent',
                'border-r-teal-300',
                'rounded-full',
                'animate-spin',
                'animate-reverse'
              )}
              style={{ animationDuration: '1.5s' }}
            ></div>
          </div>

          {/* Progress Steps */}
          <div
            className={classNames(
              'bg-white/60',
              'backdrop-blur-sm',
              'border',
              'border-slate-200/60',
              'rounded-lg',
              'p-6',
              'max-w-md',
              'mx-auto'
            )}
          >
            <div className={classNames('text-center', 'mb-4')}>
              <h3 className={classNames('text-lg', 'font-medium', 'text-slate-800', 'mb-2')}>
                {mode === 'input'
                  ? t('loading.analyzing_translation')
                  : t('loading.loading_alignment_data')}
              </h3>
              <p className={classNames('text-sm', 'text-slate-600')}>
                {mode === 'input' ? t('loading.processing_text') : t('loading.loading_examples')}
              </p>
            </div>

            {mode === 'input' && (
              <div className="space-y-3">
                {steps.map((step) => (
                  <div key={step.name} className={classNames('flex', 'items-center', 'space-x-3')}>
                    <div
                      className={classNames(
                        'flex-shrink-0',
                        'w-5',
                        'h-5',
                        'flex',
                        'items-center',
                        'justify-center'
                      )}
                    >
                      {step.status === 'completed' ? (
                        <svg
                          className={classNames('w-4', 'h-4', 'text-green-600')}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <title id="step-completed-icon">Step Completed Icon</title>
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                      ) : step.status === 'active' ? (
                        <div
                          className={classNames(
                            'w-3',
                            'h-3',
                            'bg-teal-700',
                            'rounded-full',
                            'animate-pulse'
                          )}
                        ></div>
                      ) : (
                        <div
                          className={classNames('w-3', 'h-3', 'bg-slate-300', 'rounded-full')}
                        ></div>
                      )}
                    </div>
                    <span
                      className={classNames(
                        'text-sm',
                        'transition-colors',
                        'duration-300',
                        step.status === 'completed'
                          ? 'text-green-700 font-medium'
                          : step.status === 'active'
                            ? 'text-slate-700'
                            : 'text-slate-500'
                      )}
                    >
                      {step.name}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <p className={classNames('text-xs', 'text-slate-500', 'mt-4', 'max-w-sm', 'text-center')}>
            {t('loading.time_estimate')}
          </p>
        </div>
      </div>
    </div>
  )
}
