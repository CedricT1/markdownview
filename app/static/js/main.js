document.addEventListener('DOMContentLoaded', () => {
    const markdownInput = document.getElementById('markdown-input');
    const markdownPreview = document.getElementById('markdown-preview');
    const themeToggleButton = document.getElementById('theme-toggle');
    const exportForm = document.getElementById('export-form');
    const exportMarkdownContentField = document.getElementById('export-markdown-content');
    const editorStats = document.getElementById('editor-stats');

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

    // Compteur de mots / caractères
    function updateStats() {
        if (!editorStats) return;
        const text = markdownInput.value;
        const words = text.trim() ? text.trim().split(/\s+/).length : 0;
        const chars = text.length;
        const pl = (n) => (n > 1 ? 's' : '');
        editorStats.textContent = `${words} mot${pl(words)} · ${chars} caractère${pl(chars)}`;
    }

    // Met à jour l'aperçu (rendu serveur)
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

    // Anti-rebond : on évite de requêter /render à chaque frappe.
    let renderTimer = null;
    function scheduleRender() {
        clearTimeout(renderTimer);
        renderTimer = setTimeout(updatePreview, 180);
    }

    if (markdownInput) {
        markdownInput.addEventListener('input', () => {
            updateStats();
            scheduleRender();
        });
        // Rendu initial (le textarea contient un document de bienvenue)
        updateStats();
        if (markdownInput.value) {
            updatePreview();
        }
    }

    // Gestion du thème
    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', () => {
            const isDark = document.body.classList.toggle('theme-dark');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
        });

        // Thème sauvegardé, sinon préférence système
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia
            && window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
            document.body.classList.add('theme-dark');
        } else {
            document.body.classList.remove('theme-dark');
        }
    }

    // Injecte le Markdown courant dans le formulaire d'export avant soumission
    if (exportForm && markdownInput && exportMarkdownContentField) {
        exportForm.addEventListener('submit', () => {
            exportMarkdownContentField.value = markdownInput.value;
        });
    }
});
