"""
Commandes fun et divertissantes (sans conflits avec le casino)
"""
import discord
from discord import app_commands
from discord.ext import commands
import random
import aiohttp

class Fun(commands.Cog):
    """Commandes fun pour s'amuser"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="8ball", description="Pose une question à la boule magique")
    @app_commands.describe(question="Ta question")
    async def eightball(self, interaction: discord.Interaction, question: str):
        """Répond à une question avec une réponse aléatoire"""
        responses = [
            "Oui, absolument !",
            "C'est certain.",
            "Sans aucun doute.",
            "Oui, définitivement.",
            "Tu peux compter dessus.",
            "De mon point de vue, oui.",
            "Les signes pointent vers oui.",
            "Tout indique que oui.",
            "Réponse floue, réessaye.",
            "Demande à nouveau plus tard.",
            "Je ne peux pas prédire maintenant.",
            "Concentre-toi et demande à nouveau.",
            "Ne compte pas dessus.",
            "Ma réponse est non.",
            "Mes sources disent non.",
            "Les perspectives ne sont pas bonnes.",
            "Très douteux."
        ]
        
        embed = discord.Embed(
            title="🎱 Boule Magique",
            color=discord.Color.purple()
        )
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Réponse", value=random.choice(responses), inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="flip", description="Lance une pièce (version fun sans mise)")  # ← RENOMMÉ EN 'flip'
    async def flip(self, interaction: discord.Interaction):  # ← RENOMMÉ
        """Lance une pièce (sans mise)"""
        result = random.choice(["Pile", "Face"])
        emoji = "🪙"
        
        embed = discord.Embed(
            title=f"{emoji} Lancer de pièce",
            description=f"Résultat: **{result}**",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="chooserandom", description="Choisis aléatoirement parmi plusieurs options")
    @app_commands.describe(options="Options séparées par des virgules")
    async def chooserandom(self, interaction: discord.Interaction, options: str):
        """Choisis aléatoirement parmi plusieurs options"""
        choices = [choice.strip() for choice in options.split(',')]
        
        if len(choices) < 2:
            await interaction.response.send_message(
                "❌ Fournis au moins 2 options séparées par des virgules.",
                ephemeral=True
            )
            return
        
        chosen = random.choice(choices)
        
        embed = discord.Embed(
            title="🤔 Choix aléatoire",
            description=f"J'ai choisi: **{chosen}**",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Parmi {len(choices)} options")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="lovecalc", description="Calcule le pourcentage d'amour entre deux personnes")
    @app_commands.describe(
        person1="Première personne",
        person2="Deuxième personne"
    )
    async def lovecalc(self, interaction: discord.Interaction, person1: str, person2: str):
        """Calcule le pourcentage d'amour"""
        # Utiliser un seed pour avoir toujours le même résultat pour les mêmes personnes
        names = sorted([person1.lower(), person2.lower()])
        seed = sum(ord(c) for c in ''.join(names))
        random.seed(seed)
        percentage = random.randint(0, 100)
        random.seed()  # Reset le seed
        
        # Déterminer le message et la couleur
        if percentage < 25:
            message = "C'est pas vraiment ça... 💔"
            color = discord.Color.red()
            emoji = "😢"
        elif percentage < 50:
            message = "Peut-être avec du temps... 🤷"
            color = discord.Color.orange()
            emoji = "😐"
        elif percentage < 75:
            message = "Ça a l'air prometteur ! 😊"
            color = discord.Color.blue()
            emoji = "😊"
        else:
            message = "Match parfait ! 💕"
            color = discord.Color.pink()
            emoji = "😍"
        
        embed = discord.Embed(
            title=f"{emoji} Calculateur d'amour",
            color=color
        )
        embed.add_field(name="Entre", value=f"**{person1}** et **{person2}**", inline=False)
        embed.add_field(name="Résultat", value=f"**{percentage}%** ❤️", inline=False)
        embed.add_field(name="Verdict", value=message, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="dog", description="Affiche une image de chien aléatoire")
    async def dog(self, interaction: discord.Interaction):
        """Récupère une image de chien aléatoire"""
        await interaction.response.defer()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://dog.ceo/api/breeds/image/random") as response:
                    if response.status == 200:
                        data = await response.json()
                        embed = discord.Embed(
                            title="🐕 Chien aléatoire",
                            color=discord.Color.orange()
                        )
                        embed.set_image(url=data["message"])
                        await interaction.followup.send(embed=embed)
                    else:
                        await interaction.followup.send("❌ Impossible de récupérer l'image.")
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {e}")
    
    @app_commands.command(name="cat", description="Affiche une image de chat aléatoire")
    async def cat(self, interaction: discord.Interaction):
        """Récupère une image de chat aléatoire"""
        await interaction.response.defer()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.thecatapi.com/v1/images/search") as response:
                    if response.status == 200:
                        data = await response.json()
                        embed = discord.Embed(
                            title="🐱 Chat aléatoire",
                            color=discord.Color.purple()
                        )
                        embed.set_image(url=data[0]["url"])
                        await interaction.followup.send(embed=embed)
                    else:
                        await interaction.followup.send("❌ Impossible de récupérer l'image.")
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {e}")
    
    @app_commands.command(name="joke", description="Raconte une blague aléatoire")
    async def joke(self, interaction: discord.Interaction):
        """Raconte une blague"""
        jokes = [
            ("Pourquoi les plongeurs plongent-ils toujours en arrière et pas en avant ?", 
             "Parce que sinon ils tombent dans le bateau."),
            ("Que dit un oignon quand il se cogne ?", "Aïe !"),
            ("Pourquoi les vampires ne sont pas photogéniques ?", "Parce qu'ils manquent de reflets."),
            ("Qu'est-ce qu'un canard avec une carte bleue ?", "Un canard à découvert."),
            ("Que fait une lampe qui a peur ?", "Elle s'allume."),
            ("Pourquoi les poissons sont mauvais en tennis ?", "Parce qu'ils ont leur filet."),
            ("Quel est le comble pour un électricien ?", "De ne pas être au courant."),
            ("Que dit une imprimante dans l'eau ?", "J'ai papier."),
        ]
        
        question, answer = random.choice(jokes)
        
        embed = discord.Embed(
            title="😂 Blague du jour",
            color=discord.Color.green()
        )
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Réponse", value=answer, inline=False)
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="fact", description="Un fait aléatoire intéressant")
    async def fact(self, interaction: discord.Interaction):
        """Affiche un fait intéressant"""
        facts = [
            "Les baleines bleues peuvent entendre à plus de 1600 km de distance.",
            "Le miel ne se périme jamais. Des pots de miel vieux de 3000 ans ont été retrouvés comestibles.",
            "Les pieuvres ont trois cœurs.",
            "Il existe plus d'arbres sur Terre que d'étoiles dans la Voie lactée.",
            "Les escargots peuvent dormir pendant 3 ans.",
            "Les fraises ne sont pas des baies, mais les bananes en sont.",
            "Le cœur d'une crevette est dans sa tête.",
            "Les dauphins donnent des noms les uns aux autres.",
            "Il y a plus de bactéries dans ta bouche que d'humains sur Terre.",
            "Les nuages peuvent peser plusieurs tonnes."
        ]
        
        embed = discord.Embed(
            title="📚 Fait intéressant",
            description=random.choice(facts),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Saviez-vous que ?")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="poll", description="Crée un sondage rapide")
    @app_commands.describe(question="La question du sondage", options="Options séparées par des |")
    async def poll(self, interaction: discord.Interaction, question: str, options: str = "Oui|Non|Peut-être"):
        """Crée un sondage avec réactions"""
        choices = [choice.strip() for choice in options.split('|')]
        
        if len(choices) < 2 or len(choices) > 10:
            await interaction.response.send_message(
                "❌ Fournis 2 à 10 options séparées par des |",
                ephemeral=True
            )
            return
        
        # Emojis pour les réactions
        number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        # Créer l'embed du sondage
        embed = discord.Embed(
            title="📊 Sondage",
            description=f"**{question}**",
            color=discord.Color.purple()
        )
        
        for i, choice in enumerate(choices):
            if i < len(number_emojis):
                embed.add_field(
                    name=f"{number_emojis[i]} {choice}",
                    value="\u200b",
                    inline=False
                )
        
        embed.set_footer(text=f"Sondage créé par {interaction.user.display_name}")
        
        message = await interaction.response.send_message(embed=embed)
        
        # Ajouter les réactions
        try:
            # Récupérer le message envoyé
            if isinstance(message, discord.InteractionResponse):
                message = await interaction.original_response()
            
            # Ajouter les réactions d'emoji
            for i in range(len(choices)):
                if i < len(number_emojis):
                    await message.add_reaction(number_emojis[i])
        except Exception as e:
            print(f"Erreur lors de l'ajout des réactions: {e}")

async def setup(bot):
    await bot.add_cog(Fun(bot))