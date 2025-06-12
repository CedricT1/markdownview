from markdown_it import MarkdownIt

def to_html(markdown_text):
    """
    Convertit du texte Markdown en HTML.
    """
    md = MarkdownIt('commonmark', {'breaks': True, 'linkify': True})
    md.enable(['table'])
    html = md.render(markdown_text)
    return html

# Exemple d'utilisation si vous voulez tester ce module directement
if __name__ == '__main__':
    sample_markdown = """
# Titre de niveau 1
## Titre de niveau 2

Ceci est un paragraphe avec du **gras** et de l'*italique*.

- Liste à puces 1
- Liste à puces 2

1. Liste numérotée 1
2. Liste numérotée 2

```python
def hello():
    print("Hello, Markdown!")
```
"""
    html_output = to_html(sample_markdown)
    print(html_output)