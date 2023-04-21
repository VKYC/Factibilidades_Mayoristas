from odoo import _, api, fields, models
from odoo.http import request

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'
    _description = 'Ir Http'
    
    def webclient_rendering_context(self):
        rendering_context =  super(IrHttp, self).webclient_rendering_context()
        rendering_context['google_maps_api_key'] = request.env['ir.config_parameter'].sudo().get_param('google_maps_api_key')
        return rendering_context
