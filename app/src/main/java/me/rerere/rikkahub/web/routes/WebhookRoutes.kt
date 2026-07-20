package me.rerere.rikkahub.web.routes

import io.ktor.http.HttpStatusCode
import io.ktor.server.request.receive
import io.ktor.server.response.respond
import io.ktor.server.routing.Route
import io.ktor.server.routing.post
import io.ktor.server.routing.route
import kotlinx.coroutines.flow.first
import kotlinx.serialization.Serializable
import me.rerere.ai.ui.UIMessagePart
import me.rerere.rikkahub.data.datastore.SettingsStore
import me.rerere.rikkahub.data.repository.ConversationRepository
import me.rerere.rikkahub.service.ChatService
import kotlin.uuid.Uuid

@Serializable
data class WebhookRequest(
    val type: String = "proactive",
    val prompt: String = "",
    val conversationId: String? = null,
    val source: String = "external",
    val token: String? = null
)

fun Route.webhookRoutes(
    chatService: ChatService,
    conversationRepo: ConversationRepository,
    settingsStore: SettingsStore
) {
    route("/webhook") {
        post {
            val request = call.receive<WebhookRequest>()

            val convId = request.conversationId?.let {
                runCatching { Uuid.parse(it) }.getOrNull()
            } ?: run {
                val settings = settingsStore.settingsFlow.first()
                val conversations = conversationRepo
                    .getConversationsOfAssistant(settings.assistantId)
                    .first()
                conversations.firstOrNull()?.id ?: Uuid.random()
            }

            chatService.initializeConversation(convId)

            when (request.type.lowercase()) {
                "proactive" -> {
                    // 不创建user消息，把prompt作为system上下文注入后直接触发生成
                    chatService.triggerGenerationWithoutUserMessage(
                        conversationId = convId,
                        systemPromptExtra = request.prompt
                    )
                    call.respond(
                        HttpStatusCode.Accepted,
                        mapOf("status" to "accepted", "conversation_id" to convId.toString())
                    )
                }

                "inject" -> {
                    // 注入system上下文，不创建user消息，不触发生成
                    chatService.triggerGenerationWithoutUserMessage(
                        conversationId = convId,
                        systemPromptExtra = request.prompt
                    )
                    call.respond(
                        HttpStatusCode.Accepted,
                        mapOf("status" to "injected", "conversation_id" to convId.toString())
                    )
                }

                "notification" -> {
                    call.respond(
                        HttpStatusCode.Accepted,
                        mapOf("status" to "notified")
                    )
                }

                else -> {
                    call.respond(
                        HttpStatusCode.BadRequest,
                        mapOf("error" to "Unknown type: ${request.type}")
                    )
                }
            }
        }
    }
}
