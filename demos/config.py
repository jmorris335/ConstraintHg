def runInPlace():
    if not __package__:
        import os
        import sys
        package_source_path = os.path.dirname(os.path.dirname(__file__))
        sys.path.insert(0, package_source_path)