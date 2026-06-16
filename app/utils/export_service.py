import ipaddress
import os
import socket
import subprocess
from io import BytesIO
from urllib.parse import urlparse

from weasyprint import HTML as WeasyHTML, default_url_fetcher

from .markdown_processor import to_html as markdown_to_html

# CSS du projet, inliné dans les exports pour un rendu cohérent et portable.
_CSS_PATH = os.path.join(os.path.dirname(__file__), '..', 'static', 'css', 'style.css')

# Mermaid n'est rendu que côté navigateur (JS) : utile pour l'export HTML,
# inutile pour le PDF (WeasyPrint n'exécute pas de JavaScript).
_MERMAID_SCRIPT = (
    '<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>'
    '<script>mermaid.initialize({startOnLoad: true, securityLevel: "strict"});</script>'
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


def _standalone_html(html_fragment, title, include_mermaid):
    mermaid = _MERMAID_SCRIPT if include_mermaid and 'class="mermaid"' in html_fragment else ''
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
    """Exporte le Markdown en document HTML autonome (CSS inliné + Mermaid)."""
    fragment = markdown_to_html(markdown_text)
    return _standalone_html(fragment, "Export HTML", include_mermaid=True)


def export_pdf(markdown_text):
    """Convertit le Markdown en flux binaire PDF (stylé, sans accès réseau interne)."""
    fragment = markdown_to_html(markdown_text)
    full_html = _standalone_html(fragment, "Export PDF", include_mermaid=False)
    pdf_file = BytesIO()
    WeasyHTML(string=full_html, url_fetcher=_safe_url_fetcher).write_pdf(pdf_file)
    pdf_file.seek(0)
    return pdf_file


def export_odt(markdown_text):
    """
    Convertit le Markdown en flux binaire ODT via Pandoc.

    Lève ExportError en cas d'échec (Pandoc absent ou erreur de conversion),
    afin que la route renvoie un vrai code HTTP au lieu d'un .odt corrompu.
    """
    try:
        process = subprocess.run(
            ['pandoc', '--from=markdown', '--to=odt', '--output=-'],
            input=markdown_text.encode('utf-8'),
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
