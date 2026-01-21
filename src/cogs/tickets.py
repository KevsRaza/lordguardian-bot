"""
Système de tickets de support
"""
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from core.logger import setup_logger

logger = setup_logger("Tickets")

class TicketButton(discord.ui.Button):
    """Bouton pour créer un ticket"""
    
    def __init__(self):
        super().__init__(
            label="Créer un ticket",
            style=discord.ButtonStyle.green,
            emoji="🎫",
            custom_id="ticket_create_button"  # Persistant au redémarrage
        )
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TicketModal())

class TicketModal(discord.ui.Modal, title="Créer un ticket"):
    """Modal pour créer un ticket"""
    
    subject = discord.ui.TextInput(
        label="Sujet",
        placeholder="Ex: Problème de connexion",
        max_length=100,
        required=True
    )
    
    description = discord.ui.TextInput(
        label="Description",
        placeholder="Décris ton problème en détail...",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        bot = interaction.client
        
        try:
            await bot.db.connect()
            
            async with bot.db.connection.cursor() as cursor:
                # Vérifier si l'utilisateur a déjà un ticket ouvert
                await cursor.execute(
                    """SELECT channel_id FROM tickets 
                    WHERE guild_id = ? AND user_id = ? AND status = 'open'""",
                    (interaction.guild_id, interaction.user.id)
                )
                existing_ticket = await cursor.fetchone()
                
                if existing_ticket:
                    channel = interaction.guild.get_channel(existing_ticket[0])
                    if channel:
                        await interaction.followup.send(
                            f"❌ Tu as déjà un ticket ouvert: {channel.mention}",
                            ephemeral=True
                        )
                        return
                
                # Créer le canal du ticket
                category = discord.utils.get(interaction.guild.categories, name="Tickets")
                if not category:
                    category = await interaction.guild.create_category("Tickets")
                
                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
                
                # Ajouter les modérateurs
                for role in interaction.guild.roles:
                    if role.permissions.manage_messages:
                        overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                
                ticket_channel = await category.create_text_channel(
                    name=f"ticket-{interaction.user.name}",
                    overwrites=overwrites
                )
                
                # Sauvegarder dans la base de données
                now = datetime.utcnow()
                await cursor.execute(
                    """INSERT INTO tickets 
                    (guild_id, channel_id, user_id, category, description, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        interaction.guild_id,
                        ticket_channel.id,
                        interaction.user.id,
                        str(self.subject.value),
                        str(self.description.value),
                        "open",
                        now
                    )
                )
                
                await bot.db.connection.commit()
                
                # Créer l'embed du ticket
                embed = discord.Embed(
                    title=f"🎫 Ticket de {interaction.user.display_name}",
                    color=discord.Color.green()
                )
                embed.add_field(name="Sujet", value=self.subject.value, inline=False)
                embed.add_field(name="Description", value=self.description.value, inline=False)
                embed.add_field(name="Créé le", value=f"<t:{int(now.timestamp())}:F>", inline=False)
                embed.set_footer(text=f"ID: {interaction.user.id}")
                
                # Ajouter un bouton pour fermer le ticket
                view = TicketControlView()
                
                await ticket_channel.send(
                    content=f"{interaction.user.mention}",
                    embed=embed,
                    view=view
                )
                
                await interaction.followup.send(
                    f"✅ Ticket créé: {ticket_channel.mention}",
                    ephemeral=True
                )
                
                logger.info(f"Ticket créé par {interaction.user.name} dans {interaction.guild.name}")
                
        except Exception as e:
            logger.error(f"Erreur création ticket: {e}")
            await interaction.followup.send(
                f"❌ Erreur lors de la création du ticket: {str(e)[:100]}",
                ephemeral=True
            )

class TicketControlView(discord.ui.View):
    """Vue pour contrôler le ticket"""
    
    def __init__(self):
        super().__init__(timeout=None)  # Pas de timeout
    
    @discord.ui.button(
        label="Fermer le ticket", 
        style=discord.ButtonStyle.red, 
        emoji="🔒",
        custom_id="ticket_close_button"  # Persistant au redémarrage
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Ferme le ticket"""
        bot = interaction.client
        
        try:
            await bot.db.connect()
            
            async with bot.db.connection.cursor() as cursor:
                # Récupérer le ticket
                await cursor.execute(
                    "SELECT * FROM tickets WHERE channel_id = ? AND status = 'open'",
                    (interaction.channel_id,)
                )
                ticket = await cursor.fetchone()
                
                if not ticket:
                    await interaction.response.send_message(
                        "❌ Ce ticket est déjà fermé ou introuvable.", 
                        ephemeral=True
                    )
                    return
                
                # Mettre à jour le statut
                now = datetime.utcnow()
                await cursor.execute(
                    """UPDATE tickets 
                    SET status = 'closed', closed_at = ?, closed_by = ? 
                    WHERE channel_id = ?""",
                    (now, interaction.user.id, interaction.channel_id)
                )
                
                await bot.db.connection.commit()
                
                embed = discord.Embed(
                    title="🔒 Ticket fermé",
                    description=f"Ce ticket a été fermé par {interaction.user.mention}.",
                    color=discord.Color.red()
                )
                embed.add_field(
                    name="⏱️ Actions",
                    value="Ce canal sera supprimé dans 10 secondes.",
                    inline=False
                )
                embed.set_footer(text=f"Fermé le {now.strftime('%d/%m/%Y à %H:%M')}")
                
                await interaction.response.send_message(embed=embed)
                
                logger.info(f"Ticket {interaction.channel.name} fermé par {interaction.user.name}")
                
                # Attendre avant de supprimer
                await interaction.channel.delete(delay=10)
                
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Je n'ai pas la permission de supprimer ce canal.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Erreur fermeture ticket: {e}")
            await interaction.response.send_message(
                f"❌ Erreur lors de la fermeture du ticket: {str(e)[:100]}",
                ephemeral=True
            )

class TicketPanelView(discord.ui.View):
    """Vue pour le panel de tickets"""
    
    def __init__(self):
        super().__init__(timeout=None)  # Pas de timeout
        self.add_item(TicketButton())

class Tickets(commands.Cog):
    """Système de tickets de support"""
    
    def __init__(self, bot):
        self.bot = bot
        # Rendre les vues persistantes au redémarrage du bot
        self.bot.add_view(TicketPanelView())
        self.bot.add_view(TicketControlView())
        logger.info("Système de tickets chargé avec vues persistantes")
    
    @app_commands.command(name="ticket-panel", description="Crée un panel pour ouvrir des tickets")
    @app_commands.describe(channel="Le canal où envoyer le panel (optionnel)")
    @app_commands.default_permissions(administrator=True)
    async def ticket_panel(
        self, 
        interaction: discord.Interaction, 
        channel: discord.TextChannel = None
    ):
        """Crée un panel pour ouvrir des tickets"""
        target_channel = channel or interaction.channel
        
        embed = discord.Embed(
            title="🎫 Support - Créer un ticket",
            description=(
                "Besoin d'aide ? Clique sur le bouton ci-dessous pour créer un ticket.\n\n"
                "**Quand créer un ticket ?**\n"
                "• Pour signaler un problème\n"
                "• Pour poser une question\n"
                "• Pour demander de l'aide\n"
                "• Pour contacter le staff\n\n"
                "Un membre du staff te répondra dès que possible."
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Notre équipe est là pour t'aider !")
        
        view = TicketPanelView()
        
        try:
            await target_channel.send(embed=embed, view=view)
            
            if channel:
                await interaction.response.send_message(
                    f"✅ Panel de tickets créé dans {target_channel.mention}",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "✅ Panel de tickets créé !",
                    ephemeral=True
                )
            
            logger.info(f"Panel de tickets créé dans #{target_channel.name} par {interaction.user.name}")
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Je n'ai pas la permission d'envoyer des messages dans ce canal.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Erreur création panel: {e}")
            await interaction.response.send_message(
                f"❌ Erreur: {str(e)[:100]}",
                ephemeral=True
            )
    
    @app_commands.command(name="ticket-close", description="Ferme le ticket actuel")
    @app_commands.describe(reason="Raison de la fermeture (optionnel)")
    async def ticket_close(self, interaction: discord.Interaction, reason: str = None):
        """Ferme le ticket actuel"""
        try:
            await self.bot.db.connect()
            
            async with self.bot.db.connection.cursor() as cursor:
                # Vérifier si c'est un ticket ouvert
                await cursor.execute(
                    """SELECT * FROM tickets 
                    WHERE channel_id = ? AND status = 'open'""",
                    (interaction.channel_id,)
                )
                ticket = await cursor.fetchone()
                
                if not ticket:
                    await interaction.response.send_message(
                        "❌ Ce canal n'est pas un ticket ou il est déjà fermé.",
                        ephemeral=True
                    )
                    return
                
                # Fermer le ticket
                now = datetime.utcnow()
                await cursor.execute(
                    """UPDATE tickets 
                    SET status = 'closed', closed_at = ?, closed_by = ? 
                    WHERE channel_id = ?""",
                    (now, interaction.user.id, interaction.channel_id)
                )
                
                await self.bot.db.connection.commit()
                
                embed = discord.Embed(
                    title="🔒 Ticket fermé",
                    description=f"Ce ticket a été fermé par {interaction.user.mention}.",
                    color=discord.Color.red()
                )
                
                if reason:
                    embed.add_field(name="📝 Raison", value=reason, inline=False)
                
                embed.add_field(
                    name="⏱️ Actions",
                    value="Ce canal sera supprimé dans 10 secondes.",
                    inline=False
                )
                
                await interaction.response.send_message(embed=embed)
                
                logger.info(f"Ticket {interaction.channel.name} fermé par {interaction.user.name}")
                
                await interaction.channel.delete(delay=10)
                
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Je n'ai pas la permission de supprimer ce canal.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Erreur fermeture ticket via commande: {e}")
            await interaction.response.send_message(
                f"❌ Erreur: {str(e)[:100]}",
                ephemeral=True
            )
    
    @app_commands.command(name="tickets", description="Liste tous les tickets")
    @app_commands.describe(
        status="Filtrer par statut",
        user="Filtrer par utilisateur"
    )
    @app_commands.default_permissions(manage_messages=True)
    async def tickets_list(
        self, 
        interaction: discord.Interaction, 
        status: str = None,
        user: discord.Member = None
    ):
        """Liste tous les tickets du serveur"""
        try:
            await self.bot.db.connect()
            
            async with self.bot.db.connection.cursor() as cursor:
                # Construire la requête
                query = "SELECT * FROM tickets WHERE guild_id = ?"
                params = [interaction.guild_id]
                
                if status:
                    query += " AND status = ?"
                    params.append(status)
                
                if user:
                    query += " AND user_id = ?"
                    params.append(user.id)
                
                query += " ORDER BY created_at DESC LIMIT 25"
                
                await cursor.execute(query, tuple(params))
                tickets = await cursor.fetchall()
                
                if not tickets:
                    await interaction.response.send_message(
                        "📋 Aucun ticket trouvé.",
                        ephemeral=True
                    )
                    return
                
                embed = discord.Embed(
                    title=f"🎫 Tickets de {interaction.guild.name}",
                    color=discord.Color.blue()
                )
                
                open_tickets = [t for t in tickets if t[5] == "open"]  # status
                closed_tickets = [t for t in tickets if t[5] == "closed"]
                
                embed.add_field(
                    name="📊 Statistiques",
                    value=f"**Ouverts:** {len(open_tickets)}\n**Fermés:** {len(closed_tickets)}\n**Total:** {len(tickets)}",
                    inline=False
                )
                
                if open_tickets:
                    tickets_text = []
                    for t in open_tickets[:10]:
                        channel = interaction.guild.get_channel(t[2])  # channel_id
                        user_obj = interaction.guild.get_member(t[3])  # user_id
                        
                        if channel and user_obj:
                            tickets_text.append(
                                f"{channel.mention} - {user_obj.mention} - <t:{int(t[7].timestamp()) if isinstance(t[7], datetime) else 0}:R>"
                            )
                    
                    if tickets_text:
                        embed.add_field(
                            name="🟢 Tickets ouverts",
                            value="\n".join(tickets_text),
                            inline=False
                        )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
        except Exception as e:
            logger.error(f"Erreur liste tickets: {e}")
            await interaction.response.send_message(
                f"❌ Erreur: {str(e)[:100]}",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(Tickets(bot))