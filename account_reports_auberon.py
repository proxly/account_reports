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

class account_reports_auberon_gl(osv.osv):
    _name = "account.reports.auberon.gl"
    _description = "Accounting Reports by Auberon"
    _columns = {
        'account_code': fields.char('Account Code', size=64),
        'account_name': fields.char('Account Name', size=64),
        'account_debit': fields.float('Debit'),
        'account_credit': fields.float('Credit', size=64),
        'journal_name':fields.char('Journal', size=64),
        'report_creator':fields.char('User', size=64,),
        'date_generated':fields.datetime('Generate Date'),
        'creator_updated':fields.boolean('updated creator'),
    }
    _order = 'date_generated desc'
    
    def update_ledger(self, cr, uid, ids,context=None):
        update_date = str(time.strftime('%Y-%m-%d'))
        user = 'Administrator'
        cr.execute('update account_reports_auberon_gl set report_creator=%s, date_generated=%s where date_generated=Null',(user,update_date,))
        return True
    
    def get_ledger(self, cr, uid, ids, context=None):
        cr.execute('insert into account_reports_auberon_gl(account_code,account_name,account_debit, account_credit, journal_name) select aa.code, aa.name, aml.debit, aml.credit, journ.name from account_account aa , account_journal journ , account_move_line aml where aml.account_id=aa.id and journ.id=aml.journal_id')
        user='Administrator'
        creator_updated_stat='t'
        tester='t'
        cr.execute('update account_reports_auberon_gl set report_creator=%s, creator_updated=%s',(user,creator_updated_stat,))
        self.update_ledger(cr, uid, ids,context=context)
        return True
       
account_reports_auberon_gl()
