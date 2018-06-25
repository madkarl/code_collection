#!/usr/bin/python3
# coding:utf-8

import socket
from struct import pack, unpack


class Ip2Loc(object):
    def __init__(self, db_path):
        self._db_path = db_path
        f = open(db_path, 'rb')
        self._db_image = f.read()
        f.close()
        (self._first_index, self._last_index) = unpack('<II', self._db_image[:8])
        self._index_count = int((self._last_index - self._first_index) / 7) + 1

    def _get_string(self, offset=0):
        o2 = self._db_image.find(b'\0', offset)
        gb2312_str = self._db_image[offset:o2]
        try:
            utf8_str = gb2312_str.decode('gb2312')
        except ValueError:
            return '未知'
        return utf8_str

    def _get_long3(self, offset=0):
        s = self._db_image[offset: offset + 3]
        s += b'\0'
        return unpack('<I', s)[0]

    def _get_area_address(self, offset=0):
        byte = self._db_image[offset]
        if byte == 1 or byte == 2:
            return self._get_area_address(self._get_long3(offset + 1))
        else:
            return self._get_string(offset)

    def _get_address(self, offset):
        byte = self._db_image[offset]

        if byte == 1:
            return self._get_address(self._get_long3(offset + 1))

        if byte == 2:
            area1 = self._get_area_address(self._get_long3(offset + 1))
            offset += 4
            area2 = self._get_area_address(offset)
            return area1, area2

        if byte != 1 and byte != 2:
            area1 = self._get_area_address(offset)
            offset = self._db_image.find(b'\0', offset) + 1
            area2 = self._get_area_address(offset)
            return area1, area2

    def _find(self, ip, l, r):
        if r - l <= 1:
            return l

        m = int((l + r) / 2)
        o = self._first_index + m * 7
        new_ip = unpack('<I', self._db_image[o: o + 4])[0]

        if ip <= new_ip:
            return self._find(ip, l, m)
        else:
            return self._find(ip, m, r)

    def get_location(self, ip):
        ip = unpack('!I', socket.inet_aton(ip))[0]
        i = self._find(ip, 0, self._index_count - 1)
        o = self._first_index + i * 7
        o2 = self._get_long3(o + 4)
        (c, a) = self._get_address(o2 + 4)
        return c, a

    def view_all(self, first, last):
        for i in range(first, last):
            o = self._first_index + i * 7
            ip = socket.inet_ntoa(pack('!I', unpack('I', self._db_image[o:o + 4])[0]))
            offset = self._get_long3(o + 4)
            (c, a) = self._get_address(offset + 4)
            print("%s %d %s/%s" % (ip, offset, c, a))


if __name__ == "__main__":
    from tools import tools
    i2l = Ip2Loc(tools.get_base_dir() + "/qqwry.dat")
    loc = i2l.get_location("121.69.50.26")
    print(loc)
