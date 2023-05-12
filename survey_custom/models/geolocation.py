from odoo import _, api, fields, models

class Geolocation(models.Model):
    _name = 'geolocation'
    _description = 'Geolocation'
    
    name = fields.Char('name', compute='_compute_name_longitude_latitude')
    # * Longitud y latitud
    longitude = fields.Float('Longitude', digits=(12,7))
    latitude = fields.Float('Latitude', digits=(12,7))
    survey_custom_id = fields.Many2one('survey.custom', string='Survey Custom')

    def _compute_name_longitude_latitude(self):
        for record in self:
            record.name = f"{record.longitude}:{record.latitude}"