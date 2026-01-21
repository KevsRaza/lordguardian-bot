"""
Cog d'utilitaires pour le bot
"""
import discord
from discord.ext import commands
from discord import app_commands
from core.logger import setup_logger
from core.embeds import Embeds  # ← AJOUT
import datetime
import random

logger = setup_logger("Utilities")

class Utilities(commands.Cog):
    """Commandes utilitaires"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="serverinfo")
    async def server_info(self, ctx):
        """Affiche les informations du serveur"""
        # ← UTILISER L'EMBED STANDARDISÉ
        embed = Embeds.server_info(ctx.guild)
        await ctx.send(embed=embed)
    
    @commands.command(name="userinfo")
    async def user_info(self, ctx, member: discord.Member = None):
        """Affiche les informations d'un utilisateur"""
        member = member or ctx.author
        
        # ← UTILISER L'EMBED STANDARDISÉ
        embed = Embeds.member_info(member)
        await ctx.send(embed=embed)
    
    @commands.command(name="avatar")
    async def get_avatar(self, ctx, member: discord.Member = None):
        """Affiche l'avatar d'un utilisateur"""
        member = member or ctx.author
        
        # ← CRÉER UN EMBED SIMPLE AVEC create_base_embed
        embed = Embeds.create_base_embed(
            title=f"Avatar de {member.display_name}",
            description=f"[Télécharger en haute qualité]({member.display_avatar.url})",
            color=member.color.value if member.color != discord.Color.default() else Embeds.EmbedColors.INFO,
            image=member.display_avatar.url
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="poll")
    @commands.has_permissions(manage_messages=True)
    async def create_poll(self, ctx, *, question: str):
        """
        Crée un sondage
        
        Usage: !poll "Question du sondage"
        """
        # ← UTILISER L'EMBED STANDARDISÉ
        embed = Embeds.create_base_embed(
            title="📊 Sondage",
            description=question,
            color=0x9B59B6  # Violet
        )
        embed.set_footer(text=f"Sondage créé par {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        
        message = await ctx.send(embed=embed)
        await message.add_reaction("✅")
        await message.add_reaction("❌")
        
        # Supprimer le message de commande pour garder propre
        try:
            await ctx.message.delete()
        except:
            pass
    
    @commands.command(name="8ball")
    async def eight_ball(self, ctx, *, question: str):
        """
        Pose une question à la boule magique
        
        Usage: !8ball [question]
        """
        responses = [
            "C'est certain.",
            "Sans aucun doute.",
            "Oui, définitivement.",
            "Vous pouvez compter dessus.",
            "D'après moi, oui.",
            "Probablement.",
            "Les perspectives sont bonnes.",
            "Oui.",
            "Les signes indiquent que oui.",
            "Réponse floue, réessayez.",
            "Redemandez plus tard.",
            "Mieux vaut ne pas vous le dire maintenant.",
            "Impossible de prédire maintenant.",
            "Concentrez-vous et redemandez.",
            "Ne comptez pas dessus.",
            "Ma réponse est non.",
            "Mes sources disent non.",
            "Les perspectives ne sont pas bonnes.",
            "Très douteux."
        ]
        
        answer = random.choice(responses)
        
        # ← UTILISER L'EMBED STANDARDISÉ
        embed = Embeds.create_base_embed(
            title="🎱 Boule Magique",
            description=f"**Question :** {question}\n\n**Réponse :** {answer}",
            color=0x2C2F33  # Gris foncé
        )
        embed.set_footer(text=f"Demandé par {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="ping")
    async def ping_command(self, ctx):
        """Affiche la latence du bot"""
        latency = round(self.bot.latency * 1000)
        
        # Choisir la couleur selon la latence
        if latency < 100:
            color = Embeds.EmbedColors.SUCCESS
            status = "Excellente"
        elif latency < 200:
            color = Embeds.EmbedColors.INFO
            status = "Bonne"
        elif latency < 300:
            color = Embeds.EmbedColors.WARNING
            status = "Moyenne"
        else:
            color = Embeds.EmbedColors.ERROR
            status = "Mauvaise"
        
        # ← UTILISER L'EMBED STANDARDISÉ
        embed = Embeds.create_base_embed(
            title="🏓 Pong !",
            description=f"**Latence :** {latency}ms\n**Qualité :** {status}",
            color=color
        )
        
        await ctx.send(embed=embed)
    
    # BONUS : Ajouter des versions slash commands
    @app_commands.command(name="serverinfo", description="Affiche les informations du serveur")
    async def serverinfo_slash(self, interaction: discord.Interaction):
        """Version slash command de serverinfo"""
        embed = Embeds.server_info(interaction.guild)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="userinfo", description="Affiche les informations d'un utilisateur")
    @app_commands.describe(member="L'utilisateur dont afficher les informations")
    async def userinfo_slash(self, interaction: discord.Interaction, member: discord.Member = None):
        """Version slash command de userinfo"""
        member = member or interaction.user
        embed = Embeds.member_info(member)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="avatar", description="Affiche l'avatar d'un utilisateur")
    @app_commands.describe(member="L'utilisateur dont afficher l'avatar")
    async def avatar_slash(self, interaction: discord.Interaction, member: discord.Member = None):
        """Version slash command de avatar"""
        member = member or interaction.user
        
        embed = Embeds.create_base_embed(
            title=f"Avatar de {member.display_name}",
            description=f"[Télécharger en haute qualité]({member.display_avatar.url})",
            color=member.color.value if member.color != discord.Color.default() else Embeds.EmbedColors.INFO,
            image=member.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="ping", description="Affiche la latence du bot")
    async def ping_slash(self, interaction: discord.Interaction):
        """Version slash command de ping"""
        latency = round(self.bot.latency * 1000)
        
        if latency < 100:
            color = Embeds.EmbedColors.SUCCESS
            status = "Excellente"
        elif latency < 200:
            color = Embeds.EmbedColors.INFO
            status = "Bonne"
        elif latency < 300:
            color = Embeds.EmbedColors.WARNING
            status = "Moyenne"
        else:
            color = Embeds.EmbedColors.ERROR
            status = "Mauvaise"
        
        embed = Embeds.create_base_embed(
            title="🏓 Pong !",
            description=f"**Latence :** {latency}ms\n**Qualité :** {status}",
            color=color
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Utilities(bot))