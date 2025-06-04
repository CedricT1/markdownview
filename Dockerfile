# Étape 1: Base Python et installation des dépendances Python
FROM python:3.10-slim AS builder

# Définir le répertoire de travail
WORKDIR /opt/app

# Variables d'environnement pour Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Installer les dépendances système nécessaires pour la compilation de WeasyPrint (au cas où)
# et pour Pandoc (même si Pandoc est plus une dépendance d'exécution, l'avoir ici ne nuit pas)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpango-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    # Pandoc n'est pas strictement nécessaire ici si on l'installe dans l'image finale,
    # mais le garder ici peut être utile si des scripts de build l'utilisaient.
    # Pour simplifier, on peut l'omettre ici et ne l'installer que dans l'image finale.
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copier le fichier des dépendances Python et les installer
# Les paquets seront installés globalement dans cette étape
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Étape 2: Application finale
FROM python:3.10-slim

WORKDIR /opt/app

# Installer les dépendances système d'exécution (WeasyPrint, Pandoc)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    pandoc \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copier les paquets Python installés depuis l'étape builder
# Ces chemins sont standards pour une installation globale de pip dans les images Python officielles
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copier le reste de l'application
# Il est préférable de copier le code avant de changer d'utilisateur
COPY . .

# Créer un utilisateur non-root pour l'application et lui donner la propriété des fichiers
RUN useradd --create-home appuser && \
    chown -R appuser:appuser /opt/app
USER appuser

# Exposer le port sur lequel Gunicorn va écouter
EXPOSE 5000

# Commande pour lancer l'application avec Gunicorn
# Le 'run:app' fait référence au fichier run.py et à l'instance 'app' de Flask.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]