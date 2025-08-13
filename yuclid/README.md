# Yuclid

Yuclid is a fast planar geometry solver written in C++. It solves planar
geometry problems like the ones that appear at
[IMO](https://www.imo-official.org/) and other contests.

Yuclid is very fast: it solves 17 out of the 30 IMO problems from the
AlphaGeometry benchmark and saturates the other 13 in less than 0.5s on
a single Intel 3.1GHz core.

Yuclid uses STL and [Boost libraries](https://boost.org/) for generic
utilities, including containers, safe numerics, and rational numbers.

Currently, it lacks a user-friendly interface, so the recommended way to
use it is via [Newclid](https://github.com/Newclid/Newclid/). However,
some of Yuclid\'s features are only available in C++.

## Quickstart

The main user interface for Yuclid is Newclid.
However, if you want to try some of the features
that are not exposed via Newclid's interface,
you can [install](https://github.com/Newclid/Newclid/yuclid/INSTALL.md) it,
generate a file in [input format](#input-format),
and run
```bash
$ yuclid in-file.txt
```
This will show information about progress in solving the problem,
then either print a solution, or say that it failed to solve the problem.

For automatic interaction with Yuclid, you can add `--use-json`,
then the solution will be printed as a JSON object
instead of plain text.

Note that the format of the JSON export is designed for Newclid,
and can change in the future versions.

## How does it work

Similarly to Alpha Geometry and Newclid 2.0, Yuclid uses deduction
database (i.e., theorems from planar geometry) and algebraic reasoning,
see [below](#features) for more details.

First, it finds all theorems that match *numerically* on the diagram.
Then, in a loop, it tries to prove the hypotheses and the conclusions of
these matched theorems using already established statements and
algebraic reasoning. This loop ends when either all goals of the problem
are proved, or no new statements were established after going through
all the theorems. In the latter case, the problem is \"saturated\", and
can\'t be solved by DD/AR only.

The whole program is written aiming for higher speed. Here are some
optimizations we use, besides writing the whole engine in C++.

-   We numerically match theorems by matching certain common
    configurations (e.g., pairs of similar triangles, circumcenters
    etc), then adding all theorems about these configurations.
-   The statements that appear in matched theorems are deduplicated, and
    we track the progress in proving each statement in the same object,
    no matter which theorem uses it as a hypothesis or a conclusion.
-   Similarly, AR equations are deduplicated. Moreover, if we fail to
    prove an equation, then we store the row reduced form of this
    equation, so that next time we\'re trying to prove it we resume work
    instead of restarting it.

As a result of these optimizations of the solver, on a typical IMO
problem, the main DD/AR loop is faster than numerically matching the
theorems.

## Features

The Yuclid engine is capable of

-   applying rules from the Deduction Database (DD);
-   performing algebraic reasoning (AR) on:
    -   lengths (additive relations like `|AB|+|BC|=|AC|`);
    -   squared lengths (additive relations like
        `|AB|² + |BC|² = |AC|²`);
    -   lengths and sines of angles (multiplicative relations like
        `|AB|:|BC|=|DE|:|EF|` or the law of sines).

Extra AR tables allow us to state theorems like the law of sines and the
Pythagoras theorem. Adding the law of sines to the mix makes Yuclid
about 10x slower, so this feature is disabled by default.

## Input format

Yuclid relies on a *numerical graph* of a problem to select theorems
that apply in the problem and to verify the inequalities numerically.
Currently, it expects the caller to build the graph.

An example input file looks like this

``` {caption="Yuclid encoding of IMO 2000 p1"}
point a -0.40746902984670474446 -0.66665500610231753775
point b -0.11560335689440992546 -0.59371690741631888422
point g1 -0.44257354475251259318 -0.52618242659683756024
point g2 -0.17244267242498786952 -0.36627136967481344065
point m -0.40604502710432055501 -0.38607339777242094536
point n -0.30216699079418207763 -0.56155009778454667568
point c -0.54071880847663988945 -0.41972877579886108679
point d 0.043012537427953148605 -0.27385257842686294705
point e -0.27421925121677109827 -0.91358123640577104663
point p -0.032948325893715921242 -0.29283542382004185134
point q -0.77914172831492523041 -0.47931137172479987285
assume perp g1 a a b
assume perp g2 b b a
assume cong g1 m g1 a
assume cong g2 m g2 b
assume cong g1 n g1 a
assume cong g2 n g2 b
assume para c m a b
assume cong g1 c g1 a
assume para d m a b
assume cong g2 d g2 b
assume coll e a c
assume coll e b d
assume coll p a n
assume coll p c d
assume coll q b n
assume coll q c d
prove cong e p e q
```

Running `yuclid < translated_imo_2000_p1.txt` on this
file produces a text proof. On the author\'s dev box
(`Intel(R) Xeon(R) CPU @ 3.10GHz`), it takes 0.017s on a single core.

## Python bindings

The module `py_yuclid` wraps a call to the `yuclid` command line utility
in a [Python](https://www.python.org/) interface which is just enough
for Newclid to use it.

Only DD and the \"multiplicative\" AR without sines is exposed via
Newclid at the moment.
