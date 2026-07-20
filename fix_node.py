path = "app/src/main/java/me/rerere/rikkahub/service/ChatService.kt"
with open(path, "r") as f:
    content = f.read()

content = content.replace(
    "node.message.role == MessageRole.SYSTEM &&\n                                node.message.parts.any { p ->",
    "node.role == MessageRole.SYSTEM &&\n                                node.currentMessage.parts.any { p ->"
)

with open(path, "w") as f:
    f.write(content)
print("Fixed!")
