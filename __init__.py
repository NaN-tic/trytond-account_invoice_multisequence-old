# This file is part of the account_invoice_sequence module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .account import *


def register():
    Pool.register(
        AccountJournalInvoiceSequence,
        Journal,
        Invoice,
        module='account_invoice_sequence', type_='model')
