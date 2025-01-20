# Copyright 2011 Daniel Reis
# Copyright 2016 LasLabs Inc.
# this is needed to generate connection string
import pymssql
import logging

from odoo import fields, models

assert pymssql

_logger = logging.getLogger(__name__)

class BaseExternalDbsource(models.Model):
    """It provides logic for connection to a MSSQL data source."""

    _inherit = "base.external.dbsource"

    connector = fields.Selection(
        selection_add=[("mssql", "Microsoft SQL Server")], ondelete={"mssql": "cascade"}
    )

    def connection_close_mssql(self, connection):
        return connection.close()

    def connection_open_mssql(self):
        return self._connection_open_mssql()

    def execute_mssql(self, sqlquery, sqlparams, metadata):
        return self._execute_mssql(sqlquery, sqlparams, metadata)

    def _connection_open_mssql(self):
        args = dict(e.split('=') for e in self.conn_string_full.split(','))
        return pymssql.connect(
            server=args['server'],
            user=args['user'],
            password=args['password'],
            database=args['database'],
            as_dict=True
        )

    def _execute_mssql(self, sqlquery, sqlparams, metadata):
        rows, cols = list(), list()
        for record in self:
            with record.connection_open() as connection:
                cur = connection.cursor()
                if sqlparams is None:
                    cur.execute(sqlquery)
                else:
                    _logger.error("MAB - Query: %s - Params: %s" % (sqlquery, sqlparams))
                    #cur = connection.execute(sqlquery)
                    cur.execute(sqlquery, sqlparams)
                # If the query doesn't return rows, trying to get them anyway
                # will raise an exception `sqlalchemy.exc.ResourceClosedError`
                rows = cur.fetchall() #[r for r in cur] if cur.returns_rows else []
                if metadata:
                    cols = rows and list(rows[0].keys())
        return rows, cols
