#!/usr/bin/python3
#
# Author: Joshua Go
# Course: CPSC 326, Spring 2019
# Assignment: 7
# Description:
#   Implementation of a basic interpreter for MyPL
# ----------------------------------------------------------------------

import mypl_token as token
import mypl_ast as ast
import mypl_error as error
import mypl_symbol_table as sym_tbl


class ReturnException(Exception): pass


class Interpreter(ast.Visitor):
    """A MyPL interpreter visitor implementation"""

    def __init__(self):
        # initialize the symbol table (for ids -> values)
        self.sym_table = sym_tbl.SymbolTable()
        # holds the type of last expression type
        self.current_value = None
        # the heap {oid:struct_obj}
        self.heap = {}

    def __error(self, msg, the_token):
        raise error.MyPLError(msg, the_token.line, the_token.column)

    def __built_in_fun_helper(self, call_rvalue):
        fun_name = call_rvalue.fun.lexeme
        arg_vals = []
        # evaluate each call argument and store in arg_vals
        for i, arg in enumerate(call_rvalue.args):
            arg.accept(self)
            arg_vals.append(self.current_value)
        # check for nil values
        for i, arg in enumerate(arg_vals):
            if arg is None:
                self.__error('nil value error', call_rvalue.fun)
        # perform each function
        if fun_name == 'print':
            arg_vals[0] = arg_vals[0].replace(r'\n', '\n')
            print(arg_vals[0], end='')
        elif fun_name == 'length':
            self.current_value = len(arg_vals[0])
        elif fun_name == 'get':
            if 0 <= arg_vals[0] < len(arg_vals[1]):
                self.current_value = arg_vals[1][arg_vals[0]]
            else:
                self.__error('index out of range error', call_rvalue.fun)
        elif fun_name == 'reads':
            self.current_value = input()
        elif fun_name == 'readi':
            try:
                self.current_value = int(input())
            except ValueError:
                self.__error('bad int value', call_rvalue.fun)
        elif fun_name == 'readf':
            try:
                self.current_value = float(input())
            except ValueError:
                self.__error('bad float value', call_rvalue.fun)
        elif fun_name == 'itof':
            self.current_value = float(self.current_value)
        elif fun_name == 'itos':
            self.current_value = str(self.current_value)
        elif fun_name == 'ftos':
            self.current_value = str(self.current_value)
        elif fun_name == 'stoi':
            self.current_value = int(self.current_value)
        elif fun_name == 'stof':
            self.current_value = float(self.current_value)
        else:
            self.__error('unknown function call', call_rvalue.fun)

    def visit_stmt_list(self, stmt_list):
        self.sym_table.push_environment()
        for stmt in stmt_list.stmts:
            stmt.accept(self)
        self.sym_table.pop_environment()

    def visit_expr_stmt(self, expr_stmt):
        expr_stmt.expr.accept(self)

    def visit_var_decl_stmt(self, var_decl):
        var_decl.var_expr.accept(self)
        exp_value = self.current_value
        var_name = var_decl.var_id.lexeme
        self.sym_table.add_id(var_name)
        self.sym_table.set_info(var_name, exp_value)

    def visit_assign_stmt(self, assign_stmt):
        assign_stmt.lhs.accept(self)
        lhs_value = self.current_value
        assign_stmt.rhs.accept(self)
        rhs_value = self.current_value
        self.sym_table.set_info(lhs_value, rhs_value)

    def visit_struct_decl_stmt(self, struct_decl):
        struct_lexeme = struct_decl.struct_id.lexeme
        env_id = self.sym_table.get_env_id()
        self.sym_table.add_id(struct_lexeme)
        self.sym_table.set_info(struct_lexeme, [env_id, struct_decl])
        # for var_decl in struct_decl.var_decls:
        #     var_decl.accept(self)

    #
    # def visit_fun_decl_stmt(self, fun_decl):
    #     self.__write('\nfun ')
    #     self.__write(fun_decl.return_type.lexeme)
    #     self.__write(' ')
    #     self.__write(fun_decl.fun_name.lexeme)
    #     self.__write('(')
    #     for i, param in enumerate(fun_decl.params):
    #         param.accept(self)
    #         if i != len(fun_decl.params) - 1:
    #             self.__write(', ')
    #     self.__write(')\n')
    #     self.indent += 1
    #     fun_decl.stmt_list.accept(self)
    #     self.indent -= 1
    #     self.__write('end\n\n')
    #
    # def visit_return_stmt(self, return_stmt):
    #     self.__write(self.__indent() + 'return')
    #     if return_stmt.return_expr is not None:
    #         self.__write(' ')
    #         return_stmt.return_expr.accept(self)
    #     self.__write(';\n')
    #

    def visit_while_stmt(self, while_stmt):
        while_stmt.bool_expr.accept(self)
        self.sym_table.push_environment()
        cond_bool = self.current_value
        while cond_bool:   # loop while condition is true
            while_stmt.stmt_list.accept(self)
            while_stmt.bool_expr.accept(self)   # check if boolean expression of parameter is still true
            cond_bool = self.current_value
        self.sym_table.pop_environment()

    def visit_if_stmt(self, if_stmt):
        condition_met = False   # keeps track if the boolean condition is met in one of the if statements
        if_stmt.if_part.bool_expr.accept(self)
        conditional = self.current_value    # keeps track if statement boolean is true or false
        if conditional:
            self.sym_table.push_environment()
            if_stmt.if_part.stmt_list.accept(self)
            self.sym_table.pop_environment()
        else:
            for elseif in if_stmt.elseifs:
                elseif.bool_expr.accept(self)
                conditional = self.current_value
                if conditional and not condition_met:
                    condition_met = True
                    self.sym_table.push_environment()
                    elseif.stmt_list.accept(self)
                    self.sym_table.pop_environment()
            if if_stmt.has_else and not condition_met:
                self.sym_table.push_environment()
                if_stmt.else_stmts.accept(self)
                self.sym_table.pop_environment()

    def visit_simple_expr(self, simple_expr):
        simple_expr.term.accept(self)

    def visit_complex_expr(self, complex_expr):
        complex_expr.first_operand.accept(self)
        first_expr = self.current_value
        mathrel = complex_expr.math_rel.tokentype
        complex_expr.rest.accept(self)
        second_expr = self.current_value
        if mathrel == token.PLUS:
            self.current_value = first_expr + second_expr
        elif mathrel == token.MINUS:
            self.current_value = first_expr - second_expr
        elif mathrel == token.MULTIPLY:
            self.current_value = first_expr * second_expr
        elif mathrel == token.DIVIDE:
            if type(first_expr) == int and type(second_expr) == int:    # both values are int, result is an int
                self.current_value = int(first_expr / second_expr)
            else:
                self.current_value = first_expr / second_expr
        else:
            self.current_value = first_expr % second_expr

    def visit_bool_expr(self, bool_expr):
        is_negated = False  # expression is negated
        if bool_expr.negated:
            is_negated = True
        bool_expr.first_expr.accept(self)
        first_expr = self.current_value
        if self.sym_table.id_exists(first_expr):    # set first_expr to its value if ID
            first_expr = self.sym_table.get_info(first_expr)
        if bool_expr.bool_rel is not None:  # comparisons for booleans
            bool_expr.second_expr.accept(self)
            second_expr = self.current_value
            if bool_expr.bool_rel.tokentype == token.EQUAL:
                if first_expr == second_expr:
                    self.current_value = True
                else:
                    self.current_value = False
            elif bool_expr.bool_rel.tokentype == token.NOT_EQUAL:
                if first_expr == second_expr:
                    self.current_value = False
                else:
                    self.current_value = True
            elif bool_expr.bool_rel.tokentype == token.LESS_THAN:
                if first_expr < second_expr:
                    self.current_value = True
                else:
                    self.current_value = False
            elif bool_expr.bool_rel.tokentype == token.LESS_THAN_EQUAL:
                if first_expr <= second_expr:
                    self.current_value = True
                else:
                    self.current_value = False
            elif bool_expr.bool_rel.tokentype == token.GREATER_THAN:
                if first_expr > second_expr:
                    self.current_value = True
                else:
                    self.current_value = False
            elif bool_expr.bool_rel.tokentype == token.GREATER_THAN_EQUAL:
                if first_expr >= second_expr:
                    self.current_value = True
                else:
                    self.current_value = False

        if bool_expr.bool_connector is not None:    # AND, OR connectors
            first_rest_val = self.current_value
            bool_expr.rest.accept(self)
            second_rest_val = self.current_value
            if bool_expr.bool_connector.tokentype == token.AND:
                if first_rest_val == second_rest_val:
                    self.current_value = True
                else:
                    self.current_value = False
            elif bool_expr.bool_connector.tokentype == token.OR:
                if first_rest_val is True or second_rest_val is True:
                    self.current_value = True
                else:
                    self.current_value = False
        if is_negated:  # expression is negated
            if self.current_value is True:
                self.current_value = False
            else:
                self.current_value = True

    def visit_lvalue(self, lval):
        identifier = lval.path[0].lexeme
        self.current_value = self.sym_table.get_info(identifier)
        if len(lval.path) == 1:
            self.sym_table.set_info(identifier, self.current_value)
        else:
            for path_id in lval.path[1:]:
                identifier = path_id.lexeme  # handle path expressions
            struct_obj = self.heap[self.current_value]
            struct_obj[identifier] = self.sym_table.get_info(identifier)
            print(struct_obj)
            self.sym_table.set_info(identifier, self.current_value)
        self.current_value = identifier

    #
    # def visit_fun_param(self, fun_param):
    #     self.__write(fun_param.param_name.lexeme)
    #     self.__write(': ')
    #     self.__write(fun_param.param_type.lexeme)
    #

    def visit_simple_rvalue(self, simple_rvalue):
        if simple_rvalue.val.tokentype == token.INTVAL:
            self.current_value = int(simple_rvalue.val.lexeme)
        elif simple_rvalue.val.tokentype == token.FLOATVAL:
            self.current_value = float(simple_rvalue.val.lexeme)
        elif simple_rvalue.val.tokentype == token.BOOLVAL:
            self.current_value = True
            if simple_rvalue.val.lexeme == 'false':
                self.current_value = False
        elif simple_rvalue.val.tokentype == token.STRINGVAL:
            self.current_value = simple_rvalue.val.lexeme
        elif simple_rvalue.val.tokentype == token.NIL:
            self.current_value = None

    def visit_new_rvalue(self, new_rvalue):
        struct_info = self.sym_table.get_info(new_rvalue.struct_type.lexeme)
        for var_decl in struct_info[1].var_decls:
            var_decl.accept(self)
        # save current environment, go to struct def's environment
        curr_env = self.sym_table.get_env_id()
        self.sym_table.set_env_id(struct_info[0])
        # create empty struct, initialize vars, reset environment
        struct_obj = {}
        self.sym_table.push_environment()
        for var_decl in struct_info[1].var_decls:  # initialize struct_obj w/ vars in struct_info[1]
            var_decl.accept(self)
            struct_obj[var_decl.var_id.lexeme] = self.current_value
        self.sym_table.pop_environment()
        self.sym_table.set_env_id(curr_env)     # return to starting environment
        oid = id(struct_obj)    # create oid, add struct_obj to the heap, assign current value
        self.heap[oid] = struct_obj
        self.current_value = oid

    def visit_call_rvalue(self, call_rvalue):
        # handle built in functions first
        built_ins = ['print', 'length', 'get', 'readi', 'reads', 'readf', 'itof', 'itos', 'ftos', 'stoi', 'stof']
        if call_rvalue.fun.lexeme in built_ins:
            self.__built_in_fun_helper(call_rvalue)
        # else:
        # for i, arg in enumerate(call_rvalue.args):
        #     arg.accept(self)
        #     if i != len(call_rvalue.args) - 1:
        #         self.__write(', ')
        # self.__write(')')

    def visit_id_rvalue(self, id_rvalue):
        var_name = id_rvalue.path[0].lexeme
        var_val = self.sym_table.get_info(var_name)
        for path_id in id_rvalue.path[1:]:
            var_val = self.sym_table.get_info(path_id.lexeme)   # handle path expressions
        self.current_value = var_val