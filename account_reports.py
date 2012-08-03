
import time
from osv import osv, fields, orm
import netsvc
import pooler
import psycopg2
from tools.translate import _


class account_reports_pl(osv.osv):
    _name = "account.reports.pl"
    _description = "Profit and Loss"
    _columns = {
        'period_id': fields.many2one('account.period', 'Effectivity Period'),
        'generation_date':fields.datetime('Generate Date', readonly=True),
        'income_ids':fields.one2many('account.reports.pl.income','pl_id','Income', readonly=True),
        'expense_ids':fields.one2many('account.reports.pl.expense','pl_id','Expense', readonly=True),
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
    def get_entries(self, cr, uid, ids, context=None):
        income="'"+'income'+"'"
        for get_period in self.browse(cr, uid, ids, context=None):
            if get_period.period_id:
                period_id=get_period.period_id.name
                period_id="'"+period_id+"'"
                inv_id=get_period.id
                #Insert Income Accounts               
                         
                query = ("""insert into account_reports_pl_income(account_name,total_amount,period_name,account_type) select aa.name,sum(aml.credit), ap.name, aat.name from account_period ap, account_account aa, account_move_line aml, account_account_type aat where aml.account_id=aa.id and aat.id=aa.user_type and aml.period_id=ap.id and aat.report_type='income' and ap.name=%s group by aa.name, aat.name, ap.name"""% (period_id))
                cr.execute(query)
                netsvc.Logger().notifyChannel("Query", netsvc.LOG_INFO, ' '+query)
                
                #Update Income Accounts
                query = ("""update account_reports_pl_income set pl_id=%s where pl_id is Null"""% (inv_id))
                cr.execute(query)
                netsvc.Logger().notifyChannel("Query", netsvc.LOG_INFO, ' '+query)
                
                
                query = ("""insert into account_reports_pl_expense(account_name,total_amount,period_name,account_type) select aa.name,sum(aml.debit), ap.name, aat.name from account_period ap, account_account aa, account_move_line aml, account_account_type aat where aml.account_id=aa.id and aat.id=aa.user_type and aml.period_id=ap.id and aat.report_type='expense' and ap.name=%s group by aa.name, aat.name, ap.name"""% (period_id))
                cr.execute(query)
                #netsvc.Logger().notifyChannel("Query", netsvc.LOG_INFO, ' '+query)
                query = ("""update account_reports_pl_expense set pl_id=%s where pl_id is Null"""% (inv_id))
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
        
account_reports_pl()

class account_reports_pl_income(osv.osv):
    _name = "account.reports.pl.income"
    _description = "Profit and Loss (Income)"
    _columns = {
        'account_name':fields.char('Account',size=64),
        'total_amount':fields.float('Total Amount'),
        'account_type':fields.char('Report Type',size=64),
        'period_name':fields.char('Period',size=64),
        'pl_id':fields.many2one('account.reports.pl', 'Profit and Loss', ondelete='cascade',select=True),
        }
account_reports_pl_income()

class account_reports_pl_expense(osv.osv):
    _name = "account.reports.pl.expense"
    _description = "Profit and Loss (Expense)"
    _columns = {
        'account_name':fields.char('Account',size=64),
        'total_amount':fields.float('Total Amount'),
        'account_type':fields.char('Report Type',size=64),
        'period_name':fields.char('Period',size=64),
        'pl_id':fields.many2one('account.reports.pl', 'Profit and Loss', ondelete='cascade',select=True),
        }
account_reports_pl_expense()

class account_reports_gl(osv.osv):
    _name = "account.reports.gl"
    _description = "General Ledger"
    _columns = {
            'name':fields.char('Entry Label',size=100),
            'date':fields.date('Entry Date'),
            'entry_id':fields.integer('Entry ID'),
            'period':fields.char('Period', size=100),
            'journal':fields.char('Journal',size=100),
            'partner':fields.char('Partner Name',size=100),
            'ref':fields.char('Ref',size=100),
            'move':fields.char('Move',size=100),
            'counterpart':fields.char('Counterpart',size=100),
            'debit':fields.float('Debit'),
            'credit':fields.float('Credit'),
            'balance':fields.float('Balance'),
            'account':fields.char('Account', size=100),
            }
    _order = 'account asc'
    
    def fetch_entries(self, cr, uid, ids, context=None):
        ap_pool = self.pool.get('account.period')
        journal_pool=self.pool.get('account.journal')
        partner_pool=self.pool.get('res.partner')
        move_pool=self.pool.get('account.move')
        account_pool=self.pool.get('account.account')
        query=("""select * from account_move_line where not exists(select * from account_reports_gl where account_reports_gl.entry_id=account_move_line.id)""")
        cr.execute(query)
        for t in cr.dictfetchall():
            period_id=t['period_id']
            name=t['name']
            date=t['date']
            entry_id=t['id']
            ref=t['ref']
            debit=t['debit']
            credit=t['credit']
            journal_id=t['journal_id']
            partner_id=t['partner_id']
            move_id = t['move_id']
            account_id = t['account_id']
            balance = debit-credit
            period_obj = ap_pool.browse(cr, uid, period_id)
            journal_obj=journal_pool.browse(cr, uid, journal_id)
            partner_obj=partner_pool.browse(cr, uid, partner_id)
            move_obj=move_pool.browse(cr, uid, move_id)
            account_obj=account_pool.browse(cr, uid, account_id)
            period_name = period_obj['name']
            journal_name=journal_obj['name']
            partner_name=partner_obj['name']
            move_name=move_obj['name']
            account_name=account_obj['name']
            values={
                    'name':name,
                    'date':date,
                    'entry_id':entry_id,
                    'period':period_name,
                    'journal':journal_name,
                    'partner':partner_name,
                    'ref':ref,
                    'move':move_name,
                    'debit':debit,
                    'credit':credit,
                    'balance':balance,
                    'account':account_name,
                }
            self.create(cr, uid, values, context=context)
        return True
        
    def create(self, cr, uid, vals, context=None):
        new_id = super(account_reports_gl, self).create(cr, uid, vals,context)
        return new_id
account_reports_gl()

