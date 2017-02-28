# This file is part of the account_invoice_multisequence module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView, ModelSQL, fields, Unique
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, If, In, Not
from trytond.transaction import Transaction


__all__ = ['AccountJournalInvoiceSequence', 'Journal', 'FiscalYear', 'Invoice']
__metaclass__ = PoolMeta


class AccountJournalInvoiceSequence(ModelSQL, ModelView):
    'Account Journal Invoice Sequence'
    __name__ = 'account.journal.invoice.sequence'
    journal = fields.Many2One('account.journal', 'Journal', required=True,
        domain=[
            ('type', '=', 'revenue'),
            ], depends=['company'])
    fiscalyear = fields.Many2One('account.fiscalyear', 'Fiscalyear',
        required=True, domain=[
            ('company', '=', Eval('company', -1)),
            ], depends=['company'])
    company = fields.Many2One('company.company', 'Company', required=True,
        domain=[
            ('id', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', -1)),
            ], select=True)
    out_invoice_sequence = fields.Many2One('ir.sequence.strict',
        'Customer Invoice Sequence', required=True,
        domain=[
            ['OR',
                ('company', '=', Eval('company')),
                ('company', '=', None),
                ]
            ],
        context={
            'code': 'account.invoice',
            'company': Eval('company'),
            },
        depends=['company'])
    out_credit_note_sequence = fields.Many2One('ir.sequence.strict',
        'Customer Credit Note Sequence', required=True,
        domain=[
            ['OR',
                ('company', '=', Eval('company')),
                ('company', '=', None),
                ]
            ],
        context={
            'code': 'account.invoice',
            'company': Eval('company'),
            },
        depends=['company'])

    @classmethod
    def __setup__(cls):
        super(AccountJournalInvoiceSequence, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints += [
            ('journal_fiscalyear_uniq', Unique(t, t.journal, t.fiscalyear),
                'Fiscal Year - Journal pair must be unique.'),
            ]

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @fields.depends('journal')
    def on_change_journal(self):
        if self.journal and self.journal.type:
            self.type = self.journal.type


class Journal:
    __name__ = 'account.journal'
    sequences = fields.One2Many('account.journal.invoice.sequence', 'journal',
        'Sequences', states={
            'invisible': Eval('type') == 'revenue',
            })

    def get_invoice_sequence(self, invoice):
        pool = Pool()
        Date = pool.get('ir.date')
        date = invoice.invoice_date or Date.today()
        for sequence in self.sequences:
            fiscalyear = sequence.fiscalyear
            if (fiscalyear.start_date < date and
                    fiscalyear.end_date > date):
                return getattr(sequence, invoice.type + '_sequence')


class FiscalYear:
    __name__ = 'account.fiscalyear'
    journal_sequences = fields.One2Many('account.journal.invoice.sequence',
        'fiscalyear', 'Journal Sequences')


class Invoice:
    __name__ = 'account.invoice'

    def set_number(self):
        '''
        Set number to the invoice
        '''
        pool = Pool()
        Sequence = pool.get('ir.sequence.strict')
        Date = pool.get('ir.date')

        if self.number:
            return super(Invoice, self).set_number()

        if self.type == 'out':
            sequence = self.journal.get_invoice_sequence(self)
            if sequence:
                with Transaction().set_context(
                        date=self.invoice_date or Date.today()):
                    self.number = Sequence.get_id(sequence.id)
                    if not self.invoice_date:
                        self.invoice_date = Transaction().context['date']
                    self.save()
        return super(Invoice, self).set_number()
