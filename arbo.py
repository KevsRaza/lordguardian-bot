# tree_view.py
import os
import sys
from pathlib import Path

class ProjectTree:
    def __init__(self):
        # Dossiers à exclure
        self.exclude_dirs = {
            '.venv', '.vscode', '.github', '.git',
            '__pycache__', 'venv', 'env', 'node_modules',
            '.idea', '.pytest_cache', '.mypy_cache',
            'dist', 'build', '*.egg-info'
        }
        
        # Fichiers à exclure
        self.exclude_files = {
            '*.pyc', '*.pyo', '*.pyd', '.DS_Store',
            'Thumbs.db', 'desktop.ini', '.coverage',
            '.env', '.env.local', '*.log'
        }
        
        # Extensions à afficher avec des icônes
        self.file_icons = {
            '.py': '🐍',
            '.json': '📋',
            '.txt': '📄',
            '.md': '📖',
            '.yml': '⚙️',
            '.yaml': '⚙️',
            '.ini': '⚙️',
            '.cfg': '⚙️',
            '.toml': '⚙️',
            '.html': '🌐',
            '.css': '🎨',
            '.js': '📜',
            '.sql': '🗃️',
            '.db': '🗄️',
            '.csv': '📊',
            '.png': '🖼️',
            '.jpg': '🖼️',
            '.ico': '🖼️'
        }
        
        # Couleurs ANSI
        self.COLORS = {
            'reset': '\033[0m',
            'dir': '\033[94m',      # Bleu
            'py': '\033[92m',       # Vert
            'json': '\033[93m',     # Jaune
            'md': '\033[96m',       # Cyan
            'other': '\033[90m',    # Gris
            'title': '\033[1;36m',  # Cyan gras
            'line': '\033[90m',     # Gris pour les lignes
        }
    
    def should_exclude(self, path):
        """Vérifie si un chemin doit être exclu"""
        path_str = str(path)
        
        # Vérifier les dossiers exclus
        for excl_dir in self.exclude_dirs:
            if excl_dir.startswith('*'):
                if excl_dir[1:] in path_str:
                    return True
            elif f'{os.sep}{excl_dir}{os.sep}' in path_str or path_str.endswith(f'{os.sep}{excl_dir}'):
                return True
        
        # Vérifier les fichiers exclus par pattern
        name = path.name
        for excl_pattern in self.exclude_files:
            if excl_pattern.startswith('*'):
                if name.endswith(excl_pattern[1:]):
                    return True
            elif name == excl_pattern:
                return True
        
        return False
    
    def get_icon(self, filename):
        """Retourne l'icône appropriée pour un fichier"""
        ext = os.path.splitext(filename)[1].lower()
        return self.file_icons.get(ext, '📄')
    
    def get_color(self, item, is_dir=False):
        """Retourne la couleur appropriée"""
        if is_dir:
            return self.COLORS['dir']
        
        ext = os.path.splitext(item)[1].lower()
        if ext == '.py':
            return self.COLORS['py']
        elif ext == '.json':
            return self.COLORS['json']
        elif ext == '.md':
            return self.COLORS['md']
        else:
            return self.COLORS['other']
    
    def print_tree(self, start_path='.', max_depth=5, show_all=False):
        """Affiche l'arborescence du projet"""
        
        start_path = Path(start_path).resolve()
        
        print(f"\n{self.COLORS['title']}📁 ARBORESCENCE DU PROJET{self.COLORS['reset']}")
        print(f"{self.COLORS['line']}{'=' * 60}{self.COLORS['reset']}")
        print(f"{self.COLORS['dir']}Racine :{self.COLORS['reset']} {start_path}")
        print(f"{self.COLORS['line']}{'-' * 60}{self.COLORS['reset']}\n")
        
        # Statistiques
        stats = {
            'dirs': 0,
            'files': 0,
            'py_files': 0,
            'other_files': 0
        }
        
        def walk_directory(current_path, depth=0, prefix=""):
            if depth > max_depth:
                return
            
            if self.should_exclude(current_path):
                return
            
            # Récupérer les éléments du dossier
            try:
                items = sorted(os.listdir(current_path))
            except (PermissionError, OSError):
                return
            
            # Séparer dossiers et fichiers
            dirs = []
            files = []
            
            for item in items:
                item_path = current_path / item
                
                if self.should_exclude(item_path):
                    continue
                
                if item_path.is_dir():
                    dirs.append(item)
                else:
                    # Filtrer les fichiers si on ne montre pas tout
                    if not show_all and not any(item.endswith(ext) for ext in ['.py', '.json', '.md', '.txt', '.yml', '.yaml', '.ini']):
                        continue
                    files.append(item)
            
            # Afficher les fichiers d'abord
            for i, file in enumerate(sorted(files)):
                is_last_file = (i == len(files) - 1) and (len(dirs) == 0)
                
                # Préfixe de ligne
                if depth == 0:
                    line_prefix = ""
                else:
                    line_prefix = prefix + ("└── " if is_last_file else "├── ")
                
                # Couleur et icône
                color = self.get_color(file, False)
                icon = self.get_icon(file)
                
                print(f"{self.COLORS['line']}{prefix}{'└── ' if is_last_file else '├── '}{self.COLORS['reset']}"
                      f"{color}{icon} {file}{self.COLORS['reset']}")
                
                # Statistiques
                stats['files'] += 1
                if file.endswith('.py'):
                    stats['py_files'] += 1
                else:
                    stats['other_files'] += 1
            
            # Puis les dossiers
            for i, dir_name in enumerate(sorted(dirs)):
                is_last_dir = (i == len(dirs) - 1)
                dir_path = current_path / dir_name
                
                # Préfixe de ligne
                if depth == 0:
                    line_prefix = ""
                    print(f"{self.COLORS['dir']}📂 {dir_name}/{self.COLORS['reset']}")
                else:
                    line_prefix = prefix + ("└── " if is_last_dir else "├── ")
                    print(f"{self.COLORS['line']}{prefix}{'└── ' if is_last_dir else '├── '}{self.COLORS['reset']}"
                          f"{self.COLORS['dir']}📂 {dir_name}/{self.COLORS['reset']}")
                
                stats['dirs'] += 1
                
                # Nouveau préfixe pour le niveau suivant
                new_prefix = prefix + ("    " if is_last_dir else "│   ")
                
                # Explorer récursivement
                walk_directory(dir_path, depth + 1, new_prefix)
        
        # Démarrer l'affichage
        walk_directory(start_path)
        
        # Afficher les statistiques
        print(f"\n{self.COLORS['line']}{'-' * 60}{self.COLORS['reset']}")
        print(f"{self.COLORS['title']}📊 STATISTIQUES :{self.COLORS['reset']}")
        print(f"  📂 Dossiers: {stats['dirs']}")
        print(f"  📄 Fichiers totaux: {stats['files']}")
        print(f"    ├── {self.COLORS['py']}🐍 Python: {stats['py_files']}{self.COLORS['reset']}")
        print(f"    └── {self.COLORS['other']}📄 Autres: {stats['other_files']}{self.COLORS['reset']}")
        print(f"{self.COLORS['line']}{'=' * 60}{self.COLORS['reset']}")
    
    def print_simple_list(self):
        """Affiche une liste simple des fichiers Python"""
        print(f"\n{self.COLORS['title']}🐍 FICHIERS PYTHON DU PROJET{self.COLORS['reset']}")
        print(f"{self.COLORS['line']}{'=' * 60}{self.COLORS['reset']}")
        
        py_files = []
        for root, dirs, files in os.walk('.'):
            # Exclure les dossiers
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                if file.endswith('.py') and not self.should_exclude(Path(root) / file):
                    rel_path = os.path.relpath(os.path.join(root, file), '.')
                    py_files.append(rel_path)
        
        for py_file in sorted(py_files):
            # Compter le nombre de lignes
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = sum(1 for _ in f)
            except:
                lines = 0
            
            # Afficher avec indentation basée sur la profondeur
            depth = py_file.count(os.sep)
            indent = '  ' * depth
            
            print(f"{indent}{self.COLORS['py']}🐍 {py_file}{self.COLORS['reset']} "
                  f"{self.COLORS['other']}({lines} lignes){self.COLORS['reset']}")
        
        print(f"\n{self.COLORS['title']}Total: {len(py_files)} fichiers Python{self.COLORS['reset']}")
    
    def analyze_project(self):
        """Analyse la structure du projet pour un bot Discord"""
        print(f"\n{self.COLORS['title']}🔍 ANALYSE POUR BOT DISCORD{self.COLORS['reset']}")
        print(f"{self.COLORS['line']}{'=' * 60}{self.COLORS['reset']}")
        
        cogs = []
        other_py = []
        
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                if file.endswith('.py') and not self.should_exclude(Path(root) / file):
                    full_path = Path(root) / file
                    
                    # Lire le fichier pour détecter les cogs
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            if 'class' in content and ('commands.Cog' in content or 'app_commands.Group' in content):
                                cogs.append(str(full_path))
                            else:
                                other_py.append(str(full_path))
                    except:
                        other_py.append(str(full_path))
        
        # Afficher les cogs détectés
        if cogs:
            print(f"\n{self.COLORS['dir']}📁 COGS DÉTECTÉS ({len(cogs)}) :{self.COLORS['reset']}")
            for cog in sorted(cogs):
                print(f"  {self.COLORS['py']}✅ {cog[2:]}{self.COLORS['reset']}")
        else:
            print(f"\n{self.COLORS['other']}⚠️  Aucun cog détecté{self.COLORS['reset']}")
        
        # Afficher les autres fichiers Python
        if other_py:
            print(f"\n{self.COLORS['other']}📄 Autres fichiers Python ({len(other_py)}) :{self.COLORS['reset']}")
            for i, py_file in enumerate(sorted(other_py)[:10]):  # Limiter à 10
                print(f"  {py_file[2:]}")
            if len(other_py) > 10:
                print(f"  ... et {len(other_py) - 10} autres")


def main():
    """Fonction principale"""
    tree = ProjectTree()
    
    # Arguments de ligne de commande
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command in ['-s', '--simple', 'simple']:
            tree.print_simple_list()
        elif command in ['-a', '--analyze', 'analyze']:
            tree.analyze_project()
        elif command in ['-h', '--help', 'help']:
            print("""
Utilisation : python tree_view.py [OPTION]

Options :
  (sans option)  Affiche l'arborescence complète
  -s, --simple   Liste simple des fichiers Python
  -a, --analyze  Analyse pour bot Discord
  -h, --help     Affiche cette aide
            """)
        else:
            print(f"Option inconnue: {command}")
            print("Utilisez -h pour l'aide")
    else:
        # Mode par défaut : arborescence complète
        tree.print_tree(max_depth=6)


if __name__ == "__main__":
    main()