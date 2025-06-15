import os
from weasyprint import HTML, CSS
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse
import datetime


def render_pdf_view(template_path, context, filename="report.pdf"):
    html_string = render_to_string(template_path, context)
    html = HTML(string=html_string)
    css_path = os.path.join(settings.BASE_DIR, 'static', 'css', 'pdf.css')
    css = CSS(filename=css_path)
    pdf_file = html.write_pdf(stylesheets=[css])

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def parse_date_range(request):
    from_date = request.GET.get("from")
    to_date = request.GET.get("to")
    
    try:
        from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date() if from_date else None
        to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date() if to_date else None
    except ValueError:
        from_date = to_date = None

    return from_date, to_date
