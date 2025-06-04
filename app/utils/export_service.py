import subprocess
from io import BytesIO
from weasyprint import HTML as WeasyHTML
from .markdown_processor import to_html as markdown_to_html

def export_html(markdown_text):
    """
    Exporte le Markdown en tant que chaîne HTML complète.
    """
    return markdown_to_html(markdown_text)

def export_pdf(markdown_text):
    """
    Convertit le texte Markdown en un flux binaire PDF.
    Pour l'instant, sans CSS spécifique, le rendu sera basique.
    """
    html_content = markdown_to_html(markdown_text)
    
    # WeasyPrint a besoin d'une page HTML complète, même simple
    full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Export PDF</title>
    <!-- Ici, on pourrait lier des CSS pour le PDF -->
</head>
<body>
    {html_content}
</body>
</html>
"""
    pdf_file = BytesIO()
    WeasyHTML(string=full_html).write_pdf(pdf_file)
    pdf_file.seek(0)
    return pdf_file

def export_odt(markdown_text):
    """
    Convertit le texte Markdown en un flux binaire ODT en utilisant Pandoc.
    """
    try:
        process = subprocess.run(
            ['pandoc', '--from=markdown', '--to=odt', '--output=-'],
            input=markdown_text,
            text=True,
            capture_output=True,
            check=True
        )
        odt_content = process.stdout.encode('utf-8') # Pandoc sort du texte, on encode pour le binaire
        return BytesIO(odt_content)
    except FileNotFoundError:
        # Gérer le cas où pandoc n'est pas installé ou non trouvé dans le PATH
        # Pour l'environnement Docker, cela ne devrait pas arriver si bien configuré.
        error_message = "Erreur: Pandoc n'a pas été trouvé. Veuillez vérifier l'installation."
        print(error_message) # Log pour le serveur
        return BytesIO(error_message.encode('utf-8')) # Renvoyer un message d'erreur dans le fichier
    except subprocess.CalledProcessError as e:
        # Gérer les erreurs de Pandoc
        error_message = f"Erreur lors de la conversion avec Pandoc: {e.stderr}"
        print(error_message) # Log pour le serveur
        return BytesIO(error_message.encode('utf-8')) # Renvoyer un message d'erreur dans le fichier

# Exemple d'utilisation
if __name__ == '__main__':
    sample_md = "# Test ODT\nCeci est un test."
    
    # Test HTML
    # html_data = export_html(sample_md)
    # print("HTML Output:\n", html_data)

    # Test PDF (nécessite les dépendances WeasyPrint)
    # try:
    #     pdf_data_stream = export_pdf(sample_md)
    #     with open("test_export.pdf", "wb") as f:
    #         f.write(pdf_data_stream.read())
    #     print("PDF 'test_export.pdf' généré.")
    # except Exception as e:
    #     print(f"Erreur lors de la génération PDF: {e}")

    # Test ODT (nécessite Pandoc)
    try:
        odt_data_stream = export_odt(sample_md)
        with open("test_export.odt", "wb") as f:
            f.write(odt_data_stream.read())
        print("ODT 'test_export.odt' généré.")
    except Exception as e:
        print(f"Erreur lors de la génération ODT: {e}")