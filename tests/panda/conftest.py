# from pytest_reorder import make_reordering_hook

# Make unit tests run before 'db' tests, which run before 'web' tests. Other tests will run at
# the very beginning of the suite:
# pytest_collection_modifyitems = make_reordering_hook(
#     [None, r'(^|.*/)(test_)?unit', r'(^|.*/)(test_)?db', r'(^|.*/)(test_)?'])
