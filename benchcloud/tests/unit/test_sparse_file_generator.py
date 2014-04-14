from benchcloud.file_generators.sparse_file_generator import SparseFileGenerator

if __name__ == '__main__':
    generator = SparseFileGenerator(directory="./", prefix="sparse-", suffix=".txt")
    generator.make_file(size=10240, repeat_str="hello!")