from odoo import fields, models, api
import datetime

class MokaPrestationInvoice(models.Model):
    _inherit='account.invoice'

    #Add fields into a new DB to store the infos about benefits
    moka_is_sejour_invoice = fields.Boolean(string='Packaged benefit',
                                    help='If checked, display all the'
                                          ' the fields and options to'
                                          ' build a benefit order',
                                    compute="_change_stay_fields_invoice_is")
    moka_sejour_titre_invoice = fields.Char(string='Benefit title',
                                    help="Specific title to the current benefit.",
                                    compute="_change_stay_fields_invoice_titre")
    moka_sejour_debut_invoice = fields.Date("Starting day",
                                    help="Starting date and hour of the benefit.",
                                    compute="_change_stay_fields_invoice_sejourd")
    moka_sejour_fin_invoice = fields.Date("Ending day",
                                    help="Ending date and hour of the benefit.",
                                    compute="_change_stay_fields_invoice_sejourf")
    moka_nombre_personnes_invoice = fields.Integer(string="Number of persons",
                                        help="Number of persons participating in"
                                             " the benefit.",
                                        compute="_change_stay_fields_invoice_nbp")
    moka_prix_pp_invoice = fields.Monetary(string="Price / Person",
                                help="The price per person calculated from"
                                     " the number of persons participating in"
                                     " the benefit, and the total price of"
                                     " the benefit. (not displayed in the CRM)",
                                compute="_change_stay_fields_invoice_ppp")
    moka_prix_pp_ht_invoice = fields.Monetary(string="Price / Person HT",
                                help="The price per person calculated from"
                                     " the number of persons participating in"
                                     " the benefit, and the total price of"
                                     " the benefit. (not displayed in the CRM)",
                                compute="_change_stay_fields_invoice_pppht")

    moka_heure_debut_invoice = fields.Float(string='Starting hour',
                                    help="The hour when the benefit will begin."
                                         " If the hour is 00:00, the all journey will"
                                         " be selected, without hours.",
                                    compute="_change_stay_fields_invoice_heured")
    moka_heure_fin_invoice = fields.Float(string="Ending hour",
                                  help="The hour when the benefit will end."
                                       " If the hour is 00:00, the all journey will"
                                       " be selected, without hours.",
                                  compute="_change_stay_fields_invoice_heuref")

    def _get_line(self):
        #Get the line of the sale order linked to the invoice
        return self.env['sale.order'].search([('name', '=', self.origin)], limit=1)

    def _get_hour_end(self, name):
        #Get the hour of the benefit end in the good format

        #Get the current line of the invoice in the DB
        line = self.env['account.invoice'].search([('name', '=', name)], limit=1)
        return str(datetime.timedelta(hours = line.moka_heure_fin_invoice)).rsplit(':', 1)[0]

    def _get_hour_start(self, name):
        #Get the hour of the benefit start in the good format

        #Get the current line of the invoice in the DB
        line = self.env['account.invoice'].search([('name', '=', name)], limit=1)
        return str(datetime.timedelta(hours = line.moka_heure_debut_invoice)).rsplit(':', 1)[0]

    @api.onchange('origin')
    def _change_stay_fields_invoice_is(self):
        #Do the researche in the sale.order model to find the assiociated model's record
        for invoice in self:
            sale_order_line = invoice._get_line()

            if(sale_order_line):
                #Update all the fields in the invoice's model
                invoice.moka_is_sejour_invoice = sale_order_line.moka_is_sejour_devis
                invoice.moka_heure_fin_invoice = sale_order_line.moka_heure_fin_devis
                invoice.moka_sejour_fin_invoice = sale_order_line.moka_sejour_fin_devis
                invoice.moka_heure_debut_invoice = sale_order_line.moka_heure_debut_devis
                invoice.moka_sejour_debut_invoice = sale_order_line.moka_sejour_debut_devis
                invoice.moka_sejour_titre_invoice = sale_order_line.moka_sejour_titre_devis
                invoice.moka_nombre_personnes_invoice = sale_order_line.moka_nombre_personnes_devis
                invoice.moka_prix_pp_invoice = sale_order_line.moka_prix_pp_devis
                invoice.moka_prix_pp_ht_invoice = sale_order_line.moka_prix_pp_ht_devis
