"""
Keep Alive - Maintient le bot actif (utile pour les hébergements comme Replit)
"""
from flask import Flask
from threading import Thread
import logging

# Désactiver les logs Flask
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

@app.route('/')
def home():
    """Page d'accueil pour vérifier que le bot est en ligne"""
    return """
    <html>
        <head>
            <title>GuildGreeter Bot</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }
                .container {
                    text-align: center;
                    color: white;
                }
                h1 { font-size: 3em; margin: 0; }
                p { font-size: 1.5em; }
                .status { 
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    background: #00ff00;
                    border-radius: 50%;
                    animation: pulse 2s infinite;
                }
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 GuildGreeter Bot</h1>
                <p><span class="status"></span> Bot en ligne</p>
            </div>
        </body>
    </html>
    """

@app.route('/health')
def health():
    """Endpoint de santé pour les checks"""
    return {"status": "online", "bot": "GuildGreeter"}, 200

def keep_alive():
    """
    Lance un serveur web Flask en arrière-plan
    Utile pour garder le bot actif sur des plateformes comme Replit
    """
    def run():
        app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)
    
    server = Thread(target=run)
    server.daemon = True
    server.start()
    print("🌐 Serveur Keep-Alive démarré sur http://0.0.0.0:8080")