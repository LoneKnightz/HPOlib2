import time
import numpy as np

from param_net import ParamFCNetClassification
from param_net.util import zero_mean_unit_var_normalization

from hpolib.util import rng_helper
from hpolib.util.data_manager import MNISTData
from hpolib.util.openml_data_manager import OpenMLHoldoutDataManager
from hpolib.abstract_benchmark import AbstractBenchmark

from sklearn.model_selection import StratifiedShuffleSplit


class ParamNetBenchmark(AbstractBenchmark):

    def __init__(self, train, train_targets, valid, valid_targets, test, test_targets,
                 do_early_stopping, n_epochs, rng=None):

        self.train = train
        self.train_targets = train_targets
        self.valid = valid
        self.valid_targets = valid_targets
        self.test = test
        self.test_targets = test_targets
        self.n_epochs = n_epochs
        self.do_early_stopping = do_early_stopping

        # Use 10 time the number of classes as lower bound for the dataset
        # fraction
        n_classes = np.unique(self.train_targets).shape[0]
        self.s_min = float(10 * n_classes) / self.train.shape[0]
        self.rng = rng_helper.create_rng(rng)

        super(ParamNetBenchmark, self).__init__()

    @AbstractBenchmark._check_configuration
    def objective_function(self, x, dataset_fraction=1, **kwargs):
        start_time = time.time()

        rng = kwargs.get("rng", None)
        self.rng = rng_helper.get_rng(rng=rng, self_rng=self.rng)

        if dataset_fraction < 1.0:
            sss = StratifiedShuffleSplit(n_splits=1, train_size=np.round(dataset_fraction, 3), test_size=None)
            idx = list(sss.split(self.train, self.train_targets))[0][0]

            train = self.train[idx]
            train_targets = self.train_targets[idx]
        else:
            train = self.train
            train_targets = self.train_targets

        pc = ParamFCNetClassification(config=x, n_feat=train.shape[1], n_classes=np.unique(train_targets).shape[0])
        history = pc.train(train, train_targets, self.valid, self.valid_targets,
                           n_epochs=self.n_epochs, do_early_stopping=self.do_early_stopping)
        y = 1 - history.history["val_acc"][-1]

        if not np.isfinite(y):
            y = 1

        c = time.time() - start_time

        return {'function_value': y, "cost": c}

    @AbstractBenchmark._check_configuration
    def objective_function_test(self, x, **kwargs):
        start_time = time.time()

        rng = kwargs.get("rng", None)
        self.rng = rng_helper.get_rng(rng=rng, self_rng=self.rng)

        train = np.concatenate((self.train, self.valid))
        train_targets = np.concatenate((self.train_targets, self.valid_targets))

        pc = ParamFCNetClassification(config=x, n_feat=X_train.shape[1], n_classes=np.unique(y_train).shape[0])
        history = pc.train(train, train_targets, self.test, self.test_targets,
                           n_epochs=self.n_epochs, do_early_stopping=self.do_early_stopping)
        y = 1 - history.history["val_acc"][-1]

        if not np.isfinite(y):
            y = 1

        c = time.time() - start_time

        return {'function_value': y, "cost": c}

    @staticmethod
    def get_configuration_space(max_num_layers=10):
        cs = ParamFCNetClassification.get_config_space(max_num_layers=max_num_layers)
        return cs

    @staticmethod
    def get_meta_information():
        info = dict()
        info["cvfolds"] = 1
        info["wallclocklimit"] = np.inf
        info['num_function_evals'] = 100
        info['cutoff'] = 1800
        info['memorylimit'] = 1024 * 3
        return info


class ParamNetOnMnist(ParamNetBenchmark):

    def get_data(self):
        dm = MNISTData()
        return dm.load()

    @staticmethod
    def get_meta_information():
        d = ParamNetBenchmark.get_meta_information()
        d["references"].append("@article{lecun-ieee98,"
                               "title={Gradient-based learning applied to document recognition},"
                               "author={Y. LeCun and L. Bottou and Y. Bengio and P. Haffner},"
                               "journal={Proceedings of the IEEE},"
                               "pages={2278--2324},"
                               "year={1998},"
                               "publisher={IEEE}"
                               )
        return d


class ParamNetOnVehicle(ParamNetBenchmark):

    def get_data(self):
        dm = OpenMLHoldoutDataManager(openml_task_id=75191)
        X_train, y_train, X_valid, y_valid, X_test, y_test = dm.load()

        # Make sparse matrices dense
        X_train = X_train.toarray()
        X_valid = X_valid.toarray()
        X_test = X_test.toarray()

        # Zero mean / unit std normalization
        X_train, mean, std = zero_mean_unit_var_normalization(X_train)
        X_valid, _, _ = zero_mean_unit_var_normalization(X_valid, mean, std)
        X_test, _, _ = zero_mean_unit_var_normalization(X_test, mean, std)

        return X_train, y_train, X_valid, y_valid, X_test, y_test


class ParamNetOnCovertype(ParamNetBenchmark):

    def get_data(self):
        dm = OpenMLHoldoutDataManager(openml_task_id=2118)

        X_train, y_train, X_valid, y_valid, X_test, y_test = dm.load()

        # Zero mean / unit std normalization
        X_train, mean, std = zero_mean_unit_var_normalization(X_train)
        X_valid, _, _ = zero_mean_unit_var_normalization(X_valid, mean, std)
        X_test, _, _ = zero_mean_unit_var_normalization(X_test, mean, std)

        return X_train, y_train, X_valid, y_valid, X_test, y_test


class ParamNetOnLetter(ParamNetBenchmark):

    def get_data(self):
        dm = OpenMLHoldoutDataManager(openml_task_id=236)

        X_train, y_train, X_valid, y_valid, X_test, y_test = dm.load()

        # Zero mean / unit std normalization
        X_train, mean, std = zero_mean_unit_var_normalization(X_train)
        X_valid, _, _ = zero_mean_unit_var_normalization(X_valid, mean, std)
        X_test, _, _ = zero_mean_unit_var_normalization(X_test, mean, std)

        return X_train, y_train, X_valid, y_valid, X_test, y_test
