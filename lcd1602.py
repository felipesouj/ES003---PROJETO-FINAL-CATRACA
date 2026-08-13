from time import sleep_ms


class LCD1602:

    def __init__(self, i2c, endereco=0x27):
        self.i2c = i2c
        self.endereco = endereco
        self.backlight = 0x08

        sleep_ms(20)

        self._write4bits(0x30)
        sleep_ms(5)

        self._write4bits(0x30)
        sleep_ms(1)

        self._write4bits(0x30)
        sleep_ms(1)

        self._write4bits(0x20)
        sleep_ms(1)

        self.command(0x28)
        self.command(0x0C)
        self.command(0x06)
        self.clear()

    def _write4bits(self, valor):

        self.i2c.writeto(
            self.endereco,
            bytes([valor | self.backlight])
        )

        self.i2c.writeto(
            self.endereco,
            bytes([valor | self.backlight | 0x04])
        )

        self.i2c.writeto(
            self.endereco,
            bytes([valor | self.backlight])
        )

    def _send(self, valor, modo):

        alto = valor & 0xF0
        baixo = (valor << 4) & 0xF0

        self._write4bits(alto | modo)
        self._write4bits(baixo | modo)

    def command(self, comando):
        self._send(comando, 0)

    def write_char(self, caractere):
        self._send(ord(caractere), 1)

    def print(self, texto):

        for caractere in texto:
            self.write_char(caractere)

    def clear(self):
        self.command(0x01)
        sleep_ms(2)

    def cursor(self, linha, coluna):

        endereco = 0x80

        if linha == 1:
            endereco = 0xC0

        endereco += coluna

        self.command(endereco)