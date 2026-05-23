import { useEffect, useState } from 'react'
import { useConfigStore } from '@/store/configStore'
import type { ProviderInfo } from '@/types/config'
import { api } from '@/api/client'
import * as Select from '@radix-ui/react-select'
import * as Switch from '@radix-ui/react-switch'
import { Save, RotateCcw, ChevronDown, Check } from 'lucide-react'

const LANGUAGES = ['English', 'Chinese', 'Japanese', 'Korean', 'Spanish', 'Portuguese', 'French', 'German', 'Arabic', 'Russian', 'Hindi']
const VENDORS = ['yfinance', 'alpha_vantage']

function RadixSelect({ value, onValueChange, options, placeholder }: {
  value: string
  onValueChange: (v: string) => void
  options: { label: string; value: string }[]
  placeholder?: string
}) {
  return (
    <Select.Root value={value} onValueChange={onValueChange}>
      <Select.Trigger className="w-full flex items-center justify-between px-3 py-2 border border-slate-700 rounded-md text-sm bg-slate-950 focus:border-sky-500 focus:outline-none data-[placeholder]:text-slate-500">
        <Select.Value placeholder={placeholder} />
        <Select.Icon><ChevronDown className="w-4 h-4 text-slate-400" /></Select.Icon>
      </Select.Trigger>
      <Select.Portal>
        <Select.Content className="z-50 bg-slate-900 border border-slate-700 rounded-md shadow-xl overflow-hidden">
          <Select.Viewport>
            {options.map((opt) => (
              <Select.Item key={opt.value} value={opt.value}
                className="flex items-center gap-2 px-3 py-2 text-sm cursor-pointer hover:bg-slate-800 focus:bg-slate-800 focus:outline-none data-[state=checked]:text-sky-400">
                <Select.ItemText>{opt.label}</Select.ItemText>
                <Select.ItemIndicator><Check className="w-3.5 h-3.5 text-sky-400" /></Select.ItemIndicator>
              </Select.Item>
            ))}
          </Select.Viewport>
        </Select.Content>
      </Select.Portal>
    </Select.Root>
  )
}

export function Settings() {
  const { config, fetchConfig, updateConfig, resetConfig, isLoading } = useConfigStore()
  const [providers, setProviders] = useState<ProviderInfo[]>([])
  const [local, setLocal] = useState<Record<string, unknown>>({})
  const [savedSections, setSavedSections] = useState<Record<string, boolean>>({})

  useEffect(() => {
    fetchConfig()
    api.get<ProviderInfo[]>('/models/providers').then(setProviders).catch(() => {})
  }, [])

  useEffect(() => { setLocal({ ...config }) }, [config])

  const handleSave = async (section: string, updates: Record<string, unknown>) => {
    await updateConfig(updates)
    setSavedSections((s) => ({ ...s, [section]: true }))
    setTimeout(() => setSavedSections((s) => ({ ...s, [section]: false })), 2000)
  }

  const currentProvider = providers.find((p) => p.key === (local.llm_provider as string || 'openai'))
  const providerOptions = providers.map((p) => ({ label: p.display_name, value: p.key }))

  if (isLoading) return <div className="text-center py-8 text-slate-400">Loading settings...</div>

  return (
    <div className="max-w-3xl space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-slate-400 mt-1">Configure the TradingAgents system</p>
      </div>

      {/* LLM Provider */}
      <section className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
        <h3 className="font-semibold">LLM Provider</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium block mb-1">Provider</label>
            <RadixSelect
              value={local.llm_provider as string || 'openai'}
              onValueChange={(v) => setLocal({ ...local, llm_provider: v })}
              options={providerOptions}
            />
          </div>
          <div>
            <label className="text-sm font-medium block mb-1">Output Language</label>
            <RadixSelect
              value={local.output_language as string || 'English'}
              onValueChange={(v) => setLocal({ ...local, output_language: v })}
              options={LANGUAGES.map((l) => ({ label: l, value: l }))}
            />
          </div>
          <div>
            <label className="text-sm font-medium block mb-1">Quick-Thinking Model</label>
            <input value={local.quick_think_llm as string || ''}
              onChange={(e) => setLocal({ ...local, quick_think_llm: e.target.value })}
              className="w-full px-3 py-2 border border-slate-700 rounded-md text-sm bg-slate-950 focus:border-sky-500 focus:outline-none" />
          </div>
          <div>
            <label className="text-sm font-medium block mb-1">Deep-Thinking Model</label>
            <input value={local.deep_think_llm as string || ''}
              onChange={(e) => setLocal({ ...local, deep_think_llm: e.target.value })}
              className="w-full px-3 py-2 border border-slate-700 rounded-md text-sm bg-slate-950 focus:border-sky-500 focus:outline-none" />
          </div>
          <div>
            <label className="text-sm font-medium block mb-1">Backend URL (optional)</label>
            <input value={local.backend_url as string || ''}
              onChange={(e) => setLocal({ ...local, backend_url: e.target.value || null })}
              placeholder="Custom API endpoint"
              className="w-full px-3 py-2 border border-slate-700 rounded-md text-sm bg-slate-950 focus:border-sky-500 focus:outline-none" />
          </div>
          {currentProvider?.supports_thinking_config && (
            <div>
              <label className="text-sm font-medium block mb-1">Thinking Effort</label>
              <RadixSelect
                value={(local.openai_reasoning_effort || local.google_thinking_level || local.anthropic_effort || 'medium') as string}
                onValueChange={(v) => {
                  const key = local.llm_provider === 'openai' ? 'openai_reasoning_effort'
                    : local.llm_provider === 'google' ? 'google_thinking_level' : 'anthropic_effort'
                  setLocal({ ...local, [key]: v })
                }}
                options={[
                  { label: 'Low', value: 'low' },
                  { label: 'Medium', value: 'medium' },
                  { label: 'High', value: 'high' },
                ]}
              />
            </div>
          )}
        </div>
        <button onClick={() => handleSave('provider', {
          llm_provider: local.llm_provider, quick_think_llm: local.quick_think_llm,
          deep_think_llm: local.deep_think_llm, output_language: local.output_language,
          backend_url: local.backend_url, google_thinking_level: local.google_thinking_level,
          openai_reasoning_effort: local.openai_reasoning_effort, anthropic_effort: local.anthropic_effort,
        })} className="flex items-center gap-2 px-4 py-2 bg-sky-500 text-slate-900 rounded-md text-sm hover:bg-sky-400 transition-colors font-medium">
          <Save className="w-4 h-4" /> {savedSections['provider'] ? 'Saved!' : 'Save Provider Settings'}
        </button>
      </section>

      {/* Analysis Parameters */}
      <section className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
        <h3 className="font-semibold">Analysis Parameters</h3>
        <div className="grid grid-cols-3 gap-4">
          {[
            { key: 'max_debate_rounds', label: 'Debate Rounds', min: 1, max: 5 },
            { key: 'max_risk_discuss_rounds', label: 'Risk Rounds', min: 1, max: 5 },
            { key: 'analyst_concurrency_limit', label: 'Concurrency', min: 1, max: 4 },
            { key: 'news_article_limit', label: 'News Limit', min: 1, max: 100 },
            { key: 'global_news_lookback_days', label: 'News Lookback', min: 1, max: 30 },
          ].map(({ key, label, min, max }) => (
            <div key={key}>
              <label className="text-sm font-medium block mb-1">{label}</label>
              <input type="number" min={min} max={max}
                value={local[key] as number || min}
                onChange={(e) => setLocal({ ...local, [key]: parseInt(e.target.value) || min })}
                className="w-full px-3 py-2 border border-slate-700 rounded-md text-sm bg-slate-950 focus:border-sky-500 focus:outline-none" />
            </div>
          ))}
          <div>
            <label className="text-sm font-medium block mb-1">Checkpoint Resume</label>
            <div className="flex items-center gap-3 mt-2">
              <Switch.Root
                checked={local.checkpoint_enabled as boolean || false}
                onCheckedChange={(checked) => setLocal({ ...local, checkpoint_enabled: checked })}
                className="w-9 h-5 rounded-full bg-slate-700 data-[state=checked]:bg-sky-500 transition-colors relative"
              >
                <Switch.Thumb className="block w-4 h-4 rounded-full bg-white translate-x-0.5 data-[state=checked]:translate-x-[18px] transition-transform" />
              </Switch.Root>
              <span className="text-sm text-slate-400">{local.checkpoint_enabled ? 'Enabled' : 'Disabled'}</span>
            </div>
          </div>
        </div>
        <button onClick={() => handleSave('analysis', {
          max_debate_rounds: local.max_debate_rounds, max_risk_discuss_rounds: local.max_risk_discuss_rounds,
          analyst_concurrency_limit: local.analyst_concurrency_limit, news_article_limit: local.news_article_limit,
          global_news_lookback_days: local.global_news_lookback_days, checkpoint_enabled: local.checkpoint_enabled,
        })} className="flex items-center gap-2 px-4 py-2 bg-sky-500 text-slate-900 rounded-md text-sm hover:bg-sky-400 transition-colors font-medium">
          <Save className="w-4 h-4" /> {savedSections['analysis'] ? 'Saved!' : 'Save Analysis Settings'}
        </button>
      </section>

      {/* Data Vendors */}
      <section className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
        <h3 className="font-semibold">Data Vendors</h3>
        <div className="grid grid-cols-2 gap-4">
          {['core_stock_apis', 'technical_indicators', 'fundamental_data', 'news_data'].map((category) => (
            <div key={category}>
              <label className="text-sm font-medium block mb-1 capitalize">{category.replace(/_/g, ' ')}</label>
              <RadixSelect
                value={((local.data_vendors as Record<string, string>)?.[category]) || 'yfinance'}
                onValueChange={(v) => {
                  const dv = { ...(local.data_vendors as Record<string, string> || {}), [category]: v }
                  setLocal({ ...local, data_vendors: dv })
                }}
                options={VENDORS.map((v) => ({ label: v, value: v }))}
              />
            </div>
          ))}
        </div>
        <button onClick={() => handleSave('vendors', { data_vendors: local.data_vendors })}
          className="flex items-center gap-2 px-4 py-2 bg-sky-500 text-slate-900 rounded-md text-sm hover:bg-sky-400 transition-colors font-medium">
          <Save className="w-4 h-4" /> {savedSections['vendors'] ? 'Saved!' : 'Save Vendor Settings'}
        </button>
      </section>

      {/* Reset */}
      <div className="border-t border-slate-800 pt-6">
        <button onClick={async () => { await resetConfig(); fetchConfig(); }}
          className="flex items-center gap-2 px-4 py-2 border border-red-500/30 text-red-400 rounded-md text-sm hover:bg-red-500/10 transition-colors font-medium">
          <RotateCcw className="w-4 h-4" /> Reset All to Factory Defaults
        </button>
      </div>
    </div>
  )
}
