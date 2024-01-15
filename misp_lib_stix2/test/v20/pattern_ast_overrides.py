"""
AST node class overrides for testing the pattern AST builder.
"""
from misp_lib_stix2.patterns import (
    EqualityComparisonExpression, StartStopQualifier, StringConstant,
)


class EqualityComparisonExpressionForTesting(EqualityComparisonExpression):
    pass


class StringConstantForTesting(StringConstant):
    pass


class StartStopQualifierForTesting(StartStopQualifier):
    pass
