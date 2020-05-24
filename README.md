# Tobrie
Le magnifique bot de l'asso Eirbot, sur Telegram et Discord.

Ce bot a avant tout été développé pour être déployé sur Telegram. Il a ensuite été remodelé dans une forme relativement adaptative pour supporter facilement l'ajout d'une nouvelle API pour le déploiement sur une autre plateforme. Il est ainsi partiellement supporté simultanément sur Discord.

Les fonctions non déployées sur Discord sont en fait des fonctions relativement propres à Telegram, qu'il serait difficle d'adapter facilement à Discord (InlineQuerry, stickers...). Les fonctions de réponses automatiques de texte, vidéo ou image ont en revanche été très facile à adapter, et seront facile à également déployer sur une autre plateforme de chat en ligne fournissant une API python.

### bot4.0.py
C'est le fichier principal, à la racine de l'exécution. Il importe les fichiers auxiliaires, instancie les bots sur Telegram et Discord, définit les commandes et en implémente certaines.

### contextual_bot.py
Cette classe permet de généraliser les entrées/sorties du bot pour n'importe quelle API. On y retrouve une partie pour l'API Telegram, et une autre partie pour l'API Discord.

### shared_core.py
Cette classe permet de fournir un accès commun à des ressources partagées aux divers événements des bots. On y trouve notemment un système de log sur fichiers en local, ainsi qu'une redirection des événements vers une console.

### audio.py
Ce fichier permet d'effectuer diverses concaténations de fichiers audios.

### auto_reply.py
Ce fichier regroupe les fonctionnalités principales de réponses automatiques dans les chats vus par le bot. Ces réponses peuvent contenir du texte, des images, des vidéos, des fichiers son, des stickers...

### config.py
On trouve ici différentes constantes...

### inventory.py
Ce fichier fournit des fonctions pour lire l'inventaire du local sous forme de fichier html, ainsi que pour y effectuer des recherches.

### web_texts.py
Ici, un regroupement de diverses fonctions renvoyant des contenus sous forme de texte issus de divers sites internet.
