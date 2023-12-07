import time
import random
from colorsys import hsv_to_rgb
import board                # 수업때 실습한 라이브러리는 혹시 몰라서 전부 끌고 옴
from digitalio import DigitalInOut, Direction
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
from Joystick import Joystick 
from math import sqrt
from random import randint  # 랜덤성이 필요하다 도형 순서대로 주면 재미 없기 때문


joystick = Joystick()
background = Image.new("RGB", (joystick.width, joystick.height))
my_draw = ImageDraw.Draw(background)
width = 12               #테트리스판 가로 크기설정
height = 22              #테트리스판 세로 크기설정
speed = 30               #떨어지는 속도
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" 
font_size = 30
font = ImageFont.truetype(font_path, font_size)
block_size = 9           #블록크기(색칠된부분)
block_grid_size = 10     #블록 격자 (구분을 위해)
gameboard = []           #테트리스 판 list

# 게임 플레이때마다 색 랜덤으로 바꿔주기
colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(9)]
# 배경은 색 바뀌면 안된다....
background_color = (0, 0, 0)
colors[0] = background_color
 
CURRENT_BLOCK = None     # 현재 떨어지는 블록
NEXT_BLOCK = None        # 다음 보여지는 블록
BLOCK_DATA = [
    [[0, 0, 1, 1, 1, 1, 0, 0, 0], [0, 1, 0, 0, 1, 0, 0, 1, 1], [0, 0, 0, 1, 1, 1, 1, 0, 0], [1, 1, 0, 0, 1, 0, 0, 1, 0]],
    [[2, 0, 0, 2, 2, 2, 0, 0, 0], [0, 2, 2, 0, 2, 0, 0, 2, 0], [0, 0, 0, 2, 2, 2, 0, 0, 2], [0, 2, 0, 0, 2, 0, 2, 2, 0]],
    [[0, 3, 0, 3, 3, 3, 0, 0, 0], [0, 3, 0, 0, 3, 3, 0, 3, 0], [0, 0, 0, 3, 3, 3, 0, 3, 0], [0, 3, 0, 3, 3, 0, 0, 3, 0]],
    [[4, 4, 0, 0, 4, 4, 0, 0, 0], [0, 0, 4, 0, 4, 4, 0, 4, 0], [0, 0, 0, 4, 4, 0, 0, 4, 4], [0, 4, 0, 4, 4, 0, 4, 0, 0]],
    [[0, 5, 5, 5, 5, 0, 0, 0, 0], [0, 5, 0, 0, 5, 5, 0, 0, 5], [0, 0, 0, 0, 5, 5, 5, 5, 0], [5, 0, 0, 5, 5, 0, 0, 5, 0]],
    [[6, 6, 6, 6], [6, 6, 6, 6], [6, 6, 6, 6], [6, 6, 6, 6]],
    [[0, 7, 0, 0, 0, 7, 0, 0, 0, 7, 0, 0, 0, 7, 0, 0], [0, 0, 0, 0, 7, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 7, 0, 0, 0, 7, 0, 0, 0, 7, 0, 0, 0, 7, 0], [0, 0, 0, 0, 0, 0, 0, 0, 7, 7, 7, 7, 0, 0, 0, 0]]
]

#테트리스의 블록 클래스 정의 (생성, 관리)
class Block:                                        
    def __init__(self, count):
        self.turn = randint(0,3)                    # 방향값
        self.type = BLOCK_DATA[randint(0,6)]        # 종류 7가지
        self.data = self.type[self.turn]            # 블록데이터
        self.size = int(sqrt(len(self.data)))       # 블록 크기 (n x n)
        self.xpos = randint(2, 8 - self.size)       # 떨어질 블록 x 좌표
        self.ypos = 1 - self.size                   # 떨어질 블록 y 좌표
        self.fire = count + speed                   # 블럭이 떨어지는 속도 (시간)
 
    def update(self, count):                              # 블록 상태 업데이트, current_block이 아래로 이동하다 
        erased = 0                                        # 다른 블록과 충동시 해당 블록을 게임보드에 추가하고 다음 블록 설정한다
        if overlap(self.xpos, self.ypos + 1, self.turn):  # 겹치는지 확인해본다
            for ypos in range(CURRENT_BLOCK.size):
                for xpos in range(CURRENT_BLOCK.size):
                    index = ypos * self.size + xpos
                    val = CURRENT_BLOCK.data[index]
                    if 0 <= self.ypos+ypos < height and 0 <= self.xpos+xpos < width and val != 0:
                        gameboard[self.ypos+ypos][self.xpos+xpos] = val 
            erased = erase_line()
            next_block(count)
        if self.fire < count:
            self.fire = count + speed
            self.ypos += 1
        return erased
 
    def draw(self):                                 # 블록 표현 (생성) 부분
        for index in range(len(self.data)):
            xpos = index % self.size
            ypos = index // self.size
            val = self.data[index]                
            if 0 <= ypos + self.ypos < height and 0 <= xpos + self.xpos < width and val != 0:
                x_pos = (block_grid_size + (xpos + self.xpos) * block_grid_size)
                y_pos = (block_grid_size + (ypos + self.ypos) * block_grid_size) 
                my_draw.rectangle((x_pos, y_pos, x_pos + block_size, y_pos + block_size), fill=(colors[val]))

def draw_score(score):      # 점수 표시 부분
    my_draw.rectangle((180, 20, 240, 40), fill = (colors[0]))
    score_str = str(score).zfill(6)
    my_draw.text((195, 23), score_str)

def erase_line():         # 줄 삭제 부분 (테트리스 규칙상 한 줄 차면 점수를 얻을 수 있다)
    erased = 0
    ypos = 20
    while (ypos >= 0):
        if all(gameboard[ypos]):
            erased += 1
            del gameboard[ypos]
            gameboard.insert(0, [8,0,0,0,0,0,0,0,0,0,0,8])
        else:
            ypos -= 1
    return erased
 
def is_game_over():       # 패배 (게임 종료) 조건
    count = 0
    for block in gameboard[0]:
        if block != 0:
            count += 1
    if count > 2:
        return True
    else:
        return False
 
def next_block(count):                  # 다음 블록
    global CURRENT_BLOCK, NEXT_BLOCK
    if NEXT_BLOCK != None:
        CURRENT_BLOCK = NEXT_BLOCK
    else:
        CURRENT_BLOCK = Block(count)
    NEXT_BLOCK = Block(count)
 
def overlap(xpos, ypos, turn):          # 블록 이동/회전 시 다른 블록과 겹치는지 확인해보아야 한다
    data = CURRENT_BLOCK.type[turn]
    for y_pos in range(CURRENT_BLOCK.size):
        for x_pos in range(CURRENT_BLOCK.size):
            index = y_pos * CURRENT_BLOCK.size + x_pos
            val = data[index]
            if 0 <= xpos+x_pos < width and 0 <= ypos+y_pos < height:
                if val != 0 and gameboard[ypos+y_pos][xpos+x_pos] != 0:
                    return True
    return False
 
def make_game_board():            # 게임보드 생성 (위에서 리스트로 되어있다)
    for i in range (height-1):
        gameboard.insert(i, [8,0,0,0,0,0,0,0,0,0,0,8])
    gameboard.insert(height-1, [8,8,8,8,8,8,8,8,8,8,8,8])
 
def draw_game_board():            # 현재 상태 게임보드
    for ypos in range(height):
        for xpos in range(width):
            val = gameboard[ypos][xpos]
            my_draw.rectangle((block_grid_size+xpos*block_grid_size,block_grid_size+ypos*block_grid_size,block_grid_size+xpos*block_grid_size+ block_size ,block_grid_size+ypos*block_grid_size+ block_size), fill=(colors[val]))
 
def draw_current_block():         # 현재 떨어지고 있는 블록 표현
    CURRENT_BLOCK.draw()

def draw_next_block():           # 다음에 나올 블록
    for ypos in range(4):
        for xpos in range(4):                   # 아래로 이동하는 격자 표현
            index = ypos * NEXT_BLOCK.size + xpos
            x_pos = 200 + xpos * block_grid_size
            y_pos = 70 + ypos * block_grid_size
            my_draw.rectangle((x_pos, y_pos, x_pos + block_size, y_pos + block_size), fill=(colors[0]))

    for ypos in range(NEXT_BLOCK.size):         # 아래로 이동하여 생긴 블럭의 사이즈, 격자를 활용하여 표현
        for xpos in range(NEXT_BLOCK.size):
            index = ypos * NEXT_BLOCK.size + xpos
            val = NEXT_BLOCK.data[index]
            x_pos = 200 + xpos * block_grid_size
            y_pos = 70 + ypos * block_grid_size
            my_draw.rectangle((x_pos, y_pos, x_pos + block_size, y_pos + block_size), fill=(colors[val]))

def draw_game_over():              # 게임 종료 메시지
    text = "GAME OVER"
    my_draw.text((10, 90), text, fill='white', font=font)




def main():                        
    global speed
    count = 0
    score = 0
    
    next_block(speed)
 
    make_game_board()
 
    while True:         #계속 돌린다
 
        game_over = is_game_over()  # 게임오버 호출

        if not game_over:           # 게임 진행 시, count 스택에 따라 
            count += 5
            if count % 1000 == 0:
                speed = max(1, speed - 5)
            erased = CURRENT_BLOCK.update(count) 

            if (erased > 0):                # 삭제될 때마다 점수가 score변수에 200씩 추가된다.
                score += (200 * erased)

            next_x = CURRENT_BLOCK.xpos
            next_y = CURRENT_BLOCK.ypos
            next_t = CURRENT_BLOCK.turn

            if not joystick.button_A.value:
                next_t = (next_t + 1) % 4           # B 버튼과 마찬가지로 모양이 너무 빠르게 두번 바뀌는 경우가 발생
                time.sleep(0.05)                    # 위 문제 해결을 위해 sleep으로 지연시킴
            elif not joystick.button_L.value:
                next_x -= 1
            elif not joystick.button_R.value:
                next_x += 1
            elif not joystick.button_D.value:
                next_y += 1
            elif not joystick.button_B.value:                      # B 버튼을 눌렀을 때
                while not overlap(next_x, next_y + 1, next_t):     #너무 빠르게 내려오는 바람에 생기는 문제: 다음도형도 내려와버림
                    next_y += 1
                    time.sleep(0.1)                             # 위 문제를 해결하기 위해 sleep 으로 일부로 지연시킴으로서 해결
            
            if not overlap(next_x, next_y, next_t):
                CURRENT_BLOCK.xpos = next_x
                CURRENT_BLOCK.ypos = next_y
                CURRENT_BLOCK.turn = next_t
                CURRENT_BLOCK.data = CURRENT_BLOCK.type[CURRENT_BLOCK.turn]
 
        draw_game_board()
 
        draw_current_block()

        draw_next_block()

        draw_score(score);


        if game_over:
            draw_game_over()
            
        joystick.disp.image(background)
        
if __name__ == '__main__':
    main()