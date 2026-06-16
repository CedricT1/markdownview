from flask import render_template, request, Response, send_file
from .utils import markdown_processor
from .utils import export_service


def init_app(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/render', methods=['POST'])
    def render_markdown():
        markdown_text = request.form.get('markdown', '')
        try:
            html_content = markdown_processor.to_html(markdown_text)
        except Exception as exc:  # rendu défensif : ne jamais renvoyer un 500 brut
            app.logger.exception("Erreur de rendu Markdown")
            return Response(
                f'<p class="error">Erreur lors du rendu : {exc}</p>',
                status=500,
                mimetype='text/html',
            )
        return Response(html_content, mimetype='text/html')

    @app.route('/export/<format_type>', methods=['POST'])
    def export_file(format_type):
        markdown_text = request.form.get('markdown', '')

        if format_type == 'html':
            html_content = export_service.export_html(markdown_text)
            return Response(
                html_content,
                mimetype='text/html',
                headers={"Content-Disposition": "attachment;filename=export.html"},
            )
        elif format_type == 'pdf':
            pdf_content_stream = export_service.export_pdf(markdown_text)
            return send_file(
                pdf_content_stream,
                mimetype='application/pdf',
                as_attachment=True,
                download_name='export.pdf',
            )
        elif format_type == 'odt':
            try:
                odt_content_stream = export_service.export_odt(markdown_text)
            except export_service.ExportError as exc:
                return Response(f"Erreur d'export ODT : {exc}", status=500)
            return send_file(
                odt_content_stream,
                mimetype='application/vnd.oasis.opendocument.text',
                as_attachment=True,
                download_name='export.odt',
            )
        else:
            return "Format d'export non supporté", 400
