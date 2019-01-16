# From How to What
This package contains many versions of an arithmetic expression evaluator.

It starts with a simple imperative style, refactors to a functional style, and
concludes with an object oriented style that uses python's operator overloading
to make a succinct DSL capable of describing a wide range of grammars.

Each module is functionally equivalent. You can import any of them and execute
the following:
```python
In [2]: evaluate("1+(2+4)*3+4+3*5")
Out[2]: 38
```

## arith1
The arith1 module is a straightforward implementation of a recursive decent
parser. Each non-terminal is represented as a function that explicitly calls the
other functions.

## arith2
The arith2 module is still a straightforward implementation of recursive decent,
but we begin to isolate some ideas to show commonality.

## arith3
The arith3 module separates operations on recognized data from the recognition
logic. It shows how number, term, and expr are almost identical and emphasizes
the distinction between rules for matching raw data and the higher level meaning
of a recognized pattern.

## arith4
The arith4 module extracts a common control structure among number, term, and
expr and gives it a name: many. This is the first step toward a functional
design.

## arith5
The arith5 module continues the theme of arith4 by factoring out even more
high level control stuctures to create an almost entirely functional style
parser. It reads like the grammar, but the explicitly nested function calls are
cumbersome.

## arith6
The arith6 module concludes with a parser that is virtually identical to its
grammar. While arith1 explicitly implements how to parse the grammar, arith6
simply describes it.
