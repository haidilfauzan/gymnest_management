from odoo import models, fields, api, _
import qrcode
import base64
from io import BytesIO
import uuid # Impor uuid untuk kode unik

class GymMembership(models.Model):
    _name = 'gym.membership'
    _description = 'Gym Membership'

    name = fields.Char(string='Name', compute='_compute_name', store=True, readonly=True)
    member_id = fields.Many2one('gymnest.user', string='Member')
    start_datetime = fields.Datetime(string='Date Join', required=True, default=fields.Datetime.now )
    end_datetime = fields.Datetime(string='End Join',)
    package_id = fields.Many2one('gym.packages', string='Package')
    state = fields.Selection(selection=[('draft', 'Draft'),('active', 'Active'),('expired', 'Expired'),],default='draft',string='Status')
    membership_code = fields.Char(string='membership_code', )

     # Field baru untuk menyimpan gambar QR code
    qr_code = fields.Binary(string="QR Code", readonly=True)
    # download_url = fields.Char(string="Download URL", compute='_compute_download_url')

    # def _compute_download_url(self):
    #     for rec in self:
    #         rec.download_url = f'/gym/download_qr/{rec.id}'

    @api.depends('member_id.name', 'package_id.name', 'package_id.gym_id.name', 'start_datetime')
    def _compute_name(self):

        for rec in self:
            # Mengambil nama gym dari relasi package_id -> gym_id
            gym_name = rec.package_id.gym_id.name if rec.package_id and rec.package_id.gym_id else ''
            # Mengambil nama paket
            package_name = rec.package_id.name if rec.package_id else ''
            # Mengambil nama member
            member_name = rec.member_id.name if rec.member_id else 'New'
            # Mengambil dan memformat tanggal join
            join_date = rec.start_datetime.strftime('%Y-%m-%d') if rec.start_datetime else ''
            # Menggabungkan semua bagian menjadi satu nama
            rec.name = f"{member_name} - {gym_name} - {package_name} - {join_date}"

    def action_generate_qr_code(self):
        """
        Fungsi ini akan dipanggil oleh tombol di form view.
        """
        for rec in self:
            # Generate kode unik jika belum ada
            if not rec.membership_code:
                rec.membership_code = str(uuid.uuid4())

            # Generate QR Code dari membership_code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(rec.membership_code)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            
            # Simpan gambar ke dalam buffer
            temp = BytesIO()
            img.save(temp, format="PNG")
            
            # Konversi gambar ke base64 dan simpan ke field qr_code
            qr_image = base64.b64encode(temp.getvalue())
            rec.qr_code = qr_image
        return True

class GymRegister(models.Model):
    _name = 'gym.register'
    _description = 'Gym register'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('gym.register') or _('New')
        return super().create(vals_list)

    name = fields.Char(string='Name', default=lambda s: s.env._('New'), readonly=True,)
    gym_id = fields.Many2one('gym.gym', string='Gym')
    member_id = fields.Many2one('gymnest.user', string='Member',domain="[('state', '=', 'active')]")
    add_payment_ids = fields.One2many('add.payment', 'payment_id', string='Addional Payments')
    state = fields.Selection([('draft','Draft'),('registered','Registered'),('cancel','Canceled')], string='Status', default='draft',)
    total = fields.Float(string='Total',compute="_compute_total")

    @api.depends('add_payment_ids','add_payment_ids.amount')
    def _compute_total(self):
        for record in self:
            total = 0
            if record.add_payment_ids:
                total = sum(payment.amount for payment in record.add_payment_ids)
            record.total = total

    def register_action(self):
        for record in self:
            if record.state != 'registered':
                record.state = 'registered'

    def cancel_action(self):
        for record in self:
            if record.state != 'cancel':
                record.state = 'cancel'

    def draft_action(self):
        for record in self:
            if record.state != 'draft':
                record.state = 'draft'

class AddPayments(models.Model):
    _name = 'add.payment'
    _description = 'Addional Payments'

    item_id = fields.Many2one('gym.item', string='Item')
    qty = fields.Integer('Qty', required=True, default=0)
    price = fields.Float(string='Price',compute="_compute_price")
    amount = fields.Float(string='Amount',compute="_compute_amount")
    payment_id = fields.Many2one('gym.register', string='Payment')

    @api.depends('item_id')
    def _compute_price(self):
        for payment in self:
            price = 0
            if payment.item_id:
                price = payment.item_id.price
            payment.price = price

    @api.depends('qty', 'price')
    def _compute_amount(self):
        for payment in self:
            amount = 0
            if payment.price and payment.qty:
                amount = payment.price * payment.qty
            payment.amount = amount
