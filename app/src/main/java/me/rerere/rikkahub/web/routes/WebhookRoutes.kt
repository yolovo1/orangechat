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
                    val promptText = if (request.source == "wake_up") {
                        "[主动消息] ${request.prompt}"
                    } else {
                        request.prompt
                    }
                    chatService.sendMessage(
                        conversationId = convId,
                        content = listOf(UIMessagePart.Text(promptText)),
                        answer = true
                    )
                    call.respond(
                        HttpStatusCode.Accepted,
                        mapOf("status" to "accepted", "conversation_id" to convId.toString())
                    )
                }

                "inject" -> {
                    chatService.sendMessage(
                        conversationId = convId,
                        content = listOf(UIMessagePart.Text("[上下文注入] ${request.prompt}")),
                        answer = false
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
