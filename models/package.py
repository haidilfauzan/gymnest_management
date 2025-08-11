from odoo import models, fields, api, _

class GymPackages(models.Model):
    _name = 'gym.packages'
    _description = 'Gym Packages'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    gym_id = fields.Many2one('gym.gym', string='Gym')
    is_active = fields.Boolean(default=True)
    price = fields.Float(string='Price')
    duration = fields.Integer('Duration', required=True, default=2)
    unit_duration = fields.Selection([('hour','Hour'),('day','Day'),('week','Week'),('month','Month'),('year', 'Year')], string='Unit Duration', default='day', required=True)
    package_type = fields.Many2one('packages.type', string='Type')

class PackagesType(models.Model):
    _name = 'packages.type'
    _description = 'Packages Type'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    certain_entries = fields.Boolean(default=True)