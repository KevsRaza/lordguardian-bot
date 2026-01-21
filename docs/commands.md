# 📖 Guide des Commandes

Liste complète des commandes disponibles dans GuildGreeter.

## 🎉 Bienvenue

### `/setwelcome <channel>`
Configure le canal pour les messages de bienvenue et de départ.

**Permissions requises:** Administrateur  
**Exemple:** `/setwelcome #bienvenue`

### `/welcomemsg <message>`
Personnalise le message de bienvenue.

**Variables disponibles:**
- `{user}` - Mention de l'utilisateur
- `{server}` - Nom du serveur
- `{count}` - Nombre de membres

**Permissions requises:** Administrateur  
**Exemple:** `/welcomemsg Bienvenue {user} sur {server} ! 🎉 Tu es le membre #{count} !`

### `/setautorole <role>`
Définit un rôle à donner automatiquement aux nouveaux membres.

**Permissions requises:** Administrateur  
**Exemple:** `/setautorole @Membre`

---

## 📊 Leveling

### `/rank [user]`
Affiche le niveau et l'XP d'un utilisateur.

**Permissions requises:** Aucune  
**Exemple:** 
- `/rank` - Ton niveau
- `/rank @User` - Niveau d'un autre utilisateur

### `/leaderboard`
Affiche le classement des 10 meilleurs membres du serveur.

**Permissions requises:** Aucune

**Système de niveaux:**
- Gain d'XP: 15-25 par message
- Cooldown: 60 secondes entre chaque gain
- Formule de niveau: niveau = √(xp / 100)

---

## 💰 Économie

### `/balance [user]`
Affiche ton solde ou celui d'un autre utilisateur.

**Permissions requises:** Aucune  
**Exemple:** `/balance @User`

### `/daily`
Récupère ta récompense quotidienne (100-500 coins).

**Permissions requises:** Aucune  
**Cooldown:** 24 heures

### `/deposit <amount>`
Dépose de l'argent à la banque.

**Permissions requises:** Aucune  
**Exemples:**
- `/deposit 1000` - Dépose 1000 coins
- `/deposit all` - Dépose tout

### `/withdraw <amount>`
Retire de l'argent de la banque.

**Permissions requises:** Aucune  
**Exemples:**
- `/withdraw 500` - Retire 500 coins
- `/withdraw all` - Retire tout

---

## 🛡️ Modération

### `/ban <member> [reason]`
Bannit un membre du serveur.

**Permissions requises:** Bannir des membres  
**Exemple:** `/ban @User spam répété`

### `/kick <member> [reason]`
Expulse un membre du serveur.

**Permissions requises:** Expulser des membres  
**Exemple:** `/kick @User comportement inapproprié`

### `/timeout <member> <duration> [reason]`
Met un membre en timeout.

**Permissions requises:** Modérer les membres  
**Formats de durée:** `10s`, `5m`, `1h`, `1d`  
**Exemple:** `/timeout @User 10m spam`

### `/warn <member> <reason>`
Avertit un membre.

**Permissions requises:** Modérer les membres  
**Exemple:** `/warn @User langage inapproprié`

### `/clear <amount>`
Supprime des messages dans le canal (max 100).

**Permissions requises:** Gérer les messages  
**Exemple:** `/clear 50`

---

## 🎫 Tickets

### `/ticket-panel`
Crée un panel interactif pour créer des tickets.

**Permissions requises:** Administrateur  
**Usage:** Utilisez cette commande dans le canal où vous voulez afficher le panel

### `/ticket-close`
Ferme le ticket actuel.

**Permissions requises:** Gérer les messages (ou être le créateur du ticket)  
**Usage:** À utiliser dans un canal de ticket

### `/tickets`
Liste tous les tickets du serveur.

**Permissions requises:** Gérer les messages  
**Affiche:** Tickets ouverts et fermés avec statistiques

---

## 🔧 Utilitaires

### `/ping`
Affiche la latence du bot.

**Permissions requises:** Aucune

### `/serverinfo`
Affiche les informations détaillées du serveur.

**Permissions requises:** Aucune  
**Informations affichées:**
- Propriétaire
- Date de création
- Nombre de membres
- Canaux
- Rôles
- Boosts

### `/userinfo [user]`
Affiche les informations d'un utilisateur.

**Permissions requises:** Aucune  
**Exemple:** `/userinfo @User`

### `/botinfo`
Affiche les informations du bot.

**Permissions requises:** Aucune  
**Informations affichées:**
- Statistiques (serveurs, utilisateurs)
- Utilisation système (CPU, RAM)
- Uptime

### `/avatar [user]`
Affiche l'avatar d'un utilisateur en haute résolution.

**Permissions requises:** Aucune  
**Exemple:** `/avatar @User`

---

## 🎮 Fun

### `/8ball <question>`
Pose une question à la boule magique.

**Permissions requises:** Aucune  
**Exemple:** `/8ball Vais-je gagner au loto ?`

### `/coinflip`
Lance une pièce (Pile ou Face).

**Permissions requises:** Aucune

### `/roll [dice]`
Lance un ou plusieurs dés.

**Permissions requises:** Aucune  
**Format:** XdY (X dés à Y faces)  
**Exemples:**
- `/roll` - Lance 1d6 (par défaut)
- `/roll 2d6` - Lance 2 dés à 6 faces
- `/roll 3d20` - Lance 3 dés à 20 faces

### `/choose <options>`
Choisit aléatoirement parmi plusieurs options.

**Permissions requises:** Aucune  
**Exemple:** `/choose pizza, burger, sushi`

### `/lovecalc <person1> <person2>`
Calcule le pourcentage d'amour entre deux personnes.

**Permissions requises:** Aucune  
**Exemple:** `/lovecalc Alice Bob`

### `/dog`
Affiche une image de chien aléatoire.

**Permissions requises:** Aucune

### `/cat`
Affiche une image de chat aléatoire.

**Permissions requises:** Aucune

---

## 👑 Administration (Owner Only)

### `/reload <cog>`
Recharge un cog du bot.

**Permissions requises:** Propriétaire du bot  
**Exemple:** `/reload welcome`

### `/load <cog>`
Charge un cog.

**Permissions requises:** Propriétaire du bot  
**Exemple:** `/load economy`

### `/unload <cog>`
Décharge un cog.

**Permissions requises:** Propriétaire du bot  
**Exemple:** `/unload fun`

### `/sync [scope] [guild_id]`
Synchronise les commandes slash avec Discord.

**Permissions requises:** Propriétaire du bot  
**Scopes:**
- `global` - Synchronisation globale (peut prendre 1h)
- `guild` - Synchronisation pour un serveur (instantané)
- `clear` - Supprime les commandes d'un serveur

**Exemples:**
- `/sync global` - Sync global
- `/sync guild` - Sync serveur actuel
- `/sync guild 123456789` - Sync serveur spécifique

### `/guilds`
Liste tous les serveurs où le bot est présent.

**Permissions requises:** Propriétaire du bot

### `/leave <guild_id>`
Fait quitter le bot d'un serveur.

**Permissions requises:** Propriétaire du bot  
**Exemple:** `/leave 123456789`

---

## 📊 Permissions Discord

### Hiérarchie des permissions

1. **Administrateur** - Accès complet
2. **Bannir des membres** - Peut bannir
3. **Expulser des membres** - Peut kick
4. **Modérer les membres** - Peut timeout/warn
5. **Gérer les messages** - Peut clear et gérer tickets
6. **Gérer les rôles** - Peut donner des rôles
7. **Gérer le serveur** - Configuration générale

### Permissions recommandées pour le bot

```
PERMISSIONS = 8 (Administrateur)
```

Ou permissions spécifiques:
- Gérer les canaux
- Gérer les rôles
- Bannir des membres
- Expulser des membres
- Gérer les messages
- Lire les messages
- Envoyer des messages
- Envoyer des messages dans les fils
- Gérer les fils
- Intégrer des liens
- Joindre des fichiers
- Lire l'historique des messages
- Ajouter des réactions
- Utiliser des commandes slash

---

## 💡 Conseils d'utilisation

### Pour les administrateurs

1. **Configurez d'abord les bases:**
   - Canal de bienvenue (`/setwelcome`)
   - Message de bienvenue (`/welcomemsg`)
   - Panel de tickets (`/ticket-panel`)

2. **Définissez les rôles:**
   - Auto-rôle pour les nouveaux (`/setautorole`)
   - Rôles de modération avec les bonnes permissions

3. **Activez les fonctionnalités:**
   - Vérifiez `.env` pour activer économie, leveling, etc.

### Pour les modérateurs

1. **Utilisez les commandes progressivement:**
   - Warn → Timeout → Kick → Ban
   
2. **Toujours donner une raison:**
   - Aide à la traçabilité
   - Informe l'utilisateur

3. **Gérez les tickets rapidement:**
   - Répondez dans les 24h
   - Fermez les tickets résolus

### Pour les utilisateurs

1. **Soyez actifs pour gagner de l'XP:**
   - Envoyez des messages (cooldown 60s)
   - Participez aux discussions

2. **Utilisez l'économie:**
   - Réclamez votre `/daily`
   - Déposez à la banque pour sécuriser

3. **Créez des tickets pour l'aide:**
   - Soyez clair et précis
   - Un ticket à la fois

---

## 🔗 Liens utiles

- [Documentation complète](https://github.com/KevsRaza/GuildGreeter/wiki)
- [Serveur de support](https://discord.gg/support)
- [Signaler un bug](https://github.com/KevsRaza/GuildGreeter/issues)

---

**Version:** 1.0.0  
**Dernière mise à jour:** Janvier 2026