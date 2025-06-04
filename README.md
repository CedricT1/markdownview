# Markdown Viewer & Exporter

Une application web simple pour visualiser du Markdown, avec un aperçu en direct, et l'exporter aux formats HTML, PDF et ODT (OpenDocument Text). L'application est conteneurisée avec Docker.

## Fonctionnalités

*   **Éditeur Markdown :** Zone de texte pour saisir ou coller votre contenu Markdown.
*   **Aperçu en direct :** Visualisation instantanée du rendu HTML de votre Markdown.
*   **Thèmes :** Basculez entre un thème clair et un thème sombre pour l'interface. La préférence est sauvegardée dans le `localStorage` de votre navigateur.
*   **Export :**
    *   HTML : Téléchargez le rendu HTML brut.
    *   PDF : Générez un fichier PDF à partir de votre Markdown.
    *   ODT : Générez un fichier OpenDocument Text (compatible LibreOffice, OpenOffice) à partir de votre Markdown.

## Technologies Utilisées

*   **Backend :** Python avec Flask
*   **Serveur WSGI :** Gunicorn
*   **Parsing Markdown :** `markdown-it-py`
*   **Génération PDF :** `WeasyPrint`
*   **Génération ODT :** `Pandoc`
*   **Frontend :** HTML5, CSS3, JavaScript (Vanilla)
*   **Conteneurisation :** Docker

## Structure du Projet

```
markdownview/
├── app/                     # Module principal de l'application Flask
│   ├── __init__.py          # Factory de l'application Flask
│   ├── routes.py            # Logique des routes et des vues
│   ├── static/              # Fichiers statiques (CSS, JS)
│   │   ├── css/style.css
│   │   └── js/main.js
│   ├── templates/           # Templates HTML (Jinja2)
│   │   └── index.html
│   └── utils/               # Modules utilitaires
│       ├── markdown_processor.py
│       └── export_service.py
├── Dockerfile               # Instructions pour construire l'image Docker
├── docker-compose.yml       # (À ajouter) Fichier pour Docker Compose
├── requirements.txt         # Dépendances Python
├── run.py                   # Point d'entrée pour l'application Flask
└── README.md                # Ce fichier
```

## Prérequis

*   Docker Engine
*   Docker Compose (si vous utilisez `docker-compose.yml`)

## Installation et Lancement

### Avec Docker (via Dockerfile)

1.  **Construire l'image Docker :**
    Depuis la racine du projet, exécutez :
    ```bash
    docker build -t markdownview-app .
    ```

2.  **Lancer le conteneur Docker :**
    ```bash
    docker run -p 5000:5000 markdownview-app
    ```

    L'application sera accessible à l'adresse `http://localhost:5050`.

### Avec Docker Compose (Recommandé)

1.  **Lancer l'application :**
    Depuis la racine du projet, où se trouve le fichier `docker-compose.yml`, exécutez :
    ```bash
    docker-compose up
    ```
    Pour lancer en mode détaché (en arrière-plan) :
    ```bash
    docker-compose up -d
    ```

2.  **Arrêter l'application :**
    ```bash
    docker-compose down
    ```

    L'application sera accessible à l'adresse `http://localhost:5000`.

## Utilisation

1.  Ouvrez votre navigateur et allez sur `http://localhost:5050` (si vous utilisez `docker-compose up`) ou `http://localhost:5000` (si vous utilisez `docker run -p 5000:5000 ...`).
2.  Collez ou écrivez votre texte Markdown dans la zone de gauche.
3.  L'aperçu se mettra à jour automatiquement dans la zone de droite.
4.  Utilisez le bouton "Changer de Thème" pour basculer entre les thèmes clair et sombre.
5.  Utilisez les boutons dans la section "Exporter" pour télécharger votre document au format désiré.

## Auteurs

*   Votre Nom / Pseudo

## Licence

Ce projet est sous licence MIT - voir le fichier `LICENSE` (à ajouter si besoin) pour plus de détails.