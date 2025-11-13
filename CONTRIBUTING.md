# How to Contribute

ConstraintHg is an open-source project. We welcome contributions, additions, corrections, and new features from everyone, anywhere. To help improve the process of contributing, please follow the guidelines listed here.

**[Code of Conduct](https://github.com/jmorris335/ConstraintHg/blob/main/CODE_OF_CONDUCT.md): We expect all contributors to adhere to our code of conduct. Please read [here](https://github.com/jmorris335/ConstraintHg/blob/main/CODE_OF_CONDUCT.md) before contributing.**

## Discussion
We'd love to talk to you about the package. If you want to read more about what we're doing, and see how you can contribute (of if you have a great idea for the package), check out our [discussion board](https://github.com/jmorris335/ConstraintHg/discussions):
- [Plans for development](https://github.com/jmorris335/ConstraintHg/discussions/categories/plans-for-development): Our discussion board where we'll announce our plans for development going forward.
- [Ideas](https://github.com/jmorris335/ConstraintHg/discussions/categories/ideas): Place to discuss ideas for improving ConstraintHg.
- [Demos](https://github.com/jmorris335/ConstraintHg/discussions/categories/demonstrations): We would love to feature your work! Upload links to your use of ConstraintHg here.

## Issues
You can submit bug reports or feature requests as a GitHub [issue](https://github.com/jmorris335/ConstraintHg/issues). Please include as much code as possible. If you have a good idea, we recommend discussing it on our discussion board rather than opening a new issue.

### Bug Reports
For bug reports, include your script, all error output, and the debugging log for the specific simulation run. To get the log you'll need to set the logging level to `logging.DEBUG` (level 10). You can do that by calling:

```python
hypergraph.solve(<target>, <inputs>, logging_level=10)
```

Afterwards the log will be in a file called constrainthg.log. More information on logging is available [here](https://constrainthg.readthedocs.io/en/latest/tutorial/simulation.html#logging).

## Submitting Changes
Please submit a GitHub [pull request](https://github.com/jmorris335/ConstraintHg/pulls) for any change. The request should include a clear list of what changes you've made, with a clear commit message. Big changes (especially that would induce version number increases) require full descriptions of all changes made. Make sure that your pull requests:
- Add tests for any new features
- Are focused on a single issue
- Adhere to our style guides
- Pass the linter

## Testing
We use pytest for all of our testing. Navigate to the root repository and call `pytest` to run all tests. Otherwise, all commits are passed automatically to a linter (flake8) and pytest.

## Style Guide
Please read through our code to get a feel for our style. We emphasize the following principles:
- Clear names: longer, more explicit function and variables names are better than short and confusing. For example, we prefer `dispose_of_found_tnodes(found_tnodes: list)` rather than `dispose_t(tn: list)`
- Specify argument types if possible
- We mostly follow [numpy documentation syntax](https://numpydoc.readthedocs.io/en/latest/format.html), especially for docstrings
- Repository information (README, CODE_OF_CONDUCT) are written in markdown, while all documentation (including docstrings) is written in reStructuredText.

## Constraint Hypergraph Theory
If you have questions or ideas about constraint hypergraphs, especially the theory of how they're used for interoperable simulation, please let us know on our [discussion board](https://github.com/jmorris335/ConstraintHg/discussions/categories/constraint-hypergraph-theory). There you can [ask questions](https://github.com/jmorris335/ConstraintHg/discussions/categories/q-a) or see [tips](https://github.com/jmorris335/ConstraintHg/discussions/categories/tips) for using constraint hypergraphs.

You can also learn more about these mathematical structures by going to our [overview](https://constrainthg.readthedocs.io/en/latest/CHGs/chg_overview.html), which contains the most recent research and insights.