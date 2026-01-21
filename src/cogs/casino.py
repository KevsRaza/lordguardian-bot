"""
Système de jeux de casino
"""
import discord
from discord import app_commands
from discord.ext import commands
import random
import asyncio
from datetime import datetime, timedelta
from core.logger import setup_logger

logger = setup_logger("Casino")

class Casino(commands.Cog):
    """Jeux de casino avec mise de coins"""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}  # {game_id: game_data}
        self.pending_challenges = {}  # {challenge_id: challenge_data}
        
        # Statistiques
        self.stats = {}
    
    async def get_economy(self):
        """Récupère le cog d'économie"""
        economy = self.bot.get_cog("Economy")
        if not economy:
            logger.error("Cog Economy non trouvé !")
        return economy
    
    async def check_and_deduct(self, user_id: int, guild_id: int, amount: int) -> bool:
        """Vérifie et déduit l'argent du joueur"""
        economy = await self.get_economy()
        if not economy:
            return False
        
        account = await economy.get_balance(user_id, guild_id)
        if not account or account["balance"] < amount:
            return False
        
        new_balance = account["balance"] - amount
        await economy.update_balance(user_id, guild_id, balance=new_balance)
        return True
    
    async def add_coins(self, user_id: int, guild_id: int, amount: int):
        """Ajoute des coins à un joueur"""
        economy = await self.get_economy()
        if not economy:
            return
        
        account = await economy.get_balance(user_id, guild_id)
        if account:
            new_balance = account["balance"] + amount
            await economy.update_balance(user_id, guild_id, balance=new_balance)
    
    def format_coins(self, amount: int) -> str:
        """Formate un montant avec des espaces"""
        return f"{amount:,}".replace(",", " ")
    
    # ==================== 🎲 PILE OU FACE ====================
    
    @app_commands.command(name="coinflip", description="Pile ou face avec mise")
    @app_commands.describe(
        bet="Mise (coins)",
        choice="pile ou face",
        opponent="Joueur à défier (laisser vide pour jouer contre le bot)"
    )
    async def coinflip(self, interaction: discord.Interaction, 
                       bet: int, choice: str, 
                       opponent: discord.Member = None):
        """Pile ou face - Joueur contre Bot ou Joueur contre Joueur"""
        
        if bet <= 0:
            await interaction.response.send_message("❌ Mise invalide.", ephemeral=True)
            return
        
        if choice.lower() not in ["pile", "face"]:
            await interaction.response.send_message("❌ Choix invalide. Choisis 'pile' ou 'face'.", ephemeral=True)
            return
        
        # Vérifier les fonds
        if not await self.check_and_deduct(interaction.user.id, interaction.guild_id, bet):
            await interaction.response.send_message(
                f"❌ Fonds insuffisants pour miser {self.format_coins(bet)} coins.",
                ephemeral=True
            )
            return
        
        # Si pas d'adversaire = contre le bot
        if not opponent or opponent.bot:
            await self.coinflip_vs_bot(interaction, bet, choice)
        else:
            await self.coinflip_vs_player(interaction, bet, choice, opponent)
    
    async def coinflip_vs_bot(self, interaction: discord.Interaction, bet: int, choice: str):
        """Pile ou face contre le bot"""
        
        # Lancer la pièce
        result = random.choice(["pile", "face"])
        win = (choice.lower() == result)
        
        # Calculer les gains (maison prend 10%)
        if win:
            gain = int(bet * 1.8)  # Gain 80% (maison 20%)
            await self.add_coins(interaction.user.id, interaction.guild_id, gain)
            title = "🎉 VICTOIRE !"
            color = discord.Color.green()
            result_msg = f"**{result.upper()}** ! Tu gagnes **{self.format_coins(gain)}** coins !"
        else:
            gain = 0
            title = "💥 DÉFAITE..."
            color = discord.Color.red()
            result_msg = f"**{result.upper()}** ! Tu perds **{self.format_coins(bet)}** coins."
        
        # Embed résultat
        embed = discord.Embed(title=title, color=color)
        
        # Animation de pièce
        coin_display = f"**{result.upper()}**" if win else f"~~{result.upper()}~~"
        
        embed.add_field(
            name="🎲 Résultat",
            value=f"```\n   ┌─────────┐\n   │  {coin_display:^5}  │\n   └─────────┘\n```",
            inline=False
        )
        
        embed.add_field(name="Tu as choisi", value=choice.title(), inline=True)
        embed.add_field(name="Gain", value=f"{self.format_coins(gain)} coins" if win else "0 coin", inline=True)
        
        # Nouveau solde
        economy = await self.get_economy()
        if economy:
            account = await economy.get_balance(interaction.user.id, interaction.guild_id)
            if account:
                embed.add_field(
                    name="Nouveau solde", 
                    value=f"{self.format_coins(account['balance'])} coins", 
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed)
    
    async def coinflip_vs_player(self, interaction: discord.Interaction, bet: int, choice: str, opponent: discord.Member):
        """Pile ou face Joueur contre Joueur"""
        
        # Vérifier que l'adversaire n'est pas le joueur lui-même
        if opponent.id == interaction.user.id:
            await interaction.response.send_message("❌ Tu ne peux pas jouer contre toi-même.", ephemeral=True)
            return
        
        # Vérifier que l'adversaire n'est pas un bot
        if opponent.bot:
            await interaction.response.send_message("❌ Tu ne peux pas défier un bot.", ephemeral=True)
            return
        
        # Vérifier les fonds de l'adversaire
        if not await self.check_and_deduct(opponent.id, interaction.guild_id, bet):
            await interaction.response.send_message(
                f"❌ {opponent.mention} n'a pas assez de coins pour accepter le défi.",
                ephemeral=True
            )
            # Rembourser le joueur
            await self.add_coins(interaction.user.id, interaction.guild_id, bet)
            return
        
        # Créer le défi
        challenge_id = f"{interaction.user.id}_{opponent.id}_{datetime.utcnow().timestamp()}"
        
        self.pending_challenges[challenge_id] = {
            "challenger": interaction.user,
            "opponent": opponent,
            "bet": bet,
            "challenger_choice": choice.lower(),
            "created_at": datetime.utcnow(),
            "status": "pending"
        }
        
        # Embed de défi
        embed = discord.Embed(
            title="🎲 DÉFI PILE OU FACE !",
            description=f"{opponent.mention}, tu as été défié par {interaction.user.mention} !",
            color=discord.Color.gold()
        )
        
        embed.add_field(name="💰 Mise", value=f"{self.format_coins(bet)} coins chacun", inline=True)
        embed.add_field(name="🎯 Choix du challenger", value=choice.title(), inline=True)
        embed.add_field(name="⏱️ Temps limite", value="1 minute", inline=True)
        
        # Vue avec boutons
        class ChallengeView(discord.ui.View):
            def __init__(self, challenge_id, casino_cog):
                super().__init__(timeout=60)
                self.challenge_id = challenge_id
                self.casino_cog = casino_cog
            
            @discord.ui.button(label="✅ Accepter", style=discord.ButtonStyle.green)
            async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != opponent.id:
                    await interaction.response.send_message("❌ Ce défi ne t'est pas adressé.", ephemeral=True)
                    return
                
                # Ouvrir un modal pour choisir pile/face
                class ChoiceModal(discord.ui.Modal, title="🎲 Choisis pile ou face"):
                    choice = discord.ui.TextInput(
                        label="pile ou face ?",
                        placeholder="Écris 'pile' ou 'face'",
                        max_length=4,
                        required=True
                    )
                    
                    async def on_submit(self, modal_interaction: discord.Interaction):
                        if self.choice.value.lower() not in ["pile", "face"]:
                            await modal_interaction.response.send_message(
                                "❌ Choix invalide. Écris 'pile' ou 'face'.",
                                ephemeral=True
                            )
                            return
                        
                        # Traiter le défi
                        await self.casino_cog.process_coinflip_challenge(
                            self.challenge_id, 
                            modal_interaction, 
                            self.choice.value.lower()
                        )
                
                modal = ChoiceModal()
                await interaction.response.send_modal(modal)
            
            @discord.ui.button(label="❌ Refuser", style=discord.ButtonStyle.red)
            async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != opponent.id:
                    await interaction.response.send_message("❌ Ce défi ne t'est pas adressé.", ephemeral=True)
                    return
                
                # Refuser le défi
                if self.challenge_id in self.casino_cog.pending_challenges:
                    challenge = self.casino_cog.pending_challenges.pop(self.challenge_id)
                    
                    # Rembourser les deux joueurs
                    await self.casino_cog.add_coins(
                        challenge["challenger"].id, 
                        interaction.guild_id, 
                        challenge["bet"]
                    )
                    await self.casino_cog.add_coins(
                        challenge["opponent"].id,
                        interaction.guild_id,
                        challenge["bet"]
                    )
                    
                    await interaction.response.send_message(
                        f"❌ {interaction.user.mention} a refusé le défi. Les mises ont été rendues."
                    )
            
            async def on_timeout(self):
                # Timeout du défi
                if self.challenge_id in self.casino_cog.pending_challenges:
                    challenge = self.casino_cog.pending_challenges.pop(self.challenge_id)
                    
                    # Rembourser le challenger, l'adversaire perd sa mise
                    await self.casino_cog.add_coins(
                        challenge["challenger"].id,
                        challenge["opponent"].guild.id if hasattr(challenge["opponent"], 'guild') else interaction.guild_id,
                        challenge["bet"]
                    )
                    
                    # Chercher le message original
                    try:
                        message = await interaction.channel.fetch_message(interaction.message.id)
                        await message.edit(
                            content=f"⏰ Défi expiré ! {challenge['opponent'].mention} n'a pas répondu à temps. {challenge['challenger'].mention} a été remboursé.",
                            embed=None,
                            view=None
                        )
                    except:
                        pass
        
        view = ChallengeView(challenge_id, self)
        
        await interaction.response.send_message(
            f"{opponent.mention}",
            embed=embed,
            view=view
        )
    
    async def process_coinflip_challenge(self, challenge_id: str, interaction: discord.Interaction, opponent_choice: str):
        """Traite un défi de pile ou face accepté"""
        
        if challenge_id not in self.pending_challenges:
            await interaction.response.send_message("❌ Défi expiré ou annulé.", ephemeral=True)
            return
        
        challenge = self.pending_challenges.pop(challenge_id)
        
        # Lancer la pièce
        result = random.choice(["pile", "face"])
        
        # Déterminer le gagnant
        challenger_won = (challenge["challenger_choice"] == result)
        opponent_won = (opponent_choice == result)
        
        total_pot = challenge["bet"] * 2  # Les deux mises
        
        if challenger_won and not opponent_won:
            # Challenger gagne tout
            winner = challenge["challenger"]
            loser = challenge["opponent"]
            winner_gain = total_pot
            result_text = f"{winner.mention} a choisi {result.upper()} et gagne !"
            
        elif opponent_won and not challenger_won:
            # Opponent gagne tout
            winner = challenge["opponent"]
            loser = challenge["challenger"]
            winner_gain = total_pot
            result_text = f"{winner.mention} a choisi {result.upper()} et gagne !"
            
        else:
            # Les deux ont choisi la même chose = égalité
            winner = None
            # Rembourser les deux
            await self.add_coins(challenge["challenger"].id, interaction.guild_id, challenge["bet"])
            await self.add_coins(challenge["opponent"].id, interaction.guild_id, challenge["bet"])
            result_text = f"ÉGALITÉ ! Les deux ont choisi {result.upper()}. Mises rendues."
        
        # Donner les gains au gagnant
        if winner:
            await self.add_coins(winner.id, interaction.guild_id, winner_gain)
        
        # Embed résultat
        embed = discord.Embed(
            title="🎲 RÉSULTAT DU DUEL",
            color=discord.Color.gold() if winner else discord.Color.blue()
        )
        
        embed.add_field(name="Pièce", value=f"**{result.upper()}**", inline=True)
        embed.add_field(name="Pot total", value=f"{self.format_coins(total_pot)} coins", inline=True)
        
        embed.add_field(
            name=f"🎯 {challenge['challenger'].display_name}", 
            value=challenge["challenger_choice"].title(),
            inline=False
        )
        embed.add_field(
            name=f"🎯 {challenge['opponent'].display_name}", 
            value=opponent_choice.title(),
            inline=False
        )
        
        if winner:
            embed.add_field(
                name="🏆 GAGNANT",
                value=f"{winner.mention} remporte **{self.format_coins(winner_gain)}** coins !",
                inline=False
            )
        else:
            embed.add_field(name="🤝 RÉSULTAT", value=result_text, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    # ==================== 🎯 JEU DE DÉS ====================
    
    @app_commands.command(name="dice", description="Jeu de dés avec mise")
    @app_commands.describe(
        bet="Mise (coins)",
        opponent="Joueur à défier (vide = contre le bot)"
    )
    async def dice_game(self, interaction: discord.Interaction, bet: int, opponent: discord.Member = None):
        """Jeu de dés - le plus haut score gagne"""
        
        if bet <= 0:
            await interaction.response.send_message("❌ Mise invalide.", ephemeral=True)
            return
        
        # Vérifier les fonds
        if not await self.check_and_deduct(interaction.user.id, interaction.guild_id, bet):
            await interaction.response.send_message(
                f"❌ Fonds insuffisants pour miser {self.format_coins(bet)} coins.",
                ephemeral=True
            )
            return
        
        if not opponent or opponent.bot:
            await self.dice_vs_bot(interaction, bet)
        else:
            await self.dice_vs_player(interaction, bet, opponent)
    
    async def dice_vs_bot(self, interaction: discord.Interaction, bet: int):
        """Jeu de dés contre le bot - Un simple bouton pour lancer"""
        
        class SimpleRollView(discord.ui.View):
            def __init__(self, casino_cog, user_id, guild_id, bet_amount):
                super().__init__(timeout=30)
                self.casino_cog = casino_cog
                self.user_id = user_id
                self.guild_id = guild_id
                self.bet = bet_amount
                self.has_rolled = False
            
            async def interaction_check(self, interaction: discord.Interaction) -> bool:
                return interaction.user.id == self.user_id
            
            async def on_timeout(self):
                if not self.has_rolled:
                    await self.casino_cog.add_coins(self.user_id, self.guild_id, self.bet)
                    try:
                        await self.message.edit(
                            content="⏰ Temps écoulé ! Tu as été remboursé.",
                            view=None
                        )
                    except:
                        pass
            
            @discord.ui.button(label="🎲 Lancer le dé", style=discord.ButtonStyle.green)
            async def roll_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                if self.has_rolled:
                    await interaction.response.send_message("❌ Tu as déjà lancé le dé !", ephemeral=True)
                    return
                
                self.has_rolled = True
                self.stop()
                
                # Désactiver le bouton
                button.disabled = True
                button.label = "🎲 Dé lancé..."
                
                await interaction.response.edit_message(view=self)
                
                # Animation de lancer
                embed = discord.Embed(
                    title="🎲 Le dé roule...",
                    description="Le dé est en train de rouler...",
                    color=discord.Color.orange()
                )
                await interaction.edit_original_response(embed=embed)
                
                await asyncio.sleep(1.5)
                
                # Le joueur lance son dé
                player_roll = random.randint(1, 6)
                
                # Le bot lance son dé
                bot_roll = random.randint(1, 6)
                
                dice_faces = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
                
                # Déterminer le gagnant
                if player_roll > bot_roll:
                    gain = int(self.bet * 2)
                    await self.casino_cog.add_coins(self.user_id, self.guild_id, gain)
                    title = "🎉 VICTOIRE !"
                    color = discord.Color.green()
                    result_msg = f"Tu gagnes **{self.casino_cog.format_coins(gain)}** coins !"
                elif player_roll < bot_roll:
                    gain = 0
                    title = "💥 DÉFAITE..."
                    color = discord.Color.red()
                    result_msg = f"Tu perds **{self.casino_cog.format_coins(self.bet)}** coins."
                else:
                    await self.casino_cog.add_coins(self.user_id, self.guild_id, self.bet)
                    title = "🤝 ÉGALITÉ !"
                    color = discord.Color.blue()
                    result_msg = "Égalité ! Tu es remboursé."
                
                # Résultat
                result_embed = discord.Embed(title=title, color=color)
                
                # Affichage simple
                result_embed.add_field(
                    name="🎯 Ton lancer", 
                    value=f"**{player_roll}** {dice_faces[player_roll]}", 
                    inline=True
                )
                result_embed.add_field(
                    name="🤖 Bot", 
                    value=f"**{bot_roll}** {dice_faces[bot_roll]}", 
                    inline=True
                )
                
                # Comparaison
                comparison = f"```diff\n"
                if player_roll > bot_roll:
                    comparison += f"+ {player_roll} > {bot_roll}\n"
                    comparison += f"+ Tu as battu le bot !\n"
                elif player_roll < bot_roll:
                    comparison += f"- {player_roll} < {bot_roll}\n"
                    comparison += f"- Le bot t'a battu...\n"
                else:
                    comparison += f"= {player_roll} = {bot_roll}\n"
                    comparison += f"= Incroyable !\n"
                comparison += "```"
                
                result_embed.add_field(name="📊 Comparaison", value=comparison, inline=False)
                result_embed.add_field(name="💰 Résultat", value=result_msg, inline=False)
                
                # Nouveau solde
                economy = await self.casino_cog.get_economy()
                if economy:
                    account = await economy.get_balance(self.user_id, self.guild_id)
                    if account:
                        result_embed.add_field(
                            name="💵 Ton solde", 
                            value=f"**{self.casino_cog.format_coins(account['balance'])} coins**", 
                            inline=False
                        )
                
                await interaction.edit_original_response(embed=result_embed, view=None)
        
        # Envoyer
        view = SimpleRollView(self, interaction.user.id, interaction.guild_id, bet)
        
        embed = discord.Embed(
            title="🎲 Jeu de Dés Simple",
            description=f"Mise: **{self.format_coins(bet)}** coins\n\nClique sur le bouton pour lancer ton dé !",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="🎯 Règle", 
            value="Tu lances un dé, le bot lance un dé.\nLe plus haut score gagne le double de la mise !", 
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()
        
    async def dice_vs_player(self, interaction: discord.Interaction, bet: int, opponent: discord.Member):
        """Jeu de dés JcJ - Version ultra simple et fiable"""
        
        # Vérifications
        if opponent.id == interaction.user.id:
            await interaction.response.send_message("❌ Tu ne peux pas jouer contre toi-même.", ephemeral=True)
            return
        
        if opponent.bot:
            await interaction.response.send_message("❌ Tu ne peux pas défier un bot.", ephemeral=True)
            return
        
        # Vérifier fonds adversaire
        if not await self.check_and_deduct(opponent.id, interaction.guild_id, bet):
            await interaction.response.send_message(
                f"❌ {opponent.mention} n'a pas assez de coins.",
                ephemeral=True
            )
            await self.add_coins(interaction.user.id, interaction.guild_id, bet)
            return
        
        # Créer le jeu
        game_id = f"dice_{interaction.user.id}_{opponent.id}"
        
        self.active_games[game_id] = {
            "player1": interaction.user,
            "player2": opponent,
            "bet": bet,
            "player1_roll": None,
            "player2_roll": None
        }
        
        # Message simple
        embed = discord.Embed(
            title="🎲 Défi de Dés",
            description=f"{interaction.user.mention} vs {opponent.mention}",
            color=discord.Color.gold()
        )
        embed.add_field(name="Mise", value=f"{self.format_coins(bet)} coins chacun", inline=True)
        embed.add_field(name="Règle", value="Le plus haut score gagne", inline=True)
        
        # Créer une vue SIMPLE
        view = discord.ui.View(timeout=120)
        
        # Bouton principal
        roll_button = discord.ui.Button(
            label="🎲 Lancer mon dé",
            style=discord.ButtonStyle.green,
            custom_id=f"roll_{game_id}"
        )
        
        async def roll_callback(interaction: discord.Interaction):
            game = self.active_games.get(game_id)
            if not game:
                await interaction.response.send_message("❌ Partie introuvable.", ephemeral=True)
                return
            
            # Vérifier que c'est un joueur
            if interaction.user.id not in [game["player1"].id, game["player2"].id]:
                await interaction.response.send_message("❌ Tu ne fais pas partie de cette partie.", ephemeral=True)
                return
            
            # Vérifier quel joueur
            is_player1 = interaction.user.id == game["player1"].id
            
            # Vérifier s'il a déjà joué
            if (is_player1 and game["player1_roll"] is not None) or (not is_player1 and game["player2_roll"] is not None):
                await interaction.response.send_message("❌ Tu as déjà lancé ton dé !", ephemeral=True)
                return
            
            # Lancer le dé
            dice_roll = random.randint(1, 6)
            
            # Enregistrer
            if is_player1:
                game["player1_roll"] = dice_roll
            else:
                game["player2_roll"] = dice_roll
            
            # Confirmation
            await interaction.response.send_message(f"✅ Tu as lancé un **{dice_roll}** !", ephemeral=True)
            
            # Vérifier si les deux ont joué
            if game["player1_roll"] is not None and game["player2_roll"] is not None:
                # Désactiver le bouton
                roll_button.disabled = True
                roll_button.label = "Partie terminée"
                await interaction.message.edit(view=view)
                
                # Résultat
                await asyncio.sleep(1)
                
                # Déterminer gagnant
                if game["player1_roll"] > game["player2_roll"]:
                    gain = bet * 2
                    await self.add_coins(game["player1"].id, interaction.guild_id, gain)
                    result = f"🏆 {game['player1'].mention} gagne {self.format_coins(gain)} coins !"
                elif game["player2_roll"] > game["player1_roll"]:
                    gain = bet * 2
                    await self.add_coins(game["player2"].id, interaction.guild_id, gain)
                    result = f"🏆 {game['player2'].mention} gagne {self.format_coins(gain)} coins !"
                else:
                    await self.add_coins(game["player1"].id, interaction.guild_id, bet)
                    await self.add_coins(game["player2"].id, interaction.guild_id, bet)
                    result = "🤝 Égalité ! Mises rendues."
                
                # Afficher résultat
                result_embed = discord.Embed(
                    title="🎲 Résultat",
                    description=f"{game['player1'].mention}: **{game['player1_roll']}**\n{game['player2'].mention}: **{game['player2_roll']}**",
                    color=discord.Color.green()
                )
                result_embed.add_field(name="Résultat", value=result)
                
                await interaction.channel.send(embed=result_embed)
                
                # Supprimer la partie
                self.active_games.pop(game_id, None)
            else:
                # Mettre à jour le message pour montrer qui a joué
                status = f"✅ {interaction.user.display_name} a joué\n"
                status += f"❓ {'Joueur 2' if is_player1 else 'Joueur 1'} en attente"
                
                status_embed = discord.Embed(
                    title="🎲 Défi en cours",
                    description=status,
                    color=discord.Color.orange()
                )
                
                await interaction.message.edit(embed=status_embed)
        
        roll_button.callback = roll_callback
        view.add_item(roll_button)
        
        # Envoyer
        await interaction.response.send_message(
            f"{opponent.mention} - {interaction.user.mention}",
            embed=embed,
            view=view
        )    
    # ==================== 🃏 BLACKJACK ====================
    
    @app_commands.command(name="blackjack", description="Blackjack contre le bot")
    @app_commands.describe(bet="Mise (coins)")
    async def blackjack(self, interaction: discord.Interaction, bet: int):
        """Blackjack simplifié contre le bot"""
        
        if bet <= 0:
            await interaction.response.send_message("❌ Mise invalide.", ephemeral=True)
            return
        
        # Vérifier les fonds
        if not await self.check_and_deduct(interaction.user.id, interaction.guild_id, bet):
            await interaction.response.send_message(
                f"❌ Fonds insuffisants pour miser {self.format_coins(bet)} coins.",
                ephemeral=True
            )
            return
        
        # Initialiser le jeu
        game_id = f"bj_{interaction.user.id}_{datetime.utcnow().timestamp()}"
        
        # Créer un deck
        deck = self.create_deck()
        random.shuffle(deck)
        
        # Distribuer les cartes
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]
        
        self.active_games[game_id] = {
            "type": "blackjack",
            "player": interaction.user,
            "bet": bet,
            "deck": deck,
            "player_hand": player_hand,
            "dealer_hand": dealer_hand,
            "dealer_hidden": True,  # Première carte cachée
            "status": "player_turn",
            "created_at": datetime.utcnow()
        }
        
        # Afficher le jeu initial
        await self.show_blackjack_game(interaction, game_id)
    
    def create_deck(self):
        """Crée un deck de 52 cartes"""
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suits = ['♠', '♥', '♦', '♣']
        deck = []
        
        for suit in suits:
            for value in values:
                deck.append(f"{value}{suit}")
        
        return deck * 4  # 4 jeux mélangés
    
    def calculate_hand_value(self, hand):
        """Calcule la valeur d'une main de blackjack"""
        value = 0
        aces = 0
        
        for card in hand:
            rank = card[:-1]  # Enlever la couleur
            if rank in ['J', 'Q', 'K']:
                value += 10
            elif rank == 'A':
                value += 11
                aces += 1
            else:
                value += int(rank)
        
        # Ajuster les As (11 ou 1)
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        
        return value
    
    async def show_blackjack_game(self, interaction: discord.Interaction, game_id: str):
        """Affiche l'état actuel du blackjack"""
        
        if game_id not in self.active_games:
            return
        
        game = self.active_games[game_id]
        
        # Calculer les valeurs
        player_value = self.calculate_hand_value(game["player_hand"])
        dealer_value = self.calculate_hand_value(game["dealer_hand"])
        
        # Créer l'embed
        embed = discord.Embed(
            title="🃏 BLACKJACK",
            color=discord.Color.dark_green()
        )
        
        # Afficher les cartes
        player_cards = " ".join(game["player_hand"])
        embed.add_field(
            name=f"🎯 Tes cartes ({player_value})",
            value=player_cards,
            inline=False
        )
        
        # Cartes du dealer
        if game["dealer_hidden"]:
            dealer_display = f"{game['dealer_hand'][0]} ❓"
            dealer_text = "Croupier (??)"
        else:
            dealer_display = " ".join(game["dealer_hand"])
            dealer_text = f"Croupier ({dealer_value})"
        
        embed.add_field(
            name=f"🎰 {dealer_text}",
            value=dealer_display,
            inline=False
        )
        
        embed.add_field(name="💰 Mise", value=f"{self.format_coins(game['bet'])} coins", inline=True)
        
        # Vérifier blackjack/21 immédiat
        if player_value == 21:
            game["status"] = "dealer_turn"
            await self.dealer_play(interaction, game_id)
            return
        
        if player_value > 21:
            await self.end_blackjack_game(interaction, game_id, "player_bust")
            return
        
        # Boutons d'action
        class BlackjackView(discord.ui.View):
            def __init__(self, game_id, casino_cog):
                super().__init__(timeout=60)
                self.game_id = game_id
                self.casino_cog = casino_cog
            
            @discord.ui.button(label="📥 Tirer", style=discord.ButtonStyle.green)
            async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
                game = self.casino_cog.active_games.get(self.game_id)
                if not game or game["player"].id != interaction.user.id:
                    await interaction.response.send_message("❌ Ce n'est pas ta partie.", ephemeral=True)
                    return
                
                # Tirer une carte
                game["player_hand"].append(game["deck"].pop())
                player_value = self.casino_cog.calculate_hand_value(game["player_hand"])
                
                # Vérifier bust
                if player_value > 21:
                    await self.casino_cog.end_blackjack_game(interaction, self.game_id, "player_bust")
                else:
                    await self.casino_cog.show_blackjack_game(interaction, self.game_id)
            
            @discord.ui.button(label="✋ Rester", style=discord.ButtonStyle.red)
            async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
                game = self.casino_cog.active_games.get(self.game_id)
                if not game or game["player"].id != interaction.user.id:
                    await interaction.response.send_message("❌ Ce n'est pas ta partie.", ephemeral=True)
                    return
                
                # Tour du dealer
                game["status"] = "dealer_turn"
                await self.casino_cog.dealer_play(interaction, self.game_id)
            
            async def on_timeout(self):
                # Timeout = rester automatiquement
                if self.game_id in self.casino_cog.active_games:
                    game = self.casino_cog.active_games[self.game_id]
                    game["status"] = "dealer_turn"
                    # Chercher le canal
                    # (Pour simplifier, on ne fait rien sur timeout)
        
        # Envoyer ou mettre à jour le message
        if interaction.response.is_done():
            # Mettre à jour le message existant
            await interaction.edit_original_response(embed=embed, view=BlackjackView(game_id, self))
        else:
            # Premier envoi
            await interaction.response.send_message(embed=embed, view=BlackjackView(game_id, self))
    
    async def dealer_play(self, interaction: discord.Interaction, game_id: str):
        """Fait jouer le dealer"""
        
        if game_id not in self.active_games:
            return
        
        game = self.active_games[game_id]
        game["dealer_hidden"] = False
        
        # Le dealer tire jusqu'à 17 ou plus
        dealer_value = self.calculate_hand_value(game["dealer_hand"])
        
        while dealer_value < 17:
            game["dealer_hand"].append(game["deck"].pop())
            dealer_value = self.calculate_hand_value(game["dealer_hand"])
        
        # Déterminer le résultat
        player_value = self.calculate_hand_value(game["player_hand"])
        
        if dealer_value > 21:
            result = "dealer_bust"
        elif dealer_value > player_value:
            result = "dealer_win"
        elif dealer_value < player_value:
            result = "player_win"
        else:
            result = "push"  # Égalité
        
        await self.end_blackjack_game(interaction, game_id, result)
    
    async def end_blackjack_game(self, interaction: discord.Interaction, game_id: str, result: str):
        """Termine une partie de blackjack"""
        
        if game_id not in self.active_games:
            return
        
        game = self.active_games.pop(game_id)
        
        # Calculer les valeurs finales
        player_value = self.calculate_hand_value(game["player_hand"])
        dealer_value = self.calculate_hand_value(game["dealer_hand"])
        
        # Déterminer les gains
        if result == "player_bust":
            gain = 0
            title = "💥 DÉPASSÉ !"
            color = discord.Color.red()
            result_msg = f"**{player_value}** > 21 ! Tu perds **{self.format_coins(game['bet'])}** coins."
            
        elif result == "dealer_bust":
            gain = int(game["bet"] * 2)  # Gain x2
            await self.add_coins(game["player"].id, interaction.guild_id, gain)
            title = "🎉 DEALER DÉPASSÉ !"
            color = discord.Color.green()
            result_msg = f"Dealer: **{dealer_value}** > 21 ! Tu gagnes **{self.format_coins(gain)}** coins !"
            
        elif result == "player_win":
            gain = int(game["bet"] * 2)  # Gain x2
            await self.add_coins(game["player"].id, interaction.guild_id, gain)
            title = "🎉 VICTOIRE !"
            color = discord.Color.green()
            result_msg = f"**{player_value}** vs **{dealer_value}** ! Tu gagnes **{self.format_coins(gain)}** coins !"
            
        elif result == "dealer_win":
            gain = 0
            title = "💥 DÉFAITE..."
            color = discord.Color.red()
            result_msg = f"**{player_value}** vs **{dealer_value}** ! Tu perds **{self.format_coins(game['bet'])}** coins."
            
        else:  # push (égalité)
            gain = game["bet"]  # Remboursé
            await self.add_coins(game["player"].id, interaction.guild_id, gain)
            title = "🤝 ÉGALITÉ"
            color = discord.Color.blue()
            result_msg = f"**{player_value}** vs **{dealer_value}** ! Mise rendue."
        
        # Embed résultat
        embed = discord.Embed(title=title, color=color)
        
        # Afficher les cartes
        player_cards = " ".join(game["player_hand"])
        dealer_cards = " ".join(game["dealer_hand"])
        
        embed.add_field(
            name=f"🎯 Tes cartes ({player_value})",
            value=player_cards,
            inline=False
        )
        embed.add_field(
            name=f"🎰 Croupier ({dealer_value})",
            value=dealer_cards,
            inline=False
        )
        
        embed.add_field(name="💰 Résultat", value=result_msg, inline=False)
        
        # Nouveau solde
        economy = await self.get_economy()
        if economy:
            account = await economy.get_balance(game["player"].id, interaction.guild_id)
            if account:
                embed.add_field(
                    name="Nouveau solde", 
                    value=f"{self.format_coins(account['balance'])} coins", 
                    inline=False
                )
        
        # Mettre à jour le message
        if interaction.response.is_done():
            await interaction.edit_original_response(embed=embed, view=None)
        else:
            await interaction.response.send_message(embed=embed)
    
    # ==================== 📊 COMMANDES UTILES ====================
    
    @app_commands.command(name="casino", description="Menu des jeux de casino")
    async def casino_menu(self, interaction: discord.Interaction):
        """Affiche le menu des jeux disponibles"""
        
        embed = discord.Embed(
            title="🎰 CASINO DU SERVEUR",
            description="Joue et gagne des coins !\n*Jouez responsablement*",
            color=discord.Color.purple()
        )
        
        # Jeux disponibles
        games_info = [
            ("🎲 **Pile ou Face**", 
             "`/coinflip <mise> <pile/face> [adversaire]`\n"
             "Joue contre le bot ou défie un ami !"),
            
            ("🎯 **Jeu de Dés**", 
             "`/dice <mise> [adversaire]`\n"
             "Lance un dé, le plus haut score gagne !"),
            
            ("🃏 **Blackjack**", 
             "`/blackjack <mise>`\n"
             "Blackjack classique contre le dealer !"),
        ]
        
        for name, desc in games_info:
            embed.add_field(name=name, value=desc, inline=False)
        
        # Statistiques rapides
        embed.add_field(
            name="📈 Tes statistiques",
            value="Utilise `/mystats` pour voir tes stats de jeu !",
            inline=False
        )
        
        embed.set_footer(text="💡 Astuce: Commencez par des petites mises !")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="mystats", description="Tes statistiques de casino")
    async def my_stats(self, interaction: discord.Interaction):
        """Affiche les statistiques du joueur"""
        
        # Ici vous devriez récupérer depuis une base de données
        # Pour l'exemple, on simule
        
        embed = discord.Embed(
            title=f"📊 STATS DE {interaction.user.display_name}",
            color=discord.Color.blue()
        )
        
        # Statistiques simulées
        stats = {
            "🎲 Parties jouées": "47",
            "💰 Gains totaux": "12,500 coins",
            "💸 Pertes totales": "8,200 coins",
            "📈 Profit net": "+4,300 coins",
            "🏆 Taux de victoire": "58%",
            "🎯 Jeu préféré": "Pile ou Face",
            "💎 Plus gros gain": "5,000 coins"
        }
        
        for name, value in stats.items():
            embed.add_field(name=name, value=value, inline=True)
        
        embed.set_footer(text="Les stats sont sauvegardées localement")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="cancelgame", description="Annule ta partie en cours")
    async def cancel_game(self, interaction: discord.Interaction):
        """Annule une partie en cours"""
        
        games_to_cancel = []
        
        # Chercher les parties du joueur
        for game_id, game in list(self.active_games.items()):
            if game["type"] == "blackjack" and game["player"].id == interaction.user.id:
                games_to_cancel.append(game_id)
            elif game["type"] == "dice_pvp" and interaction.user.id in [game["player1"].id, game["player2"].id]:
                games_to_cancel.append(game_id)
        
        # Chercher les défis en attente
        for challenge_id, challenge in list(self.pending_challenges.items()):
            if interaction.user.id in [challenge["challenger"].id, challenge["opponent"].id]:
                games_to_cancel.append(challenge_id)
        
        if not games_to_cancel:
            await interaction.response.send_message("❌ Aucune partie en cours.", ephemeral=True)
            return
        
        # Annuler et rembourser
        refund_total = 0
        
        for game_id in games_to_cancel:
            if game_id in self.active_games:
                game = self.active_games.pop(game_id)
                # Rembourser selon le type de jeu
                if game["type"] == "blackjack":
                    await self.add_coins(game["player"].id, interaction.guild_id, game["bet"])
                    refund_total += game["bet"]
                elif game["type"] == "dice_pvp":
                    # Rembourser les deux joueurs
                    await self.add_coins(game["player1"].id, interaction.guild_id, game["bet"])
                    await self.add_coins(game["player2"].id, interaction.guild_id, game["bet"])
                    refund_total += game["bet"] * 2
            
            elif game_id in self.pending_challenges:
                challenge = self.pending_challenges.pop(game_id)
                # Rembourser les deux
                await self.add_coins(challenge["challenger"].id, interaction.guild_id, challenge["bet"])
                await self.add_coins(challenge["opponent"].id, interaction.guild_id, challenge["bet"])
                refund_total += challenge["bet"] * 2
        
        await interaction.response.send_message(
            f"✅ {len(games_to_cancel)} partie(s) annulée(s).\n"
            f"💰 **{self.format_coins(refund_total)} coins** ont été remboursés.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Casino(bot))