import network
from machine import Pin, I2C, PWM
from time import sleep

from lcd1602 import LCD1602


# ==========================================
# LCD
# ==========================================

i2c = I2C(
    0,
    scl=Pin(22),
    sda=Pin(21),
    freq=400000
)

lcd = LCD1602(i2c, 0x27)


# ==========================================
# TECLADO
# ==========================================

linhas = [
    Pin(19, Pin.OUT, value=1),
    Pin(18, Pin.OUT, value=1),
    Pin(5, Pin.OUT, value=1),
    Pin(17, Pin.OUT, value=1)
]

colunas = [
    Pin(16, Pin.IN, Pin.PULL_UP),
    Pin(4, Pin.IN, Pin.PULL_UP),
    Pin(2, Pin.IN, Pin.PULL_UP),
    Pin(0, Pin.IN, Pin.PULL_UP)
]


teclas = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]


# ==========================================
# LEDs
# ==========================================

led_verde = Pin(25, Pin.OUT)
led_vermelho = Pin(26, Pin.OUT)

led_verde.value(0)
led_vermelho.value(0)


# ==========================================
# SERVO
# ==========================================

servo = PWM(Pin(27))
servo.freq(50)


def mover_servo(angulo):

    pulso = 500 + (angulo * 2000 // 180)

    duty = int(pulso * 65535 / 20000)

    servo.duty_u16(duty)


# Catraca começa fechada
mover_servo(0)


# ==========================================
# TECLADO
# ==========================================

def ler_tecla():

    for i in range(4):

        for linha in linhas:
            linha.value(1)

        linhas[i].value(0)

        for j in range(4):

            if colunas[j].value() == 0:

                tecla = teclas[i][j]

                while colunas[j].value() == 0:
                    sleep(0.01)

                return tecla

    return None


# ==========================================
# ACESSO LIBERADO
# ==========================================

def liberar_acesso(nome):

    print("================================")
    print("ACESSO LIBERADO")
    print("Usuario:", nome)
    print("================================")

    # LED verde
    led_verde.value(1)
    led_vermelho.value(0)

    # LCD
    lcd.clear()

    lcd.cursor(0, 0)
    lcd.print(nome)

    lcd.cursor(1, 0)
    lcd.print("ACESSO LIBERADO")

    # Abre a catraca
    print("Abrindo catraca...")
    mover_servo(90)

    sleep(3)

    # Fecha a catraca
    print("Fechando catraca...")
    mover_servo(0)

    # Apaga LED
    led_verde.value(0)


# ==========================================
# ACESSO NEGADO
# ==========================================

def negar_acesso():

    print("================================")
    print("ACESSO NEGADO")
    print("================================")

    # LED vermelho
    led_verde.value(0)
    led_vermelho.value(1)

    # LCD
    lcd.clear()

    lcd.cursor(0, 0)
    lcd.print("ACESSO NEGADO")

    lcd.cursor(1, 0)
    lcd.print("NAO AUTORIZADO")

    # Servo permanece fechado
    mover_servo(0)

    sleep(3)

    # Apaga LED
    led_vermelho.value(0)


# ==========================================
# WIFI
# ==========================================

def conectar_wifi():

    print("Conectando ao Wi-Fi...")

    lcd.clear()

    lcd.cursor(0, 0)
    lcd.print("CONECTANDO...")

    lcd.cursor(1, 0)
    lcd.print("AGUARDE...")

    wifi = network.WLAN(network.STA_IF)

    wifi.active(True)

    wifi.connect("Wokwi-GUEST", "")

    while not wifi.isconnected():

        print("Aguardando conexao...")
        sleep(1)

    print("Wi-Fi conectado!")
    print("IP:", wifi.ifconfig()[0])

    return wifi


# ==========================================
# INICIALIZAÇÃO
# ==========================================

print("================================")
print("       CATRACA ESP32")
print("================================")


wifi = conectar_wifi()


lcd.clear()

lcd.cursor(0, 0)
lcd.print("WI-FI OK")

lcd.cursor(1, 0)
lcd.print("CONECTADO")

sleep(2)


lcd.clear()

lcd.cursor(0, 0)
lcd.print("CATRACA PRONTA")

lcd.cursor(1, 0)
lcd.print("DIGITE MATRICULA")

sleep(2)


# ==========================================
# MATRÍCULA
# ==========================================

matricula = ""

print("Digite sua matricula:")


# ==========================================
# LOOP PRINCIPAL
# ==========================================

while True:

    tecla = ler_tecla()

    if tecla is not None:

        # ==================================
        # NÚMERO
        # ==================================

        if tecla.isdigit():

            matricula += tecla

            print("Matricula atual:", matricula)

            lcd.clear()

            lcd.cursor(0, 0)
            lcd.print("MATRICULA:")

            lcd.cursor(1, 0)
            lcd.print(matricula)


        # ==================================
        # CONFIRMAR
        # ==================================

        elif tecla == '#':

            if matricula == "":

                lcd.clear()

                lcd.cursor(0, 0)
                lcd.print("DIGITE UMA")

                lcd.cursor(1, 0)
                lcd.print("MATRICULA!")

                sleep(2)

            else:

                print("Matricula confirmada:", matricula)

                # ==================================
                # SIMULAÇÃO DA API
                # ==================================

                if matricula == "123456":

                    nome = "JOAO"

                    liberar_acesso(nome)

                else:

                    negar_acesso()


                # ==================================
                # RESET
                # ==================================

                matricula = ""

                lcd.clear()

                lcd.cursor(0, 0)
                lcd.print("CATRACA PRONTA")

                lcd.cursor(1, 0)
                lcd.print("DIGITE MATRICULA")


        # ==================================
        # APAGAR
        # ==================================

        elif tecla == '*':

            matricula = ""

            print("Matricula apagada.")

            lcd.clear()

            lcd.cursor(0, 0)
            lcd.print("MATRICULA")

            lcd.cursor(1, 0)
            lcd.print("APAGADA!")

            sleep(1)

            lcd.clear()

            lcd.cursor(0, 0)
            lcd.print("CATRACA PRONTA")

            lcd.cursor(1, 0)
            lcd.print("DIGITE MATRICULA")


        # ==================================
        # OUTRAS TECLAS
        # ==================================

        else:

            print("Tecla ignorada:", tecla)

    sleep(0.05)