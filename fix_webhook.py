path = "app/src/main/java/me/rerere/rikkahub/service/ChatService.kt"
with open(path, "r") as f:
    content = f.read()

old = '''fun triggerGenerationWithoutUserMessage(conversationId: Uuid, systemPromptExtra: String? = null) {
        val session = getOrCreateSession(conversationId)
        session.getJob()?.cancel()
        val job = appScope.launch {
            try {
                if (!systemPromptExtra.isNullOrBlank()) {
                    session.saveMutex.withLock {
                        val conv = conversationRepo.getConversationById(conversationId) ?: session.state.value
                        val injected = conv.copy(
                            messageNodes = conv.messageNodes + UIMessage(
                                role = MessageRole.SYSTEM,
                                parts = listOf(UIMessagePart.Text("[注入上下文] $systemPromptExtra"))
                            ).toMessageNode()
                        )
                        updateConversation(conversationId, injected)
                        saveConversation(conversationId, injected)
                    }
                }
                handleMessageComplete(conversationId)
            } catch (e: Exception) {
                Log.e(TAG, "triggerGenerationWithoutUserMessage failed", e)
            }
        }
        session.setJob(job)
    }'''

new = '''fun triggerGenerationWithoutUserMessage(conversationId: Uuid, systemPromptExtra: String? = null) {
        val session = getOrCreateSession(conversationId)
        if (session.getJob()?.isActive == true) {
            Log.i(TAG, "triggerGenerationWithoutUserMessage skipped: generation in progress")
            return
        }
        val job = appScope.launch {
            try {
                if (!systemPromptExtra.isNullOrBlank()) {
                    session.saveMutex.withLock {
                        val conv = conversationRepo.getConversationById(conversationId) ?: session.state.value
                        val injected = conv.copy(
                            messageNodes = conv.messageNodes + UIMessage(
                                role = MessageRole.SYSTEM,
                                parts = listOf(UIMessagePart.Text("[注入上下文] $systemPromptExtra"))
                            ).toMessageNode()
                        )
                        updateConversation(conversationId, injected)
                    }
                }
                handleMessageComplete(conversationId)
                if (!systemPromptExtra.isNullOrBlank()) {
                    session.saveMutex.withLock {
                        val conv = conversationRepo.getConversationById(conversationId) ?: session.state.value
                        val cleaned = conv.copy(
                            messageNodes = conv.messageNodes.filterNot { node ->
                                node.message.role == MessageRole.SYSTEM &&
                                node.message.parts.any { p ->
                                    (p as? UIMessagePart.Text)?.text?.startsWith("[注入上下文]") == true
                                }
                            }
                        )
                        updateConversation(conversationId, cleaned)
                        saveConversation(conversationId, cleaned)
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "triggerGenerationWithoutUserMessage failed", e)
            }
        }
        session.setJob(job)
    }'''

if old not in content:
    print("ERROR: old method not found!")
    exit(1)

content = content.replace(old, new)
with open(path, "w") as f:
    f.write(content)
print("Fix applied!")
