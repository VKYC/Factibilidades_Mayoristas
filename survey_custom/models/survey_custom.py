from odoo import _, api, fields, models
from odoo.exceptions import UserError

class SurveyCustom(models.Model):
    _name = 'survey.custom'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Survey Custom'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('cancel', 'Cancel'),
    ], string='state', default='draft', readonly=True, copy=False, index=True, tracking=3)

    # * World
    name = fields.Char('Nombre', related='partner_id.name')
    
    assigned_zone_cl_id = fields.Many2one('assigned.zone.cl', string='Zona asignada')
    applicant_world_partner_id = fields.Many2one('res.partner', string='Solicitante Mundo')
    applicant_type_world = fields.Selection([
        ('business_area', 'Área empresas'),
        ('public_affairs_area', 'Área asuntos públicos'),
        ('project_area_wholesalers', 'Área proyecto mayoristas'),
        ('management _area', 'Área gerencias'),
    ], string='Tipo Solicitante Mundo')
    points_request_number = fields.Integer('Cantidad de puntos solicitados', required=True)
    application_datetime = fields.Datetime('Fecha de solicitud')

    # * Applicant Identification
    partner_id = fields.Many2one('res.partner', string='Socio')
    # applicant_name = fields.Char('Empresa o Entidad Solicitante')
    # applicant_type = fields.Selection([
    #     ('public', 'Público'),
    #     ('private', 'Privado'),
    #     ('natural_person', 'Persona natural'),
    # ], string='Tipo Empresa o Entidad Solicitante')
    # contact_name = fields.Char('Nombre Contacto')
    # phone = fields.Char('Teléfono de contacto')
    # email = fields.Char('Correo Electrónico Empresa o Entidad Solicitante')
    # service_type_requested = fields.Selection([
    #     ('dedicated', 'Dedicado'),
    #     ('extended_ftth', 'FTTH extendido'),
    #     ('ftth', 'FTTH'),
    # ], string='Tipo de Servicio Solicitado')
    observations    = fields.Text('Observaciones (Opcional)')
    file = fields.Binary('Adjuntar documentación')

    # * Ubication
    address = fields.Char('Dirección', required=True)
    comuna_id = fields.Many2one('res.city', string='Comuna', required=True)
    geolocation = fields.Char('Geolocalización de Empresa o Entidad Solicitante')
    requires_access_validation = fields.Boolean('¿Requiere validación de acceso?')
    priority = fields.Selection([
        ('high', 'Alta'),
        ('medium', 'Media'),
        ('low', 'Baja'),
    ], string='Prioridad')


    @api.constrains('points_request_number')
    def _constrains_points_request_number(self):
        for record in self:
            if record.points_request_number <= 0:
                raise UserError("La cantidad de puntos debe de ser mayor a 0.")
   

    def action_confirm(self):
        # vals={

        # }
        # self.env[model].create(vals)
        self.write({'state': 'confirm'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_draft(self):
        self.write({'state': 'draft'})

