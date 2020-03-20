odoo.define('aspl_pos_close_session.pos', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var DB = require('point_of_sale.DB');
    var chrome = require('point_of_sale.chrome');
    var screens = require('point_of_sale.screens');
    var PopupWidget = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var _t = core._t;
    var QWeb = core.qweb;
    var framework = require('web.framework');

    models.load_fields("pos.session", ['opening_balance']);
    models.load_fields("res.users", ['login_with_pos_screen']);

    chrome.HeaderButtonWidget.include({
        renderElement: function(){
            var self = this;
            this._super();
            if(this.action){
                this.$el.click(function(){
                    self.gui.show_popup('confirm_close_session_wizard');
                });
            }
        },
    });

    chrome.Chrome.include({
          build_widgets:function(){
                var self = this;
                this._super(arguments);
                if(self.pos.pos_session.opening_balance){
                    self.gui.show_screen('openingbalancescreen');
                } else{
                    self.gui.show_screen('products');
                }
          },
     });

    var ConfirmCloseSessionPopupWizard = PopupWidget.extend({
        template: 'ConfirmCloseSessionPopupWizard',
        show: function(options){
            options = options || {};
            this._super(options);
            this.statement_id = options.statement_id;
            var self = this;
            $("#close_session").click(function(){
                if(self.pos.config.cash_control){
                    self.gui.show_popup('cash_control',{
                            title:'Closing Cash Control',
                            statement_id:self.statement_id,
                    });
                } else{
                    var params = {
                        model: 'pos.session',
                        method: 'custom_close_pos_session',
                        args:[self.pos.pos_session.id]
                    }
                    rpc.query(params, {async: false}).then(function(res){
                        if(res){
                            if(self.pos.config.z_report_pdf){
                                var pos_session_id = [self.pos.pos_session.id];
                                self.pos.chrome.do_action('aspl_pos_close_session.pos_z_report',{additional_context:{
                                           active_ids:pos_session_id,
                                }});
                            }
                            if(self.pos.config.iface_print_via_proxy){
                                var pos_session_id = [self.pos.pos_session.id];
                                var report_name = "aspl_pos_close_session.pos_z_thermal_report_template";
                                var params = {
                                    model: 'ir.actions.report',
                                    method: 'get_html_report',
                                    args: [pos_session_id, report_name],
                                }
                                rpc.query(params, {async: false})
                                .then(function(report_html){
                                    if(report_html && report_html[0]){
                                        self.pos.proxy.print_receipt(report_html[0]);
                                    }
                                });
                            }
                            if(self.pos.config.email_close_session_report){
                                var pos_session_id = self.pos.pos_session.id;
                                var params = {
                                    model: 'pos.session',
                                    method: 'send_email_z_report',
                                    args: [pos_session_id]
                                }
                                rpc.query(params, {async: false})
                                .then(function(res){
                                    if(res){}
                                }).fail(function(){
                                    self.db.notification('danger',"Connection lost");
                                });
                            }
                            setTimeout(function(){
                                var cashier = self.pos.user || false;
                                if(cashier && cashier.login_with_pos_screen){
                                    framework.redirect('/web/session/logout');
                                } else{
                                    self.pos.gui.close();
                                }
                            }, 5000);
                        }
                    });
                }
            });
        },
        click_confirm: function(){
            var self = this;
            framework.redirect('/web/session/logout');
        },
    });
    gui.define_popup({name:'confirm_close_session_wizard', widget: ConfirmCloseSessionPopupWizard});

    var CashControlWizardPopup = PopupWidget.extend({
        template : 'CashControlWizardPopup',
        show : function(options) {
            var self = this;
            options = options || {};
            this.title = options.title || ' ';
            this.statement_id = options.statement_id || false;
            var selectedOrder = self.pos.get_order();
            this._super();
            this.renderElement();
            var self = this;
            $(document).keypress(function (e) {
                if (e.which != 8 && e.which != 46 && e.which != 0 && (e.which < 48 || e.which > 57)) {
                    return false;
                }
            });
            var session_data = {
                                    model: 'pos.session',
                                    method: 'search_read',
                                    domain: [['id', '=', self.pos.pos_session.id]],
                                }
            rpc.query(session_data, {async: false}).then(function(data){
                if(data){
                     _.each(data, function(value){
                        $("#open_bal").text(value.cash_register_balance_start.toFixed(2));
                        $("#transaction").text(value.cash_register_total_entry_encoding.toFixed(2));
                        $("#theo_close_bal").text(value.cash_register_balance_end.toFixed(2));
                        $("#real_close_bal").text(value.cash_register_balance_end_real.toFixed(2));
                        $("#differ").text(value.cash_register_difference.toFixed(2));
                        $('.button.close_session').show();
                     });
                }
            });
            $("#cash_details").show();
            this.$('.button.close_session').hide();
            this.$('.button.ok').click(function() {
                var dict = [];
                var items=[]
                var cash_details = []
                $(".cashcontrol_td").each(function(){
                    items.push($(this).val());
                });
                while (items.length > 0) {
                  cash_details.push(items.splice(0,3))
                }
                _.each(cash_details, function(cashDetails){
                    if(cashDetails[2] > 0.00){
                        dict.push({
                                   'coin_value':Number(cashDetails[0]),
                                   'number_of_coins':Number(cashDetails[1]),
                                   'subtotal':Number(cashDetails[2]),
                                   'pos_session_id':self.pos.pos_session.id
                        })
                    }
                });
                if(dict.length > 0){
                    var params = {
                                    model: 'pos.session',
                                    method: 'cash_control_line',
                                    args:[self.pos.pos_session.id,dict]
                                 }
                    rpc.query(params, {async: false}).then(function(res){
                            if(res){
                            }
                    }).fail(function (type, error){
                        if(error.code === 200 ){    // Business Logic Error, not a connection problem
                           self.gui.show_popup('error-traceback',{
                                'title': error.data.message,
                                'body':  error.data.debug
                           });
                        }
                    });
                }
                var session_data = {
                                        model: 'pos.session',
                                        method: 'search_read',
                                        domain: [['id', '=', self.pos.pos_session.id]],
                                    }
                rpc.query(session_data, {async: false}).then(function(data){
                    if(data){
                         _.each(data, function(value){
                            $("#open_bal").text(value.cash_register_balance_start.toFixed(2));
                            $("#transaction").text(value.cash_register_total_entry_encoding.toFixed(2));
                            $("#theo_close_bal").text(value.cash_register_balance_end.toFixed(2));
                            $("#real_close_bal").text(value.cash_register_balance_end_real.toFixed(2));
                            $("#differ").text(value.cash_register_difference.toFixed(2));
                            $('.button.close_session').show();
                         });
                    }
                });
    		});
            this.$('.button.close_session').click(function() {
                self.gui.close_popup();
                var params = {
                    model: 'pos.session',
                    method: 'custom_close_pos_session',
                    args:[self.pos.pos_session.id]
                }
                rpc.query(params, {async: false}).then(function(res){
                    if(res){
                        if(self.pos.config.z_report_pdf){
                            var pos_session_id = [self.pos.pos_session.id];
                            self.pos.chrome.do_action('aspl_pos_close_session.pos_z_report',{additional_context:{
                                       active_ids:pos_session_id,
                            }});
                        }
                        if(self.pos.config.iface_print_via_proxy){
                            var pos_session_id = [self.pos.pos_session.id];
                            var report_name = "aspl_pos_close_session.pos_z_thermal_report_template";
                            var params = {
                                model: 'ir.actions.report',
                                method: 'get_html_report',
                                args: [pos_session_id, report_name],
                            }
                            rpc.query(params, {async: false})
                            .then(function(report_html){
                                if(report_html && report_html[0]){
                                    self.pos.proxy.print_receipt(report_html[0]);
                                }
                            });
                        }
                        if(self.pos.config.email_close_session_report){
                            var pos_session_id = self.pos.pos_session.id;
                            var params = {
                                model: 'pos.session',
                                method: 'send_email_z_report',
                                args: [pos_session_id]
                            }
                            rpc.query(params, {async: false})
                            .then(function(res){
                                if(res){}
                            }).fail(function(){
                                self.db.notification('danger',"Connection lost");
                            });
                        }
                        setTimeout(function(){
                            var cashier = self.pos.user || false;
                            if(cashier && cashier.login_with_pos_screen){
                                framework.redirect('/web/session/logout');
                            } else{
                                self.pos.gui.close();
                            }
                        }, 5000);
                    }
                }).fail(function (type, error){
                    if(error.code === 200 ){    // Business Logic Error, not a connection problem
                       self.gui.show_popup('error-traceback',{
                            'title': error.data.message,
                            'body':  error.data.debug
                       });
                    }
                });
            });
            this.$('.button.cancel').click(function() {
                  self.gui.close_popup();
            });
        },
        renderElement: function() {
            var self = this;
            this._super();
            var selectedOrder = self.pos.get_order();
            var table_row = "<tr id='cashcontrol_row'>" +
                            "<td><input type='text'  class='cashcontrol_td coin' id='value' value='0.00' /></td>" + "<span id='errmsg'/>"+
                            "<td><input type='text' class='cashcontrol_td no_of_coin' id='no_of_values' value='0.00' /></td>" +
                            "<td><input type='text' class='cashcontrol_td subtotal' id='subtotal' disabled='true' value='0.00' /></td>" +
                            "<td id='delete_row'><span class='fa fa-trash-o'></span></td>" +
                            "</tr>";
            $('#cashbox_data_table tbody').append(table_row);
            $('#add_new_item').click(function(){
                $('#cashbox_data_table tbody').append(table_row);
            });
            $('#cashbox_data_table tbody').on('click', 'tr#cashcontrol_row td#delete_row',function(){
				$(this).parent().remove();
				self.compute_subtotal();
			});
            $('#cashbox_data_table tbody').on('change focusout', 'tr#cashcontrol_row td',function(){
                var no_of_value, value;
                if($(this).children().attr('id') === "value"){
                    value = Number($(this).find('#value').val());
                    no_of_value = Number($(this).parent().find('td #no_of_values').val());
                }else if($(this).children().attr('id') === "no_of_values"){
                    no_of_value = Number($(this).find('#no_of_values').val());
                    value = Number($(this).parent().find('td #value').val());
                }
                $(this).parent().find('td #subtotal').val(value * no_of_value);
                self.compute_subtotal();
            });
            this.compute_subtotal = function(event){
                var subtotal = 0;
                _.each($('#cashcontrol_row td #subtotal'), function(input){
                    if(Number(input.value) && Number(input.value) > 0){
                        subtotal += Number(input.value);
                    }
                });
                $('.subtotal_end').text(subtotal);
            }
        }
    });
    gui.define_popup({name:'cash_control', widget: CashControlWizardPopup});

    var OpeningBalanceScreenWidget = screens.ScreenWidget.extend({
        template: 'OpeningBalanceScreenWidget',
        init: function(parent, options){
            var self = this;
            this._super(parent, options);
        },
        show: function() {
        	this._super();
        	var self = this;
        	this.renderElement();
        	$('#skip').click(function(){
                self.gui.show_screen('products');
                var params = {
                                model: 'pos.session',
                                method: 'close_open_balance',
                                args:[self.pos.pos_session.id]
                              }
                rpc.query(params, {async: false})
        	});
        	$(document).keypress(function (e) {
                if (e.which != 8 && e.which != 46 && e.which != 0 && (e.which < 48 || e.which > 57)) {
                    return false;
                }
            });
        },
        renderElement:function(){
            this._super();
            var self = this;
        	self.open_form();
        },
        open_form: function() {
        	var self = this;
            var open_table_row = "<tr id='open_balance_row'>" +
                            "<td><input type='text'  class='openbalance_td' id='value' value='0.00' /></td>" +
                            "<td><input type='text' class='openbalance_td' id='no_of_values' value='0.00' /></td>" +
                            "<td><input type='text' class='openbalance_td' id='subtotal' disabled='true' value='0.00' /></td>" +
                            "<td id='delete_row'><span class='fa fa-trash-o' style='font-size: 20px;'></span></td>" +
                            "</tr>";
            $('#opening_cash_table tbody').append(open_table_row);
            $('#add_open_balance').click(function(){
                $('#opening_cash_table tbody').append(open_table_row);
            });
            $('#opening_cash_table tbody').on('click', 'tr#open_balance_row td#delete_row',function(){
                $(this).parent().remove();
                self.compute_subtotal();
			});
            $('#opening_cash_table tbody').on('change focusout', 'tr#open_balance_row td',function(){
                var no_of_value, value;
                if($(this).children().attr('id') === "value"){
                    value = Number($(this).find('#value').val());
                    no_of_value = Number($(this).parent().find('td #no_of_values').val());
                }else if($(this).children().attr('id') === "no_of_values"){
                    no_of_value = Number($(this).find('#no_of_values').val());
                    value = Number($(this).parent().find('td #value').val());
                }
                $(this).parent().find('td #subtotal').val(value * no_of_value);
                self.compute_subtotal();
            });
            this.compute_subtotal = function(event){
                var subtotal = 0;
                _.each($('#open_balance_row td #subtotal'), function(input){
                    if(Number(input.value) && Number(input.value) > 0){
                        subtotal += Number(input.value);
                    }
                });
                $('.open_subtotal').text(subtotal);
            }
            $('#validate_open_balance').click(function(){
                var items = []
                var open_balance = []
                var total_open_balance = 0.00;
                $(".openbalance_td").each(function(){
                    items.push($(this).val());
                });
                while (items.length > 0) {
                  open_balance.push(items.splice(0,3))
                }
                _.each(open_balance, function(balance){
                    total_open_balance += Number(balance[2])
                });
                if(self.pos.config.allow_with_zero_amount){
                    var params = {
                                    model: 'pos.session',
                                    method: 'open_balance',
                                    args:[self.pos.pos_session.id,total_open_balance]
                                 }
                    rpc.query(params, {async: false}).then(function(res){
                            if(res){
                                self.gui.show_screen('products');
                            }
                    }).fail(function (type, error){
                        if(error.code === 200 ){    // Business Logic Error, not a connection problem
                           self.gui.show_popup('error-traceback',{
                                'title': error.data.message,
                                'body':  error.data.debug
                           });
                        }
                    });
                } else{
                    if(total_open_balance > 0){
                        var params = {
                                        model: 'pos.session',
                                        method: 'open_balance',
                                        args:[self.pos.pos_session.id,total_open_balance]
                                     }
                        rpc.query(params, {async: false}).then(function(res){
                                if(res){
                                    self.gui.show_screen('products');
                                }
                        }).fail(function (type, error){
                            if(error.code === 200 ){    // Business Logic Error, not a connection problem
                               self.gui.show_popup('error-traceback',{
                                    'title': error.data.message,
                                    'body':  error.data.debug
                               });
                            }
                        });
                    } else{
                        return;
                    }
                }
            });
        },
    });
    gui.define_screen({name:'openingbalancescreen', widget: OpeningBalanceScreenWidget});
});