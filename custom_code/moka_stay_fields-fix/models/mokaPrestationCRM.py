from odoo import fields, models, api
from ..controller import time_manipulation
import datetime

class MokaPrestationCRM(models.Model):
    _inherit='crm.lead'

    #Add fields into a new DB to store the infos about benefits
    moka_is_sejour = fields.Boolean(string='Packaged benefit',
                                    help='If checked, display all the'
                                          ' the fields and options to'
                                          ' build a benefit order.')
    moka_sejour_titre = fields.Char(string='Benefit title',
                                    help="Specific title to the current benefit.")
    moka_sejour_debut = fields.Date("Starting day",
                                    help="Starting date and hour of the benefit.")
    moka_sejour_fin = fields.Date("Ending day",
                                    help="Ending date and hour of the benefit.")
    moka_nombre_personnes = fields.Integer(string="Number of persons",
                                        help="Number of persons participating in"
                                             " the benefit.")
    moka_prix_pp = fields.Char(string="Price / Person",
                                help="The price per person calculated from"
                                     " the number of persons participating in"
                                     " the benefit, and the total price of"
                                     " the benefit. (not displayed in the CRM)")

    moka_heure_debut = fields.Float(string='Starting hour',
                                    help="The hour when the benefit will begin."
                                         " If the hour is 00:00, the all journey will"
                                         " be selected, without hours.")
    moka_heure_fin = fields.Float(string="Ending hour",
                                  help="The hour when the benefit will end."
                                       " If the hour is 00:00, the all journey will"
                                       " be selected, without hours.")
    moka_is_full_day = fields.Boolean(string='All day', help="Check to fix an event all the day.")
    calendar_id_crm = fields.One2many('calendar.event', 'crm_id')
    moka_number_event = fields.Integer(string="Events", compute="_count_numbre_event")

    #############################
    ##### Calendar features #####
    #############################

    @api.multi
    def redirect_calendar(self):
        #Action of the button to redirect to the calendar via the CRM page

        #Get the id of the view to display
        id_view = self.env['ir.actions.act_window.view'].search([('display_name', '=', 'calendar.event.search')], limit=1).id

        return{
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'views': [[False, 'calendar']],
            'search_view_id': (id_view, 'calendar.event.form')
        }

    @api.multi
    def _count_numbre_event(self):
        #Count the numbre of event during all the benefit

        for lead in self:
            if(lead.moka_sejour_debut == lead.moka_sejour_fin):
                #We look at all the event at this day wich are linked to a opp
                lines = self.env['calendar.event'].search([
                    '&', ('crm_id', '!=', False),
                    '&', ('start', '<=', lead.moka_sejour_debut),
                    ('stop', '>=', lead.moka_sejour_fin)
                ])
                lead.moka_number_event = len(lines)
            else:
                lines = self.env['calendar.event'].search(
                    ['&', ('crm_id', '!=', False),
                     '&', ('start', '>=', lead.moka_sejour_debut),
                     ('start', '<=', lead.moka_sejour_fin)])
                lead.moka_number_event = len(lines)

    @api.multi
    def write(self, vals):
        #Get all the fields modified into the form
        if(vals.get('moka_is_sejour') == False or vals.get('moka_is_sejour') == True):
            vals_is_sejour = vals.get('moka_is_sejour')
        else:
            vals_is_sejour = self[0].moka_is_sejour

        if(vals.get('moka_sejour_debut')):
            vals_start_date = vals.get('moka_sejour_debut')
        else:
            vals_start_date = self[0].moka_sejour_debut

        if(vals.get('moka_sejour_fin')):
            vals_stop_date = vals.get('moka_sejour_fin')
        else:
            vals_stop_date = self[0].moka_sejour_fin

        if(vals.get('moka_heure_debut')):
            vals_start_hour = vals.get('moka_heure_debut')
        else:
            vals_start_hour = self[0].moka_heure_debut

        if(vals.get('moka_heure_fin')):
            vals_stop_hour = vals.get('moka_heure_fin')
        else:
            vals_stop_hour = self[0].moka_heure_fin

        if(vals.get('moka_sejour_titre')):
            vals_title = vals.get('moka_sejour_titre')
        else:
            vals_title = self[0].moka_sejour_titre

        if(vals.get('moka_is_full_day') == False or vals.get('moka_is_full_day') == True):
            vals_full_day = vals.get('moka_is_full_day')
        else:
            vals_full_day = self[0].moka_is_full_day

        if(vals.get('team_id')):
            vals_teamid = vals.get('team_id')
        else:
            vals_teamid = self[0].team_id.id

        if(vals.get('stage_id')):
            vals_stage_id = vals.get('stage_id')
        else:
            vals_stage_id = self[0].stage_id.id

        if(vals.get('active') == False):
            #Delete the event when an opp is lost
            for event in self[0].calendar_id_crm:
                event.unlink()

            return super(MokaPrestationCRM, self).write(vals)

        #Get the different values for the title
        if(vals.get('partner_name')):
            #Get the name of the company
            company_name = vals.get('partner_name')
        elif(self[0].partner_name):
            #Set the company name to none
            company_name = self[0].partner_name
        else:
            company_name = ''

        #Get the price of the CRM
        if(vals.get('planned_revenue')):
            revenue = str(int(vals.get('planned_revenue')))
        elif(self[0].planned_revenue):
            revenue = str(int(self[0].planned_revenue))
        else:
            revenue = 'N.A.'

        if(vals.get('moka_nombre_personnes')):
            nb_personnes = vals.get('moka_nombre_personnes')
        else:
            nb_personnes = self[0].moka_nombre_personnes

        #Get the name of the current stage of the opportunity
        name_stage = self.env['crm.stage'].search([('id', '=', vals_stage_id)]).name

        #Create the new dictionnary to add into calendar.event
        event_created = self[0]._add_event(vals_is_sejour, vals_full_day ,vals_start_date, vals_stop_date, \
                                        vals_start_hour, vals_stop_hour, vals_title, name_stage, vals_teamid, \
                                        company_name, revenue, nb_personnes)

        if(event_created):
            if(len(self[0].calendar_id_crm) != 0):
                #Update the previous event
                calendar_id = {'calendar_id_crm': [(1, self[0].calendar_id_crm.id, event_created)]}
            else:
                #Create a new event
                calendar_id = {'calendar_id_crm': [(0, 0, event_created)]}

            vals.update(calendar_id)

        return super(MokaPrestationCRM, self).write(vals)

    @api.model
    def create(self, vals):
        #Call the method to add an event in the calendar with some parameters whenever a field
        #in relation with the calendard is changed
        if(vals.get('moka_is_sejour')):
            #Get the different values for the title
            if(vals.get('partner_name')):
                #Get the name of the company
                company_name = vals.get('partner_name')
            else:
                #Set the company name to none
                company_name = ''

            #Get the price of the CRM
            if(vals.get('planned_revenue')):
                revenue = str(int(vals.get('planned_revenue')))
            else:
                revenue = 'N.A.'

            if(vals.get('moka_nombre_personnes')):
                nb_personnes = vals.get('moka_nombre_personnes')
            else:
                nb_personnes = 0

            if(vals.get('moka_sejour_titre')):
                title = vals.get('moka_sejour_titre')
            else:
                title = ''

            #Add the field calendar_id in the vals to create
            event_created = self._add_event(vals.get('moka_is_sejour'), vals.get('moka_is_full_day') ,vals.get('moka_sejour_debut'), vals.get('moka_sejour_fin'), \
                                            vals.get('moka_heure_debut'), vals.get('moka_heure_fin'), title, vals.get('state'), vals.get('team_id'), \
                                            company_name, revenue, nb_personnes)
            calendar_id = {'calendar_id_crm': [(0, 0, event_created)]}
            vals.update(calendar_id)

        #Overwrite the write method of odoo to catch the update of a current line in dataBase
        return super(MokaPrestationCRM, self).create(vals)

    #Function for an event fixed all the day
    def _add_event_date(self, sejour_title, state, benefit_start, benefit_stop, team_id, company_name, revenue, nb_personnes):
        #Creation of the attributes

        #Get the currency of the CRM
        currency = self.env['res.currency'].search([('id', '=', self[0].company_currency.id)]).symbol

        if(company_name != ''):
            name_tempo = company_name + ' - ' + revenue + currency + ' ( ' + state + ' )'
        else:
            name_tempo = revenue + currency + ' ( ' + state + ' )'

        description = sejour_title + ' - ' + str(nb_personnes)

        #Add all the ids of the partner of the sale order
        list_ids = self[0]._create_list_uid(team_id)

        #Creation of the dictionnary to register the line
        line = {'name': name_tempo,
                'start': benefit_start,
                'stop': benefit_stop,
                'allday': True,
                'partner_ids': [(6, 0, list_ids)],
                'description': description
                }

        return line

    #Function for an event with a duration (in hours)
    def _add_event_date_time(self, sejour_title, state, benefit_start_date, benefit_start_hour, benefit_end_date, benefit_end_hour, \
                            team_id, company_name, revenue, nb_personnes):
        #Creation of the attributes

        #Get the currency of the CRM
        currency = self.env['res.currency'].search([('id', '=', self[0].company_currency.id)]).symbol

        if(company_name != ''):
            name_tempo = company_name + ' - ' + revenue + currency + ' ( ' + state + ' )'
        else:
            name_tempo = revenue + currency + ' ( ' + state + ' )'

        description = sejour_title + ' - ' + str(nb_personnes)


        start_time = str(datetime.timedelta(hours = benefit_start_hour)).rsplit(':', 1)[0]
        end_time = str(datetime.timedelta(hours = benefit_end_hour)).rsplit(':', 1)[0]

        start_tempo = time_manipulation.generate_datetime(benefit_start_date, start_time)
        stop_tempo = time_manipulation.generate_datetime(benefit_end_date, end_time)

        #Add all the ids of the partner of the sale order
        list_ids = self[0]._create_list_uid(team_id)

        #Creation of the dictionnary to register the line
        line = {'name': name_tempo,
                'start': benefit_start_date,
                'stop': benefit_end_date,
                'start_datetime': start_tempo,
                'stop_datetime': stop_tempo,
                'allday': False,
                'partner_ids': [(6, 0, list_ids)],
                'description': description
                }

        #Need help to associate the event to the participant properly : the participant can't see the event without the responsible checked

        return line

    @api.multi
    def _add_event(self, is_sejour, is_full_day ,sejour_debut, sejour_fin, heure_debut, heure_fin, sejour_titre, state, team_id, \
                    company_name, revenue, nb_personnes):
        event_created = False
        if(is_sejour):
            if(not is_full_day and heure_debut != heure_fin):
                event_created = self[0]._add_event_date_time(sejour_titre,
                                            state,
                                            str(sejour_debut),
                                            heure_debut - 2,
                                            str(sejour_fin),
                                            heure_fin - 2,
                                            team_id,
                                            company_name,
                                            revenue,
                                            nb_personnes)
            else:
                event_created = self[0]._add_event_date(sejour_titre,
                                      state,
                                      sejour_debut,
                                      sejour_fin,
                                      team_id,
                                      company_name,
                                      revenue,
                                      nb_personnes)
        return event_created

    def _create_list_uid(self, team_id):
        #variable
        ids_list_user = []
        ids_list_partner = []

        #Search for the team in crm.team
        crm_team = self.env['crm.team'].search([('id', '=', team_id)], limit=1)

        #Save all the res.user id in a list
        for user in crm_team.member_ids:
            ids_list_user.append(user.id)

        #Find the res.partner ids related to the res.user
        for user_id in ids_list_user:
            user_line = self.env['res.users'].search([('id', '=', user_id)], limit=1)
            ids_list_partner.append(user_line.partner_id.id)

        return ids_list_partner
