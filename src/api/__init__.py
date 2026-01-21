"""
API REST pour le bot.
Endpoints pour l'intégration avec d'autres services.
"""

from .discord_auth import DiscordOAuth, get_user_info, exchange_code
from .endpoints import (
    stats_endpoint, guilds_endpoint, users_endpoint,
    config_endpoint, webhook_endpoint
)
from .middleware import (
    require_auth, rate_limit, json_response,
    handle_errors, log_request
)

# Version de l'API
API_VERSION = "v1"
API_BASE_PATH = f"/api/{API_VERSION}"

# Codes d'erreur API
API_ERRORS = {
    1000: "Erreur interne",
    1001: "Non authentifié",
    1002: "Permission refusée",
    1003: "Ressource non trouvée",
    1004: "Limite de taux atteinte",
    1005: "Paramètres invalides"
}

# Endpoints disponibles
ENDPOINTS = {
    "stats": f"{API_BASE_PATH}/stats",
    "guilds": f"{API_BASE_PATH}/guilds",
    "guild": f"{API_BASE_PATH}/guilds/<int:guild_id>",
    "users": f"{API_BASE_PATH}/users",
    "user": f"{API_BASE_PATH}/users/<int:user_id>",
    "config": f"{API_BASE_PATH}/config",
    "webhook": f"{API_BASE_PATH}/webhook"
}

def get_endpoint_url(endpoint_name: str, **params):
    """Génère l'URL complète d'un endpoint."""
    pattern = ENDPOINTS.get(endpoint_name)
    if not pattern:
        raise ValueError(f"Endpoint inconnu: {endpoint_name}")
    
    if params:
        return pattern.format(**params)
    return pattern

def create_api_response(data=None, error=None, code=200):
    """Crée une réponse API standardisée."""
    response = {
        "success": error is None,
        "timestamp": datetime.utcnow().isoformat(),
        "api_version": API_VERSION
    }
    
    if error:
        response["error"] = {
            "code": error.get("code", 1000),
            "message": error.get("message", "Erreur inconnue"),
            "details": error.get("details")
        }
    else:
        response["data"] = data
    
    return response

__all__ = [
    # Auth
    "DiscordOAuth", "get_user_info", "exchange_code",
    
    # Endpoints
    "stats_endpoint", "guilds_endpoint", "users_endpoint",
    "config_endpoint", "webhook_endpoint",
    
    # Middleware
    "require_auth", "rate_limit", "json_response",
    "handle_errors", "log_request",
    
    # Utilitaires
    "API_VERSION", "API_BASE_PATH", "API_ERRORS",
    "ENDPOINTS", "get_endpoint_url", "create_api_response"
]

# Import datetime pour create_api_response
from datetime import datetime