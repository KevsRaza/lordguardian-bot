"""
Système de boutique pour dépenser les coins
"""
import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
from datetime import datetime, timedelta
from core.logger import setup_logger
from core.embeds import Embeds

logger = setup_logger("Shop")

class Shop(commands.Cog):
    """Boutique du serveur"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Catalogue des items disponibles
        self.items = {
            # 🎭 APPARENCE - Rôles colorés
            "role_rouge": {
                "name": "🔴 Rôle Rouge",
                "price": 300,
                "description": "Rôle rouge visible par tous (permanent)",
                "category": "appearance",
                "type": "role",
                "emoji": "🔴"
            },
            "role_bleu": {
                "name": "🔵 Rôle Bleu",
                "price": 300,
                "description": "Rôle bleu visible par tous (permanent)",
                "category": "appearance", 
                "type": "role",
                "emoji": "🔵"
            },
            "role_vip": {
                "name": "⭐ Rôle VIP",
                "price": 1000,
                "description": "Rôle VIP doré + accès salons spéciaux",
                "category": "appearance",
                "type": "role",
                "emoji": "⭐"
            },
            
            # 🎪 DIVERTISSEMENT - Effets spéciaux
            "rainbow_wave": {
                "name": "🌈 Vague Arc-en-ciel",
                "price": 75,
                "description": "Crée une magnifique vague de couleurs dans le chat",
                "category": "fun",
                "type": "effect",
                "emoji": "🌈"
            },
            "meteor_shower": {
                "name": "☄️ Pluie de Météores",
                "price": 150,
                "description": "Déclenche une impressionnante pluie de météores cosmique",
                "category": "fun",
                "type": "effect",
                "emoji": "☄️"
            },
            "aurora_borealis": {
                "name": "🌌 Aurore Boréale",
                "price": 200,
                "description": "Illumine le chat avec une aurore boréale mystique",
                "category": "fun",
                "type": "effect",
                "emoji": "🌌"
            },
            
            # 💼 UTILITAIRE - Avantages pratiques
            "daily_boost": {
                "name": "💰 Daily Boost",
                "price": 500,
                "description": "Double ta prochaine récompense quotidienne",
                "category": "utility",
                "type": "boost",
                "emoji": "💰"
            },
            "xp_boost": {
                "name": "⚡ XP Boost 24h",
                "price": 400,
                "description": "+50% d'XP pendant 24 heures",
                "category": "utility",
                "type": "boost",
                "emoji": "⚡"
            },
            
            # 🎁 SURPRISE - Boîtes mystères
            "boite_mystere": {
                "name": "🎁 Boîte Mystère",
                "price": 200,
                "description": "Contient entre 100 et 500 coins ou un item rare !",
                "category": "mystery",
                "type": "lootbox",
                "emoji": "🎁"
            }
        }
        
        # Rôles par serveur (à configurer par les admins)
        self.role_configs = {}
    
    async def get_economy_cog(self):
        """Récupère le cog d'économie"""
        return self.bot.get_cog("Economy")
    
    def format_price(self, price: int) -> str:
        """Formate un prix avec des espaces pour les milliers"""
        return f"{price:,}".replace(",", " ")
    
    def create_shop_embed(self) -> discord.Embed:
        """Crée l'embed principal de la boutique"""
        embed = Embeds.create_base_embed(
            title="🛒 BOUTIQUE DU SERVEUR",
            description="Achète des objets avec tes coins !\nUtilise `/buy <nom_item>` pour acheter.",
            color=0x9B59B6  # Violet
        )
        
        # Regrouper les items par catégorie
        categories = {
            "appearance": "🎭 **Apparence**",
            "fun": "🎪 **Divertissement**",
            "utility": "💼 **Utilitaire**",
            "mystery": "🎁 **Surprise**"
        }
        
        for cat_id, cat_title in categories.items():
            cat_items = [item for item in self.items.values() if item["category"] == cat_id]
            
            if cat_items:
                items_text = ""
                for item in cat_items:
                    items_text += f"• {item['emoji']} **{item['name']}** - {self.format_price(item['price'])} coins\n"
                
                embed.add_field(
                    name=cat_title,
                    value=items_text,
                    inline=False
                )
        
        return embed
    
    def create_item_info_embed(self, item: dict, item_key: str, account: dict = None) -> discord.Embed:
        """Crée l'embed d'information détaillée d'un item"""
        embed = Embeds.create_base_embed(
            title=f"{item['emoji']} {item['name']}",
            description=item["description"],
            color=Embeds.EmbedColors.INFO
        )
        
        # Informations détaillées
        embed.add_field(name="💰 Prix", value=f"{self.format_price(item['price'])} coins", inline=True)
        
        category_names = {
            "appearance": "🎭 Apparence",
            "fun": "🎪 Divertissement", 
            "utility": "💼 Utilitaire",
            "mystery": "🎁 Surprise"
        }
        embed.add_field(name="📂 Catégorie", value=category_names[item["category"]], inline=True)
        
        type_names = {
            "role": "👑 Rôle",
            "effect": "✨ Effet",
            "boost": "⚡ Boost",
            "lootbox": "🎁 Boîte mystère"
        }
        embed.add_field(name="🎯 Type", value=type_names[item["type"]], inline=True)
        
        # Vérifier si l'utilisateur peut acheter
        if account and account["balance"] < item["price"]:
            missing = item["price"] - account["balance"]
            embed.add_field(
                name="❌ Fonds insuffisants",
                value=f"Il te manque {self.format_price(missing)} coins !",
                inline=False
            )
        
        embed.set_footer(text=f"ID: {item_key}")
        
        return embed
    
    def create_purchase_success_embed(self, item: dict, new_balance: int) -> discord.Embed:
        """Crée l'embed de confirmation d'achat"""
        embed = Embeds.success(
            "Achat réussi !",
            f"Tu as acheté **{item['name']}**"
        )
        
        embed.add_field(name="💰 Prix payé", value=f"{self.format_price(item['price'])} coins", inline=True)
        embed.add_field(name="💵 Nouveau solde", value=f"{self.format_price(new_balance)} coins", inline=True)
        
        if item["type"] == "role":
            embed.add_field(
                name="🎭 Rôle attribué", 
                value="Le rôle t'a été attribué avec succès !",
                inline=False
            )
        elif item["type"] == "effect":
            embed.add_field(
                name="✨ Effet activé",
                value="L'effet a été déclenché dans le chat !",
                inline=False
            )
        elif item["type"] == "boost":
            embed.add_field(
                name="⚡ Boost activé",
                value="Ton boost est maintenant actif !",
                inline=False
            )
        
        return embed
    
    def create_items_catalog_embed(self) -> discord.Embed:
        """Crée l'embed du catalogue complet"""
        embed = Embeds.create_base_embed(
            title="📋 CATALOGUE COMPLET",
            description="Tous les items disponibles à l'achat\nUtilise `/iteminfo <nom>` pour plus de détails",
            color=Embeds.EmbedColors.INFO
        )
        
        for item_id, item in self.items.items():
            description = item['description']
            if len(description) > 50:
                description = description[:50] + "..."
            
            embed.add_field(
                name=f"{item['emoji']} {item['name']}",
                value=f"`{item_id}`\n💰 {self.format_price(item['price'])} coins\n{description}",
                inline=True
            )
        
        return embed
    
    # ==================== COMMANDES PRINCIPALES ====================
    
    @app_commands.command(name="shop", description="Affiche la boutique")
    async def shop(self, interaction: discord.Interaction):
        """Affiche tous les items disponibles par catégorie"""
        
        embed = self.create_shop_embed()
        
        # Afficher le solde de l'utilisateur
        economy = await self.get_economy_cog()
        if economy:
            account = await economy.get_balance(interaction.user.id, interaction.guild_id)
            if account:
                embed.set_footer(
                    text=f"💰 Ton solde: {self.format_price(account['balance'])} coins | " +
                         f"Total: {self.format_price(account['balance'] + account['bank'])} coins"
                )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="iteminfo", description="Informations détaillées sur un item")
    @app_commands.describe(item_name="Nom de l'item (ex: role_rouge)")
    async def item_info(self, interaction: discord.Interaction, item_name: str):
        """Affiche les détails d'un item spécifique"""
        
        # Trouver l'item (insensible à la casse)
        item = None
        item_key = None
        
        for key, data in self.items.items():
            if item_name.lower() in key.lower() or item_name.lower() in data["name"].lower():
                item = data
                item_key = key
                break
        
        if not item:
            embed = Embeds.error(
                "Item non trouvé",
                "Utilise `/items` pour voir la liste complète."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Récupérer le compte de l'utilisateur
        economy = await self.get_economy_cog()
        account = None
        can_afford = False
        
        if economy:
            account = await economy.get_balance(interaction.user.id, interaction.guild_id)
            if account and account["balance"] >= item["price"]:
                can_afford = True
        
        embed = self.create_item_info_embed(item, item_key, account)
        
        # Créer une vue avec bouton d'achat
        class BuyView(discord.ui.View):
            def __init__(self, item_key, item_data, can_afford):
                super().__init__(timeout=60)
                self.item_key = item_key
                self.item_data = item_data
                self.can_afford = can_afford
            
            @discord.ui.button(label="🛒 Acheter maintenant", style=discord.ButtonStyle.green, disabled=not can_afford)
            async def buy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                
                # Appeler la commande d'achat
                cog = interaction.client.get_cog("Shop")
                if cog:
                    await cog.buy_item(interaction, self.item_key)
            
            @discord.ui.button(label="❌ Fermer", style=discord.ButtonStyle.red)
            async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.edit_message(content="❌ Achat annulé.", embed=None, view=None)
        
        view = BuyView(item_key, item, can_afford)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="items", description="Liste complète de tous les items")
    async def items_list(self, interaction: discord.Interaction):
        """Affiche tous les items avec leurs IDs"""
        
        embed = self.create_items_catalog_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="buy", description="Achète un item de la boutique")
    @app_commands.describe(item_id="ID de l'item (voir /items)")
    async def buy_command(self, interaction: discord.Interaction, item_id: str):
        """Commande principale d'achat"""
        await self.buy_item(interaction, item_id)
    
    # ==================== LOGIQUE D'ACHAT ====================
    
    async def buy_item(self, interaction: discord.Interaction, item_id: str):
        """Logique d'achat d'un item"""
        
        # Vérifier si l'item existe
        if item_id not in self.items:
            embed = Embeds.error(
                "Item inexistant",
                f"L'item `{item_id}` n'existe pas.\nUtilise `/items` pour la liste."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        item = self.items[item_id]
        
        # Vérifier l'économie
        economy = await self.get_economy_cog()
        if not economy:
            embed = Embeds.error(
                "Système indisponible",
                "Le système économique n'est pas disponible actuellement."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Vérifier le solde
        account = await economy.get_balance(interaction.user.id, interaction.guild_id)
        if not account:
            embed = Embeds.error(
                "Compte introuvable",
                "Ton compte économique n'a pas été trouvé."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if account["balance"] < item["price"]:
            missing = item["price"] - account["balance"]
            embed = Embeds.warning(
                "Fonds insuffisants",
                f"**Prix:** {self.format_price(item['price'])} coins\n"
                f"**Ton solde:** {self.format_price(account['balance'])} coins\n"
                f"**Il te manque:** {self.format_price(missing)} coins\n\n"
                f"💡 **Astuce:** Utilise `/daily` pour gagner des coins !"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Débiter l'utilisateur
        new_balance = account["balance"] - item["price"]
        await economy.update_balance(interaction.user.id, interaction.guild_id, balance=new_balance)
        
        # Donner l'item
        success = await self.deliver_item(interaction, item_id, item)
        
        if success:
            # Confirmation d'achat
            embed = self.create_purchase_success_embed(item, new_balance)
            await interaction.response.send_message(embed=embed)
        else:
            # Erreur lors de la livraison - rembourser
            await economy.update_balance(interaction.user.id, interaction.guild_id, balance=account["balance"])
            
            embed = Embeds.error(
                "Erreur de livraison",
                "Une erreur s'est produite lors de l'attribution de l'item.\n"
                "Tu as été remboursé. Contacte un administrateur si le problème persiste."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ==================== LIVRAISON DES ITEMS ====================
    
    async def deliver_item(self, interaction: discord.Interaction, item_id: str, item: dict) -> bool:
        """Donne l'item acheté à l'utilisateur"""
        
        try:
            item_type = item["type"]
            
            if item_type == "role":
                return await self.give_role(interaction, item_id, item)
            elif item_type == "effect":
                return await self.give_effect(interaction, item_id, item)
            elif item_type == "boost":
                return await self.give_boost(interaction, item_id, item)
            elif item_type == "lootbox":
                return await self.give_lootbox(interaction, item_id, item)
            else:
                logger.info(f"{interaction.user} a acheté {item['name']}")
                return True
                
        except Exception as e:
            logger.error(f"Erreur livraison item {item_id}: {e}")
            return False
    
    async def give_role(self, interaction: discord.Interaction, item_id: str, item: dict) -> bool:
        """Attribue un rôle à l'utilisateur"""
        
        # Mapping des rôles par ID d'item
        role_configs = {
            "role_rouge": {"name": "🔴 Rouge", "color": discord.Color.red()},
            "role_bleu": {"name": "🔵 Bleu", "color": discord.Color.blue()},
            "role_vip": {"name": "⭐ VIP", "color": discord.Color.gold()}
        }
        
        if item_id not in role_configs:
            return False
        
        role_info = role_configs[item_id]
        
        try:
            # Vérifier si le rôle existe déjà
            role = discord.utils.get(interaction.guild.roles, name=role_info["name"])
            
            if not role:
                # Créer le rôle
                role = await interaction.guild.create_role(
                    name=role_info["name"],
                    color=role_info["color"],
                    reason=f"Achat boutique par {interaction.user}"
                )
                
                # Positionner le rôle (au-dessus des rôles basiques)
                try:
                    everyone = interaction.guild.default_role
                    position = everyone.position + 1
                    await role.edit(position=position)
                except:
                    pass
            
            # Vérifier si l'utilisateur a déjà le rôle
            if role in interaction.user.roles:
                await interaction.channel.send(
                    f"ℹ️ {interaction.user.mention}, tu as déjà le rôle **{role.name}** !",
                    delete_after=10
                )
                return True
            
            # Donner le rôle
            await interaction.user.add_roles(role, reason="Achat boutique")
            
            # Message de confirmation publique
            await interaction.channel.send(
                f"🎉 {interaction.user.mention} a obtenu le rôle **{role.name}** !",
                delete_after=10
            )
            
            logger.info(f"{interaction.user} a reçu le rôle {role.name}")
            return True
            
        except discord.Forbidden:
            await interaction.channel.send(
                "❌ Je n'ai pas la permission de gérer les rôles. Contacte un administrateur.",
                delete_after=10
            )
            return False
        except Exception as e:
            logger.error(f"Erreur attribution rôle: {e}")
            return False
    
    async def give_effect(self, interaction: discord.Interaction, item_id: str, item: dict) -> bool:
        """Déclenche un effet visuel amélioré"""
        
        effects = {
            "rainbow_wave": {
                "frames": [
                    "🟥⬜⬜⬜⬜⬜⬜⬜⬜⬜",
                    "⬜🟧⬜⬜⬜⬜⬜⬜⬜⬜",
                    "⬜⬜🟨⬜⬜⬜⬜⬜⬜⬜",
                    "⬜⬜⬜🟩⬜⬜⬜⬜⬜⬜",
                    "⬜⬜⬜⬜🟦⬜⬜⬜⬜⬜",
                    "⬜⬜⬜⬜⬜🟪⬜⬜⬜⬜",
                    "⬜⬜⬜⬜⬜⬜🟥⬜⬜⬜",
                    "⬜⬜⬜⬜⬜⬜⬜🟧⬜⬜",
                    "⬜⬜⬜⬜⬜⬜⬜⬜🟨⬜",
                    "⬜⬜⬜⬜⬜⬜⬜⬜⬜🟩"
                ],
                "title": "🌈 ══════ VAGUE ARC-EN-CIEL ══════ 🌈",
                "speed": 0.3
            },
            "meteor_shower": {
                "frames": [
                    "🌌                    ☄️",
                    "🌌                ☄️    ",
                    "🌌            ☄️        ",
                    "🌌        ☄️            ",
                    "🌌    ☄️                ",
                    "🌌☄️                    ",
                    "💥 ✨ ✨ ✨ ✨ ✨ ✨",
                    "    ☄️          ☄️      ",
                    "        ☄️  ☄️          ",
                    "💥 ✨   💥 ✨   💥 ✨"
                ],
                "title": "☄️ ══════ PLUIE DE MÉTÉORES ══════ ☄️",
                "speed": 0.4
            },
            "aurora_borealis": {
                "frames": [
                    "🌌 ～～～～～～～～～～ 🌌",
                    "🌌 ～💚～～～～～～～～ 🌌",
                    "🌌 ～～💙～～～～～～～ 🌌",
                    "🌌 ～～～💜～～～～～～ 🌌",
                    "🌌 ～～～～💚～～～～～ 🌌",
                    "🌌 ～～～～～💙～～～～ 🌌",
                    "🌌 ～～～～～～💜～～～ 🌌",
                    "🌌 ～～～～～～～💚～～ 🌌",
                    "🌌 ～～～～～～～～💙～ 🌌",
                    "🌌 ～～～～～～～～～💜 🌌",
                    "🌌 💚💙💜～～～～～～～ 🌌",
                    "🌌 ✨💚💙💜～～～～～～ 🌌",
                    "🌌 ✨✨💚💙💜～～～～～ 🌌"
                ],
                "title": "🌌 ══════ AURORE BORÉALE ══════ 🌌",
                "speed": 0.4
            }
        }
        
        if item_id not in effects:
            return False
        
        effect = effects[item_id]
        
        try:
            # Message initial
            msg = await interaction.channel.send(
                f"{effect['title']}\n*Commandé par {interaction.user.mention}*"
            )
            
            # Animation
            for frame in effect["frames"]:
                await asyncio.sleep(effect["speed"])
                await msg.edit(content=f"{effect['title']}\n{frame}\n*Commandé par {interaction.user.mention}*")
            
            # Message final
            await asyncio.sleep(1)
            await msg.edit(content=f"{effect['title']}\n✨ **C'était magnifique !** ✨\n*Commandé par {interaction.user.mention}*")
            
            # Supprimer après 5 secondes
            await asyncio.sleep(5)
            await msg.delete()
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur effet {item_id}: {e}")
            return False
    
    async def give_boost(self, interaction: discord.Interaction, item_id: str, item: dict) -> bool:
        """Applique un boost"""
        
        if item_id == "daily_boost":
            # Ici vous devriez stocker en base de données
            await interaction.channel.send(
                f"💰 {interaction.user.mention} a activé un **Daily Boost** !\n"
                f"Sa prochaine récompense quotidienne sera doublée !",
                delete_after=10
            )
            return True
            
        elif item_id == "xp_boost":
            # Ici vous devriez stocker en base de données
            await interaction.channel.send(
                f"⚡ {interaction.user.mention} a activé un **XP Boost 24h** !\n"
                f"+50% d'XP pendant 24 heures !",
                delete_after=10
            )
            return True
        
        return False
    
    async def give_lootbox(self, interaction: discord.Interaction, item_id: str, item: dict) -> bool:
        """Ouvre une boîte mystère"""
        
        if item_id == "boite_mystere":
            # Simuler une ouverture de boîte
            await interaction.channel.send(
                f"🎁 {interaction.user.mention} ouvre une **Boîte Mystère**...",
                delete_after=3
            )
            
            # Attendre pour l'effet de suspense
            await asyncio.sleep(2)
            
            # Déterminer la récompense
            reward_type = random.choices(
                ["coins", "coins_big", "item"],
                weights=[70, 20, 10]
            )[0]
            
            economy = await self.get_economy_cog()
            
            if reward_type == "coins":
                coins = random.randint(100, 300)
                if economy:
                    account = await economy.get_balance(interaction.user.id, interaction.guild_id)
                    if account:
                        new_balance = account["balance"] + coins
                        await economy.update_balance(interaction.user.id, interaction.guild_id, balance=new_balance)
                
                await interaction.channel.send(
                    f"🎉 {interaction.user.mention} a trouvé **{self.format_price(coins)} coins** dans la boîte !",
                    delete_after=10
                )
                
            elif reward_type == "coins_big":
                coins = random.randint(400, 500)
                if economy:
                    account = await economy.get_balance(interaction.user.id, interaction.guild_id)
                    if account:
                        new_balance = account["balance"] + coins
                        await economy.update_balance(interaction.user.id, interaction.guild_id, balance=new_balance)
                
                await interaction.channel.send(
                    f"🎊 **JACKPOT** ! {interaction.user.mention} a trouvé **{self.format_price(coins)} coins** dans la boîte !",
                    delete_after=10
                )
                
            elif reward_type == "item":
                # Donner un rôle gratuit
                free_roles = ["role_rouge", "role_bleu"]
                free_role = random.choice(free_roles)
                
                await interaction.channel.send(
                    f"🎭 **ITEM RARE** ! {interaction.user.mention} a trouvé un **{self.items[free_role]['name']}** gratuit !",
                    delete_after=10
                )
                
                # Donner le rôle
                await self.give_role(interaction, free_role, self.items[free_role])
            
            return True
        
        return False
    
    # ==================== COMMANDES ADMIN ====================
    
    @app_commands.command(name="additem", description="[ADMIN] Ajoute un item à la boutique")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(
        item_id="ID unique de l'item",
        name="Nom affiché",
        price="Prix en coins",
        description="Description",
        category="Catégorie (appearance/fun/utility/mystery)",
        type="Type (role/effect/boost/lootbox)"
    )
    async def add_item(self, interaction: discord.Interaction, 
                      item_id: str, name: str, price: int, 
                      description: str, category: str, type: str):
        """Ajoute un item personnalisé à la boutique"""
        
        # Validation
        if item_id in self.items:
            embed = Embeds.error("ID existant", "Cet ID existe déjà.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if price <= 0:
            embed = Embeds.error("Prix invalide", "Le prix doit être supérieur à 0.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        valid_categories = ["appearance", "fun", "utility", "mystery"]
        if category not in valid_categories:
            embed = Embeds.error(
                "Catégorie invalide",
                f"Choisis parmi: {', '.join(valid_categories)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        valid_types = ["role", "effect", "boost", "lootbox"]
        if type not in valid_types:
            embed = Embeds.error(
                "Type invalide",
                f"Choisis parmi: {', '.join(valid_types)}"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Ajouter l'item
        self.items[item_id] = {
            "name": name,
            "price": price,
            "description": description,
            "category": category,
            "type": type,
            "emoji": "🛒"
        }
        
        embed = Embeds.success(
            "Item ajouté !",
            f"L'item **{name}** a été ajouté à la boutique."
        )
        
        embed.add_field(name="ID", value=item_id, inline=True)
        embed.add_field(name="Prix", value=f"{self.format_price(price)} coins", inline=True)
        embed.add_field(name="Catégorie", value=category, inline=True)
        embed.add_field(name="Type", value=type, inline=True)
        embed.add_field(name="Description", value=description, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="removeitem", description="[ADMIN] Retire un item de la boutique")
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(item_id="ID de l'item à retirer")
    async def remove_item(self, interaction: discord.Interaction, item_id: str):
        """Retire un item de la boutique"""
        
        if item_id not in self.items:
            embed = Embeds.error("Item introuvable", "Cet item n'existe pas.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        item_name = self.items[item_id]["name"]
        del self.items[item_id]
        
        embed = Embeds.success(
            "Item retiré",
            f"L'item **{item_name}** a été retiré de la boutique."
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="shopconfig", description="[ADMIN] Configuration de la boutique")
    @app_commands.default_permissions(administrator=True)
    async def shop_config(self, interaction: discord.Interaction):
        """Affiche la configuration actuelle de la boutique"""
        
        embed = Embeds.create_base_embed(
            title="⚙️ CONFIGURATION BOUTIQUE",
            description="Paramètres actuels de la boutique",
            color=Embeds.EmbedColors.INFO
        )
        
        embed.add_field(
            name="📊 Statistiques",
            value=f"**{len(self.items)}** items disponibles",
            inline=False
        )
        
        # Items par catégorie
        category_names = {
            "appearance": "🎭 Apparence",
            "fun": "🎪 Divertissement",
            "utility": "💼 Utilitaire",
            "mystery": "🎁 Surprise"
        }
        
        for cat_id, cat_name in category_names.items():
            count = len([i for i in self.items.values() if i["category"] == cat_id])
            if count > 0:
                embed.add_field(
                    name=cat_name,
                    value=f"{count} items",
                    inline=True
                )
        
        # Liste des items (limité à 10)
        items_list = "\n".join([f"• `{id}` - {data['name']}" for id, data in list(self.items.items())[:10]])
        if len(self.items) > 10:
            items_list += f"\n... et {len(self.items) - 10} autres"
        
        embed.add_field(name="📋 Items disponibles", value=items_list or "Aucun item", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Shop(bot))