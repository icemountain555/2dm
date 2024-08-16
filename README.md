# SAC_HOER_data.lmdb 说明

## 数据库来源
[Design Principle of Carbon-Supported Single-Atom Catalysts – Interplay between d-Orbital Periodicity and Local Hybridization](https://pubs.acs.org/doi/full/10.1021/acs.chemmater.3c02549)

Github repo: https://github.com/Jeff-oakley/SAC_HOER_data/blob/main

## 数据格式如下：
Data(pos=[128, 3], cell=[1, 3, 3], atomic_numbers=[128], natoms=128, tags=[128], edge_index=[2, 4982], cell_offsets=[4982, 3], distances=[4982], fixed=[128], y_relaxed=4.893499999999904, sid='1N1_Au_O')

其中，sid='1N1_Au_O'，是 SAC_HOER_data-main/RawData 中文件夹列表名称。
吸附能计算参考能量：'_H': -3.477, '_O': -7.204,

数据量：共 559 条