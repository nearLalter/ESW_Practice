from digitalio import DigitalInOut, Direction
from adafruit_rgb_display import st7789
import board

class Joystick:
    def __init__(self):
        self.cs_pin = DigitalInOut(board.CE0)
        self.dc_pin = DigitalInOut(board.D25)
        self.reset_pin = DigitalInOut(board.D24)
        self.BAUDRATE = 24000000

        self.spi = board.SPI()
        self.disp = st7789.ST7789(
                    self.spi,
                    height=240,
                    y_offset=80,
                    rotation=180,
                    cs=self.cs_pin,
                    dc=self.dc_pin,
                    rst=self.reset_pin,
                    baudrate=self.BAUDRATE,
                    )

        # Input pins:
        self.button_A = DigitalInOut(board.D5)     # LEFTBUTTON: 조각 시계방향 회전
        self.button_A.direction = Direction.INPUT

        self.button_B = DigitalInOut(board.D6)     # RIGHTBUTTON: 조각 빠르게 떨어뜨리기
        self.button_B.direction = Direction.INPUT

        self.button_L = DigitalInOut(board.D27)    # 블록 좌로 이동
        self.button_L.direction = Direction.INPUT

        self.button_R = DigitalInOut(board.D23)    # 블록 우로 이동
        self.button_R.direction = Direction.INPUT

        self.button_D = DigitalInOut(board.D22)    # 조각 아래로 천천히? 내리기
        self.button_D.direction = Direction.INPUT

        # Turn on the Backlight
        self.backlight = DigitalInOut(board.D26)
        self.backlight.switch_to_output()
        self.backlight.value = True

        # Create blank image for drawing.
        # Make sure to create image with mode 'RGB' for color.
        self.width = self.disp.width
        self.height = self.disp.height