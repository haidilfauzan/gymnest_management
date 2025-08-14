from odoo import models, fields, _

class GymnestUser(models.Model):
    _name = 'gymnest.user'
    _inherits = {'res.users': 'user_id'}
    _description = 'Gymnest User'

    user_id = fields.Many2one('res.users', string='User ID')
    user_type = fields.Selection(string='Type',selection=[('member', 'Member'), ('gym', 'gym'),
                                                 ('manager', 'Manager')], tracking=True)
    gender = fields.Selection(string='Gender', selection=[('male', 'Male'), ('female', 'Female')], required=True,
                              tracking=True)
    date_of_birth = fields.Date(string='Date Of Birth', required=True, tracking=True)
    mobile_number = fields.Char(string='Phone Number', tracking=True)
    address = fields.Char(string='Address', tracking=True)
    geolocation = fields.Char(string='Geolocation (Lat,Lng)')
    height = fields.Float(string='Height')
    weight = fields.Float(string='Weight')
    age = fields.Integer(string='Age')
    join_date = fields.Date(string='Join Date', default=fields.Date.context_today, )
    state = fields.Selection(string='Status', selection=[('draft', 'Draft'), ('active', 'Active'), ('withdraw', 'Withdraw'), ('inactive', 'Inactive'), ('blacklist', 'Blacklist')], default='draft', tracking=True)  # state
    membership_ids = fields.One2many('gym.membership', 'member_id',string='Memberships')
    register_ids = fields.One2many('gym.register', 'member_id',string='Registers')
    state_id = fields.Many2one('gymnest.state', string='Province')
    city_id = fields.Many2one(
        'gymnest.city',
        string='City',
        domain="[('state_id', '=', state_id)]"  # Domain dinamis
    )