#!/usr/bin/python3
#
# Author: Joshua Go
# Course: CPSC 326, Spring 2019
# Assignment: 6
# Description: Tests the AST tree created from the parser
#   ----------------------------------------------------------------------

import mypl_token as token
import mypl_ast as ast


class PrintVisitor(ast.Visitor):
    """An AST pretty printer"""

    def __init__(self, output_stream):
        self.indent = 0
        self.output_stream = output_stream

    def __indent(self):
        """Get default indent of four spaces"""
        return '    ' * self.indent

    def __write(self, msg):
        self.output_stream.write(msg)

    def visit_stmt_list(self, stmt_list):
        for stmt in stmt_list.stmts:
            stmt.accept(self)

    def visit_expr_stmt(self, expr_stmt):
        self.__write(self.__indent())
        expr_stmt.expr.accept(self)
        self.__write(';\n')

    def visit_var_decl_stmt(self, var_decl):
        self.__write(self.__indent() + 'var')
        self.__write(' ' + var_decl.var_id.lexeme)
        if var_decl.var_type is not None:
            self.__write(': ' + var_decl.var_type.lexeme)
        self.__write(' = ')
        var_decl.var_expr.accept(self)
        self.__write(';\n')

    def visit_assign_stmt(self, assign_stmt):
        self.__write(self.__indent() + 'set ')
        assign_stmt.lhs.accept(self)
        self.__write(' = ')
        assign_stmt.rhs.accept(self)
        self.__write(';\n')

    def visit_struct_decl_stmt(self, struct_decl):
        self.__write('\nstruct')
        self.__write(' ' + struct_decl.struct_id.lexeme + '\n')
        self.indent += 1
        for var_decl in struct_decl.var_decls:
            var_decl.accept(self)
        self.indent -= 1
        self.__write('end\n\n')

    def visit_fun_decl_stmt(self, fun_decl):
        self.__write('\nfun ')
        self.__write(fun_decl.return_type.lexeme)
        self.__write(' ')
        self.__write(fun_decl.fun_name.lexeme)
        self.__write('(')
        for i, param in enumerate(fun_decl.params):
            param.accept(self)
            if i != len(fun_decl.params) - 1:
                self.__write(', ')
        self.__write(')\n')
        self.indent += 1
        fun_decl.stmt_list.accept(self)
        self.indent -= 1
        self.__write('end\n\n')

    def visit_return_stmt(self, return_stmt):
        self.__write(self.__indent() + 'return')
        if return_stmt.return_expr is not None:
            self.__write(' ')
            return_stmt.return_expr.accept(self)
        self.__write(';\n')

    def visit_while_stmt(self, while_stmt):
        self.__write(self.__indent() + 'while ')
        while_stmt.bool_expr.accept(self)
        self.__write(' do\n')
        self.indent += 1
        while_stmt.stmt_list.accept(self)
        self.indent -= 1
        self.__write(self.__indent() + 'end\n')

    def visit_if_stmt(self, if_stmt):
        self.__write(self.__indent() + 'if ')
        if_stmt.if_part.bool_expr.accept(self)
        self.__write(' then\n')
        self.indent += 1
        if_stmt.if_part.stmt_list.accept(self)
        self.indent -= 1
        for elseif in if_stmt.elseifs:
            self.__write(self.__indent() + 'elif ')
            elseif.bool_expr.accept(self)
            self.__write(' then\n')
            self.indent += 1
            elseif.stmt_list.accept(self)
            self.indent -= 1
        if if_stmt.has_else:
            self.__write(self.__indent() + 'else\n')
            self.indent += 1
            if_stmt.else_stmts.accept(self)
            self.indent -= 1
        self.__write(self.__indent() + 'end\n')

    def visit_simple_expr(self, simple_expr):
        simple_expr.term.accept(self)

    def visit_complex_expr(self, complex_expr):
        self.__write('(')
        complex_expr.first_operand.accept(self)
        self.__write(' ' + complex_expr.math_rel.lexeme + ' ')
        complex_expr.rest.accept(self)
        self.__write(')')

    def visit_bool_expr(self, bool_expr):
        if bool_expr.negated:
            self.__write('not ')
        if bool_expr.bool_connector:
            self.__write('(')
        if bool_expr.bool_rel:
            self.__write('(')
        bool_expr.first_expr.accept(self)
        if bool_expr.bool_rel is not None:
            self.__write(' ' + bool_expr.bool_rel.lexeme + ' ')
            bool_expr.second_expr.accept(self)
            self.__write(')')
        if bool_expr.bool_connector is not None:
            self.__write(' ' + bool_expr.bool_connector.lexeme + ' ')
            bool_expr.rest.accept(self)
            self.__write(')')

    def visit_lvalue(self, lval):
        for i, path_id in enumerate(lval.path):
            self.__write(path_id.lexeme)
            if i != len(lval.path) - 1:
                self.__write('.')

    def visit_fun_param(self, fun_param):
        self.__write(fun_param.param_name.lexeme)
        self.__write(': ')
        self.__write(fun_param.param_type.lexeme)

    def visit_simple_rvalue(self, simple_rvalue):
        if simple_rvalue.val.tokentype == token.STRINGVAL:
            self.__write('"' + simple_rvalue.val.lexeme + '"')
        else:
            self.__write(simple_rvalue.val.lexeme)

    def visit_new_rvalue(self, new_rvalue):
        self.__write('new ')
        self.__write(new_rvalue.struct_type.lexeme)

    def visit_call_rvalue(self, call_rvalue):
        self.__write(call_rvalue.fun.lexeme)
        self.__write('(')
        for i, arg in enumerate(call_rvalue.args):
            arg.accept(self)
            if i != len(call_rvalue.args) - 1:
                self.__write(', ')
        self.__write(')')

    def visit_id_rvalue(self, id_rvalue):
        for i, path_id in enumerate(id_rvalue.path):
            self.__write(path_id.lexeme)
            if i != len(id_rvalue.path) - 1:
                self.__write('.')


