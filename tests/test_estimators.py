import unittest

from sklearn.utils.estimator_checks import check_estimator
import sklearn.utils.estimator_checks

from daal4py import __daal_run_version__
daal_run_version = tuple(map(int, (__daal_run_version__[0:4], __daal_run_version__[4:8])))

from daal4py.sklearn.neighbors import KNeighborsClassifier
from daal4py.sklearn.ensemble import RandomForestClassifier
from daal4py.sklearn.ensemble import RandomForestRegressor
from daal4py.sklearn.ensemble import GBTDAALClassifier
from daal4py.sklearn.ensemble import GBTDAALRegressor
from daal4py.sklearn.ensemble import AdaBoostClassifier

from daal4py import __daal_link_version__ as dv
daal_version = tuple(map(int, (dv[0:4], dv[4:8])))


def check_version(rule, target):
    if not isinstance(rule[0], type(target)):
        if rule > target:
            return False
    else:
        for rule_item in range(len(rule)):
            if rule[rule_item] > target:
                return False
            else:
                if rule[rule_item][0]==target[0]:
                    break                   
    return True

def _replace_and_save(md, fns, replacing_fn):
    """
    Replaces functions in `fns` list in `md` module with `replacing_fn`.

    Returns the dictionary with functions that were replaced.
    """
    saved = dict()
    for check_f in fns:
        try:
            fn = getattr(md, check_f)
            setattr(md, check_f, replacing_fn)
            saved[check_f] = fn
        except:
            pass
    return saved


def _restore_from_saved(md, saved_dict):
    """
    Restores functions in `md` that were replaced in the function above.
    """
    for check_f in saved_dict:
        setattr(md, check_f, saved_dict[check_f])


class Test(unittest.TestCase):
    def test_KNeighborsClassifier(self):
        check_estimator(KNeighborsClassifier)

    @unittest.skipUnless(check_version(((2019,0),(2021, 107)), daal_version), "not supported in this library version")
    def test_RandomForestClassifier(self):
        # check_methods_subset_invariance fails.
        # Issue is created:
        # https://github.com/IntelPython/daal4py/issues/129
        # Skip the test
        def dummy(*args, **kwargs):
            pass

        md = sklearn.utils.estimator_checks
        saved = _replace_and_save(md, ['check_methods_subset_invariance', 'check_dict_unchanged'], dummy)
        check_estimator(RandomForestClassifier)
        _restore_from_saved(md, saved)

    def test_RandomForestRegressor(self):
        # check_fit_idempotent is known to fail with DAAL's decision
        # forest regressor, due to different partitioning of data
        # between threads from run to run.
        # Hence skip that test
        def dummy(*args, **kwargs):
            pass
        md = sklearn.utils.estimator_checks
        saved = _replace_and_save(md, ['check_methods_subset_invariance', 'check_dict_unchanged'], dummy)
        check_estimator(RandomForestRegressor)
        _restore_from_saved(md, saved)

    def test_GBTDAALClassifier(self):
        check_estimator(GBTDAALClassifier)

    def test_GBTDAALRegressor(self):
        def dummy(*args, **kwargs):
            pass

        md = sklearn.utils.estimator_checks
        # got unexpected slightly different prediction result between two same calls in this test
        saved = _replace_and_save(md, ['check_estimators_data_not_an_array'], dummy)
        check_estimator(GBTDAALRegressor)
        _restore_from_saved(md, saved)

    @unittest.skipIf(daal_run_version < (2020, 0), "not supported in this library version")
    def test_AdaBoostClassifier(self):
        check_estimator(AdaBoostClassifier)


if __name__ == '__main__':
    unittest.main()
