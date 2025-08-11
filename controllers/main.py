# gym_management/controllers/main.py
from odoo import http
from odoo.http import request, content_disposition
import base64

class QRCodeDownloader(http.Controller):

    @http.route('/gym/download_qr/<int:membership_id>', type='http', auth="user")
    def download_qr_code(self, membership_id, **kw):
        """
        Controller ini menangani download gambar QR code.
        """
        try:
            membership = request.env['gym.membership'].browse(membership_id)
            if not membership or not membership.qr_code:
                return request.make_response('QR Code not found.', status=404)

            # Decode data base64 dari field
            image_data = base64.b64decode(membership.qr_code)
            
            # Buat header untuk memberitahu browser agar men-download file
            headers = [
                ('Content-Type', 'image/png'),
                ('Content-Disposition', content_disposition(f'qr_code_{membership.membership_code}.png'))
            ]
            
            return request.make_response(image_data, headers)
        except Exception as e:
            return request.make_response(str(e), status=500)