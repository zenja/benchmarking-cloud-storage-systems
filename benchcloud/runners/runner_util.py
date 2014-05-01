def parse_class(path):
    parts = path.split('.')
    module_name = '.'.join(parts[:-1])
    class_name = parts[-1]
    return module_name, class_name
