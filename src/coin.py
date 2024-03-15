import data_manager
import contextual_bot

def getUserCoins(conv_id, user_id):
    dm = data_manager.DataManager()
    coins = dm.getRessourceSmart(str(conv_id), "coincount", str(user_id))
    try:
        coins = int(coins)
    except:
        coins = 0
    return coins

def increaseUserCoins(conv_id, user_id, increaseAmount):
    dm = data_manager.DataManager()
    coins = dm.getRessourceSmart(str(conv_id), "coincount", str(user_id))
    try:
        coins = int(coins)
    except:
        coins = 0
    coins += increaseAmount
    dm.saveRessourceSmart(str(conv_id), "coincount", str(user_id), str(coins))
    return coins

def increaseUserCoinsFromMessage(conv_id, user_id, msgType, msgData):
    increaseValue = 0
    if msgType == contextual_bot.ContextualBot.TEXT:
        increaseValue = len(msgData)
    elif msgType == contextual_bot.ContextualBot.DOCUMENT:
        increaseValue = 200
    elif msgType == contextual_bot.ContextualBot.VIDEO:
        # TODO: adjust coin increase depending on video rarity
        increaseValue = 200
    elif msgType == contextual_bot.ContextualBot.IMAGE:
        increaseValue = 300
    elif msgType == contextual_bot.ContextualBot.AUDIO:
        increaseValue = 200
    elif msgType == contextual_bot.ContextualBot.STICKER:
        increaseValue = 200
    elif msgType == contextual_bot.ContextualBot.CHAINED_STICKERS:
        increaseValue = 200
    elif msgType == contextual_bot.ContextualBot.ANIMATION:
        increaseValue = 200

    increaseUserCoins(conv_id, user_id, increaseValue)