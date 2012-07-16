#Accounting Legal Reports
#by Auberon Module Robot
#Auberon Solutions.com
#
#

from osv import osv, fields


class account_reports_auberon_gl(osv.osv):
    _name = "account.reports.auberon.gl"
    _description = "Accounting Reports by Auberon"
    _columns = {
        'account_code': fields.char('Account Code', size=64),
        'account_name': fields.char('Account Name', size=64),
        'account_debit': fields.char('Debit', size=64),
        'account_credit': fields.char('Credit', size=64),
        'journal_name':fields.char('Journal', size=64)
    }
    _order = "account_code"

account_reports_auberon_gl()
