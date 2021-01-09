# Tobrie
Le magnifique bot de l'asso Eirbot, actuellement déployé sur 4 plateformes:
+ Telegram: @eir_bot
+ Discord: https://discord.com/api/oauth2/authorize?client_id=693578928777854986&permissions=3197504&scope=bot
+ Mail: brenda.tobrie@gmail.com
+ Twitter: @BrendaTobrie

Déploiements futurs potentiels (non garanti lol):
+ Application mobile (en cours de développement)
+ Messenger
+ Youtube (live 24h/24)

Ce bot a avant tout été développé autour de l'API Telegram. Il a ensuite été remodelé dans une forme relativement adaptative pour supporter facilement l'ajout de nouvelles API pour le déploiement sur d'autres plateformes. Certaines fonctionnalités ne peuvent cependant pas être déployées sur toutes les plateformes, .

## Fresh install:

Pour lancer ce code, il faut:
- L'ensemble de ce repo
- Avoir un token de bot telegram pour la production
- Avoir un token de bot telegram pour le test
- Avoir un token de bot discord
- Avoir les tokens d'un bot Twitter
- Créer un fihier "tokens" dans /tobrie/src/ où il faut mettre tous les tokens, un par ligne en respectant le positionnement décrit dans le fichier /tobrie/src/tokens_description

Il n'est pas obligatoire d'avoir tous les tokens (il faut juste laisser la ligne vide dans le fichier tokens dans ce cas). Il faut cependant désactiver les fonctions associées aux tokens non disponibles. Pour cela, il faut modifier l'affectation de certains booléens dans main.py:
- TELEGRAM_ENABLE permet d'activer le bot telegram
- DISCORD_ENABLE permet d'activer le bot discord
- PERIODIC_ENABLE permet d'activer le bot twitter et email
- BRENDAPI_ENABLE permet d'activer l'API Brenda externe
- EVENTS_ENABLE permet d'activer les événements programmés

Après configuration, le bot se lance en exécutant main.py dans le répertoire /tobrie/src/. Pour lancer en mode test, ajouter -t dans la commande d'exécution de python.
Pour arrêter le bot, la commande /stopall dans Telegram permet de tout arrêter proprement (note: il faut changer le super_admin dans config.py).

## Les fonctionnalités
### Réponses automatiques
Dans un chat, lorsqu'une personne écrit un mot contenant "di", le bot répête la fin du mot après "di". De même avec "cri", sauf que le texte renvoyé par le bot est en majuscules. Ce comportement est récursif, avec tout de même une limite fixe de profondeur de récursivité.

Lorsqu'une phrase finit par "?", il y a une certaine probabilité que le bot réponde par une vidéo "oui" ou "non".

Une matrice de messages associés à des pseudos et des probabilités permet d'envoyer un message lorsqu'un certaine personne parle, avec une certaine probabilité.

Les fonctionnalités précédentes peuvent être désactivées par la commande /di.

...

WIP

### Recherche de vidéos

...

WIP

### Renvoi de contenu aléatoire
La commande /meme renvoie un meme aléatoire parmi une collection d'images enregistrée en local.

La commande /info renvoie une information inutile sous forme de texte. Les informations inutiles sont obtenues par une requête sur le site https://www.savoir-inutile.com/

La commande /quote renvoie une phrase générée aléatoirement depuis le site http://generateur.vuzi.fr/

### Génération de fichiers son
La commande /calc permet de convertir une opération sous frome textuelle en son en utilisant les voix de Dupont et Dupond (c'est une référence à un ytp Tintin). La fonctionnalité ne supporte que les chiffres et les opérations de base. Les caractères autorisés sont les suivants: 0123456789\+\-\*/cr. Example: /calc 1+2-8\*4/0r6c

La commande /croa N renvoie un son contenant N fois "croa". Example: /croa 12

## Données annexes nécessaires au fonctionnement

...

WIP

## Description des fichiers
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
