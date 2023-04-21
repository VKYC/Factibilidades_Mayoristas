from odoo import _, api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'
    _description = 'Res Company'

   
    google_maps_api_key = fields.Char(string="Google Maps APi Key", copy=True)
