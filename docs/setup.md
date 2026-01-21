# 🚀 Guide de Configuration

Ce guide vous aidera à configurer et déployer GuildGreeter.

## 📋 Prérequis

### Logiciels nécessaires
- Python 3.10 ou supérieur
- PostgreSQL 13+ (ou SQLite pour le développement)
- Git
- Un éditeur de code (VSCode recommandé)

### Compte Discord Developer
- Un compte Discord
- Accès au [Discord Developer Portal](https://discord.com/developers/applications)

## 🎯 Étape 1: Créer l'application Discord

1. Allez sur https://discord.com/developers/applications
2. Cliquez sur "New Application"
3. Donnez un nom à votre bot (ex: "GuildGreeter")
4. Cliquez sur "Create"

### Configuration du Bot

1. Dans le menu de gauche, cliquez sur "Bot"
2. Cliquez sur "Add Bot" puis "Yes, do it!"
3. **Important:** Activez les "Privileged Gateway Intents":
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent
4. Copiez le token du bot (vous en aurez besoin plus tard)

### Configuration OAuth2

1. Dans le menu de gauche, cliquez sur "OAuth2"
2. Dans "Redirects", ajoutez:
   - `http://localhost:8080/callback` (développement)
   - `https://votre-domaine.com/callback` (production)
3. Notez votre Client ID et Client Secret

## 🔧 Étape 2: Installation du projet

### Cloner le repository

```bash
git clone https://github.com/KevsRaza/GuildGreeter
cd GuildGreeter
```

### Créer un environnement virtuel

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Installer les dépendances

```bash
pip install -r requirements.txt
```

## ⚙️ Étape 3: Configuration

### Créer le fichier .env

```bash
cp .env.example .env
```

### Éditer le fichier .env

Ouvrez `.env` avec votre éditeur et remplissez:

```env
# Bot Configuration
BOT_TOKEN=votre_token_ici
BOT_PREFIX=!
BOT_STATUS=online
BOT_ACTIVITY=Watching over servers

# Database (SQLite pour le dev)
DATABASE_URL=sqlite:///data/bot.db

# Web Dashboard
WEB_HOST=0.0.0.0
WEB_PORT=8080
SECRET_KEY=votre_secret_key_aleatoire_ici
OAUTH2_CLIENT_ID=votre_client_id
OAUTH2_CLIENT_SECRET=votre_client_secret
OAUTH2_REDIRECT_URI=http://localhost:8080/callback

# Features
ENABLE_ECONOMY=true
ENABLE_LEVELING=true
ENABLE_TICKETS=true
ENABLE_WEB_DASHBOARD=true

# Logging
LOG_LEVEL=INFO

# Development
DEV_MODE=true
DEV_GUILD_ID=votre_serveur_de_test_id
```

### Générer une SECRET_KEY

```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🗄️ Étape 4: Base de données

### Option 1: SQLite (Développement)

SQLite est automatique, aucune configuration nécessaire.

```env
DATABASE_URL=sqlite:///data/bot.db
```

### Option 2: PostgreSQL (Production)

**Installation PostgreSQL:**

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS (avec Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Téléchargez l'installateur depuis https://www.postgresql.org/download/windows/

**Créer la base de données:**

```bash
# Se connecter à PostgreSQL
sudo -u postgres psql

# Créer l'utilisateur et la base de données
CREATE USER botuser WITH PASSWORD 'votre_password';
CREATE DATABASE guildgreeter OWNER botuser;
GRANT ALL PRIVILEGES ON DATABASE guildgreeter TO botuser;
\q
```

**Mettre à jour .env:**
```env
DATABASE_URL=postgresql://botuser:votre_password@localhost:5432/guildgreeter
```

## 🚀 Étape 5: Lancer le bot

### Mode développement

```bash
python main.py
```

Vous devriez voir:
```
🚀 Initialisation du bot...
✅ Base de données initialisée
✅ Chargé: cogs.welcome
✅ Chargé: cogs.leveling
...
✅ VotreBot#1234 est connecté!
```

### Tester le bot

1. Invitez votre bot sur votre serveur de test:
   ```
   https://discord.com/api/oauth2/authorize?client_id=VOTRE_CLIENT_ID&permissions=8&scope=bot%20applications.commands
   ```

2. Testez quelques commandes:
   - `/ping` - Vérifier la latence
   - `/serverinfo` - Infos du serveur
   - `/help` - Liste des commandes

## 🐳 Étape 6: Déploiement avec Docker (Optionnel)

### Créer le fichier .env de production

```bash
cp .env.example .env.production
```

Éditez `.env.production` avec vos vraies valeurs de production.

### Lancer avec Docker Compose

```bash
docker-compose up -d
```

### Vérifier les logs

```bash
docker-compose logs -f bot
```

### Arrêter les conteneurs

```bash
docker-compose down
```

## 📝 Étape 7: Configuration du serveur

### 1. Configurer le système de bienvenue

```
/setwelcome #bienvenue
/welcomemsg Bienvenue {user} sur {server} ! 🎉
```

### 2. Configurer l'auto-rôle (optionnel)

```
/setautorole @Membre
```

### 3. Créer un panel de tickets

```
/ticket-panel
```

### 4. Tester les commandes

- `/rank` - Voir ton niveau
- `/balance` - Voir ton solde
- `/serverinfo` - Infos du serveur

## 🔧 Dépannage

### Le bot ne se connecte pas

- Vérifiez que votre token est correct dans `.env`
- Vérifiez que les intents sont activés dans le Developer Portal
- Vérifiez les logs pour voir les erreurs: `tail -f logs/bot_*.log`

### Les commandes slash n'apparaissent pas

- Attendez quelques minutes (Discord peut prendre jusqu'à 1h pour synchroniser)
- En mode dev, utilisez `/sync guild` pour synchroniser instantanément
- Vérifiez que le bot a la permission `applications.commands`

### Erreurs de base de données

- Vérifiez que PostgreSQL est démarré: `sudo systemctl status postgresql`
- Vérifiez votre `DATABASE_URL` dans `.env`
- Créez les tables: le bot le fait automatiquement au démarrage

### Le bot crash au démarrage

- Vérifiez que toutes les dépendances sont installées: `pip install -r requirements.txt`
- Vérifiez que Python 3.10+ est utilisé: `python --version`
- Lisez les logs d'erreur dans `logs/`

## 📚 Étapes suivantes

1. Lisez la [documentation des commandes](commands.md)
2. Personnalisez les messages de bienvenue
3. Configurez le système d'économie
4. Activez le dashboard web
5. Rejoignez notre [serveur Discord](https://discord.gg/support) pour obtenir de l'aide

## 🎓 Ressources supplémentaires

- [Documentation Discord.py](https://discordpy.readthedocs.io/)
- [Discord Developer Portal](https://discord.com/developers/docs)
- [Guide des permissions Discord](https://discordapi.com/permissions.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 💡 Conseils

- Commencez avec SQLite en développement
- Utilisez PostgreSQL en production
- Activez les logs en mode DEBUG pour plus d'informations
- Faites des sauvegardes régulières de votre base de données
- Utilisez un process manager comme PM2 ou systemd en production

---

Besoin d'aide ? Rejoignez notre [serveur Discord](https://discord.gg/support) !