import { create } from 'zustand'
import { api } from '@/api/client'
import type { ConfigField } from '@/types/config'

interface ConfigState {
  config: Record<string, unknown>
  schema: ConfigField[]
  isLoading: boolean
  fetchConfig: () => Promise<void>
  updateConfig: (updates: Record<string, unknown>) => Promise<void>
  resetConfig: () => Promise<void>
}

export const useConfigStore = create<ConfigState>((set) => ({
  config: {},
  schema: [],
  isLoading: false,
  fetchConfig: async () => {
    set({ isLoading: true })
    try {
      const [cfgRes, schemaRes] = await Promise.all([
        api.get<{ config: Record<string, unknown> }>('/config'),
        api.get<ConfigField[]>('/config/schema'),
      ])
      set({ config: cfgRes.config, schema: Array.isArray(schemaRes) ? schemaRes : [] })
    } catch (e) {
      console.error('Failed to fetch config:', e)
    } finally {
      set({ isLoading: false })
    }
  },
  updateConfig: async (updates) => {
    await api.put('/config', { updates })
    set((s) => ({ config: { ...s.config, ...updates } }))
  },
  resetConfig: async () => {
    await api.post('/config/reset')
    set((s) => {
      const defaults: Record<string, unknown> = {}
      s.schema.forEach((f) => { defaults[f.key] = f.default })
      return { config: defaults }
    })
  },
}))
