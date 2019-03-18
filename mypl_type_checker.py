#!/usr/bin/python3
#
# Author: Joshua Go
# Assignment: 6
# Description:
#   Implementation of the type checker class for MyPL. Will output errors if the types are not correct
#   in their ordering.
#   ---------------------------------------------------------------------

import mypl_token as token
import mypl_ast as ast
import mypl_error as error
import mypl_symbol_table as symbol_table

class TypeChecker(ast.Visitor):
    """A MyPL type checker visitor implementation where struct types
    take the form: type_id -> {v1:t1, ..., vn:tn} and function types
    take the form: fun_id -> [[t1, t2, ..., tn,], return_type]
    """

    def __init__(self):
        # initialize the symbol table (for ids -> types)
        self.sym_table = symbol_table.SymbolTable()
        # current_type holds the type of the last expression type
        self.current_type = None
        # current_token holds token of last expression type
        self.current_token = None
        # current_token holds lexeme of last expression type
        self.current_lexeme = None
        # global env (for return)
        self.sym_table.push_environment()
        # set global return type to int
        self.sym_table.add_id('return')
        self.sym_table.set_info('return', [token.INTTYPE])
        # load in built-in function types
        self.sym_table.add_id('print')  # initialize print function
        self.sym_table.set_info('print', [[token.STRINGTYPE], token.NIL])
        self.sym_table.add_id('length')     # initialize length function
        self.sym_table.set_info('length', [[token.STRINGTYPE], token.INTTYPE])
        self.sym_table.add_id('get')  # initialize get function
        self.sym_table.set_info('get', [[token.INTTYPE, token.STRINGTYPE], token.STRINGTYPE])
        self.sym_table.add_id('reads')  # initialize read string function
        self.sym_table.set_info('reads', [0, token.STRINGTYPE])
        self.sym_table.add_id('readi')  # initialize read int function
        self.sym_table.set_info('readi', [0, token.INTTYPE])
        self.sym_table.add_id('readf')  # initialize read float function
        self.sym_table.set_info('readf', [0, token.FLOATTYPE])
        # conversion functions
        self.sym_table.add_id('itos')  # initialize int to string function
        self.sym_table.set_info('itos', [[token.INTTYPE], token.STRINGTYPE])
        self.sym_table.add_id('ftos')  # initialize float to string function
        self.sym_table.set_info('ftos', [[token.FLOATTYPE], token.STRINGTYPE])
        self.sym_table.add_id('itof')  # initialize int to float function
        self.sym_table.set_info('itof', [[token.INTTYPE], token.FLOATTYPE])
        self.sym_table.add_id('stoi')  # initialize string to int function
        self.sym_table.set_info('stoi', [[token.STRINGTYPE], token.INTTYPE])
        self.sym_table.add_id('stof')  # initialize string to float function
        self.sym_table.set_info('stof', [[token.STRINGTYPE], token.FLOATTYPE])

    def __error(self, error_msg, name):
        l = name.line
        c = name.column
        raise error.MyPLError(error_msg, l, c)

    def visit_stmt_list(self, stmt_list):
        # add new block (scope)
        self.sym_table.push_environment()
        for stmt in stmt_list.stmts:
            stmt.accept(self)
        # remove new block
        self.sym_table.pop_environment()

    def visit_expr_stmt(self, expr_stmt):
        expr_stmt.expr.accept(self)

    def visit_var_decl_stmt(self, var_decl):
        is_implicit = True  # keeps track if there is an implicit type declaration
        var_decl_type = None
        if var_decl.var_type is not None:
            var_decl_type = var_decl.var_type
            is_implicit = False
        var_decl.var_expr.accept(self)
        var_decl_expr_type = self.current_type
        var_decl_expr_type_token = self.current_token
        # print(self.current_lexeme)
        # print(self.current_type)
        if not is_implicit:     # explicit type declaration
            is_struct_type = False
            struct_id_type = None
            if var_decl_type.tokentype == token.ID:
                if self.sym_table.id_exists(var_decl_type.lexeme):
                    struct_id_type = self.sym_table.get_info(var_decl_type.lexeme)
                    is_struct_type = True

            if is_struct_type:  # explicit declaration checks to see if id is a struct
                if struct_id_type != var_decl_expr_type:    # if the struct types are the not the same
                    if not var_decl_expr_type == token.NIL:
                        self.__error('mismatch type in assignment', var_decl_type)
                if var_decl_type.lexeme != self.current_lexeme:     # output error if struct var names are different
                    if not self.current_type == token.NIL:
                        self.__error('mismatch type in assignment', var_decl_type)
                # store variables into symbol table when there is a type declaration
                if self.sym_table.id_exists(var_decl.var_id.lexeme):  # update value if already in table
                    self.sym_table.set_info(var_decl.var_id.lexeme, var_decl_type.lexeme)
                else:  # add the variable to the sym table
                    # print(var_decl.var_id.lexeme)
                    # print(var_decl_type.lexeme)
                    # print(self.current_lexeme)
                    # print(var_decl_type.tokentype)
                    self.sym_table.add_id(var_decl.var_id.lexeme)
                    self.sym_table.set_info(var_decl.var_id.lexeme, var_decl_type.lexeme)
            else:   # explicit declaration if id is not a struct
                if var_decl_type.tokentype != var_decl_expr_type:
                    if not var_decl_expr_type == token.NIL:
                        self.__error('mismatch type in assignment', var_decl_type)
                    # store variables into symbol table when there is a type declaration
                if self.sym_table.id_exists(var_decl.var_id.lexeme):  # update value if already in table
                    self.sym_table.set_info(var_decl.var_id.lexeme, var_decl_type.tokentype)
                else:  # add the variable to the sym table
                    self.sym_table.add_id(var_decl.var_id.lexeme)
                    self.sym_table.set_info(var_decl.var_id.lexeme, var_decl_type.tokentype)
        else:   # implicit declaration
            types = [token.STRINGTYPE, token.INTTYPE, token.BOOLTYPE, token.FLOATTYPE, token.ID, token.NIL]
            if self.current_type not in types:  # type is a struct
                if self.sym_table.id_exists(var_decl.var_id.lexeme):    # update value if already in table
                    self.sym_table.set_info(var_decl.var_id.lexeme, self.current_lexeme)
                else:   # add the variable to the sym table
                    self.sym_table.add_id(var_decl.var_id.lexeme)
                    self.sym_table.set_info(var_decl.var_id.lexeme, self.current_lexeme)
            else:   # type is not a struct
                if var_decl_expr_type == token.NIL:
                    self.__error('mismatch type in assignment', var_decl_expr_type_token)
                # store variables into symbol table when the type is implied
                if self.sym_table.id_exists(var_decl.var_id.lexeme):    # update value if already in table
                    self.sym_table.set_info(var_decl.var_id.lexeme, var_decl_expr_type)
                else:   # add the variable to the sym table
                    self.sym_table.add_id(var_decl.var_id.lexeme)
                    self.sym_table.set_info(var_decl.var_id.lexeme, var_decl_expr_type)

    def visit_assign_stmt(self, assign_stmt):
        assign_stmt.rhs.accept(self)
        rhs_type = self.current_type
        assign_stmt.lhs.accept(self)
        lhs_type = self.current_type
        if rhs_type != token.NIL and rhs_type != lhs_type:
            msg = 'mismatch type in assignment'
            self.__error(msg, assign_stmt.lhs.path[0])

    def visit_struct_decl_stmt(self, struct_decl):
        types_dict = {}     # dictionary for struct
        self.sym_table.add_id(struct_decl.struct_id.lexeme)  # add struct id to sym table
        self.sym_table.push_environment()
        for var_decl in struct_decl.var_decls:
            var_decl.accept(self)
            id_info = self.sym_table.get_info(var_decl.var_id.lexeme)   # get info for id from sym_table
            types_dict.update({var_decl.var_id.lexeme: id_info})     # store values in dictionary
        self.sym_table.set_info(struct_decl.struct_id.lexeme, types_dict)
        self.sym_table.pop_environment()

    def visit_fun_decl_stmt(self, fun_decl):
        if fun_decl.return_type.tokentype == token.ID:
            return_type = fun_decl.return_type.lexeme
        else:
            return_type = fun_decl.return_type.tokentype
        fun_name = fun_decl.fun_name.lexeme
        param_list = []     # list of parameters
        param_token_list = []   # list of token parameters
        param_num = 0
        self.sym_table.add_id(fun_name)
        self.sym_table.set_info(fun_name, [param_list, return_type])
        self.sym_table.push_environment()
        self.sym_table.add_id('return')
        self.sym_table.set_info('return', return_type)
        for i, param in enumerate(fun_decl.params):
            param.accept(self)
            param_num = param_num + 1
            param_list.append(self.current_type)    # add parameters to list
            param_token_list.append(self.current_lexeme)    # add parameter tokens to list
        if self.has_duplicate(param_token_list):    # check for duplicates in parameters
            self.__error('duplicate variable declaration in parameter', self.current_token)
        fun_decl.stmt_list.accept(self)
        self.sym_table.pop_environment()
        self.sym_table.set_info(fun_name, [param_list, return_type])

    # checks if a list has a duplicate value
    def has_duplicate(self, param_token_list):
        i = 0
        j = i + 1
        while i < len(param_token_list):
            cur_token = param_token_list[i]
            while j < len(param_token_list):
                if cur_token == param_token_list[j]:
                    return True
                j = j + 1
            i = i + 1
        return False

    def visit_return_stmt(self, return_stmt):
        # self.__write(self.__indent() + 'return')
        if return_stmt.return_expr is not None:
            return_stmt.return_expr.accept(self)
        # if the return statement is the second scope in the program (ex. not in a function)
        if len(self.sym_table.scopes) == 2:
            if not (self.current_type == token.NIL or self.current_type == token.INTTYPE):
                self.__error('return statement must either return nil or a integer type', self.current_token)

    def visit_while_stmt(self, while_stmt):
        while_stmt.bool_expr.accept(self)
        self.sym_table.push_environment()
        while_stmt.stmt_list.accept(self)
        self.sym_table.pop_environment()

    def visit_if_stmt(self, if_stmt):
        if_stmt.if_part.bool_expr.accept(self)
        self.sym_table.push_environment()
        if_stmt.if_part.stmt_list.accept(self)
        self.sym_table.pop_environment()
        for elseif in if_stmt.elseifs:
            elseif.bool_expr.accept(self)
            self.sym_table.push_environment()
            elseif.stmt_list.accept(self)
            self.sym_table.pop_environment()
        if if_stmt.has_else:
            self.sym_table.push_environment()
            if_stmt.else_stmts.accept(self)
            self.sym_table.pop_environment()

    def visit_simple_expr(self, simple_expr):
        simple_expr.term.accept(self)

    def visit_complex_expr(self, complex_expr):
        complex_expr.first_operand.accept(self)
        first_expr_type = self.current_type
        first_expr_token = self.current_token
        complex_expr_mathrel = complex_expr.math_rel
        complex_expr.rest.accept(self)
        second_expr_type = self.current_type
        # tokens and mathrels for -, *, /
        mmd_expr_tokens = [token.INTTYPE, token.FLOATTYPE]
        mmd_mathrels = [token.MINUS, token.MULTIPLY, token.DIVIDE]
        if complex_expr_mathrel.tokentype == token.PLUS:    # plus token type checks
            plus_expr_tokens = [token.STRINGTYPE, token.INTTYPE, token.FLOATTYPE]
            if not (first_expr_type in plus_expr_tokens or second_expr_type in plus_expr_tokens):
                self.__error('mismatch type in assignment', first_expr_token)
        elif complex_expr_mathrel.tokentype in mmd_mathrels:    # minus, divide, modulo type checks
            if not (first_expr_type in mmd_expr_tokens or second_expr_type in mmd_expr_tokens):
                self.__error('mismatch type in assignment', first_expr_token)
        elif complex_expr_mathrel.tokentype == token.MODULO:    # modulo type checks
            if not (first_expr_type in token.INTTYPE or second_expr_type in token.INTTYPE):
                self.__error('mismatch type in assignment', first_expr_token)
        if first_expr_type != second_expr_type:     # output error if types are different
            self.__error('mismatch type in assignment', first_expr_token)

    def visit_bool_expr(self, bool_expr):
        bool_expr.first_expr.accept(self)
        first_expr_type = self.current_type
        first_expr_lexeme = self.current_lexeme
        second_expr_type = None
        second_expr_token = None
        second_expr_lexeme = None
        bool_expr_boolrel = None
        if bool_expr.bool_rel is not None:
            bool_expr_boolrel = bool_expr.bool_rel.lexeme
            bool_expr.second_expr.accept(self)
            second_expr_type = self.current_type
            second_expr_token = self.current_token
            second_expr_lexeme = self.current_lexeme
        if bool_expr.bool_connector is not None:
            bool_expr.rest.accept(self)
        expr_types = [token.INTTYPE, token.FLOATTYPE, token.BOOLTYPE, token.STRINGVAL, token.ID]
        boolrel = ['<', '>', '<=', '>=']
        if second_expr_type is not None:   # only a first_expr and second_expr
            if bool_expr_boolrel == '==' or bool_expr_boolrel == '!=':   # check equal and not equal boolrel cases
                if first_expr_type in expr_types:
                    if not (second_expr_type == token.NIL or second_expr_type == first_expr_type):
                        self.__error('mismatch type in assignment', second_expr_token)
                else:   # comparison of struct types
                    # print(first_expr_lexeme)
                    # print(second_expr_lexeme)
                    first_expr_lexeme_type = None
                    second_expr_lexeme_type = None
                    if self.sym_table.id_exists(first_expr_lexeme):     # get lexeme type of first_expr
                        first_expr_lexeme_type = self.sym_table.get_info(first_expr_lexeme)
                    else:
                        self.__error('variable not declared', second_expr_token)
                    if self.sym_table.id_exists(second_expr_lexeme):    # get lexeme type of second_expr if exists
                        second_expr_lexeme_type = self.sym_table.get_info(second_expr_lexeme)
                    else:
                        second_expr_lexeme_type = self.current_type
                    if not first_expr_lexeme_type == second_expr_lexeme_type:   # structs are not equal
                        if second_expr_type != token.NIL:
                            self.__error('mismatch type in assignment', second_expr_token)
            elif bool_expr_boolrel in boolrel:  # check the rest of boolrel cases
                if not first_expr_type == second_expr_type:
                    self.__error('mismatch type in assignment', second_expr_token)

    def visit_lvalue(self, lval):
        lexeme = ''
        is_object = False
        lexeme_list = []
        for i, path_id in enumerate(lval.path):
            lexeme += path_id.lexeme
            if i != len(lval.path) - 1:
                is_object = True
                lexeme_list.append(lexeme)
                # lexeme += '.'
                lexeme = ''
        lexeme_list.append(lexeme)
        types = [token.STRINGTYPE, token.INTTYPE, token.BOOLTYPE, token.FLOATTYPE, token.ID, token.NIL]
        if is_object:  # if id is an object
            object_name = None
            object_params = None
            i = 0
            while i < len(lexeme_list):
                if i == 0:
                    object_name = self.sym_table.get_info(lexeme_list[i])
                    object_params = self.sym_table.get_info(object_name)
                    if not isinstance(object_params, dict):
                        object_params = self.sym_table.get_info(object_params)
                elif lexeme_list[i] not in object_params and isinstance(object_params, dict):
                    struct_name = list(object_params.values())[0]
                    object_params = self.sym_table.get_info(struct_name)
                    self.current_type = object_params.get(lexeme_list[i])  # check if types are valid
                elif lexeme_list[i] in object_params:
                    self.current_type = object_params.get(lexeme_list[i])  # check if types are valid
                    # get struct type if type is a struct
                    if self.current_type not in types and self.sym_table.id_exists(self.current_type):
                        self.current_type = self.sym_table.get_info(self.current_type)
                else:
                    self.__error('variable not in object', self.current_token)
                i = i + 1
        else:
            if self.sym_table.id_exists(lexeme):
                self.current_type = self.sym_table.get_info(lexeme)
                if self.current_type not in types and self.sym_table.id_exists(self.current_type):
                    struct_name = self.sym_table.get_info(self.current_type)
                    self.current_type = struct_name
                self.current_lexeme = lexeme
            else:
                self.__error('value has not been declared', self.current_token)

    def visit_fun_param(self, fun_param):
        self.current_lexeme = fun_param.param_name.lexeme
        self.current_type = fun_param.param_type.tokentype
        if self.current_type is token.ID:
            self.current_type = fun_param.param_type.lexeme
        self.sym_table.add_id(self.current_lexeme)
        self.sym_table.set_info(self.current_lexeme, self.current_type)

    def visit_simple_rvalue(self, simple_rvalue):
        if simple_rvalue.val.tokentype == token.INTVAL:
            self.current_token = simple_rvalue.val
            self.current_type = token.INTTYPE
            self.current_lexeme = simple_rvalue.val.lexeme
        elif simple_rvalue.val.tokentype == token.FLOATVAL:
            self.current_token = simple_rvalue.val
            self.current_type = token.FLOATTYPE
            self.current_lexeme = simple_rvalue.val.lexeme
        elif simple_rvalue.val.tokentype == token.BOOLVAL:
            self.current_token = simple_rvalue.val
            self.current_type = token.BOOLTYPE
            self.current_lexeme = simple_rvalue.val.lexeme
        elif simple_rvalue.val.tokentype == token.STRINGVAL:
            self.current_token = simple_rvalue.val
            self.current_type = token.STRINGTYPE
            self.current_lexeme = simple_rvalue.val.lexeme
        elif simple_rvalue.val.tokentype == token.NIL:
            self.current_token = simple_rvalue.val
            self.current_type = token.NIL
            self.current_lexeme = simple_rvalue.val.lexeme

    def visit_new_rvalue(self, new_rvalue):
        if self.sym_table.id_exists(new_rvalue.struct_type.lexeme):
            self.current_type = self.sym_table.get_info(new_rvalue.struct_type.lexeme)
            self.current_lexeme = new_rvalue.struct_type.lexeme
        else:
            self.__error('value has not been declared', self.current_token)

    def visit_call_rvalue(self, call_rvalue):
        fun_name = call_rvalue.fun.lexeme
        if not self.sym_table.id_exists(fun_name):    # check if function was defined
            self.__error('function has not been declared', self.current_token)
        fun_type = self.sym_table.get_info(fun_name)   # type of the function
        self.current_type = self.sym_table.get_info('return')
        if fun_type[0] == 0:    # the function takes in no parameters
            self.current_type = fun_type[1]
        else:   # function takes in parameters
            fun_type_arg_list = fun_type[0]     # obtain arg list from function
            arg_list = []
            j = 0
            var_lexeme = ''
            for i, arg in enumerate(call_rvalue.args):
                arg.accept(self)
                if j == 0:
                    var_lexeme = self.current_lexeme
                    # print(var_lexeme)
                arg_list.append(self.current_type)  # add the function parameters to a list
                j = j + 1
            self.current_type = fun_type[-1]     # set output type of function
            self.current_lexeme = var_lexeme
            # print(fun_type_arg_list)
            # print(arg_list)
            #   need to fix bug when variable is set to a function
            # if fun_type_arg_list != arg_list:
            #     if token.NIL not in arg_list:   # if one of the inputs is not nil throw error
            #         self.__error('parameter types do not match up with function', self.current_token)

    def visit_id_rvalue(self, id_rvalue):
        lexeme = ''
        is_object = False
        lexeme_list = []
        for i, path_id in enumerate(id_rvalue.path):
            lexeme += path_id.lexeme
            if i != len(id_rvalue.path) - 1:
                is_object = True
                lexeme_list.append(lexeme)
                # lexeme += '.'
                lexeme = ''
        lexeme_list.append(lexeme)
        types = [token.STRINGTYPE, token.INTTYPE, token.BOOLTYPE, token.FLOATTYPE, token.ID, token.NIL]
        if is_object:   # if id is an object
            object_name = None
            object_params = None
            i = 0
            while i < len(lexeme_list):
                if i == 0:
                    object_name = self.sym_table.get_info(lexeme_list[i])
                    object_params = self.sym_table.get_info(object_name)
                    if not isinstance(object_params, dict):
                        object_params = self.sym_table.get_info(object_params)
                elif lexeme_list[i] not in object_params and isinstance(object_params, dict):
                    struct_name = list(object_params.values())[0]
                    object_params = self.sym_table.get_info(struct_name)
                    self.current_type = object_params.get(lexeme_list[i])  # check if types are valid
                elif lexeme_list[i] in object_params:
                    self.current_type = object_params.get(lexeme_list[i])   # check if types are valid
                else:
                    self.__error('variable not in object', self.current_token)
                i = i + 1

        else:   # if id is not an object
            if self.sym_table.id_exists(lexeme):
                self.current_type = self.sym_table.get_info(lexeme)
                self.current_lexeme = lexeme
            else:
                self.__error('value has not been declared', self.current_token)
