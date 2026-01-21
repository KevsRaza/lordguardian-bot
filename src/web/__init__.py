"""
Module web du bot - Dashboard et API.
Contient l'application Flask et les routes.
"""

from .app import create_app, app
from .routes import api_bp, dashboard_bp, auth_bp
from .templates import render_template, TemplateManager

# Configuration Flask par défaut
DEFAULT_CONFIG = {
    "SECRET_KEY": "dev-secret-key-change-in-production",
    "SESSION_TYPE": "filesystem",
    "SESSION_PERMANENT": False,
    "PERMANENT_SESSION_LIFETIME": 3600,  # 1 heure
    "TEMPLATES_AUTO_RELOAD": True,
    "JSONIFY_PRETTYPRINT_REGULAR": True,
    "MAX_CONTENT_LENGTH": 16 * 1024 * 1024  # 16MB
}

# Routes disponibles
AVAILABLE_ROUTES = {
    "api": [
        ("/api/v1/stats", "GET", "Statistiques du bot"),
        ("/api/v1/guilds", "GET", "Liste des serveurs"),
        ("/api/v1/users/:id", "GET", "Informations utilisateur"),
        ("/api/v1/config", "GET/POST", "Configuration")
    ],
    "dashboard": [
        ("/", "GET", "Page d'accueil"),
        ("/login", "GET", "Connexion Discord"),
        ("/guilds", "GET", "Liste des serveurs"),
        ("/guild/:id", "GET", "Dashboard d'un serveur")
    ]
}

def get_route_info(route_type="all"):
    """Retourne les informations sur les routes disponibles."""
    if route_type == "all":
        return AVAILABLE_ROUTES
    return AVAILABLE_ROUTES.get(route_type, {})

__all__ = [
    # Application
    "create_app", "app",
    
    # Blueprints
    "api_bp", "dashboard_bp", "auth_bp",
    
    # Templates
    "render_template", "TemplateManager",
    
    # Utilitaires
    "DEFAULT_CONFIG", "AVAILABLE_ROUTES", "get_route_info"
]