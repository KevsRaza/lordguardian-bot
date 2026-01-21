# 🤖 GuildGreeter Bot

Un bot Discord multifonction professionnel avec système de bienvenue, leveling, économie, boutique, casino et modération.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Discord.py](https://img.shields.io/badge/discord.py-2.3.2-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

## ✨ Fonctionnalités

### 👋 Système de Bienvenue
- Messages de bienvenue personnalisables avec embeds
- Messages de départ automatiques
- Attribution automatique de rôles aux nouveaux membres
- Variables dynamiques (`{user}`, `{server}`, `{count}`)
- Avatar du membre affiché dans les messages
- **Commandes:** `/setwelcome`, `/welcomemsg`, `/setleavemsg`

### 📈 Système de Leveling
- Gain d'XP basé sur l'activité (messages)
- Système de niveaux progressif avec formule exponentielle
- Classement du serveur avec médailles pour le top 3
- Barre de progression visuelle dans `/rank`
- Cooldown anti-spam (60 secondes)
- **Commandes:** `/rank`, `/leaderboard`

### 💰 Système d'Économie
- Monnaie virtuelle du serveur (coins)
- Système de portefeuille et banque séparés
- Récompenses quotidiennes (`/daily`) avec bonus aléatoires
- Transferts d'argent entre joueurs avec notifications
- Classement des plus riches (`/richest`)
- Format de montants avec espaces pour lisibilité
- **Commandes:** `/balance`, `/daily`, `/deposit`, `/withdraw`, `/transfer`, `/richest`

### 🛒 Boutique Interactive
- Catalogue d'items par catégories (Apparence, Divertissement, Utilitaire, Surprise)
- **Rôles colorés:** Rouge (300), Bleu (300), VIP (1000)
- **Effets visuels animés:**
  - 🌈 Vague Arc-en-ciel (75 coins)
  - ☄️ Pluie de Météores (150 coins)
  - 🌌 Aurore Boréale (200 coins)
- **Boosts:** XP Boost 24h (400), Daily Boost (500)
- **Boîte Mystère:** 100-500 coins ou item rare (200)
- Interface avec boutons interactifs
- **Commandes:** `/shop`, `/buy`, `/iteminfo`, `/items`
- **Admin:** `/additem`, `/removeitem`, `/shopconfig`

### 🎰 Système de Casino
- **Blackjack:** Jeu classique avec croupier
- **Coinflip:** Pile ou face avec mises
- **Dice:** Lancer de dés avec multiplicateurs
- Statistiques de jeu personnelles
- Système de gains/pertes équilibré
- **Commandes:** `/casino`, `/blackjack`, `/coinflip`, `/dice`, `/mystats`, `/cancelgame`

### 🎫 Système de Tickets
- Création de tickets de support via panel interactif
- Salons privés automatiques (`ticket-{username}`)
- Boutons de gestion (Fermer, Ajouter utilisateur)
- Permissions automatiques (créateur + staff uniquement)
- Limite: 1 ticket par utilisateur à la fois
- **Commandes:** `/ticket-panel`, `/tickets`, `/ticket-close`

### 🛡️ Modération Complète
- **Sanctions:** Ban, Kick, Mute (temporaire), Warn
- Système de mute avec rôle automatique et démute programmé
- Nettoyage de messages (bulk delete) avec filtrage par utilisateur
- Unban via ID utilisateur
- Raisons enregistrées pour chaque action
- **Commandes:** `!ban`, `!kick`, `!mute`, `!unmute`, `!warn`, `!clear`, `!unban`

### 🎮 Commandes Fun
- **Images aléatoires:** Chat (`/cat`), Chien (`/dog`)
- **Jeux:** 8ball (`/8ball`), Pile ou Face (`/flip`)
- **Utilitaires fun:** Love Calculator (`/lovecalc`), Choix aléatoire (`/chooserandom`)
- **Divertissement:** Blagues (`/joke`), Faits aléatoires (`/fact`)
- **Sondages:** Création de polls avec réactions (`/poll`)

### 🔧 Utilitaires
- Informations serveur détaillées (`/serverinfo`)
- Profil utilisateur complet avec badges Discord (`/userinfo`)
- Avatar en haute résolution (`/avatar`)
- Latence bot et API (`/ping`)
- **Commandes prefix ET slash disponibles**

### ⚙️ Administration
- Rechargement de cogs à chaud (`/reload`)
- Chargement/déchargement de modules (`/load`, `/unload`)
- Synchronisation des slash commands (`/sync`)
- Liste des serveurs où le bot est présent (`/guilds`)
- Quitter un serveur spécifique (`/leave`)

## 📊 Statistiques

- **16 commandes prefix** (compatibilité legacy)
- **46 slash commands** (interface moderne)
- **11 catégories** de fonctionnalités
- **3 bases de données** (économie, leveling, tickets)

## 🚀 Installation

### Prérequis
- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)
- Un compte Discord avec application bot

### Installation rapide

1. **Cloner le repository**
```bash
git clone https://github.com/KevsRaza/GuildGreeter.git
cd GuildGreeter
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configuration**

Créez un fichier `.env` à la racine du projet :

```env
# Token du bot Discord
BOT_TOKEN=votre_token_ici

# Préfixe des commandes (optionnel, défaut: !)
BOT_PREFIX=!

# Base de données SQLite (créée automatiquement)
DATABASE_PATH=data/guildgreeter.db
```

5. **Lancer le bot**
```bash
python main.py
```

Le bot devrait maintenant être en ligne ! ✅

## 🔧 Configuration Discord

### 1. Créer l'application Discord

1. Allez sur [Discord Developer Portal](https://discord.com/developers/applications)
2. Cliquez sur "New Application"
3. Donnez un nom à votre bot (ex: GuildGreeter)

### 2. Créer le bot

1. Dans l'onglet "Bot", cliquez sur "Add Bot"
2. Copiez le token (⚠️ Ne le partagez JAMAIS)
3. Collez-le dans votre fichier `.env`

### 3. Activer les Privileged Gateway Intents

Dans l'onglet "Bot", activez :
- ✅ **Presence Intent**
- ✅ **Server Members Intent**
- ✅ **Message Content Intent**

### 4. Inviter le bot

Utilisez ce lien (remplacez `1451124617216393227` par votre Application ID) :

```
https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&permissions=277025770560&scope=bot%20applications.commands
```

**Permissions recommandées :**
- Administrator (8) pour un fonctionnement optimal
- Ou permissions spécifiques : Manage Roles, Manage Channels, Ban Members, Kick Members, Manage Messages, etc.

## 📖 Guide d'Utilisation

### Commandes de Base

```bash
# Aide générale
!help

# Informations sur le bot
/ping

# Informations serveur
/serverinfo

# Voir ton niveau
/rank

# Voir ton argent
/balance
```

### Configuration du Serveur

```bash
# 1. Configurer le canal de bienvenue
/setwelcome #bienvenue

# 2. Personnaliser le message de bienvenue
/welcomemsg Bienvenue {user} sur {server} ! Nous sommes {count} membres 🎉

# 3. Configurer le message de départ
/setleavemsg Au revoir {user}... 😢

# 4. Créer le panel de tickets
/ticket-panel
```

### Économie et Boutique

```bash
# Réclamer ta récompense quotidienne
/daily

# Voir la boutique
/shop

# Acheter un item
/buy role_rouge

# Transférer de l'argent
/transfer @User 100

# Voir le classement
/richest
```

### Casino

```bash
# Voir les jeux disponibles
/casino

# Jouer au blackjack
/blackjack 100

# Lancer une pièce
/coinflip 50 heads

# Lancer les dés
/dice 100
```

## 🗂️ Structure du Projet

```
guildgreeter/
├── main.py                 # Point d'entrée du bot
├── requirements.txt        # Dépendances Python
├── .env                    # Configuration (TOKEN, etc.)
├── README.md              # Ce fichier
├── test_manual.md         # Guide de test complet
│
├── core/                  # Modules de base
│   ├── __init__.py
│   ├── bot.py            # Classe principale du bot
│   ├── config.py         # Gestion de la configuration
│   ├── database.py       # Connexion base de données
│   ├── logger.py         # Système de logs
│   └── embeds.py         # Générateur d'embeds standardisés
│
├── cogs/                  # Modules de commandes
│   ├── __init__.py
│   ├── admin.py          # Commandes d'administration
│   ├── economy.py        # Système d'économie
│   ├── shop.py           # Boutique interactive
│   ├── casino.py         # Jeux de casino
│   ├── leveling.py       # Système de niveaux
│   ├── moderation.py     # Modération
│   ├── tickets.py        # Système de tickets
│   ├── welcome.py        # Messages de bienvenue
│   ├── fun.py            # Commandes fun
│   ├── utilities.py      # Commandes utilitaires
│   └── help_cog.py       # Système d'aide
│
├── data/                  # Données du bot
│   ├── guildgreeter.db   # Base de données SQLite
│   └── logs/             # Fichiers de logs
│       ├── bot.log
│       ├── economy.log
│       └── ...
│
└── utils/                 # Fonctions utilitaires
    ├── __init__.py
    ├── checks.py         # Vérifications de permissions
    └── helpers.py        # Fonctions d'aide
```

## 🎨 Personnalisation

### Modifier les couleurs des embeds

Éditez `core/embeds.py` :

```python
class EmbedColors:
    SUCCESS = 0x00FF00  # Vert
    ERROR = 0xFF0000    # Rouge
    WARNING = 0xFFA500  # Orange
    INFO = 0x3498DB     # Bleu
    WELCOME = 0x9B59B6  # Violet - Changez cette valeur
    GOODBYE = 0x95A5A6  # Gris
```

### Ajouter des items à la boutique

Utilisez la commande admin :

```bash
/additem <item_id> <name> <price> <description> <category> <type>

# Exemple :
/additem role_vert "🟢 Rôle Vert" 300 "Rôle vert permanent" appearance role
```

### Modifier les récompenses quotidiennes

Éditez `cogs/economy.py`, ligne ~150 :

```python
# Changer les valeurs min/max
base_reward = random.randint(100, 500)  # Modifiez ces valeurs
```

## 🧪 Tests

### Test Manuel Complet

Suivez le guide détaillé dans `test_manual.md` qui couvre :
- ✅ 62 commandes à tester
- ✅ Cas d'erreur
- ✅ Tests de performance
- ✅ Tableau de bugs

### Lancer les Tests Rapides

```bash
# Test de connexion
!ping

# Test des slash commands
/sync

# Test économie
/daily
/balance
/richest

# Test boutique
/shop
```

## 🐛 Dépannage

### Le bot ne se connecte pas

1. Vérifiez que le token dans `.env` est correct
2. Vérifiez que les intents sont activés sur le Developer Portal
3. Regardez les logs dans `logs/bot.log`

### Les slash commands n'apparaissent pas

1. Utilisez `/sync` (admin uniquement)
2. Attendez quelques minutes (jusqu'à 1h)
3. Réinvitez le bot avec les bonnes permissions

### Erreur de base de données

```bash
# Supprimer la base de données (⚠️ perte de données)
rm data/bot.db

# Relancer le bot (recrée automatiquement)
python main.py
```

### Les commandes prefix ne fonctionnent pas

Vérifiez que le Message Content Intent est activé dans le Developer Portal.

## 📝 Changelog

### Version 1.0.0 (2026-01-21)
- ✨ Système d'économie complet avec transferts
- 🛒 Boutique interactive avec effets animés
- 🎰 Casino avec blackjack, coinflip, dice
- 📈 Système de leveling amélioré
- 🎫 Système de tickets
- 🛡️ Modération complète
- 🎨 Système d'embeds standardisé
- 📊 46 slash commands + 16 prefix commands

## 🔮 Roadmap

### Prochaines fonctionnalités
- [ ] Dashboard web pour configuration
- [ ] Système de rôles de récompense pour leveling
- [ ] Logs de modération détaillés
- [ ] Auto-modération (anti-spam, anti-raid)
- [ ] Système de suggestions
- [ ] Giveaways automatiques
- [ ] Intégration Twitch/YouTube
- [ ] Système de musique

### Améliorations prévues
- [ ] Stockage persistant des boosts
- [ ] Statistiques globales du serveur
- [ ] Système de succès/achievements
- [ ] API REST pour stats externes
- [ ] Support multi-langues

## 📜 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

**En résumé :** Vous pouvez utiliser, modifier et distribuer ce code librement, mais sans garantie.

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. **Fork** le projet
2. Créez une branche (`git checkout -b feature/NouvelleFonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout de NouvelleFonctionnalite'`)
4. Pushez vers la branche (`git push origin feature/NouvelleFonctionnalite`)
5. Ouvrez une **Pull Request**

### Guidelines de Contribution

- Suivez le style de code existant
- Ajoutez des tests pour les nouvelles fonctionnalités
- Mettez à jour la documentation si nécessaire
- Utilisez le système d'embeds standardisé (`core/embeds.py`)
- Ajoutez des logs appropriés pour le debugging

## 📧 Support

- 📖 **Documentation complète :** [Wiki](hhttps://github.com/KevsRaza/GuildGreeter/wiki)
- 🐛 **Signaler un bug :** [Issues](https://github.com/KevsRaza/GuildGreeter/issues)
- 💬 **Serveur Discord :** [Rejoindre](https://discord.gg/1441412296927740035)
- 📧 **Email :** krazafindralanto@gmail.com

## 🙏 Remerciements

Ce projet utilise les librairies suivantes :

- [Discord.py](https://github.com/Rapptz/discord.py) - Wrapper Python pour l'API Discord
- [aiosqlite](https://github.com/omnilib/aiosqlite) - Base de données SQLite asynchrone
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Gestion des variables d'environnement

Merci à la communauté Discord.py pour leur aide et documentation !

## 👨‍💻 Auteur

Créé avec ❤️ par KevsRAZA

- GitHub: [@KevsRaza](https://github.com/KevsRaza/GuildGreeter)
- Discord: lordteka

---

⭐ **Si ce projet vous plaît, n'hésitez pas à lui donner une étoile !** ⭐

*Dernière mise à jour : 21 janvier 2026*