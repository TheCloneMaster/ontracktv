# Copyright 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def assign_old_sequences(env):
    expense_obj = env["hr.expense.sheet"]
    sequence_obj = env["ir.sequence"]
    for expense in expense_obj.search([], order="id"):
        expense.write({"number": sequence_obj.next_by_code("hr.expense.sheet")})
