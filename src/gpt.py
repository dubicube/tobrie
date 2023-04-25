import openai

from contextual_bot import *

GPT_SYSTEM_PROMPT = {"role": "system", "content": "Tu est un chatbot qui s'appelle Brenda"}
# GPT_SYSTEM_PROMPT = []
gpt_convData = {}

def GPT_checkChatIDExists(chatID):
    if not chatID in gpt_convData:
        gpt_convData[chatID] = (False, [GPT_SYSTEM_PROMPT.copy()])

def GPT_startConvMode(contextual_bot, sh_core):
    chatID = contextual_bot.getChatID()
    GPT_checkChatIDExists(chatID)
    prompt = "" # TODO
    gpt_conversation_mode = True
    if len(prompt) != 0:
        gpt_convData[chatID] = (False, [GPT_SYSTEM_PROMPT.copy()] + [{"role": "system", "content": prompt}])
    else:
        gpt_convData[chatID] = (True, [GPT_SYSTEM_PROMPT.copy()])
    contextual_bot.reply(ContextualBot.TEXT, "ChatGPT mode conversation activé: tous les messages sont désormais répondu par ChatGPT (avec mémoire). Exécuter la commande /gptstop pour arrêter ce mode.")

def GPT_stopConvMode(contextual_bot, sh_core):
    chatID = contextual_bot.getChatID()
    GPT_checkChatIDExists(chatID)
    gpt_convData[chatID] = (False, [GPT_SYSTEM_PROMPT.copy()])
    contextual_bot.reply(ContextualBot.TEXT, "ChatGPT mode conversation désactivé")

def GPT_setSystemPrompt(contextual_bot, sh_core):
    msg = contextual_bot.getText()[len("/gptconfig "):]
    chatID = contextual_bot.getChatID()
    GPT_checkChatIDExists(chatID)
    (conversationMode, convHistory) = gpt_convData[chatID]
    GPT_SYSTEM_PROMPT = {"role": "system", "content": msg}
    convHistory[0] = {"role": "system", "content": msg}
    gpt_convData[chatID] = (conversationMode, convHistory)

def GPT_getResponse(contextual_bot):
    msg = contextual_bot.getText()
    chatID = contextual_bot.getChatID()
    GPT_checkChatIDExists(chatID)
    
    (conversationMode, convHistory) = gpt_convData[chatID]
    if conversationMode:
        gptprompt = msg
        convHistory += [{"role": "user", "content": gptprompt}]
        completion = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo", 
            messages = convHistory
        )
        chatgpt_resp = str(completion['choices'][0]['message']['content'])
        convHistory += [{"role": "assistant", "content": chatgpt_resp}]
        gpt_convData[chatID] = (conversationMode, convHistory)
        if len(chatgpt_resp) > 1:
            return chatgpt_resp
    elif msg.endswith('@eir_bot'):
        gptprompt = msg[:-len('@eir_bot')]
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[{"role": "user", "content": gptprompt}]
        )
        chatgpt_resp = str(completion['choices'][0]['message']['content'])
        if len(chatgpt_resp) > 1:
            return chatgpt_resp
    return ""