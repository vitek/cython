import cython
cython.declare(PyrexTypes=object, Naming=object, ExprNodes=object, Nodes=object,
               Options=object, UtilNodes=object, ModuleNode=object,
               LetNode=object, LetRefNode=object, TreeFragment=object,
               TemplateTransform=object, EncodedString=object,
               error=object, warning=object, copy=object)

import ExprNodes
import Nodes

from Cython.Compiler.Visitor import CythonTransform
from Cython.Compiler.Errors import error, warning, CompileError, InternalError

try:
    set
except NameError:
    from sets import Set as set

class ControlBlock(object):
    def __init__(self):
        self.stats = []
        self.gen = {}
        self.kill = {}

        self.children = set()
        self.parents = set()
        self.positions = set()

    def empty(self):
        return (not self.stats and not self.positions)

    def detach(self):
        """Detach block from parents and children"""
        for child in self.children:
            child.parents.remove(self)
        for parent in self.parents:
            parent.children.remove(self)
        self.parents.clear()
        self.children.clear()

    def add_child(self, block):
        self.children.add(block)
        block.parents.add(self)

    def add_position(self, node):
        self.positions.add(node.pos[:2])

    def add_assignment(self, lhs, rhs):
        assignment = Assignment(lhs, rhs)
        self.stats.append(assignment)
        self.gen[lhs.entry] = assignment

    def add_defnode(self, node, entry):
        from TypeInference import object_expr
        assignment = Assignment(node, object_expr)
        assignment.entry = entry
        self.stats.append(assignment)
        self.gen[entry] = assignment

    def add_name_node(self, node, entry):
        self.stats.append(VariableUse(node, entry))
        # Local variable is definitily bound after this block
        self.kill[node.entry] = Uninitialized

    def add_del(self, node):
        self.stats.append(DeleteVariable(node))
        self.gen[node.entry] = Uninitialized

    def add_argument(self, node):
        self.stats.append(Argument(node))


class ControlFlow(object):
    """Control-flow graph"""
    def __init__(self):
        self.branches = []
        self.loops = []
        self.exceptions = []
        self.blocks = set()
        self.block = None # Current block

    def newblock(self, parent=None, attach=True):
        block = ControlBlock()
        if attach:
            self.blocks.add(block)
        if parent:
            parent.add_child(block)
        return block

    def nextblock(self, parent=None):
        """Return new block linked to the current one."""
        block = ControlBlock()
        self.blocks.add(block)
        if parent:
            parent.add_child(block)
        elif self.block:
            self.block.add_child(block)
        self.block = block
        return self.block

    def normalize(self, root):
        """Delete unreachable and orphan blocks."""
        queue = set([root])
        visited = set()
        while queue:
            root = queue.pop()
            visited.add(root)
            for child in root.children:
                if child not in visited:
                    queue.add(child)
        unreachable = self.blocks - visited
        for block in unreachable:
            block.detach()
        for block in visited:
            if block.empty():
                for parent in block.parents: # Re-parent
                    for child in block.children:
                        parent.add_child(child)
                block.detach()
                unreachable.add(block)
        self.blocks -= unreachable


class LoopDescr(object):
    def __init__(self, next_block, loop_block):
        self.next_block = next_block
        self.loop_block = loop_block

class ExceptionDescr(object):
    def __init__(self, entry_point, finally_point=None, finally_end=None):
        self.entry_point = entry_point
        self.finally_point = finally_point
        self.finally_end = finally_end

class Assignment(object):
    is_initialized = True

    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.entry = lhs.entry
        self.pos = lhs.pos

    def __repr__(self):
        return '%s(entry=%r)' % (self.__class__.__name__, self.entry)

class Uninitialized(object):
    is_initialized = False

class Argument(Assignment):
    def __init__(self, entry):
        self.entry = entry
        self.pos = None

class VariableUse(object):
    def __init__(self, node, entry):
        self.node = node
        self.entry = entry
        self.pos = node.pos

    def __repr__(self):
        return '%s(entry=%r)' % (self.__class__.__name__, self.entry)

class GVContext(object):
    def __init__(self):
        self.blockids = {}
        self.nextid = 0
        self.children = []
        self.sources = {}

    def add(self, child):
        self.children.append(child)

    def nodeid(self, block):
        if block not in self.blockids:
            self.blockids[block] = 'block%d' % self.nextid
            self.nextid += 1
        return self.blockids[block]

    def extract_sources(self, block):
        if not block.positions:
            return ''
        start = min(block.positions)
        stop = max(block.positions)
        srcdescr = start[0]
        if not srcdescr in self.sources:
            self.sources[srcdescr] = list(srcdescr.get_lines())
        lines = self.sources[srcdescr]
        return '\\n'.join([l.strip() for l in lines[start[1] - 1:stop[1]]])

    def render(self, fp, name, annotate_defs=False):
        """Render graphviz dot graph"""
        fp.write('digraph %s {\n' % name)
        fp.write(' node [shape=box];\n')
        for child in self.children:
            child.render(fp, self, annotate_defs)
        fp.write('}\n')

    def escape(self, text):
        return text.replace('"', '\\"').replace('\n', '\\n')

class GV(object):
    def __init__(self, name, flow):
        self.name = name
        self.flow = flow

    def render(self, fp, ctx, annotate_defs=False):
        fp.write(' subgraph %s {\n' % self.name)
        for block in self.flow.blocks:
            label = ctx.extract_sources(block)
            if annotate_defs:
                for stat in block.stats:
                    if isinstance(stat, Assignment):
                        label += '\n %s [definition]' % stat.entry.name
                    elif isinstance(stat, VariableUse):
                        if stat.entry:
                            label += '\n %s [reference]' % stat.entry.name
            if not label:
                label = 'empty'
            pid = ctx.nodeid(block)
            fp.write('  %s [label="%s"];\n' % (pid, ctx.escape(label)))
        for block in self.flow.blocks:
            pid = ctx.nodeid(block)
            for child in block.children:
                fp.write('  %s -> %s;\n' % (pid, ctx.nodeid(child)))
        fp.write(' }\n')


class CreateControlFlowGraph(CythonTransform):
    """Create NameNode use and assignment graph."""

    def visit_ModuleNode(self, node):
        self.gv_ctx = GVContext()

        self.env_stack = []
        self.env = node.scope
        self.stack = []
        self.flow = ControlFlow()
        self.flow.nextblock()
        self.visitchildren(node)

        dot_output = self.current_directives['control_flow.dot_output']
        if dot_output:
            annotate_defs = self.current_directives['control_flow.dot_annotate_defs']
            try:
                fp = open(dot_output, 'wt')
                self.gv_ctx.render(fp, 'module', annotate_defs=annotate_defs)
            finally:
                fp.close()
        return node

    def check_definitions(self, node, flow, entry_point):
        """Based on algo 9.11 from dragon book."""
        for block in flow.blocks:
            block.input = {}
            block.output = {}
            for entry, item in block.gen.items():
                block.output[entry] = set([item])
        entry_point.input = {}
        entry_point.output = {}
        for entry in node.local_scope.entries.values():
            if entry.from_closure or entry.is_pyglobal or entry.is_cglobal:
                continue
            if entry.is_arg:
                obj = Argument(entry)
            else:
                obj = Uninitialized
            entry_point.gen[entry] = obj
            entry_point.output[entry] = set([obj])
        dirty = True
        while dirty:
            dirty = False
            for block in flow.blocks:
                input = {}
                for parent in block.parents:
                    for entry, items in parent.output.items():
                        if entry in input:
                            input[entry].update(items)
                        else:
                            input[entry] = items.copy()
                output = {}
                for entry, items in input.items():
                    output[entry] = items.copy()
                for entry in block.kill.keys():
                    output[entry] = set([])
                for entry, item in block.gen.items():
                    output[entry] = set([item])
                if output != block.output:
                    dirty = True
                block.input = input
                block.output = output
        for block in flow.blocks:
            state = {}
            for entry, items in block.input.items():
                state[entry] = items.copy()
            for stat in block.stats:
                if isinstance(stat, Assignment):
                    state[stat.entry] = set([stat])
                elif isinstance(stat, VariableUse):
                    if stat.entry not in state:
                        continue
                    if Uninitialized in state[stat.entry]:
                        if len(state[stat.entry]) == 1:
                            warning(stat.pos, "'%s' is used uninitialized" % stat.entry.name, 2)
                        else:
                            warning(stat.pos, "'%s' might be used uninitialized" % stat.entry.name, 2)
                        state[stat.entry] -= set([Uninitialized])

    def visit_FuncDefNode(self, node):
        self.env_stack.append(self.env)
        self.env = node.local_scope
        self.stack.append(self.flow)
        self.flow = ControlFlow()

        # Enter block
        def_block = self.flow.newblock(attach=False)
        def_block.add_position(node)
        # Function body block
        self.flow.nextblock(def_block)
        self.visitchildren(node)
        # Cleanup graph
        self.flow.normalize(def_block)
        self.check_definitions(node, self.flow, def_block)
        self.flow.blocks.add(def_block)

        self.gv_ctx.add(GV(node.local_scope.name, self.flow))

        self.flow = self.stack.pop()
        self.env = self.env_stack.pop()
        return node

    def visit_DefNode(self, node):
        if self.flow.block:
            self.flow.block.add_defnode(node, self.env.lookup(node.name))
        return self.visit_FuncDefNode(node)

    def mark_assignment(self, lhs, rhs=None, internal=False):
        if not self.flow.block:
            return
        if self.flow.exceptions:
            self.flow.nextblock()
        if not rhs:
            from TypeInference import object_expr
            rhs = object_expr
        if isinstance(lhs, (ExprNodes.NameNode, Nodes.PyArgDeclNode)):
            if lhs.entry is None:
                # TODO: This shouldn't happen...
                return
            self.flow.block.add_assignment(lhs, rhs)
        elif isinstance(lhs, ExprNodes.SequenceNode):
            for arg in lhs.args:
                self.mark_assignment(arg, internal=True)
        else:
            # Could use this info to infer cdef class attributes...
            pass

    def visit_FromImportStatNode(self, node):
        for name, target in node.items:
            if name != "*":
                self.mark_assignment(target)
        self.visitchildren(node)
        return node

    def visit_SingleAssignmentNode(self, node):
        self.visit(node.rhs)
        self.mark_assignment(node.lhs)
        return node

    def visit_CascadedAssignmentNode(self, node):
        self.visit(node.rhs)
        for lhs in node.lhs_list:
            self.mark_assignment(lhs, node.rhs)
        return node

    def visit_CArgDeclNode(self, node):
        if self.flow.block:
            self.flow.block.add_argument(node)
        return node

    def visit_PyArgDeclNode(self, node):
        if self.flow.block:
            self.flow.block.add_argument(node)
        return node

    def visit_NameNode(self, node):
        if self.flow.block:
            entry = node.entry or self.env.lookup(node.name)
            if entry:
                self.flow.block.add_name_node(node, entry)
        return node

    def visit_StatListNode(self, node):
        for stat in node.stats:
            if not self.flow.block:
                break
            self.visit(stat)
        return node

    def visit_Node(self, node):
        self.visitchildren(node)
        if self.flow.block:
            self.flow.block.add_position(node)
        return node

    def visit_IfStatNode(self, node):
        next_block = self.flow.newblock()
        parent = self.flow.block
        # If clauses
        for clause in node.if_clauses:
            parent = self.flow.nextblock(parent)
            self.visit(clause.condition)
            self.flow.nextblock()
            self.visit(clause.body)
            if self.flow.block:
                self.flow.block.add_child(next_block)
        # Else clause
        if node.else_clause:
            self.flow.nextblock(parent=parent)
            self.visit(node.else_clause)
            if self.flow.block:
                self.flow.block.add_child(next_block)
        else:
            parent.add_child(next_block)

        if next_block.parents:
            self.flow.block = next_block
        else:
            self.flow.block = None
        return node

    def visit_WhileStatNode(self, node):
        condition_block = self.flow.nextblock()
        next_block = self.flow.newblock()
        # Condition block
        self.flow.loops.append(LoopDescr(next_block, condition_block))
        self.visit(node.condition)
        # Body block
        self.flow.nextblock()
        self.visit(node.body)
        # Loop it
        if self.flow.block:
            self.flow.block.add_child(condition_block)
            self.flow.block.add_child(next_block)
        # Else clause
        if node.else_clause:
            self.flow.nextblock(parent=condition_block)
            self.visit(node.else_clause)
            if self.flow.block:
                self.flow.block.add_child(next_block)
        else:
            condition_block.add_child(next_block)
        self.flow.loops.pop()
        self.flow.block = next_block
        return node

    def visit_ForInStatNode(self, node):
        condition_block = self.flow.nextblock()
        next_block = self.flow.newblock()
        # Condition with iterator
        self.flow.loops.append(LoopDescr(next_block, condition_block))
        self.visit(node.iterator)
        # Target assignment
        self.flow.nextblock()
        self.mark_assignment(node.target)
        # Body block
        self.flow.nextblock()
        self.visit(node.body)
        # Loop it
        if self.flow.block:
            self.flow.block.add_child(condition_block)
        # Else clause
        if node.else_clause:
            self.flow.nextblock(parent=condition_block)
            self.visit(node.else_clause)
            if self.flow.block:
                self.flow.block.add_child(next_block)
        else:
            condition_block.add_child(next_block)
        self.flow.loops.pop()
        self.flow.block = next_block
        return node

    def visit_ForFromStatNode(self, node):
        raise InternalError, "for-from statement is not supported now"

    def visit_LoopNode(self, node):
        raise InternalError, "Generic loops are not supported"

    def visit_WithStatNode(self, node):
        # never be here: WithStatNode is replaced with try except finally
        raise InternalError, "with statement is not supported"

    def visit_TryExceptStatNode(self, node):
        # After exception handling
        next_block = self.flow.newblock()
        # Body block
        self.flow.newblock()
        # Exception entry point
        entry_point = self.flow.newblock()
        self.flow.exceptions.append(ExceptionDescr(entry_point))
        self.flow.nextblock()
        ## XXX: links to exception handling point should be added by
        ## XXX: children nodes
        self.flow.block.add_child(entry_point)
        self.visit(node.body)
        self.flow.exceptions.pop()

        # After exception
        if self.flow.block:
            if node.else_clause:
                self.flow.nextblock()
                self.visit(node.else_clause)
            if self.flow.block:
                self.flow.block.add_child(next_block)

        for clause in node.except_clauses:
            self.flow.block = entry_point
            if clause.pattern:
                for pattern in clause.pattern:
                    self.visit(pattern)
            else:
                # TODO: handle * pattern
                pass
            if clause.target:
                self.mark_assignment(clause.target)
            entry_point = self.flow.newblock(parent=self.flow.block)
            self.flow.nextblock()
            self.visit(clause.body)
            if self.flow.block:
                self.flow.block.add_child(next_block)

        if self.flow.exceptions:
            entry_point.add_child(self.flow.exceptions[-1].entry_point)

        if next_block.parents:
            self.flow.block = next_block
        else:
            self.flow.block = None
        return node

    def visit_TryFinallyStatNode(self, node):
        body_block = self.flow.nextblock()

        # Exception entry point
        entry_point = self.flow.newblock()
        self.flow.block = entry_point
        self.visit(node.finally_clause)

        # Normal execution
        finally_point = self.flow.newblock()
        self.flow.block = finally_point
        self.visit(node.finally_clause)
        finally_end = self.flow.block

        self.flow.exceptions.append(ExceptionDescr(entry_point, finally_point, finally_end))
        self.flow.block = body_block
        ## XXX: Is it still required
        body_block.add_child(entry_point)
        self.visit(node.body)
        self.flow.exceptions.pop()

        if self.flow.block:
            self.flow.block.add_child(finally_point)
            if finally_end:
                self.flow.block = self.flow.nextblock(parent=finally_end)
            else:
                self.flow.block = None
        return node

    def visit_RaiseStatNode(self, node):
        self.flow.block.add_position(node)
        if self.flow.exceptions:
            self.flow.block.add_child(self.flow.exceptions[-1].entry_point)
        self.flow.block = None
        return node

    def visit_ReraiseStatNode(self, node):
        self.flow.block.add_position(node)
        if self.flow.exceptions:
            self.flow.block.add_child(self.flow.exceptions[-1].entry_point)
        self.flow.block = None
        return node

    def visit_ReturnStatNode(self, node):
        self.flow.block.add_position(node)
        self.visitchildren(node)

        for exception in self.flow.exceptions[::-1]:
            if exception.finally_point:
                self.flow.block.add_child(exception.finally_point)
                # Add exit reference
                break
        else:
            pass # Exit ref
        self.flow.block = None
        return node

    def visit_BreakStatNode(self, node):
        if not self.flow.loops:
            error(node.pos, "break statement not inside loop")
            return node
        loop = self.flow.loops[-1]
        self.flow.block.add_position(node)
        for exception in self.flow.exceptions[::-1]:
            if exception.finally_point:
                self.flow.block.add_child(exception.finally_point)
                if exception.finally_end:
                    exception.finally_end.add_child(loop.next_block)
                break
        else:
            self.flow.block.add_child(loop.next_block)
        self.flow.block = None
        return node

    def visit_ContinueStatNode(self, node):
        if not self.flow.loops:
            error(node.pos, "continue statement not inside loop")
            return node
        loop = self.flow.loops[-1]
        self.flow.block.add_position(node)
        for exception in self.flow.exceptions[::-1]:
            if exception.finally_point:
                self.flow.block.add_child(exception.finally_point)
                if exception.finally_end:
                    exception.finally_end.add_child(loop.loop_block)
                break
        else:
            self.flow.block.add_child(loop.loop_block)
        self.flow.block = None
        return node
