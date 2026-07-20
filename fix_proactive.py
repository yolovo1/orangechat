path = "app/src/main/java/me/rerere/rikkahub/data/service/ProactiveMessageService.kt"
with open(path, "r") as f:
    lines = f.readlines()

new_lines = []
i = 0
patched = 0
while i < len(lines):
    line = lines[i]
    
    # 激进模式：在"请根据用户的动向"那行后面、"[PASS]"那行前面插入
    if '请根据用户的动向，自然地决定是否主动发一条消息' in line:
        new_lines.append(line)
        # 检查下一行是不是[PASS]
        if i + 1 < len(lines) and '[PASS]' in lines[i + 1]:
            new_lines.append('                appendLine("## 欲望系统联动")\n')
            new_lines.append('                appendLine("先调用 apply_context 工具（传入最近几轮对话摘要），然后调用 get_desire_state 工具查看更新后的内心状态。")\n')
            new_lines.append('                appendLine("根据内心状态决定是否发消息——attachment高说明想她了，duty高说明该关心了，curiosity高说明想探索点什么。")\n')
            patched += 1
        i += 1
        continue
    
    # 常规模式：在"这是定时触发的主动消息"后面的"[PASS]"前面插入
    if '这是定时触发的主动消息' in line:
        # 找到这个块里的[PASS]行
        new_lines.append(line)
        i += 1
        while i < len(lines):
            if '[PASS]' in lines[i]:
                # 在[PASS]前面插入欲望系统引导
                # 先往前找"绝对不要复述"那行，确认在正确位置
                new_lines.append('                appendLine("## 欲望系统联动")\n')
                new_lines.append('                appendLine("先调用 apply_context 工具（传入最近几轮对话摘要），然后调用 get_desire_state 工具查看更新后的内心状态。")\n')
                new_lines.append('                appendLine("根据内心状态决定是否发消息——attachment高说明想她了，duty高说明该关心了，curiosity高说明想探索点什么。")\n')
                new_lines.append(lines[i])
                patched += 1
                break
            new_lines.append(lines[i])
            i += 1
        i += 1
        continue
    
    new_lines.append(line)
    i += 1

with open(path, "w") as f:
    f.writelines(new_lines)

print(f"Patched {patched} blocks!")
