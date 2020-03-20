from odoo import fields, models, api
from ..controller import time_manipulation
import datetime

class MokaPrestationDEVIS(models.Model):
    _inherit='sale.order'

    #Add fields into a new DB to store the infos about benefits
    moka_is_sejour_devis = fields.Boolean(string='Packaged benefit',
                                    help='If checked, display all the'
                                          ' the fields and options to'
                                          ' build a benefit order.')
    moka_sejour_titre_devis = fields.Char(string='Benefit title',
                                    help="Specific title to the current benefit.")
    moka_sejour_debut_devis = fields.Date("Starting day",
                                    help="Starting date and hour of the benefit.")
    moka_sejour_fin_devis = fields.Date("Ending day",
                                    help="Ending date and hour of the benefit.")
    moka_nombre_personnes_devis = fields.Integer(string="Number of persons",
                                        help="Number of persons participating in"
                                             " the benefit.")
    moka_prix_pp_devis = fields.Monetary(string="Price / Person",
                                help="The price per person calculated from"
                                     " the number of persons participating in"
                                     " the benefit, and the total price of"
                                     " the benefit. (not displayed in the CRM)",
                                compute="_change_price_per_person")
    moka_prix_pp_ht_devis = fields.Monetary(string="Price / Person HT",
                                help="The price per person calculated from"
                                     " the number of persons participating in"
                                     " the benefit, and the total price of"
                                     " the benefit. (not displayed in the CRM)",
                                compute="_change_price_per_person_ht")

    moka_heure_debut_devis = fields.Float(string='Starting hour',
                                    help="The hour when the benefit will begin."
                                         " If the hour is 00:00, the all journey will"
                                         " be selected, without hours.")
    moka_heure_fin_devis = fields.Float(string="Ending hour",
                                  help="The hour when the benefit will end."
                                       " If the hour is 00:00, the all journey will"
                                       " be selected, without hours.")
    moka_is_full_day_devis = fields.Boolean(string='All day', help="Check to fix an event all the day.")

    #########################################
    ##### Benefit / stay fields feature #####
    #########################################

    @api.multi
    def write(self, vals):
        #If the date or hours change, it write the new datas into the CRM linked to this sale order

        #Tempo dictionnary
        dict = {}

        if(vals.get('moka_sejour_debut_devis')):
            dict.update({'moka_sejour_debut': vals.get('moka_sejour_debut_devis')})
        if(vals.get('moka_sejour_fin_devis')):
            dict.update({'moka_sejour_fin': vals.get('moka_sejour_fin_devis')})
        if(vals.get('moka_heure_debut_devis')):
            dict.update({'moka_heure_debut': vals.get('moka_heure_debut_devis')})
        if(vals.get('moka_heure_fin_devis')):
            dict.update({'moka_heure_fin': vals.get('moka_heure_fin_devis')})
        if(vals.get('moka_is_full_day_devis') == False or vals.get('moka_is_full_day_devis') == True):
            dict.update({'moka_is_full_day': vals.get('moka_is_full_day_devis')})

        #Notify the changes to the CRM if there is changes
        if(len(dict) > 0):
            self.env['crm.lead'].search([('id', '=', self[0].opportunity_id.id)], limit=1).write(dict)

        return super(MokaPrestationDEVIS, self).write(vals)

    @api.onchange('sale_order_template_id')
    def _change_stay_fields_sale_order(self):
        #Complete the fields if they come from sale template
        for order in self:
            template_id_tempo = order._get_sale_template_id()

            if(template_id_tempo):
                #We get the current record
                sale_order_template = self.env['sale.order.template'].search([('id', '=', template_id_tempo.id)], limit=1)

                if(sale_order_template):
                    #Fill the fields with the values stored in sale_order_template
                    #Modify the fields only if the field are not already completed by an opportunity
                    if(not order.moka_is_sejour_devis):
                        order.moka_is_sejour_devis = sale_order_template.moka_is_sejour_md
                    if(not order.moka_sejour_titre_devis):
                        order.moka_sejour_titre_devis = sale_order_template.moka_sejour_titre_md
                    if(not order.moka_sejour_debut_devis):
                        order.moka_sejour_debut_devis = sale_order_template.moka_sejour_debut_md
                    if(not order.moka_sejour_fin_devis):
                        order.moka_sejour_fin_devis = sale_order_template.moka_sejour_fin_md
                    if(not order.moka_nombre_personnes_devis):
                        order.moka_nombre_personnes_devis = sale_order_template.moka_nombre_personnes_md
                    if(not order.moka_heure_debut_devis):
                        order.moka_heure_debut_devis = sale_order_template.moka_heure_debut_md
                    if(not order.moka_heure_fin_devis):
                        order.moka_heure_fin_devis = sale_order_template.moka_heure_fin_md

    def _get_hour_end(self, name):
        #Return the hour with a good format for the report and preview

        #Get the current line (sale order)
        line = self.env['sale.order'].search([('name', '=', name)], limit=1)
        return str(datetime.timedelta(hours = line.moka_heure_fin_devis)).rsplit(':', 1)[0]

    def _get_hour_start(self, name):
        #Return the hour with a good format for the report and preview

        #Get the current line (sale order)
        line = self.env['sale.order'].search([('name', '=', name)], limit=1)
        return str(datetime.timedelta(hours = line.moka_heure_debut_devis)).rsplit(':', 1)[0]

    @api.onchange('amount_total', 'moka_nombre_personnes_devis')
    def _change_price_per_person(self):
        #Recalcul the price per person whenever the total price of the order change
        for order in self:
            total_price = order.amount_total
            persons = order.moka_nombre_personnes_devis

            if(persons > 0):
                order.moka_prix_pp_devis = total_price/persons
            else:
                order.moka_prix_pp_devis = 0

    @api.onchange('amount_untaxed', 'moka_nombre_personnes_devis')
    def _change_price_per_person_ht(self):
        #Recalcul the price per person whenever the total price of the order change
        for order in self:
            total_price = order.amount_untaxed
            persons = order.moka_nombre_personnes_devis

            if(persons > 0):
                order.moka_prix_pp_ht_devis = total_price/persons
            else:
                order.moka_prix_pp_ht_devis = 0

    @api.multi
    @api.onchange('opportunity_id')
    def _change_stay_fields_opp(self):
        #Complete the fields if they come from opportunity
        for order in self:
            opp_tempo = order._get_opp_id()

            if(opp_tempo):
                #We get the current record
                opportunity = self.env['crm.lead'].search([('id', '=', opp_tempo.id)], limit=1)

                if(opportunity):
                    #We fill up the fields with the values entered in the linked opportunity
                    order.moka_is_sejour_devis = opportunity.moka_is_sejour
                    order.moka_sejour_titre_devis = opportunity.moka_sejour_titre
                    order.moka_sejour_debut_devis = opportunity.moka_sejour_debut
                    order.moka_sejour_fin_devis = opportunity.moka_sejour_fin
                    order.moka_nombre_personnes_devis = opportunity.moka_nombre_personnes
                    order.moka_heure_debut_devis = opportunity.moka_heure_debut
                    order.moka_heure_fin_devis = opportunity.moka_heure_fin
                    order.moka_is_full_day_devis = opportunity.moka_is_full_day

    def _get_opp_id(self):
        #Get the id of the linked opportunity(m2o)
        return self.opportunity_id

    def _get_sale_template_id(self):
        #Get the ID of the linked sale.order.template(m2o)
        return self.sale_order_template_id
