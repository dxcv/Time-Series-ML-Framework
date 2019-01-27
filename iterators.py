from typing import Dict, Iterable, Tuple
from numpy import ndarray as np_ndarray


class DataIterator(object):

    def __init__(self, df, config_dct: Dict):
        self._config_dct = config_dct

    def __iter__(self) -> Iterable:
        pass

    def __next__(self) -> Tuple[np_ndarray, np_ndarray, np_ndarray, np_ndarray]:
        pass


class DFIterator(DataIterator):

    from pandas import concat as pd_concat
    from tqdm import tqdm

    def __init__(self, df, config_dct):
        super(DFIterator, self).__init__(df, config_dct)
        self._sample_lag = self._config_dct["sample_lag"]
        self._predict_period = self._config_dct["predict_period"]
        self._sample_generator = None
        self._df = df

        print("Generating training target...")
        self._generate_target()
        print("Done.")

    def _generate_target(self):
        df_tpl = [i[1] for i in self._df.groupby("tkr")]
        for tdf in DFIterator.tqdm(df_tpl):
            yield_ar = tdf["yield"]
            tdf["y"] = yield_ar.shift(self._predict_period)

        self._df = DFIterator.pd_concat(df_tpl)

    def _get_sample_generator(self):
        df_lst = [i[1] for i in self._df.groupby("date")]
        len_ = len(df_lst)
        for i in range(self._sample_lag, len_ - 1, 1):
            tdf = DFIterator.pd_concat(objs=df_lst[i - self._sample_lag:i])
            x_train = tdf.iloc[:, :-1].values
            y_train = tdf["y"].values.reshape(-1, 1)

            test_df = df_lst[i + 1]
            x_test = test_df.iloc[:, :-1].values
            y_test = test_df["y"].values.reshape(-1, 1)

            yield x_train, y_train, x_test, y_test

    def __iter__(self):
        self._sample_generator = self._get_sample_generator()
        return self

    def __next__(self):
        return next(self._sample_generator)
