import argparse
import os
import pyarrow as pa
import pyarrow.parquet as pq
import numpy as np


def generate(generate_if_exists: bool, copy_dir: str):
    parquet_dir = "./test/data/parquet"
    import_slt_dir = "./test/sql/dml/import"

    table_name = "parquet_tensor_table"
    table_name1 = "parquet_tensor_table1"
    table_name_err = "parquet_tensor_table_err"
    parquet_filename = "gen_tensor.parquet"
    parquet_filename1 = "gen_tensor1.parquet"
    parquet_path = parquet_dir + "/" + parquet_filename
    import_slt_path = import_slt_dir + "/test_import_gen_parquet_tensor.slt"
    copy_path = copy_dir + "/" + parquet_filename
    copy_path1 = copy_dir + "/tmp/" + parquet_filename1

    os.makedirs(parquet_dir, exist_ok=True)
    os.makedirs(import_slt_dir, exist_ok=True)
    if (
        os.path.exists(parquet_path)
        and os.path.exists(import_slt_path)
        and not generate_if_exists
    ):
        print(
            "File {} and {} already existed. Skip Generating.".format(
                parquet_path, import_slt_path
            )
        )
        return

    row_n = 10
    dim = 10
    embedding_num_min = 1
    embedding_num_max = 10
    min_x = 0
    max_x = 100
    data = []
    for i in range(row_n):
        embedding_num = np.random.randint(embedding_num_min, embedding_num_max)
        tensor = []
        for j in range(embedding_num):
            tensor.append([int(np.random.uniform(min_x, max_x)) for _ in range(dim)])
        data.append(tensor)

    col1 = pa.array(range(row_n), type=pa.int32())
    col2 = pa.array(data, type=pa.list_(pa.list_(pa.int32(), dim)))
    table = pa.table({"c1": col1, "c2": col2})

    with pq.ParquetWriter(parquet_path, table.schema) as writer:
        writer.write_table(table)

    # t = pq.read_table(parquet_path)
    # print(t)
    with open(import_slt_path, "w") as slt_file:

        def write_query():
            for row_id in range(row_n):
                slt_file.write("{} [".format(row_id))
                for i in range(len(data[row_id])):
                    slt_file.write("[")
                    for j in range(dim):
                        slt_file.write("{}".format(data[row_id][i][j]))
                        if j != dim - 1:
                            slt_file.write(",")
                    slt_file.write("]")
                    if i != len(data[row_id]) - 1:
                        slt_file.write(",")
                slt_file.write("]\n")
            slt_file.write("\n")

        slt_file.write("statement ok\n")
        slt_file.write("DROP TABLE IF EXISTS {};\n".format(table_name))
        slt_file.write("\n")

        slt_file.write("statement ok\n")
        slt_file.write(
            "CREATE TABLE {} (c1 INT, c2 TENSOR(INT, {}));\n".format(table_name, dim)
        )
        slt_file.write("\n")

        slt_file.write("statement ok\n")
        slt_file.write(
            "COPY {} FROM '{}' WITH (FORMAT PARQUET);\n".format(table_name, copy_path)
        )
        slt_file.write("\n")

        slt_file.write("query I\n")
        slt_file.write("SELECT * FROM {};\n".format(table_name))
        slt_file.write("----\n")
        write_query()

        slt_file.write("statement ok\n")
        slt_file.write(
            "COPY {} TO '{}' WITH (FORMAT PARQUET);\n".format(table_name, copy_path1)
        )
        slt_file.write("\n")

        slt_file.write("statement ok\n")
        slt_file.write("DROP TABLE IF EXISTS {};\n".format(table_name1))
        slt_file.write("\n")

        slt_file.write("statement ok\n")
        slt_file.write(
            "CREATE TABLE {} (c1 INT, c2 TENSOR(INT, {}));\n".format(table_name1, dim)
        )
        slt_file.write("\n")

        slt_file.write("statement ok\n")
        slt_file.write(
            "COPY {} FROM '{}' WITH (FORMAT PARQUET);\n".format(table_name1, copy_path1)
        )
        slt_file.write("\n")

        slt_file.write("query II\n")
        slt_file.write("SELECT * FROM {};\n".format(table_name1))
        slt_file.write("----\n")
        write_query()

        slt_file.write("statement ok\n")
        slt_file.write("DROP TABLE {};\n".format(table_name1))
        slt_file.write("\n")

        slt_file.write("statement ok\n")
        slt_file.write("DROP TABLE {};\n".format(table_name))
        slt_file.write("\n")

        # import with incompactible schema
        slt_file.write("statement ok\n")
        slt_file.write("DROP TABLE IF EXISTS {};\n".format(table_name_err))
        slt_file.write("\n")

        slt_file.write("statement ok\n")
        slt_file.write(
            "CREATE TABLE {} (c1 INT, c2 TENSOR(INT, {}));\n".format(
                table_name_err, dim + 1
            )
        )
        slt_file.write("\n")

        slt_file.write("statement error\n")
        slt_file.write(
            "COPY {} FROM '{}' WITH (FORMAT PARQUET);\n".format(
                table_name_err, copy_path
            )
        )
        slt_file.write("\n")

        slt_file.write("statement ok\n")
        slt_file.write("DROP TABLE {};\n".format(table_name_err))
        slt_file.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate parquet data for test")
    parser.add_argument(
        "-g",
        "--generate",
        type=bool,
        default=False,
        dest="generate_if_exists",
    )
    parser.add_argument(
        "-c",
        "--copy",
        type=str,
        default="/var/infinity/test_data",
        dest="copy_dir",
    )
    args = parser.parse_args()
    generate(args.generate_if_exists, args.copy_dir)
