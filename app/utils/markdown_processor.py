from markdown_it import MarkdownIt
import mdit_py_plugins.footnote
import mdit_py_plugins.deflist  
import mdit_py_plugins.front_matter

def to_html(markdown_text):
    """
    Convertit du texte Markdown en HTML avec des extensions avancées.
    
    Extensions activées:
    - table: Tableaux GitHub Flavored Markdown
    - strikethrough: Texte barré ~~texte~~
    - linkify: Détection automatique des liens
    - breaks: Sauts de ligne automatiques
    - footnote: Notes de bas de page [^1]
    - deflist: Listes de définitions
    - front_matter: Métadonnées YAML en en-tête
    """
    md = (MarkdownIt('commonmark', {'breaks': True, 'linkify': True})
          .enable(['table', 'strikethrough'])
          .use(mdit_py_plugins.footnote.footnote_plugin)
          .use(mdit_py_plugins.deflist.deflist_plugin)
          .use(mdit_py_plugins.front_matter.front_matter_plugin))
    
    html = md.render(markdown_text)
    
    # Support Mermaid : ajouter le JavaScript si nécessaire
    if '```mermaid' in markdown_text:
        mermaid_script = """
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script>
    mermaid.initialize({
        startOnLoad: true,
        theme: 'default',
        securityLevel: 'loose'
    });
</script>
"""
        html = html + mermaid_script
    
    return html

# Exemple d'utilisation si vous voulez tester ce module directement
if __name__ == '__main__':
    sample_markdown = """---
title: Test Document
author: Système
---

# Extensions Markdown avancées

## Tableaux
| Fonctionnalité | Status | Description |
|----------------|--------|-------------|
| Tables | ✅ Actif | Tableaux GitHub |
| Notes | ✅ Actif | Notes de bas de page |
| Strikethrough | ✅ Actif | Texte ~~barré~~ |
| Mermaid | ✅ Actif | Diagrammes |

## Texte formaté
Voici du texte ~~barré~~, du **gras** et de l'*italique*.

## Notes de bas de page
Ceci contient une note[^1] importante avec plus de détails[^2].

[^1]: Voici la première note de bas de page.
[^2]: Et voici une seconde note avec plus d'informations.

## Listes de définitions
Markdown
: Un langage de balisage léger pour formater du texte

HTML
: HyperText Markup Language
: Le langage standard du web

CSS
: Cascading Style Sheets
: Pour styliser les pages web

## Détection automatique de liens
Visitez https://www.example.com ou mailto:test@example.com automatiquement.

## Diagramme Mermaid
```mermaid
graph TD
    A[Markdown] --> B[Processeur]
    B --> C[HTML]
    C --> D[Rendu]
    D --> E[Affichage]
```
"""
    
    print("=== HTML généré avec toutes les extensions ===")
    html_output = to_html(sample_markdown)
    print(html_output)