from odoo import fields, models

class MokaPrestationMD(models.Model):
    _inherit='sale.order.template'

    #Add fields into a new DB to store the infos about benefits
    moka_is_sejour_md = fields.Boolean(string='Packaged benefit',
                                    help='If checked, display all the'
                                          ' the fields and options to'
                                          ' build a benefit order.')
    moka_sejour_titre_md = fields.Char(string='Benefit title',
                                    help="Specific title to the current benefit.")
    moka_sejour_debut_md = fields.Date("Starting day",
                                    help="Starting date and hour of the benefit.")
    moka_sejour_fin_md = fields.Date("Ending day",
                                    help="Ending date and hour of the benefit.")
    moka_nombre_personnes_md = fields.Integer(string="Number of persons",
                                        help="Number of persons participating in"
                                             " the benefit.")
    moka_prix_pp_md = fields.Char(string="Price / Person",
                                help="The price per person calculated from"
                                     " the number of persons participating in"
                                     " the benefit, and the total price of"
                                     " the benefit. (not displayed in the CRM)")

    moka_heure_debut_md = fields.Float(string='Starting hour',
                                    help="The hour when the benefit will begin."
                                         " If the hour is 00:00, the all journey will"
                                         " be selected, without hours.")
    moka_heure_fin_md = fields.Float(string="Ending hour",
                                  help="The hour when the benefit will end."
                                       " If the hour is 00:00, the all journey will"
                                       " be selected, without hours.")
