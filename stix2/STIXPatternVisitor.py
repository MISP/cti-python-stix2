import stix2
from antlr4 import *
import six
from stix2patterns.grammars.STIXPatternParser import *
from stix2patterns.grammars.STIXPatternVisitor import STIXPatternVisitor
from antlr4 import CommonTokenStream, InputStream
from stix2patterns.grammars.STIXPatternLexer import STIXPatternLexer
from stix2patterns.grammars.STIXPatternParser import STIXPatternParser
from stix2patterns.validator import STIXPatternErrorListener
import importlib
import inspect


def collapse_lists(lists):
    result = []
    for c in lists:
        if isinstance(c, list):
            result.extend(c)
        else:
            result.append(c)
    return result

# This class defines a complete generic visitor for a parse tree produced by STIXPatternParser.

class STIXPatternVisitorForSTIX2(STIXPatternVisitor):
    classes = {}

    def __init__(self, module_suffix, module_name):
        self.module_suffix = module_suffix
        if STIXPatternVisitorForSTIX2.classes == {}:
            module = importlib.import_module(module_name)
            for k, c in inspect.getmembers(module, inspect.isclass):
                STIXPatternVisitorForSTIX2.classes[k] = c
        super(STIXPatternVisitor, self).__init__()

    def get_class(self, class_name):
        return STIXPatternVisitorForSTIX2.classes[class_name]

    def instantiate(self, klass_name, *args):
        if self.module_suffix:
            klass_to_instantiate = self.get_class(klass_name + "For" + self.module_suffix)
        else:
            # use the classes in python_stix2
            klass_to_instantiate = globals()[klass_name]
        return klass_to_instantiate(*args)

    # Visit a parse tree produced by STIXPatternParser#pattern.
    def visitPattern(self, ctx):
        children = self.visitChildren(ctx)
        return children[0]


    # Visit a parse tree produced by STIXPatternParser#observationExpressions.
    def visitObservationExpressions(self, ctx):
        children = self.visitChildren(ctx)
        if len(children) == 1:
            return children[0]
        else:
            return stix2.FollowedByObservationExpression([children[0], children[2]])

    # Visit a parse tree produced by STIXPatternParser#observationExpressionOr.
    def visitObservationExpressionOr(self, ctx):
        children = self.visitChildren(ctx)
        if len(children) == 1:
            return children[0]
        else:
            return self.instantiate("OrObservationExpression", [children[0], children[2]])


    # Visit a parse tree produced by STIXPatternParser#observationExpressionAnd.
    def visitObservationExpressionAnd(self, ctx):
        children = self.visitChildren(ctx)
        if len(children) == 1:
            return children[0]
        else:
            return self.instantiate("AndObservationExpression", [children[0], children[2]])


    # Visit a parse tree produced by STIXPatternParser#observationExpressionRepeated.
    def visitObservationExpressionRepeated(self, ctx):
        children = self.visitChildren(ctx)
        return self.instantiate("QualifiedObservationExpression", children[0], children[1])


    # Visit a parse tree produced by STIXPatternParser#observationExpressionSimple.
    def visitObservationExpressionSimple(self, ctx):
        children = self.visitChildren(ctx)
        return self.instantiate("ObservationExpression", children[1])


    # Visit a parse tree produced by STIXPatternParser#observationExpressionCompound.
    def visitObservationExpressionCompound(self, ctx):
        children = self.visitChildren(ctx)
        return self.instantiate("ObservationExpression", children[1])


    # Visit a parse tree produced by STIXPatternParser#observationExpressionWithin.
    def visitObservationExpressionWithin(self, ctx):
        children = self.visitChildren(ctx)
        return self.instantiate("QualifiedObservationExpression", children[0], children[1])


    # Visit a parse tree produced by STIXPatternParser#observationExpressionStartStop.
    def visitObservationExpressionStartStop(self, ctx):
        children = self.visitChildren(ctx)
        return self.instantiate("QualifiedObservationExpression", children[0], children[1])


    # Visit a parse tree produced by STIXPatternParser#comparisonExpression.
    def visitComparisonExpression(self, ctx):
        children = self.visitChildren(ctx)
        if len(children) == 1:
            return children[0]
        else:
            return self.instantiate("OrBooleanExpression", [children[0], children[2]])


    # Visit a parse tree produced by STIXPatternParser#comparisonExpressionAnd.
    def visitComparisonExpressionAnd(self, ctx):
        # TODO: NOT
        children = self.visitChildren(ctx)
        if len(children) == 1:
            return children[0]
        else:
            return self.instantiate("AndBooleanExpression", [children[0], children[2]])


    # Visit a parse tree produced by STIXPatternParser#propTestEqual.
    def visitPropTestEqual(self, ctx):
        children = self.visitChildren(ctx)
        if len(children) == 4:
            operator = children[2].symbol.type
            negated = negated=operator == STIXPatternParser.EQ
            return self.instantiate("EqualityComparisonExpression", children[0], children[3], negated)
        else:
            operator = children[1].symbol.type
            negated = negated = operator != STIXPatternParser.EQ
            return self.instantiate("EqualityComparisonExpression", children[0], children[2], negated)


    # Visit a parse tree produced by STIXPatternParser#propTestOrder.
    def visitPropTestOrder(self, ctx):
        children = self.visitChildren(ctx)
        operator = children[1].symbol.type
        if operator == STIXPatternParser.GT:
            return self.instantiate("GreaterThanComparisonExpression", children[0], children[2], False)
        elif operator == STIXPatternParser.LT:
            return self.instantiate("LessThanComparisonExpression", children[0], children[2], False)
        elif operator == STIXPatternParser.GE:
            return self.instantiate("GreaterThanEqualComparisonExpression", children[0], children[2], False)
        elif operator == STIXPatternParser.LE:
            return self.instantiate("LessThanEqualComparisonExpression", children[0], children[2], False)


    # Visit a parse tree produced by STIXPatternParser#propTestSet.
    def visitPropTestSet(self, ctx):
        # TODO
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#propTestLike.
    def visitPropTestLike(self, ctx):
        children = self.visitChildren(ctx)
        return self.instantiate("LikeComparisonExpression", children[0], children[2], False)


    # Visit a parse tree produced by STIXPatternParser#propTestRegex.
    def visitPropTestRegex(self, ctx):
        children = self.visitChildren(ctx)
        return self.instantiate("MatchesComparisonExpression", children[0], children[2], False)


    # Visit a parse tree produced by STIXPatternParser#propTestIsSubset.
    def visitPropTestIsSubset(self, ctx):
        children = self.visitChildren(ctx)
        return stix2.IsSubsetComparisonExpression(children[0], children[2])


    # Visit a parse tree produced by STIXPatternParser#propTestIsSuperset.
    def visitPropTestIsSuperset(self, ctx):
        children = self.visitChildren(ctx)
        return stix2.IsSupersetComparisonExpression(children[0], children[2])


    # Visit a parse tree produced by STIXPatternParser#propTestParen.
    def visitPropTestParen(self, ctx):
        children = self.visitChildren(ctx)
        return self.instantiate("ParentheticalExpression", children[1])


    # Visit a parse tree produced by STIXPatternParser#startStopQualifier.
    def visitStartStopQualifier(self, ctx):
        children = self.visitChildren(ctx)
        return stix2.StartStopQualifier(children[1], children[3])


    # Visit a parse tree produced by STIXPatternParser#withinQualifier.
    def visitWithinQualifier(self, ctx):
        children = self.visitChildren(ctx)
        return stix2.WithinQualifier(children[1])


    # Visit a parse tree produced by STIXPatternParser#repeatedQualifier.
    def visitRepeatedQualifier(self, ctx):
        children = self.visitChildren(ctx)
        return stix2.RepeatQualifier(children[1])


    # Visit a parse tree produced by STIXPatternParser#objectPath.
    def visitObjectPath(self, ctx):
        children = self.visitChildren(ctx)
        flat_list = collapse_lists(children[2:])
        property_path = []
        i = 0
        while i < len(flat_list):
            current = flat_list[i]
            if i == len(flat_list)-1:
                property_path.append(current)
                break
            next = flat_list[i+1]
            if isinstance(next, TerminalNode):
                property_path.append(stix2.ListObjectPathComponent(current.property_name, next.getText()))
                i += 2
            else:
                property_path.append(current)
                i += 1
        return self.instantiate("ObjectPath", children[0].getText(), property_path)


    # Visit a parse tree produced by STIXPatternParser#objectType.
    def visitObjectType(self, ctx):
        children = self.visitChildren(ctx)
        return children[0]


    # Visit a parse tree produced by STIXPatternParser#firstPathComponent.
    def visitFirstPathComponent(self, ctx):
        children = self.visitChildren(ctx)
        step = children[0].getText()
        # if step.endswith("_ref"):
        #     return stix2.ReferenceObjectPathComponent(step)
        # else:
        return stix2.BasicObjectPathComponent(step)


    # Visit a parse tree produced by STIXPatternParser#indexPathStep.
    def visitIndexPathStep(self, ctx):
        children = self.visitChildren(ctx)
        return children[1]


    # Visit a parse tree produced by STIXPatternParser#pathStep.
    def visitPathStep(self, ctx):
        return collapse_lists(self.visitChildren(ctx))


    # Visit a parse tree produced by STIXPatternParser#keyPathStep.
    def visitKeyPathStep(self, ctx):
        children = self.visitChildren(ctx)
        if isinstance(children[1], stix2.StringConstant):
            # special case for hashes
            return children[1].value
        else:
            return stix2.BasicObjectPathComponent(children[1].getText(), is_key=True)



    # Visit a parse tree produced by STIXPatternParser#setLiteral.
    def visitSetLiteral(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by STIXPatternParser#primitiveLiteral.
    def visitPrimitiveLiteral(self, ctx):
        children = self.visitChildren(ctx)
        return children[0]


    # Visit a parse tree produced by STIXPatternParser#orderableLiteral.
    def visitOrderableLiteral(self, ctx):
        children = self.visitChildren(ctx)
        return children[0]


    def visitTerminal(self, node):
        if node.symbol.type == STIXPatternParser.IntPosLiteral or node.symbol.type == STIXPatternParser.IntNegLiteral:
            return stix2.IntegerConstant(node.getText())
        elif node.symbol.type == STIXPatternParser.FloatPosLiteral or node.symbol.type == STIXPatternParser.FloatNegLiteral:
            return stix2.FloatConstant(node.getText())
        elif node.symbol.type == STIXPatternParser.HexLiteral:
            return stix2.HexConstant(node.getText())
        elif node.symbol.type == STIXPatternParser.BinaryLiteral:
            return stix2.BinaryConstant(node.getText())
        elif node.symbol.type == STIXPatternParser.StringLiteral:
            return stix2.StringConstant(node.getText().strip('\''))
        elif node.symbol.type == STIXPatternParser.BoolLiteral:
            return stix2.BooleanConstant(node.getText())
        elif node.symbol.type == STIXPatternParser.TimestampLiteral:
            return stix2.TimestampConstant(node.getText())
        # TODO: timestamp
        else:
            return node

    def aggregateResult(self, aggregate, nextResult):
        if aggregate:
            aggregate.append(nextResult)
        elif nextResult:
            aggregate = [nextResult]
        return aggregate


def create_pattern_object(pattern, module_suffix="", module_name=""):
    '''
    Validates a pattern against the STIX Pattern grammar.  Error messages are
    returned in a list.  The test passed if the returned list is empty.
    '''

    start = ''
    if isinstance(pattern, six.string_types):
        start = pattern[:2]
        pattern = InputStream(pattern)

    if not start:
        start = pattern.readline()[:2]
        pattern.seek(0)

    parseErrListener = STIXPatternErrorListener()

    lexer = STIXPatternLexer(pattern)
    # it always adds a console listener by default... remove it.
    lexer.removeErrorListeners()

    stream = CommonTokenStream(lexer)

    parser = STIXPatternParser(stream)
    parser.buildParseTrees = True
    # it always adds a console listener by default... remove it.
    parser.removeErrorListeners()
    parser.addErrorListener(parseErrListener)

    # To improve error messages, replace "<INVALID>" in the literal
    # names with symbolic names.  This is a hack, but seemed like
    # the simplest workaround.
    for i, lit_name in enumerate(parser.literalNames):
        if lit_name == u"<INVALID>":
            parser.literalNames[i] = parser.symbolicNames[i]

    tree = parser.pattern()
    builder = STIXPatternVisitorForSTIX2(module_suffix, module_name)
    return builder.visit(tree)
