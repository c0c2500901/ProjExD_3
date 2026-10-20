import os
import random
import sys
import time

import pygame as pg


WIDTH = 1100
HEIGHT = 650
NUM_OF_BOMBS = 5

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """オブジェクトが画面内にあるか判定する"""
    yoko, tate = True, True

    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False

    return yoko, tate


class Bird:
    """ゲームキャラクター（こうかとん）に関するクラス"""

    delta = {
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }

    img0 = pg.transform.rotozoom(
        pg.image.load("fig/3.png"), 0, 0.9
    )
    img = pg.transform.flip(img0, True, False)

    imgs = {
        (+5, 0): img,
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),
        (-5, 0): img0,
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),
    }

    def __init__(self, xy: tuple[int, int]):
        """こうかとん画像を生成する"""
        self.img = Bird.imgs[(+5, 0)]
        self.rct: pg.Rect = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        """こうかとん画像を切り替える"""
        self.img = pg.transform.rotozoom(
            pg.image.load(f"fig/{num}.png"), 0, 0.9
        )
        screen.blit(self.img, self.rct)

    def update(self, key_lst, screen: pg.Surface):
        """こうかとんを移動させて表示する"""
        sum_mv = [0, 0]

        for k, mv in Bird.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        self.rct.move_ip(sum_mv)

        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])

        if sum_mv != [0, 0]:
            self.img = Bird.imgs[tuple(sum_mv)]

        screen.blit(self.img, self.rct)


class Beam:
    """こうかとんが放つビームに関するクラス"""

    def __init__(self, bird: Bird):
        """ビーム画像を生成する"""
        self.img = pg.image.load("fig/beam.png")
        self.rct = self.img.get_rect()
        self.rct.centery = bird.rct.centery
        self.rct.left = bird.rct.right
        self.vx, self.vy = +5, 0

    def update(self, screen: pg.Surface):
        """ビームを移動させて表示する"""
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Bomb:
    """爆弾に関するクラス"""

    def __init__(self, color: tuple[int, int, int], rad: int):
        """爆弾を生成する"""
        self.img = pg.Surface((2 * rad, 2 * rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = (
            random.randint(rad, WIDTH - rad),
            random.randint(rad, HEIGHT - rad),
        )
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """爆弾を移動させて表示する"""
        yoko, tate = check_bound(self.rct)

        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1

        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Score:
    """スコア表示に関するクラス"""

    def __init__(self):
        self.fonto = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.score = 0
        self.img = self.fonto.render(
            f"Score: {self.score}", 0, self.color
        )
        self.rct = self.img.get_rect()
        self.rct.center = (100, HEIGHT - 50)

    def update(self, screen: pg.Surface):
        """スコアを表示する"""
        self.img = self.fonto.render(
            f"Score: {self.score}", 0, self.color
        )
        screen.blit(self.img, self.rct)


def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")

    bird = Bird((300, 200))
    score = Score()

    bombs = [
        Bomb((255, 0, 0), 10)
        for _ in range(NUM_OF_BOMBS)
    ]
    beams = []

    fonto = pg.font.Font(None, 80)
    clock = pg.time.Clock()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return
                if event.key == pg.K_SPACE:
                    beams.append(Beam(bird))

        # 背景を表示する
        screen.blit(bg_img, [0, 0])

        # こうかとんと爆弾の衝突判定
        for bomb in bombs:
            if bird.rct.colliderect(bomb.rct):
                bird.change_img(8, screen)

                txt = fonto.render(
                    "Game Over", True, (255, 0, 0)
                )
                screen.blit(
                    txt,
                    [WIDTH // 2 - 150, HEIGHT // 2],
                )

                pg.display.update()
                time.sleep(1)
                return

        # ビームと爆弾の衝突判定
        hit_beams = []
        hit_bombs = []

        for beam in beams:
            for bomb in bombs:
                if (
                    beam not in hit_beams
                    and bomb not in hit_bombs
                    and beam.rct.colliderect(bomb.rct)
                ):
                    score.score += 1
                    hit_beams.append(beam)
                    hit_bombs.append(bomb)
                    bird.change_img(6, screen)
                    break

        # 命中したビームだけを取り除く
        beams = [
            beam for beam in beams
            if beam not in hit_beams
        ]

        # 命中した爆弾だけを取り除く
        bombs = [
            bomb for bomb in bombs
            if bomb not in hit_bombs
        ]

        # 全爆弾を撃ち落としたら終了
        if len(bombs) == 0:
            return

        # こうかとんを更新する
        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)

        # ビームを更新して画面外のものを削除
        for beam in beams:
            beam.update(screen)

        beams = [
            beam for beam in beams
            if check_bound(beam.rct) == (True, True)
        ]

        # 爆弾を更新する
        for bomb in bombs:
            bomb.update(screen)

        # スコアを表示する
        score.update(screen)

        pg.display.update()
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()  