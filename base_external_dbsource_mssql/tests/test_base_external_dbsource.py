# Copyright 2016 LasLabs Inc.
# Copyright 2024 Tecnativa - Carolina Fernandez
from unittest import mock

from odoo.tests import common

ADAPTER = (
    "odoo.addons.base_external_dbsource_mssql.models" ".base_external_dbsource.pymssql"
)


class TestBaseExternalDbsource(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dbsource = cls.env.ref("base_external_dbsource_mssql.demo_mssql")

    def test_connection_close_mssql(self):
        """It should close the connection"""
        connection = mock.MagicMock()
        res = self.dbsource.connection_close_mssql(connection)
        self.assertEqual(res, connection.close())

    def test_connection_open_mssql(self):
        """It should call SQLAlchemy open"""
        with mock.patch.object(
            type(self.dbsource), "_connection_open_mssql"
        ) as parent_method:
            self.dbsource.connection_open_mssql()
            parent_method.assert_called_once_with()

    def test_excecute_mssql(self):
        """It should pass args to SQLAlchemy execute"""
        expect = "sqlquery", "sqlparams", "metadata"
        with mock.patch.object(type(self.dbsource), "_execute_mssql") as parent_method:
            self.dbsource.execute_mssql(*expect)
            parent_method.assert_called_once_with(*expect)
