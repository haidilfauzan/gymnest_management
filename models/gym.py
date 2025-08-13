# gym_management/models/gym_models.py
from odoo import models, fields
    # addional_payment_ids = fields.One2many('gym.addional.payment', 'gym_register_id', string='Payment')

class GymAddionalPayment(models.Model):
    _name = 'gym.addional.payment'
    _description = 'Gym Addional Payment'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    gym_id = fields.Many2one('gym.gym', string='Gym')
    user_id = fields.Many2one('gymnest.user', string='Gym')
    total = fields.Float(string='Total Amount')
    addional_payment_line_ids = fields.One2many('gym.addional.payment.lines', 'addional_payment_id', string='Payment line')

class GymAddionalPaymentLines(models.Model):
    _name = 'gym.addional.payment.lines'
    _description = 'Gym Addional Payment Lines'

    item_id = fields.Many2one('gym.item', string='Gym')
    description = fields.Text(string='Description')
    qty = fields.Integer(string='QTY', required=True)
    total = fields.Float(string='Total Amount')
    addional_payment_id = fields.Many2one('gym.addional.payment', string='Payment')

class GymItem(models.Model):
    _name = 'gym.item'
    _description = 'Gym Item'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    price = fields.Float(string='Price')
    gym_id = fields.Many2one('gym.gym', string='Gym')
    register_only = fields.Boolean(default=False, string="Register Only")

class GymFacility(models.Model):
    _name = 'gym.facility'
    _description = 'Gym Facility'

    name = fields.Char(string='Facility Name', required=True)
    description = fields.Text(string='Description')

class GymCompany(models.Model):
    _name = 'gym.company'
    _description = 'Gym Company'

    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email')
    logo = fields.Image(string='Logo')

class GymReview(models.Model):
    _name = 'gym.review'
    _description = 'Gym Review'

    name = fields.Char(string='Reviewer Name', required=True)
    avatar = fields.Image(string='Avatar')
    review = fields.Text(string='Review')
    rating = fields.Selection([
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')
    ], string='Rating')
    # Relasi ke Gym
    gym_id = fields.Many2one('gym.gym', string='Gym')

class GymGallery(models.Model):
    _name = 'gym.gallery'
    _description = 'Gym Gallery'

    name = fields.Char(string='Description', compute='_compute_name', store=True)
    image = fields.Image(string='Image', required=True)
    # Relasi ke Gym
    gym_id = fields.Many2one('gym.gym', string='Gym')

    def _compute_name(self):
        for record in self:
            record.name = f"Image for {record.gym_id.name}" if record.gym_id else "Gallery Image"


class GymGym(models.Model):
    _name = 'gym.gym'
    _description = 'Gym'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    address = fields.Text(string='Address')
    geolocation = fields.Char(string='Geolocation')
    rating = fields.Selection([
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')
    ], string='Average Rating')
    image = fields.Image(string='Main Image')
    item_ids = fields.One2many('gym.item', 'gym_id',
                                                string='Items')

    # --- Relationships ---
    company_id = fields.Many2one(
    'res.company',
    string='Company',
    required=True,
    default=lambda self: self.env.company
)
    # `review_ids` akan otomatis terisi dari field `gym_id` di `gym.review`
    review_ids = fields.One2many('gym.review', 'gym_id', string='Reviews')
    # `gallery_ids` akan otomatis terisi dari field `gym_id` di `gym.gallery`
    gallery_ids = fields.One2many('gym.gallery', 'gym_id', string='Gallery')
    facility_ids = fields.Many2many('gym.facility', string='Facilities')
    gym_package_ids = fields.One2many('gym.packages', 'gym_id', string='Gym Packages')
    state = fields.Selection([('draft','Draft'),('active','Active'),('inactive','Inactive')], string='Status', default='draft',)

