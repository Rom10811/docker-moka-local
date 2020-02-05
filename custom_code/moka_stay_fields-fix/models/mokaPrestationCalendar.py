
from odoo import models, fields, api

class MokaPrestationCalendar(models.Model):
    #Add a link between a calendar event and a sale order
    _inherit = 'calendar.event'

    #add the field for the link
    crm_id = fields.Many2one('crm.lead', 'CRM', ondelete='cascade')

    @api.multi
    def open_linked_crm(self):
        #Redirect the user at the page of the linked crm
        self.ensure_one()
        #Get the id of the crm
        crm_id_tempo = self.crm_id.id

        return{
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'views': [[False, "form"]],
            'res_id': crm_id_tempo
        }
