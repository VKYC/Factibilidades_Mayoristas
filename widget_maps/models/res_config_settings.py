from odoo import _, api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'Res Config Settings'
    
    google_maps_api_key = fields.Char('Google Maps APi Key')
    # , related='company_id.google_maps_api_key', readonly=False

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['google_maps_api_key'] = self.env['ir.config_parameter'].sudo().get_param('widget_maps.google_maps_api_key', default='')
        return res

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('widget_maps.google_maps_api_key', (self.google_maps_api_key or '').strip())
        super(ResConfigSettings, self).set_values()  
