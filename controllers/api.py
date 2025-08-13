# gym_management/controllers/api.py
import base64
import logging  # <-- 1. Impor library logging
from odoo import http
from odoo.http import request
from dateutil.relativedelta import relativedelta
from datetime import datetime

_logger = logging.getLogger(__name__)  # <-- 2. Inisialisasi logger

class GymAPI(http.Controller):

    def _to_base64_url(self, binary_data):
        if not binary_data:
            return None
        return f"data:image/png;base64,{binary_data.decode('utf-8')}"

    @http.route('/api/gyms', type='json', auth='user', methods=['POST'], csrf=False)
    def get_all_gyms(self, **kw):
        query = kw.get('query', '')
        limit = kw.get('limit')

        try:
            domain = []
            if query:
                domain = [
                    '|',
                    ('name', 'ilike', query),
                    ('description', 'ilike', query)
                ]
            
            gyms_recs = request.env['gym.gym'].search(domain, limit=limit)
            
            gyms_data = []
            for gym in gyms_recs:
                # Blok ini sudah terlihat benar, mencocokkan model dan interface Anda
                reviews = [{'id': r.id, 'name': r.name, 'avatar': self._to_base64_url(r.avatar), 'review': r.review, 'rating': r.rating} for r in gym.review_ids]
                gallery = [{'id': g.id, 'image': self._to_base64_url(g.image)} for g in gym.gallery_ids]
                facilities = [{'id': f.id, 'name': f.name} for f in gym.facility_ids]
                gyms_data.append({
                    'id': gym.id,
                    'name': gym.name,
                    'description': gym.description,
                    'address': gym.address,
                    'geolocation': gym.geolocation,
                    'rating': gym.rating,
                    'image': self._to_base64_url(gym.image),
                    'company': {'id': gym.company_id.id, 'name': gym.company_id.name, 'email': gym.company_id.email, 'logo': self._to_base64_url(gym.company_id.logo)} if gym.company_id else None,
                    'reviews': reviews,
                    'gallery': gallery,
                    'facilities': facilities,
                })

            return {'status': 'success', 'data': gyms_data}

        except Exception as e:
            # 3. Sekarang baris ini akan berfungsi dengan benar
            _logger.error(f"Error fetching gyms API: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}

    # --- FUNGSI BARU UNTUK MENGAMBIL SATU GYM BERDASARKAN ID ---
    @http.route('/api/gyms/<int:gym_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_gym_by_id(self, gym_id, **kw):
        try:
            gym = request.env['gym.gym'].browse(gym_id)
            if not gym.exists():
                return request.make_response('Not Found', status=404)

            # Format data sama seperti sebelumnya, tapi hanya untuk satu record
            reviews = [{'id': r.id, 'name': r.name, 'avatar': self._to_base64_url(r.avatar), 'review': r.review, 'rating': r.rating} for r in gym.review_ids]
            gallery = [{'id': g.id, 'image': self._to_base64_url(g.image)} for g in gym.gallery_ids]
            facilities = [{'id': f.id, 'name': f.name} for f in gym.facility_ids]
            
            # --- BLOK BARU UNTUK MENGAMBIL DATA PACKAGES ---
            packages = []
            for pkg in gym.gym_package_ids:
                packages.append({
                    'id': pkg.id,
                    'name': pkg.name,
                    'description': pkg.description,
                    'price': pkg.price,
                    'duration': pkg.duration,
                    'unit_duration': pkg.unit_duration,
                    'package_type': {
                        'id': pkg.package_type.id,
                        'name': pkg.package_type.name,
                    } if pkg.package_type else None
                })
            # ---------------------------------------------

              # --- BLOK BARU UNTUK MENGAMBIL DATA ITEMS ---
            items = []
            for item in gym.item_ids:
                items.append({
                    'id': item.id,
                    'name': item.name,
                    'price': item.price,
                })
            # -------------------------------------------
            
            gym_data = {
                'id': gym.id,
                'name': gym.name,
                'description': gym.description,
                'address': gym.address,
                'geolocation': gym.geolocation,
                'rating': gym.rating,
                'image': self._to_base64_url(gym.image),
                'company': {'id': gym.company_id.id, 'name': gym.company_id.name, 'email': gym.company_id.email, 'logo': self._to_base64_url(gym.company_id.logo)} if gym.company_id else None,
                'reviews': reviews,
                'gallery': gallery,
                'facilities': facilities,
                'packages': packages,
                'items': items,
            }
            
            # Karena type='http', kita kembalikan response JSON secara manual
            return request.make_json_response({'status': 'success', 'data': gym_data})

        except Exception as e:
            _logger.error(f"Error fetching gym by ID API: {e}", exc_info=True)
            return request.make_response('Internal Server Error', status=500)


    @http.route('/api/gym/apply_membership', type='json', auth='user', methods=['POST'], csrf=False)
    def apply_membership(self, **kw):
        """
        Menerima data dari aplikasi mobile untuk membuat record
        gym.register dan gym.membership.
        Parameter yang diharapkan dari kw:
        - gym_id: int
        - package_id: int
        - items: list of dicts, e.g., [{'item_id': int, 'qty': int}, ...]
        """
       
        try:
            gym_id = kw.get('gym_id')
            package_id = kw.get('package_id')
            items_data = kw.get('items', [])

            if not all([gym_id, package_id]):
                return {'status': 'error', 'message': 'Missing gym_id or package_id.'}

            print('.........................kw',kw)

            # 1. Cari record gymnest.user berdasarkan user yang sedang login (request.uid)
            gymnest_user = request.env['gymnest.user'].search([('user_id', '=', request.uid)], limit=1)
            if not gymnest_user:
                return {'status': 'error', 'message': f"No Gymnest User found for user ID {request.uid}."}

            # 2. Format data add_payment_ids untuk Odoo (One2many create command)
            # Formatnya adalah [(0, 0, {values}), (0, 0, {values}), ...]
            add_payment_vals = []
            for item in items_data:
                if item.get('qty', 0) > 0:
                    add_payment_vals.append((0, 0, {
                        'item_id': item.get('item_id'),
                        'qty': item.get('qty'),
                    }))

            # 3. Buat record baru di gym.register
            register_vals = {
                'gym_id': gym_id,
                'member_id': gymnest_user.id,
                'add_payment_ids': add_payment_vals,
                'state': 'draft',  # Langsung set ke registered
            }
            new_register = request.env['gym.register'].create(register_vals)

            # 4. Buat record baru di gym.membership
            package = request.env['gym.packages'].browse(package_id)
            start_date = datetime.now()
            # Hitung tanggal berakhir berdasarkan durasi paket
            end_date = False
            if package.unit_duration == 'day':
                end_date = start_date + relativedelta(days=package.duration)
            elif package.unit_duration == 'week':
                end_date = start_date + relativedelta(weeks=package.duration)
            elif package.unit_duration == 'month':
                end_date = start_date + relativedelta(months=package.duration)

            membership_vals = {
                'member_id': gymnest_user.id,
                'package_id': package_id,
                'start_datetime': start_date,
                'end_datetime': end_date,
                'state': 'draft',  # Langsung set ke active
            }
            request.env['gym.membership'].create(membership_vals)

            return {'status': 'success', 'message': 'Membership applied successfully!', 'register_id': new_register.id}

        except Exception as e:
            _logger.error(f"Error Applying Membership API: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}


    # --- FUNGSI BARU UNTUK MENGAMBIL PROFIL USER YANG LOGIN ---
    @http.route('/api/user/profile', type='json', auth='user', methods=['POST'], csrf=False)
    def get_user_profile(self, **kw):
        try:
            # request.uid adalah ID dari res.users yang sedang login
            user = request.env['res.users'].browse(request.uid)
            if not user.exists():
                return {'status': 'error', 'message': 'User not found.'}
            
            user_data = {
                'id': user.id,
                'name': user.name,
                'email': user.login,
                # Menggunakan helper untuk format gambar, Odoo menyimpan image_1920
                'image_1920': self._to_base64_url(user.image_1920), 
            }
            return {'status': 'success', 'data': user_data}
        except Exception as e:
            _logger.error(f"Error fetching user profile: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}

    # --- FUNGSI BARU UNTUK UPDATE GAMBAR PROFIL ---
    @http.route('/api/user/profile/update_image', type='json', auth='user', methods=['POST'], csrf=False)
    def update_user_image(self, **kw):
        """
        Mengharapkan payload: {'image_base64': '...data base64...'}
        """
        try:
            image_base64 = kw.get('image_base64')
            if not image_base64:
                return {'status': 'error', 'message': 'No image data provided.'}

            user = request.env['res.users'].browse(request.uid)
            if not user.exists():
                return {'status': 'error', 'message': 'User not found.'}
            
            # Tulis data base64 ke field image_1920
            user.write({'image_1920': image_base64})
            
            return {'status': 'success', 'message': 'Profile picture updated successfully.'}
        except Exception as e:
            _logger.error(f"Error updating user image: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}

    # --- FUNGSI BARU UNTUK MENGAMBIL DAFTAR MEMBERSHIP USER ---
    @http.route('/api/my_memberships', type='http', auth='user', methods=['GET'], csrf=False)
    def get_my_memberships(self, **kw):
        try:
            # Cari gymnest.user yang terhubung dengan res.users yang sedang login
            gymnest_user = request.env['gymnest.user'].search([('user_id', '=', request.uid)], limit=1)
            if not gymnest_user:
                return request.make_json_response({'status': 'success', 'data': []}) # Kembalikan array kosong jika bukan gymnest user

            # Cari semua membership milik user tersebut
            memberships = request.env['gym.membership'].search([('member_id', '=', gymnest_user.id)])
            
            result = []
            for membership in memberships:
                result.append({
                    'id': membership.id,
                    'name': membership.name,
                    'start_datetime': membership.start_datetime.isoformat() if membership.start_datetime else None,
                    'end_datetime': membership.end_datetime.isoformat() if membership.end_datetime else None,
                    'state': membership.state,
                    'package_name': membership.package_id.name,
                })
            
            return request.make_json_response({'status': 'success', 'data': result})
        except Exception as e:
            _logger.error(f"Error fetching my memberships: {e}", exc_info=True)
            return request.make_response('Internal Server Error', status=500)

    # --- FUNGSI BARU UNTUK MENGAMBIL DETAIL SATU MEMBERSHIP ---
    @http.route('/api/membership/<int:membership_id>', type='http', auth='user', methods=['GET'], csrf=False)
    def get_membership_detail(self, membership_id, **kw):
        try:
            membership = request.env['gym.membership'].browse(membership_id)
            # Validasi user
            gymnest_user = request.env['gymnest.user'].search([('user_id', '=', request.uid)], limit=1)
            if not membership.exists() or membership.member_id.id != gymnest_user.id:
                return request.make_response('Not Found or Access Denied', status=404)

            detail = {
                'id': membership.id,
                'name': membership.name,
                'start_datetime': membership.start_datetime.isoformat() if membership.start_datetime else None,
                'end_datetime': membership.end_datetime.isoformat() if membership.end_datetime else None,
                'state': membership.state,
                'package_name': membership.package_id.name,
                'membership_code': membership.membership_code,
                'qr_code': membership.qr_code, # Ini sudah dalam format base64
            }
            return request.make_json_response({'status': 'success', 'data': detail})
        except Exception as e:
            _logger.error(f"Error fetching membership detail: {e}", exc_info=True)
            return request.make_response('Internal Server Error', status=500)

    # --- FUNGSI BARU UNTUK MENGAMBIL PROFIL LENGKAP GYMNEST USER ---
    @http.route('/api/gymnest_user/profile', type='http', auth='user', methods=['GET'], csrf=False)
    def get_gymnest_user_profile(self, **kw):
        try:
            # Cari gymnest.user yang terhubung dengan res.users yang sedang login
            user = request.env['gymnest.user'].search([('user_id', '=', request.uid)], limit=1)
            if not user.exists():
                return request.make_response('Gymnest user profile not found.', status=404)
            
            # Ambil semua data yang dibutuhkan
            profile_data = {
                'id': user.id,
                'name': user.name,
                'email': user.login,
                'image_1920': self._to_base64_url(user.image_1920),
                'user_type': user.user_type,
                'gender': user.gender,
                'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
                'mobile_number': user.mobile_number,
                'address': user.address,
                'geolocation': user.geolocation,
                'height': user.height,
                'weight': user.weight,
                'age': user.age,
                'join_date': user.join_date.isoformat() if user.join_date else None,
                'state': user.state,
            }
            return request.make_json_response({'status': 'success', 'data': profile_data})
        except Exception as e:
            _logger.error(f"Error fetching gymnest user profile: {e}", exc_info=True)
            return request.make_response('Internal Server Error', status=500)

    # --- FUNGSI BARU UNTUK UPDATE PROFIL ---
    @http.route('/api/gymnest_user/update_profile', type='json', auth='user', methods=['POST'], csrf=False)
    def update_gymnest_user_profile(self, **kw):
        """
        Hanya akan mengupdate field yang diizinkan
        """
        try:
            user = request.env['gymnest.user'].search([('user_id', '=', request.uid)], limit=1)
            if not user.exists():
                return {'status': 'error', 'message': 'Gymnest user not found.'}

            # Siapkan dictionary berisi field yang boleh diupdate
            allowed_fields = ['mobile_number', 'address', 'weight', 'height', 'geolocation']
            vals_to_update = {}
            for field in allowed_fields:
                if field in kw:
                    vals_to_update[field] = kw.get(field)
            
            if vals_to_update:
                user.write(vals_to_update)
            
            return {'status': 'success', 'message': 'Profile updated successfully.'}
        except Exception as e:
            _logger.error(f"Error updating gymnest user profile: {e}", exc_info=True)
            return {'status': 'error', 'message': str(e)}