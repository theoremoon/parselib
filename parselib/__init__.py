from struct import unpack


class Parser(object):
    def __init__(self):
        self.to_parse = []

    class Type(object):
        def __init__(self, length):
            self.length = length

    class Integer(Type):
        def __init__(self, length, order='little'):
            super().__init__(length)
            self.order = order

    class String(Type):
        pass

    class Bytes(Type):
        pass

    class Magic(Type):
        def __init__(self, magic_bytes):
            super().__init__(len(magic_bytes))
            self.magic_bytes = magic_bytes

    class Ref(object):
        def __init__(self, ref, type):
            self.ref = ref
            self.type = type

    def register(self, name, var):
        self.to_parse.append((name, var))

    def sore(self, file, type):
        if isinstance(type, self.Integer):
            return int.from_bytes(file.read(type.length), byteorder=type.order)
        elif isinstance(type, self.String):
            return file.read(type.length).decode()
        elif isinstance(type, self.Bytes):
            return file.read(type.length)
        elif isinstance(type, self.Magic):
            v = file.read(type.length)
            if v != type.magic_bytes:
                raise Exception("expected {}, reached {}".format(type.magic_bytes, v))
            return v
        else:
            raise Exception(type)


    def try_parse(self, file):
        t = file.tell()
        print("try...", end="")
        try:
            return self.parse(file)
        except Exception as e:
            print(e)
            file.seek(t)
        return None

    def parse(self, file):
        result = {}
        for v in self.to_parse:
            if isinstance(v[1], self.Ref):
                l = result[v[1].ref]
                result[v[0]] = self.sore(file, v[1].type(l))
            else:
                result[v[0]] = self.sore(file, v[1])

        return result