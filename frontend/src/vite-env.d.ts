/// <reference types="vite/client" />

type ImportMetaEnv = {
  readonly VITE_USE_FIXTURES: string
  readonly VITE_API_BASE_URL: string
}

type ImportMeta = {
  readonly env: ImportMetaEnv
}
