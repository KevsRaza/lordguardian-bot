"""
Commandes d'administration du bot
"""
import discord
from discord import app_commands
from discord.ext import commands
from typing import Literal
from core.embeds import Embeds  # ← AJOUT

class Admin(commands.Cog):
    """Commandes d'administration du bot (owner only)"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_check(self, ctx):
        """Vérifie que l'utilisateur est le propriétaire du bot"""
        return await self.bot.is_owner(ctx.author)
    
    @app_commands.command(name="reload", description="Recharge un cog")
    @app_commands.describe(cog="Le nom du cog à recharger")
    async def reload(self, interaction: discord.Interaction, cog: str):
        """Recharge un cog du bot"""
        if not await self.bot.is_owner(interaction.user):
            embed = Embeds.error(
                "Accès refusé",
                "Cette commande est réservée au propriétaire du bot."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            embed = Embeds.success(
                "Cog rechargé",
                f"Le cog `{cog}` a été rechargé avec succès !"
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = Embeds.error(
                "Erreur de rechargement",
                f"Impossible de recharger le cog `{cog}`:\n```{str(e)[:200]}```"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="load", description="Charge un cog")
    @app_commands.describe(cog="Le nom du cog à charger")
    async def load(self, interaction: discord.Interaction, cog: str):
        """Charge un cog du bot"""
        if not await self.bot.is_owner(interaction.user):
            embed = Embeds.error(
                "Accès refusé",
                "Cette commande est réservée au propriétaire du bot."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            embed = Embeds.success(
                "Cog chargé",
                f"Le cog `{cog}` a été chargé avec succès !"
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = Embeds.error(
                "Erreur de chargement",
                f"Impossible de charger le cog `{cog}`:\n```{str(e)[:200]}```"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="unload", description="Décharge un cog")
    @app_commands.describe(cog="Le nom du cog à décharger")
    async def unload(self, interaction: discord.Interaction, cog: str):
        """Décharge un cog du bot"""
        if not await self.bot.is_owner(interaction.user):
            embed = Embeds.error(
                "Accès refusé",
                "Cette commande est réservée au propriétaire du bot."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            embed = Embeds.success(
                "Cog déchargé",
                f"Le cog `{cog}` a été déchargé avec succès !"
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = Embeds.error(
                "Erreur de déchargement",
                f"Impossible de décharger le cog `{cog}`:\n```{str(e)[:200]}```"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="sync", description="Synchronise les commandes slash")
    @app_commands.describe(
        scope="Portée de la synchronisation",
        guild_id="ID du serveur pour la synchronisation locale"
    )
    async def sync(
        self, 
        interaction: discord.Interaction, 
        scope: Literal["global", "guild", "clear"] = "global",
        guild_id: str = None
    ):
        """Synchronise les commandes slash avec Discord"""
        if not await self.bot.is_owner(interaction.user):
            embed = Embeds.error(
                "Accès refusé",
                "Cette commande est réservée au propriétaire du bot."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            if scope == "global":
                synced = await self.bot.tree.sync()
                embed = Embeds.success(
                    "Synchronisation globale",
                    f"**{len(synced)}** commande(s) synchronisée(s) globalement."
                )
                await interaction.followup.send(embed=embed)
            
            elif scope == "guild":
                guild = discord.Object(id=int(guild_id) if guild_id else interaction.guild_id)
                self.bot.tree.copy_global_to(guild=guild)
                synced = await self.bot.tree.sync(guild=guild)
                embed = Embeds.success(
                    "Synchronisation serveur",
                    f"**{len(synced)}** commande(s) synchronisée(s) pour ce serveur."
                )
                await interaction.followup.send(embed=embed)
            
            elif scope == "clear":
                guild = discord.Object(id=int(guild_id) if guild_id else interaction.guild_id)
                self.bot.tree.clear_commands(guild=guild)
                await self.bot.tree.sync(guild=guild)
                embed = Embeds.success(
                    "Commandes supprimées",
                    "Toutes les commandes ont été supprimées de ce serveur."
                )
                await interaction.followup.send(embed=embed)
        
        except Exception as e:
            embed = Embeds.error(
                "Erreur de synchronisation",
                f"Une erreur est survenue:\n```{str(e)[:200]}```"
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="guilds", description="Liste les serveurs du bot")
    async def guilds(self, interaction: discord.Interaction):
        """Liste tous les serveurs où le bot est présent"""
        if not await self.bot.is_owner(interaction.user):
            embed = Embeds.error(
                "Accès refusé",
                "Cette commande est réservée au propriétaire du bot."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guilds_list = sorted(self.bot.guilds, key=lambda g: g.member_count, reverse=True)[:25]
        
        # ← UTILISER L'EMBED STANDARDISÉ
        embed = Embeds.info(
            f"Serveurs du bot ({len(self.bot.guilds)})",
            f"Le bot est présent sur **{len(self.bot.guilds)}** serveur(s).\nVoici les 25 plus grands :"
        )
        
        for guild in guilds_list:
            embed.add_field(
                name=f"{guild.name}",
                value=f"ID: `{guild.id}`\nMembres: **{guild.member_count}**",
                inline=True
            )
        
        # Statistiques totales
        total_members = sum(g.member_count for g in self.bot.guilds)
        embed.set_footer(text=f"Total: {total_members} membres sur tous les serveurs")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="leave", description="Faire quitter le bot d'un serveur")
    @app_commands.describe(guild_id="ID du serveur à quitter")
    async def leave(self, interaction: discord.Interaction, guild_id: str):
        """Fait quitter le bot d'un serveur spécifique"""
        if not await self.bot.is_owner(interaction.user):
            embed = Embeds.error(
                "Accès refusé",
                "Cette commande est réservée au propriétaire du bot."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            guild = self.bot.get_guild(int(guild_id))
            if guild:
                guild_name = guild.name
                await guild.leave()
                embed = Embeds.success(
                    "Serveur quitté",
                    f"Le bot a quitté le serveur **{guild_name}** (ID: `{guild_id}`)"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = Embeds.error(
                    "Serveur introuvable",
                    f"Aucun serveur trouvé avec l'ID `{guild_id}`"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except ValueError:
            embed = Embeds.error(
                "ID invalide",
                f"`{guild_id}` n'est pas un ID Discord valide."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = Embeds.error(
                "Erreur",
                f"Impossible de quitter le serveur:\n```{str(e)[:200]}```"
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @commands.command(name="eval", hidden=True)
    @commands.is_owner()
    async def eval_code(self, ctx, *, code: str):
        """Évalue du code Python (DANGEREUX - Owner only)"""
        import io
        import contextlib
        
        code = code.strip("`")
        if code.startswith("py\n"):
            code = code[3:]
        
        stdout = io.StringIO()
        
        try:
            with contextlib.redirect_stdout(stdout):
                exec(f"async def __eval_func():\n" + "\n".join(f"    {line}" for line in code.split("\n")))
                result = await locals()["__eval_func"]()
            
            output = stdout.getvalue()
            if result is not None:
                output += f"\n{result}"
            
            if output:
                # ← UTILISER L'EMBED STANDARDISÉ
                embed = Embeds.success(
                    "Évaluation réussie",
                    f"```py\n{output[:1900]}\n```"
                )
                await ctx.send(embed=embed)
            else:
                await ctx.message.add_reaction("✅")
        
        except Exception as e:
            # ← UTILISER L'EMBED STANDARDISÉ
            embed = Embeds.error(
                "Erreur d'évaluation",
                f"```py\n{type(e).__name__}: {str(e)[:1900]}\n```"
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))