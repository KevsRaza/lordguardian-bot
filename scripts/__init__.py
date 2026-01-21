"""
Scripts utilitaires pour GuildGreeter.
"""

__all__ = []

# Liste des scripts disponibles
AVAILABLE_SCRIPTS = [
    "deploy.sh - Déploiement du bot",
    "backup_db.sh - Sauvegarde de la base de données",
    "setup_env.py - Configuration de l'environnement",
    "migrate_db.py - Migration de la base de données",
    "generate_docs.py - Génération de la documentation"
]

def list_scripts():
    """Affiche la liste des scripts disponibles."""
    print("📜 Scripts disponibles:")
    for script in AVAILABLE_SCRIPTS:
        print(f"  • {script}")

if __name__ == "__main__":
    list_scripts()