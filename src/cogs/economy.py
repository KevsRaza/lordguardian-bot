"""
Système d'économie avec monnaie virtuelle
"""
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import random
from core.logger import setup_logger
from core.embeds import Embeds

logger = setup_logger("Economy")

class Economy(commands.Cog):
    """Système économique du serveur"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def get_balance(self, user_id: int, guild_id: int):
        """Récupère ou crée le compte économique d'un utilisateur"""
        try:
            await self.bot.db.connect()
            
            async with self.bot.db.connection.cursor() as cursor:
                # Vérifier si l'utilisateur a un compte
                await cursor.execute(
                    """SELECT balance, bank, daily_claimed FROM economy 
                    WHERE user_id = ? AND guild_id = ?""",
                    (user_id, guild_id)
                )
                result = await cursor.fetchone()
                
                if result:
                    return {
                        "balance": result[0],
                        "bank": result[1],
                        "daily_claimed": result[2]
                    }
                else:
                    # Créer un nouveau compte
                    await cursor.execute(
                        """INSERT INTO economy (user_id, guild_id, balance, bank, daily_claimed)
                        VALUES (?, ?, ?, ?, ?)""",
                        (user_id, guild_id, 100, 0, None)
                    )
                    await self.bot.db.connection.commit()
                    
                    return {
                        "balance": 100,
                        "bank": 0,
                        "daily_claimed": None
                    }
                    
        except Exception as e:
            logger.error(f"Erreur get_balance: {e}")
            return None
    
    async def update_balance(self, user_id: int, guild_id: int, balance=None, bank=None, daily_claimed=None):
        """Met à jour le solde d'un utilisateur"""
        try:
            await self.bot.db.connect()
            
            async with self.bot.db.connection.cursor() as cursor:
                if balance is not None:
                    await cursor.execute(
                        "UPDATE economy SET balance = ? WHERE user_id = ? AND guild_id = ?",
                        (balance, user_id, guild_id)
                    )
                
                if bank is not None:
                    await cursor.execute(
                        "UPDATE economy SET bank = ? WHERE user_id = ? AND guild_id = ?",
                        (bank, user_id, guild_id)
                    )
                
                if daily_claimed is not None:
                    await cursor.execute(
                        "UPDATE economy SET daily_claimed = ? WHERE user_id = ? AND guild_id = ?",
                        (daily_claimed, user_id, guild_id)
                    )
                
                await self.bot.db.connection.commit()
                
        except Exception as e:
            logger.error(f"Erreur update_balance: {e}")
    
    def format_coins(self, amount: int) -> str:
        """Formate un montant avec des espaces pour les milliers"""
        return f"{amount:,}".replace(",", " ")
    
    def create_balance_embed(self, user: discord.Member, account: dict) -> discord.Embed:
        """Crée l'embed d'affichage du solde"""
        total = account['balance'] + account['bank']
        
        embed = Embeds.create_base_embed(
            title=f"💰 Porte-monnaie de {user.display_name}",
            description=f"Voici le solde de {user.mention}",
            color=0xFFD700  # Or
        )
        
        embed.add_field(
            name="💵 Portefeuille",
            value=f"**{self.format_coins(account['balance'])}** coins",
            inline=True
        )
        embed.add_field(
            name="🏦 Banque",
            value=f"**{self.format_coins(account['bank'])}** coins",
            inline=True
        )
        embed.add_field(
            name="💎 Total",
            value=f"**{self.format_coins(total)}** coins",
            inline=False
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        
        return embed
    
    def create_daily_embed(self, reward: int, new_balance: int, is_streak: bool = False) -> discord.Embed:
        """Crée l'embed de récompense quotidienne"""
        if is_streak:
            embed = Embeds.create_base_embed(
                title="🔥 Récompense quotidienne - SÉRIE !",
                description=f"Tu as reçu **{self.format_coins(reward)}** coins !\n🔥 Continue ta série !",
                color=0xFF6B00  # Orange vif
            )
        else:
            embed = Embeds.create_base_embed(
                title="🎁 Récompense quotidienne",
                description=f"Tu as reçu **{self.format_coins(reward)}** coins !",
                color=Embeds.EmbedColors.SUCCESS
            )
        
        embed.add_field(
            name="💰 Nouveau solde",
            value=f"**{self.format_coins(new_balance)}** coins",
            inline=False
        )
        
        embed.set_footer(text="💡 Reviens demain pour ta prochaine récompense !")
        
        return embed
    
    def create_transaction_embed(self, transaction_type: str, amount: int, new_balance: int, new_bank: int) -> discord.Embed:
        """Crée l'embed pour les transactions (dépôt/retrait)"""
        if transaction_type == "deposit":
            embed = Embeds.success(
                "Dépôt effectué",
                f"Tu as déposé **{self.format_coins(amount)}** coins à la banque."
            )
            emoji_wallet = "💵"
            emoji_bank = "🏦"
        else:  # withdraw
            embed = Embeds.success(
                "Retrait effectué",
                f"Tu as retiré **{self.format_coins(amount)}** coins de la banque."
            )
            emoji_wallet = "💰"
            emoji_bank = "🏦"
        
        embed.add_field(
            name=f"{emoji_wallet} Portefeuille",
            value=f"{self.format_coins(new_balance)} coins",
            inline=True
        )
        embed.add_field(
            name=f"{emoji_bank} Banque",
            value=f"{self.format_coins(new_bank)} coins",
            inline=True
        )
        
        return embed
    
    @app_commands.command(name="balance", description="Affiche ton solde")
    @app_commands.describe(user="L'utilisateur dont voir le solde")
    async def balance(self, interaction: discord.Interaction, user: discord.Member = None):
        """Affiche le solde d'un utilisateur"""
        target = user or interaction.user
        
        account = await self.get_balance(target.id, interaction.guild_id)
        
        if not account:
            embed = Embeds.error(
                "Erreur",
                "Impossible de récupérer le solde. Réessaye plus tard."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = self.create_balance_embed(target, account)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="daily", description="Récupère ta récompense quotidienne")
    async def daily(self, interaction: discord.Interaction):
        """Récompense quotidienne"""
        account = await self.get_balance(interaction.user.id, interaction.guild_id)
        
        if not account:
            embed = Embeds.error(
                "Erreur",
                "Impossible de récupérer ton compte. Réessaye plus tard."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        now = datetime.utcnow()
        
        # Vérifier si la récompense a déjà été réclamée aujourd'hui
        if account["daily_claimed"]:
            try:
                # Convertir en datetime si c'est une string
                if isinstance(account["daily_claimed"], str):
                    last_claimed = datetime.fromisoformat(account["daily_claimed"].replace('Z', '+00:00'))
                else:
                    last_claimed = account["daily_claimed"]
                
                time_since = now - last_claimed
                
                if time_since < timedelta(hours=24):
                    remaining = timedelta(hours=24) - time_since
                    hours = int(remaining.total_seconds() // 3600)
                    minutes = int((remaining.total_seconds() % 3600) // 60)
                    
                    embed = Embeds.warning(
                        "Déjà réclamé",
                        f"Tu as déjà récupéré ta récompense quotidienne !\n\n"
                        f"⏰ Reviens dans **{hours}h {minutes}m**."
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
            except Exception as e:
                logger.error(f"Erreur conversion date: {e}")
        
        # Calculer la récompense (avec bonus aléatoire)
        base_reward = random.randint(100, 500)
        bonus = random.randint(0, 100) if random.random() < 0.3 else 0  # 30% de chance de bonus
        reward = base_reward + bonus
        
        new_balance = account["balance"] + reward
        
        await self.update_balance(
            interaction.user.id,
            interaction.guild_id,
            balance=new_balance,
            daily_claimed=now
        )
        
        # Créer l'embed avec bonus si applicable
        embed = self.create_daily_embed(reward, new_balance, is_streak=bonus > 0)
        
        if bonus > 0:
            embed.add_field(
                name="🎉 Bonus chanceux !",
                value=f"+{self.format_coins(bonus)} coins bonus !",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="deposit", description="Dépose de l'argent à la banque")
    @app_commands.describe(amount="Montant à déposer (ou 'all' pour tout déposer)")
    async def deposit(self, interaction: discord.Interaction, amount: str):
        """Dépose de l'argent à la banque"""
        account = await self.get_balance(interaction.user.id, interaction.guild_id)
        
        if not account:
            embed = Embeds.error(
                "Erreur",
                "Impossible de récupérer ton compte. Réessaye plus tard."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Déterminer le montant à déposer
        if amount.lower() == "all":
            amount_to_deposit = account["balance"]
        else:
            try:
                amount_to_deposit = int(amount.replace(" ", ""))  # Enlever les espaces
            except ValueError:
                embed = Embeds.error(
                    "Montant invalide",
                    "Utilise un nombre ou `all` pour tout déposer.\n\n"
                    "**Exemples:**\n• `/deposit 1000`\n• `/deposit all`"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Validations
        if amount_to_deposit <= 0:
            embed = Embeds.error(
                "Montant invalide",
                "Le montant doit être supérieur à 0."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if account["balance"] < amount_to_deposit:
            embed = Embeds.warning(
                "Fonds insuffisants",
                f"Tu n'as que **{self.format_coins(account['balance'])}** coins dans ton portefeuille.\n\n"
                f"Tu essaies de déposer **{self.format_coins(amount_to_deposit)}** coins."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Effectuer la transaction
        new_balance = account["balance"] - amount_to_deposit
        new_bank = account["bank"] + amount_to_deposit
        
        await self.update_balance(
            interaction.user.id,
            interaction.guild_id,
            balance=new_balance,
            bank=new_bank
        )
        
        embed = self.create_transaction_embed("deposit", amount_to_deposit, new_balance, new_bank)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="withdraw", description="Retire de l'argent de la banque")
    @app_commands.describe(amount="Montant à retirer (ou 'all' pour tout retirer)")
    async def withdraw(self, interaction: discord.Interaction, amount: str):
        """Retire de l'argent de la banque"""
        account = await self.get_balance(interaction.user.id, interaction.guild_id)
        
        if not account:
            embed = Embeds.error(
                "Erreur",
                "Impossible de récupérer ton compte. Réessaye plus tard."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Déterminer le montant à retirer
        if amount.lower() == "all":
            amount_to_withdraw = account["bank"]
        else:
            try:
                amount_to_withdraw = int(amount.replace(" ", ""))  # Enlever les espaces
            except ValueError:
                embed = Embeds.error(
                    "Montant invalide",
                    "Utilise un nombre ou `all` pour tout retirer.\n\n"
                    "**Exemples:**\n• `/withdraw 1000`\n• `/withdraw all`"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Validations
        if amount_to_withdraw <= 0:
            embed = Embeds.error(
                "Montant invalide",
                "Le montant doit être supérieur à 0."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if account["bank"] < amount_to_withdraw:
            embed = Embeds.warning(
                "Fonds insuffisants",
                f"Tu n'as que **{self.format_coins(account['bank'])}** coins à la banque.\n\n"
                f"Tu essaies de retirer **{self.format_coins(amount_to_withdraw)}** coins."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Effectuer la transaction
        new_bank = account["bank"] - amount_to_withdraw
        new_balance = account["balance"] + amount_to_withdraw
        
        await self.update_balance(
            interaction.user.id,
            interaction.guild_id,
            balance=new_balance,
            bank=new_bank
        )
        
        embed = self.create_transaction_embed("withdraw", amount_to_withdraw, new_balance, new_bank)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="transfer", description="Transfert de l'argent à un autre utilisateur")
    @app_commands.describe(
        user="L'utilisateur à qui envoyer l'argent",
        amount="Montant à transférer"
    )
    async def transfer(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        """Transfert d'argent entre utilisateurs"""
        
        # Vérifications de base
        if user.id == interaction.user.id:
            embed = Embeds.error(
                "Transfert impossible",
                "Tu ne peux pas te transférer de l'argent à toi-même !"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if user.bot:
            embed = Embeds.error(
                "Transfert impossible",
                "Tu ne peux pas transférer de l'argent à un bot !"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if amount <= 0:
            embed = Embeds.error(
                "Montant invalide",
                "Le montant doit être supérieur à 0."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Récupérer les comptes
        sender_account = await self.get_balance(interaction.user.id, interaction.guild_id)
        receiver_account = await self.get_balance(user.id, interaction.guild_id)
        
        if not sender_account or not receiver_account:
            embed = Embeds.error(
                "Erreur",
                "Impossible de récupérer les comptes. Réessaye plus tard."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Vérifier le solde
        if sender_account["balance"] < amount:
            embed = Embeds.warning(
                "Fonds insuffisants",
                f"Tu n'as que **{self.format_coins(sender_account['balance'])}** coins dans ton portefeuille.\n\n"
                f"Tu essaies de transférer **{self.format_coins(amount)}** coins."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Effectuer le transfert
        new_sender_balance = sender_account["balance"] - amount
        new_receiver_balance = receiver_account["balance"] + amount
        
        await self.update_balance(
            interaction.user.id,
            interaction.guild_id,
            balance=new_sender_balance
        )
        
        await self.update_balance(
            user.id,
            interaction.guild_id,
            balance=new_receiver_balance
        )
        
        # Confirmation
        embed = Embeds.success(
            "Transfert effectué",
            f"Tu as transféré **{self.format_coins(amount)}** coins à {user.mention}."
        )
        
        embed.add_field(
            name="💸 Ton nouveau solde",
            value=f"{self.format_coins(new_sender_balance)} coins",
            inline=True
        )
        embed.add_field(
            name="💰 Solde du destinataire",
            value=f"{self.format_coins(new_receiver_balance)} coins",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Notification au destinataire
        try:
            notify_embed = Embeds.info(
                "Transfert reçu",
                f"{interaction.user.mention} t'a envoyé **{self.format_coins(amount)}** coins !"
            )
            notify_embed.add_field(
                name="💰 Ton nouveau solde",
                value=f"{self.format_coins(new_receiver_balance)} coins"
            )
            
            await user.send(embed=notify_embed)
        except discord.Forbidden:
            pass  # L'utilisateur a désactivé les DM
    
    @app_commands.command(name="richest", description="Affiche le classement des plus riches")
    @app_commands.describe(page="Numéro de page (10 utilisateurs par page)")
    async def richest(self, interaction: discord.Interaction, page: int = 1):
        """Affiche le classement économique du serveur"""
        
        if page < 1:
            page = 1
        
        try:
            await self.bot.db.connect()
            
            async with self.bot.db.connection.cursor() as cursor:
                # Récupérer tous les comptes du serveur triés par richesse totale
                await cursor.execute(
                    """SELECT user_id, balance, bank 
                    FROM economy 
                    WHERE guild_id = ? 
                    ORDER BY (balance + bank) DESC 
                    LIMIT ? OFFSET ?""",
                    (interaction.guild_id, 10, (page - 1) * 10)
                )
                results = await cursor.fetchall()
                
                # Compter le nombre total d'utilisateurs
                await cursor.execute(
                    "SELECT COUNT(*) FROM economy WHERE guild_id = ?",
                    (interaction.guild_id,)
                )
                total_users = (await cursor.fetchone())[0]
                
        except Exception as e:
            logger.error(f"Erreur leaderboard: {e}")
            embed = Embeds.error(
                "Erreur",
                "Impossible de récupérer le classement. Réessaye plus tard."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not results:
            embed = Embeds.info(
                "Classement vide",
                "Aucun utilisateur trouvé sur cette page."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Créer l'embed du leaderboard
        embed = Embeds.create_base_embed(
            title="🏆 CLASSEMENT ÉCONOMIQUE",
            description=f"Les plus riches du serveur • Page {page}",
            color=0xFFD700  # Or
        )
        
        leaderboard_text = ""
        start_rank = (page - 1) * 10 + 1
        
        medals = {0: "🥇", 1: "🥈", 2: "🥉"}
        
        for idx, (user_id, balance, bank) in enumerate(results):
            rank = start_rank + idx
            total = balance + bank
            
            # Récupérer le membre
            member = interaction.guild.get_member(user_id)
            username = member.display_name if member else f"Utilisateur {user_id}"
            
            # Médaille pour le top 3
            medal = medals.get(rank - 1, f"**{rank}.**")
            
            leaderboard_text += f"{medal} {username} • **{self.format_coins(total)}** coins\n"
        
        embed.add_field(
            name="💰 Classement",
            value=leaderboard_text or "Aucun utilisateur",
            inline=False
        )
        
        # Afficher la position de l'utilisateur actuel
        try:
            async with self.bot.db.connection.cursor() as cursor:
                await cursor.execute(
                    """SELECT COUNT(*) FROM economy 
                    WHERE guild_id = ? AND (balance + bank) > (
                        SELECT (balance + bank) FROM economy 
                        WHERE user_id = ? AND guild_id = ?
                    )""",
                    (interaction.guild_id, interaction.user.id, interaction.guild_id)
                )
                user_rank = (await cursor.fetchone())[0] + 1
                
                account = await self.get_balance(interaction.user.id, interaction.guild_id)
                if account:
                    user_total = account["balance"] + account["bank"]
                    embed.set_footer(
                        text=f"Ta position: #{user_rank} • {self.format_coins(user_total)} coins • "
                        f"Total: {total_users} utilisateurs"
                    )
        except Exception as e:
            logger.error(f"Erreur position utilisateur: {e}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))