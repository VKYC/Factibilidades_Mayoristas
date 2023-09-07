from odoo import _, api, fields, models


class ServiceSpeed(models.Model):
    _name = 'service.speed'
    _description = 'Service Speed'

    name = fields.Char(string='Name', required=True)
