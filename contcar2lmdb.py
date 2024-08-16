import os
import ase.io.vasp
from pymatgen.io.vasp import Oszicar
import pickle
import lmdb
import sys
sys.path.append('home/liujie/code/ocp')
from ocp.ocpmodels.preprocessing import AtomsToGraphs

# 吸附物质的参考能量
reference_energies = {
    '_H': -3.477,
    '_O': -7.204,
    '_OH': -3.477 - 7.204,
    '_OOH': -3.477 + 2 * -7.204
}

# LMDB 数据库路径
lmdb_path = '/home/liujie/code/Open-Catalyst-Dataset-main/vasp2lmdb/SAC_HOER_data.lmdb'
db = lmdb.open(
    lmdb_path,  # LMDB 文件保存位置
    map_size=1099511627776 * 2,
    subdir=False,
    meminit=False,
    map_async=True,
)

a2g = AtomsToGraphs(
    max_neigh=50,
    radius=6,
    r_energy=False,  # False for test data
    r_forces=False,  # False for test data
    r_distances=True,
    r_fixed=True,
)

dataset = []
idx = 0

# 遍历所有文件夹
for root, dirs, files in os.walk('/home/liujie/code/Open-Catalyst-Dataset-main/vasp2lmdb/SAC_HOER_data-main/RawData'):
    for dir_name in dirs:
        dir_path = os.path.join(root, dir_name)
        contcar_path = os.path.join(dir_path, 'CONTCAR')
        oszicar_path = os.path.join(dir_path, 'OSZICAR')

        # 如果是基底文件夹，跳过处理
        if '_substrate' in dir_name:
            continue

        # 对于有吸附物质的文件夹，提取CONTCAR和OSZICAR中的数据
        if os.path.exists(contcar_path) and os.path.exists(oszicar_path):
            try:
                atoms = ase.io.vasp.read_vasp(file=contcar_path)
                energy = Oszicar(filename=oszicar_path).all_energies[-1][-1]

                # 获取吸附物种类
                adsorbate = next(suffix for suffix in reference_energies.keys() if suffix in dir_name)
                ads_energy = reference_energies[adsorbate]

                # 找到相应的基底能量
                substrate_dir_name = "_".join(dir_name.split('_')[:2]) + '_substrate'
                substrate_dir_path = os.path.join(root, substrate_dir_name)
                substrate_oszicar_path = os.path.join(substrate_dir_path, 'OSZICAR')

                if os.path.exists(substrate_oszicar_path):
                    substrate_energy = Oszicar(filename=substrate_oszicar_path).all_energies[-1][-1]

                    # 计算吸附能
                    adsorption_energy = energy - ads_energy - substrate_energy

                    # 将数据转换为图并保存到LMDB
                    data = a2g.convert(atoms)
                    data.y_relaxed = adsorption_energy
                    data.sid = dir_name
                    dataset.append(data)

                    txn = db.begin(write=True)
                    data_bytes = pickle.dumps(data, protocol=-1)
                    txn.put(f"{idx}".encode("ascii"), data_bytes)
                    txn.commit()
                    idx += 1
                else:
                    print(f"Missing substrate OSZICAR: {substrate_oszicar_path}")
            except Exception as e:
                print(f"Error processing {dir_name}: {e}")
        else:
            print(f"Missing CONTCAR or OSZICAR in {dir_name}")

# 同步并关闭数据库
db.sync()
db.close()