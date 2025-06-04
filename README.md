# Markdown Viewer & Exporter (Français)

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
├── docker-compose.yml       # Fichier pour Docker Compose
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

    L'application sera accessible à l'adresse `http://localhost:5000`. (Note: si vous utilisez `docker-compose.yml` par la suite, le port par défaut sera `5050` pour l'hôte).

### Avec Docker Compose (Recommandé)

1.  **Lancer l'application :**
    Depuis la racine du projet, où se trouve le fichier `docker-compose.yml`, exécutez :
    ```bash
    docker-compose up
    ```
    Pour lancer en mode détaché (en arrière-plan) :
    ```bash
    docker-compose up -d --build # --build est optionnel si l'image est déjà à jour
    ```

2.  **Arrêter l'application :**
    ```bash
    docker-compose down
    ```

    L'application sera accessible à l'adresse `http://localhost:5050`.

## Utilisation

1.  Ouvrez votre navigateur et allez sur `http://localhost:5050` (si vous utilisez `docker-compose up`) ou `http://localhost:5000` (si vous utilisez `docker run -p 5000:5000 ...`).
2.  Collez ou écrivez votre texte Markdown dans la zone de gauche.
3.  L'aperçu se mettra à jour automatiquement dans la zone de droite.
4.  Utilisez le bouton "Changer de Thème" pour basculer entre les thèmes clair et sombre.
5.  Utilisez les boutons dans la section "Exporter" pour télécharger votre document au format désiré.

## Auteurs

*   Cédric Trachsel / CedricT1

## Licence

Ce projet est sous licence MIT - voir le fichier `LICENSE` (à ajouter si besoin) pour plus de détails.

---

# Markdown Viewer & Exporter (English)

A simple web application to visualize Markdown, with a live preview, and export it to HTML, PDF, and ODT (OpenDocument Text) formats. The application is containerized with Docker.

## Features

*   **Markdown Editor:** Text area to type or paste your Markdown content.
*   **Live Preview:** Instant visualization of the HTML rendering of your Markdown.
*   **Themes:** Switch between a light and a dark theme for the interface. The preference is saved in your browser's `localStorage`.
*   **Export:**
    *   HTML: Download the raw HTML rendering.
    *   PDF: Generate a PDF file from your Markdown.
    *   ODT: Generate an OpenDocument Text file (compatible with LibreOffice, OpenOffice) from your Markdown.

## Technologies Used

*   **Backend:** Python with Flask
*   **WSGI Server:** Gunicorn
*   **Markdown Parsing:** `markdown-it-py`
*   **PDF Generation:** `WeasyPrint`
*   **ODT Generation:** `Pandoc`
*   **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
*   **Containerization:** Docker

## Project Structure

```
markdownview/
├── app/                     # Main Flask application module
│   ├── __init__.py          # Flask application factory
│   ├── routes.py            # Route and view logic
│   ├── static/              # Static files (CSS, JS)
│   │   ├── css/style.css
│   │   └── js/main.js
│   ├── templates/           # HTML Templates (Jinja2)
│   │   └── index.html
│   └── utils/               # Utility modules
│       ├── markdown_processor.py
│       └── export_service.py
├── Dockerfile               # Instructions to build the Docker image
├── docker-compose.yml       # File for Docker Compose
├── requirements.txt         # Python dependencies
├── run.py                   # Entry point for the Flask application
└── README.md                # This file
```

## Prerequisites

*   Docker Engine
*   Docker Compose (if using `docker-compose.yml`)

## Installation and Launch

### With Docker (via Dockerfile)

1.  **Build the Docker image:**
    From the project root, run:
    ```bash
    docker build -t markdownview-app .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -p 5000:5000 markdownview-app
    ```

    The application will be accessible at `http://localhost:5000`. (Note: if you later use `docker-compose.yml`, the default host port will be `5050`).

### With Docker Compose (Recommended)

1.  **Launch the application:**
    From the project root, where the `docker-compose.yml` file is located, run:
    ```bash
    docker-compose up
    ```
    To launch in detached mode (background):
    ```bash
    docker-compose up -d --build # --build is optional if the image is already up-to-date
    ```

2.  **Stop the application:**
    ```bash
    docker-compose down
    ```

    The application will be accessible at `http://localhost:5050`.

## Usage

1.  Open your browser and go to `http://localhost:5050` (if using `docker-compose up`) or `http://localhost:5000` (if using `docker run -p 5000:5000 ...`).
2.  Paste or write your Markdown text in the left-hand area.
3.  The preview will update automatically in the right-hand area.
4.  Use the "Change Theme" button to switch between light and dark themes.
5.  Use the buttons in the "Export" section to download your document in the desired format.

## Authors

*   Cédric Trachsel / CedricT1

## License

This project is licensed under the MIT License - see the `LICENSE` file (to be added if needed) for more details.