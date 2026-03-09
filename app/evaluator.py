import re
from app.context import SessionContext
from app.models.expression import Expression, CellType

class Evaluator:
    OPERATORS = set(['+', '-', '*', '/', 'RANGE', 'SUM'])  # Add more as needed

    def __init__(self, context: SessionContext):
        self.context = context

    def split_args(self, args_str: str) -> list[str]:
        """Splits a string by commas, respecting nested parentheses."""
        parts = []
        current = []
        depth = 0
        for char in args_str:
            if char == ',' and depth == 0:
                parts.append("".join(current).strip())
                current = []
            else:
                if char == '(': depth += 1
                if char == ')': depth -= 1
                current.append(char)
        parts.append("".join(current).strip())
        return parts

    def expand_range(self, start_cell: str, end_cell: str) -> list[str]:
        """Converts 'A1:B2' into ['A1', 'A2', 'B1', 'B2']"""
        def split_ref(ref):
            match = re.match(r"([A-Z]+)(\d+)", ref.upper())
            return match.group(1), int(match.group(2))

        start_col_str, start_row = split_ref(start_cell)
        end_col_str, end_row = split_ref(end_cell)

        # Convert column letters to numbers (A=0, B=1...)
        def col_to_num(col):
            num = 0
            for char in col:
                num = num * 26 + (ord(char) - ord('A') + 1)
            return num - 1

        def num_to_col(num):
            col = ""
            while num >= 0:
                col = chr(num % 26 + ord('A')) + col
                num = num // 26 - 1
            return col

        start_col = col_to_num(start_col_str)
        end_col = col_to_num(end_col_str)

        cells = []
        for c in range(min(start_col, end_col), max(start_col, end_col) + 1):
            for r in range(min(start_row, end_row), max(start_row, end_row) + 1):
                cells.append(f"{num_to_col(c)}{r}")
        return cells

    def split_expression(self, expr: str):
        expr = expr.strip()

        # 1. Handle Top-Level Parentheses: (A1+A2) -> A1+A2
        # Only strip if the parentheses wrap the entire expression and are balanced
        if expr.startswith('(') and expr.endswith(')'):
            # Verify these are a matching pair (not "(A1+A2)+(B1+B2)")
            inner = expr[1:-1]
            if self._is_balanced(inner):
                return self.split_expression(inner)

        # 2. Functional notation: name(args)
        func_match = re.match(r"^(\w+)\((.*)\)$", expr)
        if func_match:
            return {
                "operator": func_match.group(1).upper(),
                "operands": self.split_args(func_match.group(2))
            }

        # 3. Range operator (High Precedence)
        if ':' in expr:
            range_match = re.match(r"^([A-Z]+\d+):([A-Z]+\d+)$", expr, re.IGNORECASE)
            if range_match:
                return {
                    "operator": "RANGE",
                    "operands": self.expand_range(range_match.group(1).upper(), range_match.group(2).upper())
                }

        # 4. Standard Infix Operators (Search for TOP-LEVEL operators only)
        # We iterate in reverse precedence (Add/Sub first) so they become the root of the tree
        for op in ['+', '-', '*', '/']:
            op_idx = self._find_top_level_operator(expr, op)
            if op_idx != -1:
                left = expr[:op_idx].strip()
                right = expr[op_idx+1:].strip()
                return {"operator": op, "operands": [left, right]}

        return {"operator": "identity", "operands": [expr]}

    def _is_balanced(self, text: str) -> bool:
        """Helper to ensure parentheses are balanced within a substring."""
        count = 0
        for char in text:
            if char == '(': count += 1
            elif char == ')': count -= 1
            if count < 0: return False
        return count == 0

    def _find_top_level_operator(self, expr: str, target_op: str) -> int:
        """Finds the index of an operator not enclosed in parentheses."""
        paren_level = 0
        # Search backwards (right-to-left) to handle left-associativity correctly
        for i in range(len(expr) - 1, -1, -1):
            char = expr[i]
            if char == ')': paren_level += 1
            elif char == '(': paren_level -= 1
            elif char == target_op and paren_level == 0:
                return i
        return -1

    def _verify_acyclic(self, cell: str, expr: str) -> bool:
        """Check for cyclic dependencies starting from the given cell."""
        dependencies = set([cell])

        def recursive_helper(expr: str):
            parsed = self.split_expression(expr)

            if parsed["operator"] == "identity":
                if re.match(r"^[A-Z]+\d+$", parsed["operands"][0], re.IGNORECASE):
                    if cell in self.context.state.dependencies.get(parsed["operands"][0].upper(), set()):
                        raise ValueError(f"Cyclic dependency detected: {cell} -> {parsed['operands'][0].upper()}")

                    dependencies.add(parsed["operands"][0].upper())

                    for dep in self.context.state.dependencies.get(parsed["operands"][0].upper(), set()):
                        dependencies.add(dep)
            else:
                for operand in parsed["operands"]:
                    recursive_helper(operand)

        recursive_helper(expr)

        # Successful
        dependencies.remove(cell)  # Remove self reference
        self.context.state.dependencies[cell] = dependencies
        return True

    def _recursive_expression(self, expr: str) -> Expression:
        """Recursively evaluate an expression string."""
        parsed = self.split_expression(expr)

        if parsed["operator"] == "identity":
            operand = parsed["operands"][0]
            if re.match(r"^[A-Z]+\d+$", operand, re.IGNORECASE):
                return Expression(raw=operand, type=CellType.REF, value=operand)
            elif re.match(r'^[+-]?(\d+(\.\d*)?|\.\d+)$', operand):
                    return Expression(raw=operand, value=float(operand), type=CellType.NUMBER)
            else:
                return Expression(raw=operand, value=operand, type=CellType.STRING)

        else:
            operands = []
            for operand in parsed["operands"]:
                operand_exp = self._recursive_expression(operand)
                operands.append(operand_exp)

            return Expression(
                raw=expr,
                operator=parsed["operator"],
                operands=operands,
                type=CellType.FORMULA
            )

    def string_to_expression(self, cell: str, expression_str: str) -> Expression:
        if expression_str.startswith('='):
            if self._verify_acyclic(cell, expression_str[1:]):
                self.context.logger.info(f"Expression for cell {cell} is acyclic.")
                self.mark_dependencies(cell)

            exp = self._recursive_expression(expression_str[1:])
            return exp

        else:
            if re.match(r'^[+-]?(\d+(\.\d*)?|\.\d+)$', expression_str):
                return Expression(raw=expression_str, value=float(expression_str), type=CellType.NUMBER)
            else:
                return Expression(raw=expression_str, value=expression_str, type=CellType.STRING)

    def evaluate(self, expression: Expression) -> float | str:
        if expression.type == CellType.NUMBER:
            return expression.value
        elif expression.type == CellType.STRING:
            return expression.value
        elif expression.type == CellType.REF:
            ref_cell = expression.value.upper()

            if ref_cell not in self.context.state.dirty_cells and ref_cell in self.context.state.evaluation_cache:
                return self.context.state.evaluation_cache[ref_cell]

            old_value = None
            if ref_cell in self.context.state.dependencies.get(ref_cell, set()):
                old_value = self.context.state.evaluation_cache.get(ref_cell)

            ref_expr = self.context.state.spreadsheet.get(ref_cell)

            if ref_expr is None:
                self.context.logger.warning(f"Reference to empty cell {ref_cell}")
                return None

            val = self.evaluate(ref_expr)

            if val == old_value:
                return val

            self.context.state.evaluation_cache[ref_cell] = val
            self.update_dependencies(ref_cell) # mark dependents as dirty since this value may have changed
            return val

        elif expression.type == CellType.FORMULA:
            evaluated_operands = [self.evaluate(self._recursive_expression(op.raw)) for op in expression.operands]
            if expression.operator == '+':
                return sum(evaluated_operands)
            elif expression.operator == '-':
                return evaluated_operands[0] - evaluated_operands[1]
            elif expression.operator == '*':
                result = 1
                for op in evaluated_operands:
                    result *= op
                return result
            elif expression.operator == '/':
                if evaluated_operands[1] == 0:
                    raise ValueError("Division by zero error.")
                return evaluated_operands[0] / evaluated_operands[1]
            elif expression.operator == "RANGE":
                # For simplicity, just return a list of values for the range
                return self._evaluate_range(expression)
            elif expression.operator == "SUM":
                return self._evaluate_sum(expression)
            else:
                raise ValueError(f"Unknown operator: {expression.operator}")

    def mark_dependencies(self, cell: str):
        for other_cell in self.context.state.spreadsheet:
            if cell in self.context.state.dependencies.get(other_cell, set()):
                self.context.state.upward_dependencies.setdefault(cell, set()).add(other_cell)
                self.context.state.dirty_cells.add(cell)

        for dep in self.context.state.dependencies.get(cell, set()):
            self.context.state.upward_dependencies.setdefault(dep, set()).add(cell)

    def update_dependencies(self, cell: str):
        """After a cell is updated, mark all dependent cells as dirty."""
        for dependent in self.context.state.upward_dependencies.get(cell, set()):
            self.context.state.dirty_cells.add(dependent)

    def _evaluate_range(self, expression: Expression) -> list[float | str]:
        if expression.operator != "RANGE":
            raise ValueError("Expression is not a range.")

        results = []
        for exp in expression.operands:
            cell = exp.value.upper()

            if not re.match(r"^[A-Z]+\d+$", cell, re.IGNORECASE):
                raise ValueError(f"Invalid cell reference in range: {cell}")

            ref_expr = self.context.state.spreadsheet.get(cell)
            if ref_expr is None:
                results.append(None)
            else:
                results.append(self.evaluate(ref_expr))
        return results

    def _evaluate_sum(self, expression: Expression) -> float:
        if expression.operator != "SUM":
            raise ValueError("Expression is not a SUM function.")

        total = 0

        if len(expression.operands) == 1 and expression.operands[0].operator == "RANGE":
            # Special case: SUM(A1:A10)
            range_values = self._evaluate_range(expression.operands[0])
            for value in range_values:
                if isinstance(value, (int, float)):
                    total += value

            return total

        for operand in expression.operands:
            value = self.evaluate(self._recursive_expression(operand.raw))
            if isinstance(value, (int, float)):
                # Only sum numeric values, ignore strings or errors
                total += value
        return total

    def _evaluate_average(self, expression: Expression) -> float:
        if expression.operator != "AVERAGE":
            raise ValueError("Expression is not an AVERAGE function.")

        total = 0
        count = 0
        for operand in expression.operands:
            value = self.evaluate(self._recursive_expression(operand.raw))
            if isinstance(value, (int, float)):
                total += value
                count += 1

        if count == 0:
            raise ValueError("No numeric values to average.")
        return total / count