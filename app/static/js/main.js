document.addEventListener('DOMContentLoaded', () => {
    const markdownInput = document.getElementById('markdown-input');
    const markdownPreview = document.getElementById('markdown-preview');
    const themeToggleButton = document.getElementById('theme-toggle');
    const exportForm = document.getElementById('export-form');
    const exportMarkdownContentField = document.getElementById('export-markdown-content');

    // Lance le rendu des diagrammes Mermaid présents dans l'aperçu.
    // Les <script> injectés via innerHTML ne s'exécutent pas : on appelle
    // donc mermaid.run() manuellement sur les nœuds .mermaid après chaque rendu.
    function renderMermaid() {
        if (!window.mermaid) return;
        const nodes = markdownPreview.querySelectorAll('.mermaid');
        if (nodes.length === 0) return;
        try {
            window.mermaid.run({ nodes });
        } catch (e) {
            console.error('Erreur Mermaid:', e);
        }
    }

    // Fonction pour mettre à jour l'aperçu
    async function updatePreview() {
        const markdownText = markdownInput.value;
        try {
            // URL relative : fonctionne aussi si l'app est servie dans un sous-dossier.
            const response = await fetch('render', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `markdown=${encodeURIComponent(markdownText)}`
            });
            if (response.ok) {
                const htmlContent = await response.text();
                markdownPreview.innerHTML = htmlContent;
                renderMermaid();
            } else {
                markdownPreview.innerHTML = '<p class="error">Erreur lors du rendu du Markdown.</p>';
                console.error('Erreur de rendu:', response.statusText);
            }
        } catch (error) {
            markdownPreview.innerHTML = '<p class="error">Erreur de connexion au serveur.</p>';
            console.error('Erreur de connexion:', error);
        }
    }

    // Mettre à jour l'aperçu lors de la saisie
    if (markdownInput) {
        markdownInput.addEventListener('input', updatePreview);
        // Premier rendu au chargement si du texte est déjà présent (ex: après rechargement)
        if(markdownInput.value) {
            updatePreview();
        }
    }

    // Gestion du changement de thème
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', () => {
            document.body.classList.toggle('theme-dark');
            // Sauvegarder la préférence de thème (optionnel)
            if (document.body.classList.contains('theme-dark')) {
                localStorage.setItem('theme', 'dark');
            } else {
                localStorage.setItem('theme', 'light');
            }
        });

        // Appliquer le thème sauvegardé au chargement
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('theme-dark');
        } else {
            document.body.classList.remove('theme-dark'); // Assure le thème clair par défaut
        }
    }

    // Mettre à jour le contenu Markdown dans le formulaire d'export avant soumission
    if (exportForm && markdownInput && exportMarkdownContentField) {
        exportForm.addEventListener('submit', () => {
            exportMarkdownContentField.value = markdownInput.value;
        });
    }
});