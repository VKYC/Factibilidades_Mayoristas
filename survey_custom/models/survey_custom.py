from odoo import _, api, fields, models
from odoo.exceptions import UserError
import json
from datetime import datetime


class SurveyCustom(models.Model):
    _name = "survey.custom"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin"]
    _description = "Survey Custom"

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Confirm"),
            ("cancel", "Cancel"),
        ],
        string="state",
        default="draft",
        readonly=True,
        copy=False,
        index=True,
        tracking=3,
    )

    # * World
    name = fields.Char("Nombre")

    # assigned_zone_cl_id = fields.Many2one("assigned.zone.cl", string="Zona asignada")
    # applicant_world_partner_id = fields.Many2one(
    #     "res.partner", string="Solicitante Mundo"
    # )
    partner_id = fields.Many2one('res.partner', 'Usuario actualmente conectado', default=lambda self: self.env.user.partner_id.id, readonly=True)
    vat = fields.Char("RUT", related='partner_id.vat', readonly=True)
    street = fields.Char("Dirección", related='partner_id.street', readonly=True)
    phone = fields.Char("Teléfono", related='partner_id.phone', readonly=True)
    email = fields.Char("Correo electrónico", related='partner_id.email', readonly=True)
    company_partner_id = fields.Many2one('res.partner', related='partner_id.parent_id', readonly=True)
    company_vat = fields.Char("RUT", related='partner_id.parent_id.vat', readonly=True)
    company_street = fields.Char("Dirección", related='partner_id.parent_id.street', readonly=True)
    company_phone = fields.Char("Teléfono", related='partner_id.parent_id.phone', readonly=True)
    company_email = fields.Char("Correo electrónico", related='partner_id.parent_id.email', readonly=True)
    # applicant_type_world = fields.Selection(
    #     [
    #         ("business_area", "Área empresas"),
    #         ("public_affairs_area", "Área asuntos públicos"),
    #         ("project_area_wholesalers", "Área proyecto mayoristas"),
    #         ("management _area", "Área gerencias"),
    #     ],
    #     string="Tipo Solicitante Mundo",
    # )
    points_request_number = fields.Integer(
        "Cantidad de puntos solicitados", required=True
    )
    application_date = fields.Date("Fecha de solicitud", required=True)

    # * Applicant Identification
    # partner_id = fields.Many2one("res.partner", string="Socio")
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
    observations = fields.Text("Observaciones (Opcional)")
    file = fields.Binary("Adjuntar documentación")

    # * Ubication
    comuna_id = fields.Many2one("res.city", string="Comuna", required=True)
    geolocation = fields.Char("Geolocalización de Empresa o Entidad Solicitante")
    requires_access_validation = fields.Boolean("¿Requiere validación de acceso?")
    priority = fields.Selection(
        [
            ("high", "Alta"),
            ("medium", "Media"),
            ("low", "Baja"),
        ],
        string="Prioridad",
    )

    # * Solicitud de servicio

    category_id = fields.Many2one('product.category', string='Tipo de servicio')
    product_id = fields.Many2one('product.template', string='Producto', domain="[('categ_id', '=', category_id)]")
    service_speed_id = fields.Many2one('service.speed', string='Velocidad')
    conexion = fields.Selection([
        ('simetrica', 'Simétrica'),
        ('antisimetrica', 'Asimétrica'),
    ], string='Conexión')
    planta_externa = fields.Boolean('Planta Externa')
    planta_interna = fields.Boolean('Planta Interna')
    adquisiciones = fields.Boolean('Adquisiciones')
    ingenieria = fields.Boolean('Ingenieria')

    @api.onchange('category_id')
    def _onchange_category(self):
        # self.product_id = False
        self.product_id = False
        # return {'domain': {'product_id': []}}
        # return {'domain': {'product_id': [('categ_id', '=', self.category_id.id)]}}

    # * Longitud y latitud
    address = fields.Char(
        "Dirección",
        required=True,
        compute="_compute_longitude_latitude",
        inverse="_inverse_geolocation_address",
        store=True,
        readonly=False,
    )
    longitude = fields.Float(
        "Longitude",
        compute="_compute_longitude_latitude",
        inverse="_inverse_geolocation_longitude_latitude",
        store=True,
        digits=(12, 7),
        readonly=False,
    )
    latitude = fields.Float(
        "Latitude",
        compute="_compute_longitude_latitude",
        inverse="_inverse_geolocation_longitude_latitude",
        store=True,
        digits=(12, 7),
        readonly=False,
    )
    zoom = fields.Float(
        "Zoom",
        compute="_compute_longitude_latitude",
        inverse="_inverse_geolocation_address",
        store=True,
        readonly=False,
    )
    geolocation_ids = fields.One2many(
        "geolocation", "survey_custom_id", string="geolocation"
    )

    @api.depends("geolocation")
    def _compute_longitude_latitude(self):
        for record in self:
            if record.geolocation:
                loc = json.loads(record.geolocation)
                position = loc.get("position")
                record.longitude = position.get("lng")
                record.latitude = position.get("lat")
                record.zoom = loc.get("zoom")
                record.address = loc.get(
                    "autocomplete", f"{record.longitude}:{record.latitude}"
                )
            else:
                record.longitude = 0
                record.latitude = 0
                record.zoom = 0
                record.address = ""

    @api.onchange("address", "zoom")
    def _inverse_geolocation_address(self):
        for record in self:
            geolocation = {
                "position": {
                    "lng": record.longitude,
                    "lat": record.latitude,
                },
                "autocomplete": record.address,
                "zoom": record.zoom,
            }
            record.geolocation = json.dumps(geolocation)
            if record.address != '':
                self.env["bus.bus"]._sendone(
                    self.env.user.partner_id,
                    "onchange_address",
                    {},
                )

    @api.onchange("longitude", "latitude")
    def _inverse_geolocation_longitude_latitude(self):
        for record in self:
            geolocation = {
                "position": {
                    "lng": record.longitude,
                    "lat": record.latitude,
                },
                "autocomplete": record.address,
                "zoom": record.zoom,
            }
            record.geolocation = json.dumps(geolocation)
            self.env["bus.bus"]._sendone(
                self.env.user.partner_id,
                "onchange_longitude_latitude",
                {},
            )

    def add_geolocation(self):
        record_data = {
            "longitude": self.longitude,
            "latitude": self.latitude,
            "address": self.address,
        }
        if self.points_request_number > len(self.geolocation_ids):
            self.geolocation_ids = [(0, 0, record_data)]
        else:
            raise UserError(
                "Está intentando agregando una cantidad de geolocalizaciones mayor a la cantidad de puntos solicitados."
            )

    @api.constrains("points_request_number")
    def _constrains_points_request_number(self):
        for record in self:
            if record.points_request_number <= 0 or record.points_request_number > 50:
                raise UserError(
                    "La cantidad de puntos debe de ser mayor a 0, ni mayor a 50."
                )

    @api.constrains('application_date')
    def _constrains_application_date(self):
        for record in self:
            if record.application_date < datetime.now().date():
                raise UserError(
                    "La fecha de solicitud no puede ser menor a la fecha actual."
                )

    def _constrains_points_request_number_geolocation_ids(
        self,
    ):
        geolocations = self.geolocation_ids
        points_request_number = self.points_request_number

        if len(geolocations) != points_request_number:
            raise UserError(
                "La cantidad de geolocalizaciones agregadas es menor a la cantidad de puntos solicitados."
            )

    def action_confirm(self):
        # vals={

        # }
        # self.env[model].create(vals)
        self._constrains_points_request_number_geolocation_ids()
        self.write({"state": "confirm"})

    def action_cancel(self):
        self.write({"state": "cancel"})

    def action_draft(self):
        self.write({"state": "draft"})

    def unlink(self):
        if self.state == "confirm":
            raise UserError("No puede eliminar un registro confirmado.")
        return super(SurveyCustom, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "seq.factibilidades"
            ) or _("New")
        return super(SurveyCustom, self).create(vals)
