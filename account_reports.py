#Accounting Legal Reports
#by Auberon Module Robot
#Auberon Solutions.com
#
#

import time
from osv import osv, fields, orm
import netsvc
import pooler
import psycopg2
from tools.translate import _


class account_reports_auberon_pl(osv.osv):
    _name = "account.reports.auberon.pl"
    _description = "Profit and Loss (Auberon)"
    _columns = {
        'period_id': fields.many2one('account.period', 'Effectivity Period'),
        'generation_date':fields.datetime('Generate Date', readonly=True),
        'income_ids':fields.one2many('account.reports.auberon.pl.income','pl_id','Income', readonly=True),
        'expense_ids':fields.one2many('account.reports.auberon.pl.expense','pl_id','Expense', readonly=True),
        'total_income':fields.float('Total Income', readonly=True),
        'total_expense':fields.float('Total Expense', readonly=True),
        'net_profit_loss':fields.float('Net Profit/Loss', readonly=True),
        'state': fields.selection([
            ('draft','Draft'),
            ('post','Closed'),
            ],'State', select=True, readonly=True),
        }
    _order = 'generation_date desc'
    _defaults = {
        'generation_date': lambda *a: time.strftime('%Y-%m-%d %H:%M'),
        'state':'draft',
        }
    def get_income_entries(self, cr, uid, ids, context=None):
        income="'"+'income'+"'"
        for get_period in self.browse(cr, uid, ids, context=None):
            if get_period.period_id:
                period_id=get_period.period_id.name
                period_id="'"+period_id+"'"
                inv_id=get_period.id
                #Insert Income Accounts               
                         
                query = ("""insert into account_reports_auberon_pl_income(account_name,total_amount,period_name,account_type) select aa.name,sum(aml.credit), ap.name, aat.name from account_period ap, account_account aa, account_move_line aml, account_account_type aat where aml.account_id=aa.id and aat.id=aa.user_type and aml.period_id=ap.id and aat.report_type='income' and ap.name=%s group by aa.name, aat.name, ap.name"""% (period_id))
                cr.execute(query)
                #netsvc.Logger().notifyChannel("Query", netsvc.LOG_INFO, ' '+query)
                
                #Update Income Accounts
                query = ("""update account_reports_auberon_pl_income set pl_id=%s where pl_id is Null"""% (inv_id))
                cr.execute(query)
                netsvc.Logger().notifyChannel("Query", netsvc.LOG_INFO, ' '+query)
                
                
                query = ("""insert into account_reports_auberon_pl_expense(account_name,total_amount,period_name,account_type) select aa.name,sum(aml.debit), ap.name, aat.name from account_period ap, account_account aa, account_move_line aml, account_account_type aat where aml.account_id=aa.id and aat.id=aa.user_type and aml.period_id=ap.id and aat.report_type='expense' and ap.name=%s group by aa.name, aat.name, ap.name"""% (period_id))
                cr.execute(query)
                #netsvc.Logger().notifyChannel("Query", netsvc.LOG_INFO, ' '+query)
                query = ("""update account_reports_auberon_pl_expense set pl_id=%s where pl_id is Null"""% (inv_id))
                cr.execute(query)
                total_income=0.00
                total_expense=0.00
                for this_record in self.browse(cr,uid,ids):
                    for income_ids in this_record.income_ids:
                        total_income+=income_ids.total_amount
                for this_record in self.browse(cr,uid,ids):
                    for expense_ids in this_record.expense_ids:
                        total_expense+=expense_ids.total_amount
                net_pl = 0.00
                net_pl = total_income - total_expense
                self.write(cr, uid, ids, {'state':'post','total_income':total_income,'total_expense':total_expense,'net_profit_loss':net_pl})
        return True
        
account_reports_auberon_pl()

class account_reports_auberon_pl_income(osv.osv):
    _name = "account.reports.auberon.pl.income"
    _description = "Profit and Loss (Income)"
    _columns = {
        'account_name':fields.char('Account',size=64),
        'total_amount':fields.float('Total Amount'),
        'account_type':fields.char('Report Type',size=64),
        'period_name':fields.char('Period',size=64),
        'pl_id':fields.many2one('account.reports.auberon.pl', 'Profit and Loss', ondelete='cascade',select=True),
        }
account_reports_auberon_pl_income()

class account_reports_auberon_pl_expense(osv.osv):
    _name = "account.reports.auberon.pl.expense"
    _description = "Profit and Loss (Expense)"
    _columns = {
        'account_name':fields.char('Account',size=64),
        'total_amount':fields.float('Total Amount'),
        'account_type':fields.char('Report Type',size=64),
        'period_name':fields.char('Period',size=64),
        'pl_id':fields.many2one('account.reports.auberon.pl', 'Profit and Loss', ondelete='cascade',select=True),
        }
account_reports_auberon_pl_expense()


