export interface ConfigField {
  key: string
  type: 'string' | 'int' | 'float' | 'bool' | 'dict' | 'list'
  description: string
  default: unknown
  options?: string[]
  env_override?: string
}

export interface ProviderInfo {
  key: string
  display_name: string
  default_backend_url: string | null
  requires_api_key: boolean
  api_key_env: string | null
  supports_thinking_config: boolean
}

export interface ModelItem {
  label: string
  value: string
}

export interface ModelOptions {
  provider: string
  quick: ModelItem[]
  deep: ModelItem[]
}
