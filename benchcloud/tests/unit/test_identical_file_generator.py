from file_generators.identical_file_generator import IdenticalFileGenerator

if __name__ == '__main__':
    generator = IdenticalFileGenerator(directory="./", prefix="identical-", size=102400)
    generator.make_file()
    generator.make_file()
