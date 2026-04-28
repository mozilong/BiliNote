import { useState, useEffect } from 'react'
import { useModelStore } from '@/store/modelStore'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import toast from 'react-hot-toast'

interface ModelSelectorProps {
  providerId: string
  onModelAdded?: () => void
}

export function ModelSelector({ providerId, onModelAdded }: ModelSelectorProps) {
  const { models, loading, selectedModel, loadModels, setSelectedModel, addNewModel } =
    useModelStore()
  const [search, setSearch] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [mode, setMode] = useState<'select' | 'manual'>('select')
  const [manualName, setManualName] = useState('')

  const filteredModels = models.filter(model => {
    const keywords = search.trim().toLowerCase().split(/\s+/)
    const target = model.id.toLowerCase()
    return keywords.every(kw => target.includes(kw))
  })

  useEffect(() => {
    if (providerId) {
      loadModels(providerId)
    }
  }, [providerId])

  const handleSubmit = async () => {
    const modelName = mode === 'manual' ? manualName.trim() : selectedModel
    if (!modelName) {
      toast.error('请选择或输入模型名称')
      return
    }
    try {
      setSubmitting(true)
      await addNewModel(providerId, modelName)
      toast.success('模型添加成功')
      setManualName('')
      setSelectedModel('')
      onModelAdded?.()
    } catch (error) {
      toast.error('添加模型失败')
    } finally {
      setSubmitting(false)
    }
  }

  const canSubmit = mode === 'manual' ? manualName.trim().length > 0 : !!selectedModel

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-2 font-bold">
        <span>添加模型</span>
        <Button
          variant="ghost"
          type="button"
          onClick={() => loadModels(providerId)}
          disabled={loading}
        >
          {loading ? '加载中...' : '刷新列表'}
        </Button>
        <Button
          variant="ghost"
          type="button"
          size="sm"
          onClick={() => {
            setMode(mode === 'select' ? 'manual' : 'select')
            setManualName('')
            setSelectedModel('')
          }}
        >
          {mode === 'select' ? '手动输入' : '从列表选'}
        </Button>
      </div>

      {mode === 'manual' ? (
        <Input
          placeholder="输入模型名称，如 gpt-4o, claude-3-opus..."
          value={manualName}
          onChange={e => setManualName(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'Enter') {
              e.preventDefault()
              handleSubmit()
            }
          }}
          className="w-[300px]"
        />
      ) : (
        <Select value={selectedModel} onValueChange={setSelectedModel}>
          <SelectTrigger className="w-[300px]">
            <SelectValue placeholder="从列表选择模型" />
          </SelectTrigger>
          <SelectContent>
            <div className="p-2">
              <Input
                placeholder="搜索模型..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="h-8"
              />
            </div>
            {filteredModels.map((model, index) => (
              <SelectItem key={`${model.id}-${index}`} value={model.id}>
                {model.id}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}

      <Button onClick={handleSubmit} disabled={!canSubmit || submitting}>
        {submitting ? '保存中...' : '保存模型'}
      </Button>
    </div>
  )
}
