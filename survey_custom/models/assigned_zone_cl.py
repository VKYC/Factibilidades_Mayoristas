from odoo import _, api, fields, models

class AssignedZoneCl(models.Model):
    _name = 'assigned.zone.cl'
    _description = 'Assigned Zone Cl'
    
    name = fields.Char('name')