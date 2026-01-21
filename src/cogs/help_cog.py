# cogs/help_cog.py
import discord
from discord.ext import commands
from core.embeds import Embeds  # ← AJOUT

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')  # Supprime l'aide par défaut

    @commands.command(name="debug")
    async def debug_info(self, ctx):
        """Informations de débogage"""
        
        # Liste des cogs chargés
        loaded_cogs = list(self.bot.cogs.keys())
        
        # Commandes par type
        prefix_commands = [cmd.name for cmd in self.bot.commands]
        
        # ← UTILISER L'EMBED STANDARDISÉ
        embed = Embeds.info(
            "Informations de débogage",
            f"**Bot :** {self.bot.user.name}\n**Serveurs :** {len(self.bot.guilds)}\n**Latence :** {round(self.bot.latency * 1000)}ms"
        )
        
        embed.add_field(
            name="🔌 Cogs chargés",
            value="\n".join(f"• {cog}" for cog in loaded_cogs) if loaded_cogs else "Aucun",
            inline=False
        )
        
        embed.add_field(
            name=f"⚡ Commandes préfixe ({len(prefix_commands)})",
            value=f"`{'`, `'.join(sorted(prefix_commands))}`" if prefix_commands else "Aucune",
            inline=False
        )
        
        slash_commands = len(self.bot.tree.get_commands())
        embed.add_field(
            name=f"✨ Slash commands ({slash_commands})",
            value=f"{slash_commands} commandes enregistrées",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='testcommands')
    async def test_commands(self, ctx):
        """Affiche toutes les commandes détectées par le bot"""
        
        all_commands = []
        cog_details = []
        
        # Commandes par cogs
        for cog_name in self.bot.cogs:
            cog = self.bot.get_cog(cog_name)
            commands_list = cog.get_commands()
            if commands_list:
                cmd_names = [cmd.name for cmd in commands_list]
                all_commands.extend(cmd_names)
                cog_details.append(f"**{cog_name}:** {len(cmd_names)} commandes")
                print(f"[DEBUG] Cog '{cog_name}': {cmd_names}")
        
        # Commandes sans cog
        orphan_commands = [cmd.name for cmd in self.bot.commands if not cmd.cog]
        if orphan_commands:
            all_commands.extend(orphan_commands)
            cog_details.append(f"**Sans cog:** {len(orphan_commands)} commandes")
        
        # ← UTILISER L'EMBED STANDARDISÉ
        embed = Embeds.info(
            f"Test des commandes ({len(all_commands)} trouvées)",
            "\n".join(cog_details)
        )
        
        embed.add_field(
            name="📋 Liste complète",
            value=f"`{'`, `'.join(sorted(all_commands))}`" if all_commands else "Aucune commande",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='help')
    async def help_command(self, ctx, *, command_name: str = None):
        """Affiche toutes les commandes disponibles"""
        
        if command_name:
            # Aide pour une commande spécifique
            command = self.bot.get_command(command_name.lower())
            if not command:
                # ← UTILISER L'EMBED STANDARDISÉ
                embed = Embeds.error(
                    "Commande introuvable",
                    f"La commande `{command_name}` n'existe pas.\nUtilisez `{ctx.prefix}help` pour voir toutes les commandes."
                )
                await ctx.send(embed=embed)
                return
            
            # ← UTILISER L'EMBED STANDARDISÉ
            description = command.help or "Aucune description disponible."
            embed = Embeds.info(
                f"Commande: {ctx.prefix}{command.name}",
                description
            )
            
            # Usage
            params = []
            for param in command.clean_params.values():
                if param.default == param.empty:
                    params.append(f"<{param.name}>")
                else:
                    params.append(f"[{param.name}]")
            
            usage = f"{ctx.prefix}{command.name}"
            if params:
                usage += f" {' '.join(params)}"
            
            embed.add_field(name="📝 Usage", value=f"`{usage}`", inline=False)
            
            if command.aliases:
                aliases = "`, `".join(command.aliases)
                embed.add_field(name="🔤 Alias", value=f"`{aliases}`", inline=True)
            
            # Permissions requises
            if hasattr(command, 'checks') and command.checks:
                embed.add_field(name="🔒 Permissions", value="Permissions spéciales requises", inline=True)
            
            await ctx.send(embed=embed)
            
        else:
            # ← UTILISER L'EMBED STANDARDISÉ avec help_command()
            # On peut aussi créer un embed personnalisé
            embed = discord.Embed(
                title="📚 Menu d'aide - GuildGreeter",
                description=(
                    f"**Préfixe des commandes :** `{ctx.prefix}`\n"
                    f"**Slash commands :** `/`\n\n"
                    f"Utilisez `{ctx.prefix}help <commande>` pour plus de détails sur une commande."
                ),
                color=Embeds.EmbedColors.INFO
            )
            
            # === COMMANDES PRÉFIXE (!) ===
            for cog_name, cog in self.bot.cogs.items():
                commands_list = [cmd.name for cmd in cog.get_commands() if not cmd.hidden]
                
                if commands_list:
                    icons = {
                        "Welcome": "👋",
                        "Moderation": "🛡️",
                        "Casino": "🎰",
                        "Economy": "💰",
                        "Shop": "🛒",
                        "Utilities": "🔧",
                        "Fun": "🎉",
                        "Help": "📖",
                        "Admin": "⚙️",
                        "Tickets": "🎫",
                        "Leveling": "📊"
                    }
                    icon = icons.get(cog_name, "📁")
                    
                    # Description du cog
                    cog_desc = cog.description if hasattr(cog, 'description') and cog.description else ""
                    
                    embed.add_field(
                        name=f"{icon} {cog_name}" + (f" - {cog_desc}" if cog_desc else ""),
                        value=f"`{ctx.prefix}{'`, `{ctx.prefix}'.join(sorted(commands_list))}`",
                        inline=False
                    )
            
            # === SLASH COMMANDS (/) ===
            slash_commands = self.bot.tree.get_commands()
            if slash_commands:
                slash_by_cog = {}
                
                for command in slash_commands:
                    # Essayer de déterminer le cog d'origine
                    cog_name = "Autres"
                    if hasattr(command, 'module'):
                        module_name = command.module.split('.')[-1]
                        cog_name = module_name.replace('_', ' ').title()
                    
                    if cog_name not in slash_by_cog:
                        slash_by_cog[cog_name] = []
                    slash_by_cog[cog_name].append(command.name)
                
                # Ajouter les slash commands groupées
                for cog_name, commands_list in sorted(slash_by_cog.items()):
                    if commands_list:
                        icons = {
                            "Welcome": "👋",
                            "Casino": "🎰",
                            "Economy": "💰",
                            "Moderation": "🛡️",
                            "Utilities": "🔧",
                            "Admin": "⚙️"
                        }
                        icon = icons.get(cog_name, "✨")
                        
                        embed.add_field(
                            name=f"{icon} {cog_name} (Slash)",
                            value=f"`/{'`, `/'.join(sorted(commands_list))}`",
                            inline=False
                        )
            
            # Footer avec statistiques
            total_prefix = len([c for c in self.bot.commands if not c.hidden])
            total_slash = len(self.bot.tree.get_commands())
            embed.set_footer(
                text=f"Total: {total_prefix} commandes préfixe • {total_slash} slash commands",
                icon_url=self.bot.user.display_avatar.url
            )
            
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))