#!/usr/bin/env python
# This file is part of the account_invoice_sequence module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.tests.test_tryton import test_view, test_depends
import trytond.tests.test_tryton
import unittest


class AccountInvoiceSequenceTestCase(unittest.TestCase):
    'Test Account Invoice Sequence module'

    def setUp(self):
        trytond.tests.test_tryton.install_module('account_invoice_sequence')

    def test0005views(self):
        'Test views'
        test_view('account_invoice_sequence')

    def test0006depends(self):
        'Test depends'
        test_depends()


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountInvoiceSequenceTestCase))
    return suite
