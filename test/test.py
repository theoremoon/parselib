import unittest
import parselib
from io import BytesIO

class Tester(unittest.TestCase):
    def test_parser(self):
        fobj = BytesIO(b"Magic1234")
        parser = parselib.Parser()
        parser.register("magic", parser.Magic(b"Magic"))
        r = parser.parse(fobj)

        self.assertEqual(r["magic"], b"Magic")

    def test_parser4(self):
        fobj = BytesIO(b"\x01\x02\x03\x04")

        parser = parselib.Parser()

        parser.register("hoge", parser.Integer(4))

        r = parser.parse(fobj)

        self.assertEqual(r["hoge"], 0x4030201)

    def test_parser3(self):
        fobj = BytesIO(b"hogehoge")

        parser = parselib.Parser()

        parser.register("hoge", parser.String(4))

        r = parser.parse(fobj)

        self.assertEqual(r["hoge"], "hoge")

    def test_parser2(self):
        fobj = BytesIO(b"\x04HOGEHOGEPIYOPIYO")

        parser = parselib.Parser()

        parser.register("len", parser.Integer(1))
        parser.register("hoge", parser.Ref("len", parser.String))
        r = parser.parse(fobj)

        self.assertEqual(r["hoge"], "HOGE")

    def test_pngparser(self):
        parser = parselib.Parser()
        idat = parselib.Parser()
        plt = parselib.Parser()
        iend = parselib.Parser()

        parser.register("signature", parser.Magic(b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"))
        parser.register("ihdrlen", parser.Integer(4))
        parser.register("ihdrmagic", parser.Magic(b"IHDR"))
        parser.register("ihdrwidth", parser.Integer(4))
        parser.register("ihdrheight", parser.Integer(4))
        parser.register("ihdrdepth", parser.Integer(1))
        parser.register("ihdrcolortype", parser.Integer(1))
        parser.register("ihdrcompress", parser.Integer(1))
        parser.register("ihdrfilter", parser.Integer(1))
        parser.register("ihdrinterace", parser.Integer(1))
        parser.register("CRC", parser.Integer(4))

        idat.register("length", idat.Integer(4,"big"))
        idat.register("idat", idat.Magic(b"IDAT"))
        idat.register("data", idat.Ref(ref="length", type=idat.Bytes))
        idat.register("CRC", parser.Integer(4))

        plt.register("length", idat.Integer(4, "big"))
        plt.register("plte", idat.Magic(b"PLTE"))
        plt.register("chunkdata", idat.Ref(ref="length", type=idat.Integer))
        plt.register("CRC", parser.Integer(4))

        iend.register("length", idat.Integer(4))
        iend.register("iend", idat.Magic(b"IEND"))
        iend.register("CRC", idat.Integer(4))

        a = [parser, idat, plt, iend]
        rr = []

        def is_eof(f):
            """

            :param _io.TextIOWrapper f:
            :return:
            """
            t = f.tell()
            f.seek(0, 2)
            r = f.tell() == t
            f.seek(t, 0)
            return r


        with open("theoldmoon0602.png", "rb") as f:
            while not is_eof(f):
                flag = 0
                for p in a:
                    r = p.try_parse(f)
                    if r is not None:
                        rr.append(r)
                        flag = 1
                        break
                if flag == 0:
                    break
            print(is_eof(f))
        print(rr)


