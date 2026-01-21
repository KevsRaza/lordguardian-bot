# 📋 Guide de Test Manuel - GuildGreeter Bot

> **Version:** 1.0.0  
> **Dernière mise à jour:** 2026-01-21  
> **Testeur:** [JohnnyStann]  
> **Date du test:** [2026-01-21]

---

## 🎯 Préparation du Test

### Environnement Requis
- [ ] Python 3.10+ installé
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Fichier `.env` configuré avec le token
- [ ] Base de données créée (`data/guildgreeter.db`)
- [ ] Serveur Discord de test créé

### Comptes de Test Nécessaires
- [ ] Compte principal (admin)
- [ ] Compte secondaire (utilisateur normal)
- [ ] Compte tertiaire (pour tests de modération)

---

## ⚙️ Configuration Initiale

### Démarrage du Bot
- [ ] **Commande:** `python main.py`
- [ ] **Résultat attendu:** Logs de connexion affichés
- [ ] **Vérification:** Bot apparaît en ligne sur Discord
- [ ] **Statut:** Affiche activité personnalisée

### Test de Connexion
| Commande | Type | Résultat Attendu | ✅/❌ | Notes |
|----------|------|------------------|-------|-------|
| `!ping` | Prefix | Pong! Latence: Xms | | |
| `/ping` | Slash | Embed avec latence bot et API | | |

### Synchronisation des Commandes
- [ ] `/sync` (admin uniquement)
- [ ] **Résultat:** Message de confirmation
- [ ] **Vérification:** 46 slash commands apparaissent dans Discord

---

## 📚 Système d'Aide (Help)

### Commandes d'Aide
| Commande | Type | Résultat Attendu | ✅/❌ | Notes |
|----------|------|------------------|-------|-------|
| `!help` | Prefix | Menu complet avec toutes catégories | | |
| `!help ban` | Prefix | Détails sur la commande ban | | |
| `!debug` | Prefix | Informations de debug | | |
| `!testcommands` | Prefix | Test des commandes | | |

### Vérifications Menu Help
- [ ] **Titre:** "Menu d'aide - GuildGreeter"
- [ ] **Préfixe affiché:** `!`
- [ ] **Slash commands mentionnés:** `/`
- [ ] **Total correct:** 16 commandes préfixe • 46 slash commands
- [ ] **Catégories affichées:**
  - [ ] Moderation (6 commandes)
  - [ ] Utilities (6 commandes)
  - [ ] Help (3 commandes)
  - [ ] Admin (6 slash)
  - [ ] Casino (6 slash)
  - [ ] Economy (6 slash)
  - [ ] Fun (8 slash)
  - [ ] Leveling (2 slash)
  - [ ] Shop (7 slash)
  - [ ] Tickets (3 slash)
  - [ ] Utilities (4 slash)
  - [ ] Welcome (3 slash)

---

## 👋 Système de Bienvenue (Welcome)

### Configuration
| Commande | Paramètres | Résultat Attendu | ✅/❌ | Notes |
|----------|-----------|------------------|-------|-------|
| `/setwelcome` | #salon-bienvenue | Embed de succès | | |
| `/welcomemsg` | "Bienvenue {user} sur {server}!" | Message personnalisé enregistré | | |
| `/setleavemsg` | "Au revoir {user}..." | Message de départ enregistré | | |

### Test Réel
- [ ] **Action:** Compte test rejoint le serveur
- [ ] **Vérifications:**
  - [ ] Message de bienvenue affiché
  - [ ] Variables `{user}`, `{server}`, `{count}` remplacées
  - [ ] Avatar du membre affiché
  - [ ] Embed avec couleur WELCOME (violet)

- [ ] **Action:** Compte test quitte le serveur
- [ ] **Vérification:** Message de départ affiché

---

## 💰 Système d'Économie (Economy)

### Commandes de Base
| Commande | Paramètres | Résultat Attendu | ✅/❌ | Notes |
|----------|-----------|------------------|-------|-------|
| `/balance` | - | Portefeuille, banque, total | | |
| `/balance` | @Utilisateur | Balance de l'utilisateur ciblé | | |
| `/daily` | - | 100-500 coins + possible bonus | | |
| `/daily` | (déjà réclamé) | Message d'attente avec temps restant | | |

### Transactions Bancaires
| Commande | Paramètres | Résultat Attendu | ✅/❌ | Notes |
|----------|-----------|------------------|-------|-------|
| `/deposit` | 1000 | 1000 coins déposés à la banque | | |
| `/deposit` | all | Tout le portefeuille déposé | | |
| `/withdraw` | 500 | 500 coins retirés de la banque | | |
| `/withdraw` | all | Toute la banque retirée | | |

### Transferts et Classement
- [ ] `/transfer @Utilisateur 100`
  - [ ] Coins débités de l'expéditeur
  - [ ] Coins ajoutés au destinataire
  - [ ] Notification DM envoyée (si DM activés)

- [ ] `/richest` (page 1)
  - [ ] Top 10 affiché
  - [ ] Médailles 🥇🥈🥉 pour top 3
  - [ ] Ta position en footer

### Tests d'Erreur
- [ ] `/transfer @Soi-même 100` → Erreur
- [ ] `/transfer @Bot 100` → Erreur
- [ ] `/deposit 999999` (fonds insuffisants) → Erreur
- [ ] `/withdraw 999999` (fonds insuffisants) → Erreur

---

## 🛒 Système de Boutique (Shop)

### Consultation
| Commande | Résultat Attendu | ✅/❌ | Notes |
|----------|------------------|-------|-------|
| `/shop` | Catalogue par catégories + ton solde | | |
| `/items` | Liste complète avec IDs | | |
| `/iteminfo role_rouge` | Détails + boutons Acheter/Fermer | | |

### Achats - Rôles
- [ ] `/buy role_rouge` (fonds suffisants)
  - [ ] Coins débités
  - [ ] Rôle créé et attribué
  - [ ] Message public de confirmation
  
- [ ] `/buy role_bleu`
  - [ ] Rôle bleu créé avec bonne couleur

- [ ] `/buy role_vip` 
  - [ ] Rôle VIP doré créé

### Achats - Effets Visuels
- [ ] `/buy rainbow_wave` (75 coins)
  - [ ] Animation de vague colorée affichée
  - [ ] Plusieurs frames animées
  - [ ] Auto-suppression après effet

- [ ] `/buy meteor_shower` (150 coins)
  - [ ] Animation de météores
  - [ ] Explosions affichées

- [ ] `/buy aurora_borealis` (200 coins)
  - [ ] Animation d'aurore boréale
  - [ ] Couleurs ondulantes

### Achats - Boosts et Lootbox
- [ ] `/buy xp_boost` (400 coins)
  - [ ] Message de confirmation
  - [ ] Boost actif 24h

- [ ] `/buy daily_boost` (500 coins)
  - [ ] Message "prochaine récompense doublée"

- [ ] `/buy boite_mystere` (200 coins)
  - [ ] Animation d'ouverture
  - [ ] Récompense révélée (100-500 coins OU item rare)
  - [ ] Récompense ajoutée au compte

### Tests d'Erreur
- [ ] `/buy inexistant` → Erreur "item inexistant"
- [ ] `/buy role_vip` (sans fonds) → Erreur avec montant manquant

### Commandes Admin
| Commande | Résultat Attendu | ✅/❌ | Notes |
|----------|------------------|-------|-------|
| `/additem` | Item personnalisé ajouté | | |
| `/removeitem role_rouge` | Item retiré de la boutique | | |
| `/shopconfig` | Configuration actuelle affichée | | |

---

## 📈 Système de Niveaux (Leveling)

### Progression XP
- [ ] **Action:** Envoyer 10-15 messages
- [ ] **Vérification:** XP gagné (avec cooldown de 5s)

### Commandes
| Commande | Paramètres | Résultat Attendu | ✅/❌ | Notes |
|----------|-----------|------------------|-------|-------|
| `/rank` | - | Niveau, XP, barre de progression | | |
| `/rank` | @Utilisateur | Rang de l'utilisateur ciblé | | |
| `/leaderboard` | - | Top 10 par XP/niveau | | |

### Level Up
- [ ] **Action:** Atteindre le niveau suivant
- [ ] **Vérifications:**
  - [ ] Message de level up
  - [ ] Nouveau niveau affiché
  - [ ] Rôle de récompense (si configuré)

---

## 🎰 Système de Casino

### Jeux Disponibles
| Commande | Résultat Attendu | ✅/❌ | Notes |
|----------|------------------|-------|-------|
| `/casino` | Liste des jeux + règles | | |
| `/coinflip` | Pile ou face avec mise | | |
| `/dice` | Lancer de dés | | |
| `/blackjack` | Partie de blackjack interactive | | |
| `/mystats` | Statistiques de jeu (W/L ratio) | | |
| `/cancelgame` | Annule la partie en cours | | |

### Test Coinflip
- [ ] `/coinflip 100 heads`
  - [ ] Coins débités
  - [ ] Résultat affiché (gagné/perdu)
  - [ ] Gains ajoutés si victoire

### Test Blackjack
- [ ] `/blackjack 50`
  - [ ] Cartes distribuées
  - [ ] Boutons Hit/Stand fonctionnels
  - [ ] Calcul correct des scores
  - [ ] Gains distribués correctement

### Test Dice
- [ ] `/dice 100`
  - [ ] Lancer de dés
  - [ ] Gains selon résultat

---

## 🛡️ Système de Modération

### Commandes de Base
| Commande | Type | Paramètres | Résultat Attendu | ✅/❌ | Notes |
|----------|------|-----------|------------------|-------|-------|
| `!clear` | Prefix | 5 | 5 derniers messages supprimés | | |
| `!clear` | Prefix | 5 @User | 5 messages de l'user supprimés | | |
| `!kick` | Prefix | @User raison | Utilisateur expulsé + log | | |
| `!ban` | Prefix | @User raison | Utilisateur banni + log | | |
| `!unban` | Prefix | ID_user | Utilisateur débanni | | |
| `!mute` | Prefix | @User 10m raison | Rôle Muted attribué + timer | | |
| `!unmute` | Prefix | @User | Rôle Muted retiré | | |
| `!warn` | Prefix | @User raison | Avertissement enregistré | | |

### Tests de Permissions
- [ ] `!ban` sans permissions → Erreur
- [ ] `!kick` sur un admin → Erreur "impossible de modérer"
- [ ] `!clear` sans permissions → Erreur

### Vérifications Détaillées Mute
- [ ] Rôle "Muted" créé automatiquement
- [ ] Permissions de parler retirées
- [ ] Démute automatique après le temps
- [ ] Log de modération enregistré

---

## 🎫 Système de Tickets

### Commandes
| Commande | Résultat Attendu | ✅/❌ | Notes |
|----------|------------------|-------|-------|
| `/ticket-panel` | Panel de création de tickets affiché | | |
| `/tickets` | Liste de tes tickets ouverts | | |
| `/ticket-close` | Ferme le ticket actuel | | |

### Workflow Complet
- [ ] **Étape 1:** Cliquer sur le bouton du panel
  - [ ] Salon privé créé `ticket-{username}`
  - [ ] Permissions correctes (créateur + staff)
  - [ ] Message d'accueil

- [ ] **Étape 2:** Bouton "Fermer"
  - [ ] Demande de confirmation

- [ ] **Étape 3:** Confirmer fermeture
  - [ ] Transcript créé (si implémenté)
  - [ ] Salon supprimé/archivé

### Tests Limites
- [ ] Créer 2 tickets simultanément → Erreur "ticket déjà ouvert"

---

## 🎮 Commandes Fun

### Commandes Prefix
| Commande | Type | Résultat Attendu | ✅/❌ | Notes |
|----------|------|------------------|-------|-------|
| `!8ball` | Prefix | Question? → Réponse aléatoire | | |

### Commandes Slash
| Commande | Type | Résultat Attendu | ✅/❌ | Notes |
|----------|------|------------------|-------|-------|
| `/8ball` | Slash | Question? → Réponse + embed | | |
| `/cat` | Slash | Image aléatoire de chat | | |
| `/dog` | Slash | Image aléatoire de chien | | |
| `/fact` | Slash | Fait aléatoire intéressant | | |
| `/flip` | Slash | Pile ou face (sans mise) | | |
| `/joke` | Slash | Blague aléatoire | | |
| `/lovecalc` | Slash | @User1 @User2 → Pourcentage d'amour | | |
| `/poll` | Slash | Question → Sondage avec réactions | | |
| `/chooserandom` | Slash | option1 option2 → Choix aléatoire | | |

### Vérifications Poll
- [ ] Embed avec question
- [ ] Options numérotées
- [ ] Réactions automatiques (1️⃣, 2️⃣, etc.)

---

## 🔧 Commandes Utilitaires

### Commandes Prefix
| Commande | Type | Résultat Attendu | ✅/❌ | Notes |
|----------|------|------------------|-------|-------|
| `!ping` | Prefix | Latence affichée | | |
| `!avatar` | Prefix | @User → Avatar affiché | | |
| `!serverinfo` | Prefix | Infos complètes du serveur | | |
| `!userinfo` | Prefix | @User → Infos de l'utilisateur | | |
| `!poll` | Prefix | Question → Sondage | | |

### Commandes Slash
| Commande | Type | Résultat Attendu | ✅/❌ | Notes |
|----------|------|------------------|-------|-------|
| `/ping` | Slash | Latence bot + API en embed | | |
| `/avatar` | Slash | @User → Avatar HD | | |
| `/serverinfo` | Slash | Infos serveur détaillées | | |
| `/userinfo` | Slash | @User → Profil complet | | |

### Vérifications ServerInfo
- [ ] Nom et icône du serveur
- [ ] Propriétaire mentionné
- [ ] Nombre de membres
- [ ] Nombre de salons (texte/vocal)
- [ ] Date de création
- [ ] Niveau de boost
- [ ] Embed couleur INFO

### Vérifications UserInfo
- [ ] Avatar HD
- [ ] Nom et tag
- [ ] Date de création du compte
- [ ] Date d'arrivée sur le serveur
- [ ] Liste des rôles
- [ ] Badges Discord
- [ ] Statut de boost (si applicable)

---

## ⚙️ Commandes d'Administration (Admin)

### Gestion des Cogs
| Commande | Paramètres | Résultat Attendu | ✅/❌ | Notes |
|----------|-----------|------------------|-------|-------|
| `/sync` | - | 46 slash commands synchronisées | | |
| `/reload` | economy | Cog rechargé avec succès | | |
| `/load` | nouveau_cog | Cog chargé | | |
| `/unload` | cog_name | Cog déchargé | | |

### Gestion des Serveurs
| Commande | Résultat Attendu | ✅/❌ | Notes |
|----------|------------------|-------|-------|
| `/guilds` | Liste serveurs + nombre de membres | | |
| `/leave` | Bot quitte le serveur spécifié | | |

### Tests d'Erreur
- [ ] `/reload inexistant` → Erreur "cog non trouvé"
- [ ] `/sync` par utilisateur non-admin → Erreur permissions

---

## 🔍 Tests de Gestion d'Erreurs

### Erreurs Communes
| Scénario | Résultat Attendu | ✅/❌ |
|----------|------------------|-------|
| Commande inexistante `!fakecommand` | Aucune réponse ou message d'erreur | |
| Paramètre manquant `/transfer @User` | Message d'aide ou erreur claire | |
| Permissions insuffisantes | Embed d'erreur rouge | |
| Bot sans permissions | Message sur permission manquante | |
| Utilisateur introuvable | Erreur "utilisateur non trouvé" | |
| Montant négatif | Erreur "montant invalide" | |

### Tests de Robustesse
- [ ] Spam de commandes (10 commandes en 2s)
- [ ] Commande pendant latence élevée
- [ ] Base de données déconnectée → Message propre

---

## 📊 Résumé des Commandes

### Statistiques Attendues
- **Commandes Prefix:** 16
  - Moderation: 6
  - Utilities: 6
  - Help: 3
  - 8ball: 1

- **Slash Commands:** 46
  - Admin: 6
  - Casino: 6
  - Economy: 6
  - Fun: 8
  - Leveling: 2
  - Shop: 7
  - Tickets: 3
  - Utilities: 4
  - Welcome: 3

### Vérification Totale
- [ ] `!help` affiche bien "16 commandes préfixe"
- [ ] `!help` affiche bien "46 slash commands"
- [ ] Toutes les catégories listées ci-dessus sont présentes
- [ ] Aucune commande manquante

---

## 🐛 Bugs Découverts

| # | Commande | Description | Sévérité | Reproduction | Statut |
|---|----------|-------------|----------|--------------|--------|
| 1 | | | 🔴/🟡/🟢 | | ⏳/✅/❌ |
| 2 | | | | | |
| 3 | | | | | |

**Légende Sévérité:**
- 🔴 Critique (crash, perte de données)
- 🟡 Majeur (fonctionnalité cassée)
- 🟢 Mineur (cosmétique, typo)

---

## ✅ Résumé du Test

### Statistiques Globales
- **Tests réussis:** _____ / _____
- **Tests échoués:** _____
- **Bugs critiques:** _____
- **Bugs majeurs:** _____
- **Bugs mineurs:** _____

### Fonctionnalités Validées
- [ ] Système d'aide : ✅ / ⚠️ / ❌
- [ ] Bienvenue : ✅ / ⚠️ / ❌
- [ ] Économie : ✅ / ⚠️ / ❌
- [ ] Boutique : ✅ / ⚠️ / ❌
- [ ] Niveaux : ✅ / ⚠️ / ❌
- [ ] Casino : ✅ / ⚠️ / ❌
- [ ] Modération : ✅ / ⚠️ / ❌
- [ ] Tickets : ✅ / ⚠️ / ❌
- [ ] Fun : ✅ / ⚠️ / ❌
- [ ] Utilitaires : ✅ / ⚠️ / ❌
- [ ] Admin : ✅ / ⚠️ / ❌

### Recommandations
1. 
2. 
3. 

### Prochaines Étapes
- [ ] Corriger bugs critiques
- [ ] Corriger bugs majeurs
- [ ] Améliorer UX sur: _____
- [ ] Optimiser performances

---

## 📝 Notes du Testeur

**Environnement de test:**
- OS: _____
- Python: _____
- discord.py: _____
- Serveur Discord: _____

**Commentaires généraux:**
_____

**Suggestions d'amélioration:**
_____

---

**Signature:** _____  
**Date:** _____