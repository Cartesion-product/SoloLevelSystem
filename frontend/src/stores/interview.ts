import { defineStore } from 'pinia'
import { ref } from 'vue'
import { interviewApi } from '@/api'
import { streamChat } from '@/api/client'

interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export const useInterviewStore = defineStore('interview', () => {
  const sessionId = ref('')
  const messages = ref<ChatMessage[]>([])
  const isStreaming = ref(false)
  const metadata = ref<any>({})
  const isSessionActive = ref(false)

  async function startSession(resumeId?: string, jobId?: string, maxQuestions?: number) {
    const res = await interviewApi.start({
      resume_id: resumeId,
      job_id: jobId,
      max_questions: maxQuestions || 8,
    })
    sessionId.value = res.data.id
    messages.value = []
    if (res.data.first_message) {
      messages.value.push({ role: 'assistant', content: res.data.first_message })
    }
    isSessionActive.value = true
    return res.data
  }

  async function sendMessage(text: string) {
    if (!sessionId.value || isStreaming.value) return

    messages.value.push({ role: 'user', content: text })
    isStreaming.value = true

    let assistantContent = ''
    let assistantIdx = -1

    try {
      for await (const event of streamChat(sessionId.value, text)) {
        switch (event.event) {
          case 'chunk':
            if (assistantIdx === -1) {
              messages.value.push({ role: 'assistant', content: '' })
              assistantIdx = messages.value.length - 1
            }
            assistantContent += event.data.content || ''
            messages.value[assistantIdx].content = assistantContent
            break
          case 'metadata':
            metadata.value = event.data
            break
          case 'session_end':
            isSessionActive.value = false
            metadata.value = { ...metadata.value, report: event.data }
            break
          case 'error':
            if (assistantIdx === -1) {
              messages.value.push({ role: 'assistant', content: '' })
              assistantIdx = messages.value.length - 1
            }
            messages.value[assistantIdx].content = `[错误] ${event.data.message || '服务器异常，请重试'}`
            break
        }
      }
    } finally {
      isStreaming.value = false
    }
  }

  async function endSession() {
    if (!sessionId.value) return
    await interviewApi.end(sessionId.value)
    isSessionActive.value = false
  }

  function reset() {
    sessionId.value = ''
    messages.value = []
    isStreaming.value = false
    metadata.value = {}
    isSessionActive.value = false
  }

  return {
    sessionId, messages, isStreaming, metadata, isSessionActive,
    startSession, sendMessage, endSession, reset,
  }
})
