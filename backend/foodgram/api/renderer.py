from django.utils.encoding import smart_str
from rest_framework.renderers import BaseRenderer


class PDFRenderer(BaseRenderer):
    media_type = 'application/pdf'
    format = 'pdf'
    charset = 'None'
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class TextRenderer(BaseRenderer):
    media_type = 'text/plain'
    format = 'txt'
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return smart_str(data, encoding=self.charset)
