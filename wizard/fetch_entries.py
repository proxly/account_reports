from osv import osv, fields, orm
import pooler

class fetch_entries(osv.osv):
    _name="account.report.fetch.entries"
    _description="Fetch Entries"
    
    def fetch_aml_entries(self, cr, uid, ids, context=None):
        argl_pool=self.pool.get('account.reports.gl')
        unlink_ids=[]
        query=("""select * from account_reports_gl where not exists
        (select * from account_move_line where account_reports_gl.entry_id=account_move_line.id)""")
        cr.execute(query)
        for t in cr.dictfetchall():
            unlink_ids.append(t['id'])
        argl_pool.unlink_entries(cr, uid, unlink_ids, context=context)
        ap_pool = self.pool.get('account.period')
        journal_pool=self.pool.get('account.journal')
        partner_pool=self.pool.get('res.partner')
        move_pool=self.pool.get('account.move')
        account_pool=self.pool.get('account.account')
        query=("""select * from account_move_line where not exists
        (select * from account_reports_gl where account_reports_gl.entry_id=account_move_line.id)""")
        cr.execute(query)
        balance = 0.00
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
            debit_str=str(debit)
            credit_str=str(credit)
            if debit_str=='None':
                debit=0.00
            elif credit_str=='None':
                credit=0.00
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
            argl_pool.create(cr, uid, values, context=context)
        return {'type': 'ir.actions.act_window_close'}
fetch_entries()