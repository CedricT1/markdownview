import base64
import html
import ipaddress
import os
import re
import socket
import subprocess
import tempfile
import urllib.request
from io import BytesIO
from urllib.parse import urlparse

from weasyprint import HTML as WeasyHTML, default_url_fetcher

from .markdown_processor import to_html as markdown_to_html

# CSS du projet, inliné dans les exports pour un rendu cohérent et portable.
_CSS_PATH = os.path.join(os.path.dirname(__file__), '..', 'static', 'css', 'style.css')

# Service Kroki (rendu serveur des diagrammes Mermaid -> image), pour PDF/ODT.
_KROKI_URL = os.environ.get('KROKI_URL', 'http://kroki:8000').rstrip('/')
_KROKI_TIMEOUT = 30  # Kroki/Chromium peut être lent au premier rendu (démarrage à froid)

# Mermaid n'est rendu côté navigateur (JS) que pour l'aperçu et l'export HTML.
_MERMAID_SCRIPT = (
    '<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>'
    '<script>mermaid.initialize({startOnLoad: true, securityLevel: "strict"});</script>'
)

# <div class="mermaid">SOURCE_ECHAPPEE</div> produit par markdown_processor.
_MERMAID_DIV = re.compile(r'<div class="mermaid">(.*?)</div>', re.DOTALL)
# Bloc ```mermaid ... ``` dans le Markdown source (pour le pré-traitement ODT).
_MERMAID_FENCE = re.compile(
    r'^[ \t]*```[ \t]*mermaid[ \t]*\n(.*?)\n[ \t]*```[ \t]*$',
    re.MULTILINE | re.DOTALL,
)


class ExportError(Exception):
    """Erreur métier d'export, à traduire en réponse HTTP par la route."""


def _load_css():
    try:
        with open(_CSS_PATH, encoding='utf-8') as f:
            return f.read()
    except OSError:
        return ''


_EXPORT_CSS = _load_css()


def _kroki_render(source, fmt):
    """Rend une source Mermaid en image via Kroki. fmt = 'svg' ou 'png'. Renvoie des bytes."""
    req = urllib.request.Request(
        f"{_KROKI_URL}/mermaid/{fmt}",
        data=source.encode('utf-8'),
        headers={'Content-Type': 'text/plain'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=_KROKI_TIMEOUT) as resp:
        return resp.read()


def _render_mermaid_png_in_html(html_fragment):
    """
    Remplace les <div class="mermaid"> par le PNG rendu par Kroki, en data URI (pour le PDF).

    On utilise le PNG (rastérisé par Chromium côté Kroki) plutôt que le SVG : les
    labels Mermaid sont des <foreignObject> HTML que WeasyPrint ne sait pas rendre
    (rectangles sans texte). Le PNG contient déjà le texte, le rendu est fiable.
    """
    def repl(match):
        source = html.unescape(match.group(1)).strip()
        try:
            png = _kroki_render(source, 'png')
        except Exception:
            # Kroki indisponible : on retombe sur le code brut du diagramme.
            return f'<pre class="mermaid-fallback">{match.group(1)}</pre>'
        b64 = base64.b64encode(png).decode('ascii')
        return f'<div class="mermaid"><img alt="Diagramme" src="data:image/png;base64,{b64}"></div>'

    return _MERMAID_DIV.sub(repl, html_fragment)


def _replace_mermaid_with_png(markdown_text, tmp_dir):
    """Remplace les blocs ```mermaid du Markdown par des images PNG (pour l'ODT/Pandoc)."""
    counter = {'i': 0}

    def repl(match):
        source = match.group(1).strip()
        try:
            png = _kroki_render(source, 'png')
        except Exception:
            return match.group(0)  # Kroki KO : on laisse le bloc tel quel
        path = os.path.join(tmp_dir, f"mermaid_{counter['i']}.png")
        counter['i'] += 1
        with open(path, 'wb') as f:
            f.write(png)
        return f"![Diagramme]({path})"

    return _MERMAID_FENCE.sub(repl, markdown_text)


def _standalone_html(html_fragment, title, include_mermaid_js):
    mermaid = _MERMAID_SCRIPT if include_mermaid_js and 'class="mermaid"' in html_fragment else ''
    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>{_EXPORT_CSS}</style>
</head>
<body>
    <div class="markdown-body">
{html_fragment}
    </div>
    {mermaid}
</body>
</html>"""


def _safe_url_fetcher(url, *args, **kwargs):
    """
    url_fetcher WeasyPrint anti-SSRF : refuse file:// et les hôtes résolvant
    vers une IP privée/loopback/réservée (empêche un Markdown malveillant de
    faire requêter le réseau interne par le serveur lors d'un export PDF).
    """
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    if scheme == 'data':
        return default_url_fetcher(url, *args, **kwargs)
    if scheme not in ('http', 'https'):
        raise ValueError(f"Schéma d'URL interdit pour l'export : {scheme or '(vide)'}")
    host = parsed.hostname
    if not host:
        raise ValueError("URL sans hôte interdite pour l'export")
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise ValueError(f"Hôte introuvable : {host}") from exc
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            raise ValueError("Accès à une adresse réseau interne interdit")
    return default_url_fetcher(url, *args, **kwargs)


def export_html(markdown_text):
    """Exporte le Markdown en document HTML autonome (CSS inliné + Mermaid via JS)."""
    fragment = markdown_to_html(markdown_text)
    return _standalone_html(fragment, "Export HTML", include_mermaid_js=True)


def export_pdf(markdown_text):
    """Convertit le Markdown en flux binaire PDF (Mermaid pré-rendu en SVG via Kroki)."""
    fragment = markdown_to_html(markdown_text)
    fragment = _render_mermaid_png_in_html(fragment)
    full_html = _standalone_html(fragment, "Export PDF", include_mermaid_js=False)
    pdf_file = BytesIO()
    WeasyHTML(string=full_html, url_fetcher=_safe_url_fetcher).write_pdf(pdf_file)
    pdf_file.seek(0)
    return pdf_file


def export_odt(markdown_text):
    """
    Convertit le Markdown en flux binaire ODT via Pandoc (Mermaid pré-rendu en PNG).

    Lève ExportError en cas d'échec (Pandoc absent ou erreur de conversion),
    afin que la route renvoie un vrai code HTTP au lieu d'un .odt corrompu.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        processed = _replace_mermaid_with_png(markdown_text, tmp_dir)
        try:
            process = subprocess.run(
                ['pandoc', '--from=markdown', '--to=odt', '--output=-'],
                input=processed.encode('utf-8'),
                text=False,
                capture_output=True,
                check=True,
            )
            return BytesIO(process.stdout)
        except FileNotFoundError as exc:
            raise ExportError("Pandoc n'est pas installé sur le serveur.") from exc
        except subprocess.CalledProcessError as exc:
            details = exc.stderr.decode('utf-8', 'replace') if exc.stderr else ''
            raise ExportError(f"Échec de la conversion Pandoc : {details}") from exc
