from markdown_it import MarkdownIt
from markdown_it.common.utils import escapeHtml
import mdit_py_plugins.footnote
import mdit_py_plugins.deflist
import mdit_py_plugins.front_matter


def _build_md():
    """
    Construit l'instance MarkdownIt (réutilisée pour toutes les requêtes).

    Extensions activées:
    - table: Tableaux GitHub Flavored Markdown
    - strikethrough: Texte barré ~~texte~~
    - linkify: Détection automatique des liens (nécessite linkify-it-py)
    - breaks: Sauts de ligne automatiques
    - footnote: Notes de bas de page [^1]
    - deflist: Listes de définitions
    - front_matter: Métadonnées YAML en en-tête

    Sécurité: le preset 'default' garde html=False, donc le HTML brut présent
    dans le Markdown est échappé au lieu d'être injecté tel quel (anti-XSS).
    """
    md = (MarkdownIt('default', {'breaks': True, 'linkify': True, 'html': False})
          .enable(['table', 'strikethrough'])
          .use(mdit_py_plugins.footnote.footnote_plugin)
          .use(mdit_py_plugins.deflist.deflist_plugin)
          .use(mdit_py_plugins.front_matter.front_matter_plugin))

    # Rendre les blocs ```mermaid en <div class="mermaid"> pour que mermaid.js
    # puisse les détecter. Le contenu est échappé : le navigateur le ré-interprète
    # via textContent, donc le diagramme reste correct sans risque d'injection.
    default_fence = md.renderer.rules.get('fence', md.renderer.fence)

    def render_fence(tokens, idx, options, env):
        token = tokens[idx]
        if token.info.strip().lower() == 'mermaid':
            return f'<div class="mermaid">{escapeHtml(token.content)}</div>\n'
        return default_fence(tokens, idx, options, env)

    md.renderer.rules['fence'] = render_fence
    return md


_MD = _build_md()


def to_html(markdown_text):
    """Convertit du texte Markdown en fragment HTML (sans <html>/<body>)."""
    return _MD.render(markdown_text)


# Exemple d'utilisation si vous voulez tester ce module directement
if __name__ == '__main__':
    sample_markdown = """# Test

| A | B |
|---|---|
| 1 | 2 |

Texte ~~barré~~ et lien https://example.com

```mermaid
graph TD
    A[Markdown] --> B[HTML]
```
"""
    print(to_html(sample_markdown))
