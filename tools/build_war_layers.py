"""Build data/war_layers.json: approximate territorial phases for the focus bands (time lenses).

No openly licensed year-by-year border data exists for these periods, so each phase is composed
here from the outlines of a base snapshot (data/boundaries.json), cut by hand-drawn regions
(lon/lat polygons, plus circles around held cities). Regions are simplified and approximate;
they show the broad picture, not exact frontiers.

Each layer is (side, base year, polity names, within, minus):
  within  None (the whole outline) or a list of regions whose union is kept
  minus   a list of regions taken away (for example another side's territory)
A region is a lon/lat polygon or circle(lon, lat, radius in km).

Usage:  python tools/build_war_layers.py
"""
import json
import os

import numpy as np
from shapely import make_valid
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

from build_data import laea, polygons_of, ring_ints

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "..", "data")


def circle(lon, lat, km):
    return ("circle", lon, lat, km)


# ---------------------------------------------------------------- Three Kingdoms (base: Han, 200)

# Liaodong under the Gongsun clan, outside the Three Kingdoms until Wei took it in 238
LIAODONG = [(120.8, 44), (127, 44), (127, 38), (121.5, 38), (120.8, 40.3)]
# Yuan Shao in 200: Ji, Qing, You and Bing provinces north of the Yellow River
YUAN_200 = [(110.5, 41.5), (119.5, 41.5), (121.0, 40.2), (122.7, 37.6), (122.7, 36.4), (119.0, 36.2),
            (117.0, 36.3), (115.6, 35.9), (114.5, 35.4), (113.5, 35.3), (112.8, 35.6), (110.5, 35.6)]
# Cao Cao in 200: the Han court, Yan, Yu and Xu provinces, Huainan and Guanzhong
CAO_200 = [(110.5, 35.6), (112.8, 35.6), (113.5, 35.3), (114.5, 35.4), (115.6, 35.9), (117.0, 36.3),
           (119.0, 36.2), (120.8, 36.2), (121.0, 32.0), (118.0, 31.5), (116.0, 31.5), (114.5, 32.0),
           (113.0, 32.5), (111.5, 32.6), (110.5, 33.5), (109.0, 33.8), (106.5, 34.3), (106.5, 35.6), (108, 36.0)]
# Sun Quan's Jiangdong, south of the Yangtze
SUN_200 = [(114.0, 29.8), (116.0, 29.75), (117.0, 30.45), (118.3, 31.3), (118.7, 32.0), (119.5, 32.15),
           (121.0, 31.75), (122.5, 31.5), (122.5, 27.0), (120.5, 27.0), (117.0, 25.5), (114.0, 25.5)]
# Cao Cao after taking Jingzhou, December 1208: all the north but Liangzhou, Hanzhong and Liaodong
CAO_208 = [(106.3, 43), (121.0, 43), (121.0, 40.3), (122.7, 37.6), (122.6, 32.3), (121.0, 32.0), (118.3, 31.6),
           (116.0, 31.0), (114.5, 31.0), (113.2, 30.6), (112.0, 30.2), (111.0, 30.8), (110.0, 31.5),
           (109.5, 32.8), (108.0, 33.8), (106.3, 34.3)]
# Liu Bei in 215: Yizhou and western Jingzhou, west of the Xiang River
LIU_215 = [(103.0, 33.2), (105.0, 32.6), (108.0, 32.3), (109.5, 32.3), (110.0, 31.8), (111.0, 31.7),
           (112.0, 31.3), (113.0, 31.0), (113.2, 30.3), (113.0, 29.5), (112.9, 28.0), (112.6, 26.9),
           (112.0, 25.3), (110.0, 25.5), (108.0, 25.0), (106.5, 24.8), (105.0, 24.0), (104.0, 23.0),
           (100.0, 22.0), (97.5, 24.5), (98.5, 28.5), (100.5, 30.0), (102.0, 31.5)]
# Sun Quan in 215: Jiangdong, eastern Jingzhou and Jiaozhou
SUN_215 = [(113.2, 30.3), (114.5, 30.3), (116.0, 29.75), (117.0, 30.45), (118.3, 31.3), (118.7, 32.0),
           (119.5, 32.15), (121.0, 31.75), (122.5, 31.5), (122.5, 24.0), (117, 22), (110, 17), (105, 17),
           (103.5, 22.5), (104.0, 23.0), (105.0, 24.0), (106.5, 24.8), (108.0, 25.0), (110.0, 25.5),
           (112.0, 25.3), (112.6, 26.9), (112.9, 28.0), (113.0, 29.5)]
# Shu Han after Yiling, 222: Yizhou with Hanzhong and Nanzhong
SHU_222 = [(103.0, 33.2), (105.0, 33.3), (106.5, 33.6), (107.5, 33.7), (108.5, 33.3), (109.6, 32.8),
           (109.8, 31.2), (109.5, 30.0), (108.8, 28.5), (108.5, 26.5), (107.5, 25.2), (106.5, 24.8),
           (105.0, 24.0), (104.0, 23.0), (100.0, 22.0), (97.5, 24.5), (98.5, 28.5), (100.5, 30.0), (102.0, 31.5)]
# Wu after Yiling: Jiangdong, all of Jingzhou south of the Wei frontier, and Jiaozhou
WU_222 = [(109.8, 31.2), (111.5, 31.3), (112.5, 31.1), (113.5, 31.1), (114.5, 30.8), (116.0, 30.8),
          (117.0, 31.3), (118.3, 31.6), (119.0, 32.1), (121.0, 32.0), (122.6, 32.1), (122.6, 24.0), (117, 22),
          (110, 17), (105, 17), (103.5, 22.5), (104.0, 23.0), (105.0, 24.0), (106.5, 24.8), (107.5, 25.2),
          (108.5, 26.5), (108.8, 28.5), (109.5, 30.0)]

HAN = (200, ["Han"])

# ---------------------------------------------------------------- Sixteen Kingdoms (base: Jin and Han Zhao, 300)

CHENG = [(103.0, 32.5), (105.0, 32.8), (107.5, 32.5), (108.5, 31.0), (108.0, 29.0), (106.0, 28.0), (104.0, 28.0),
         (102.5, 29.5), (102.5, 31.5)]
LIANG = [(93, 42), (98.5, 41.5), (103.5, 39.5), (104.3, 37.0), (103.5, 35.5), (102.5, 36.0), (100.0, 37.5),
         (98, 38.5), (94, 39.0), (93, 40)]
# Han Zhao in 311: Pingyang and southern Shanxi, with Luoyang just taken
ZHAO_311 = [(110.4, 37.5), (112.2, 37.2), (112.5, 36.0), (113.5, 35.3), (114.8, 35.0), (113.5, 34.3),
            (112.0, 34.2), (110.5, 34.6), (110.4, 35.5)]
ZHAO_318 = [(106.0, 34.3), (106.0, 36.8), (108, 38), (110, 41.5), (118.5, 41.5), (118.8, 40.2), (118.8, 39.0),
            (117.5, 37.8), (117.0, 36.0), (116.0, 35.0), (114.5, 34.5), (113.0, 34.0), (111.0, 33.8),
            (109.0, 33.8), (107.0, 34.0)]
ZHAO_330 = [(106.0, 34.3), (106.0, 36.8), (108, 38), (110, 41.5), (118.5, 41.5), (118.8, 40.2), (119, 39),
            (118, 38), (119, 37.3), (122.7, 37.5), (122.6, 35.0), (120.5, 34.0), (118.5, 33.3), (116.5, 33.0),
            (115.0, 32.8), (113.5, 32.7), (112.0, 33.0), (110.5, 33.5), (108.5, 33.8), (107.0, 34.0)]
# the Murong Xianbei of Liaodong and Liaoxi (Former Yan from 337)
YAN_MURONG = [(118.8, 43.0), (125, 43.0), (125, 38.5), (121, 38.5), (119.5, 39.8), (118.8, 40.2)]
# Eastern Jin in 376, after Former Qin took Sichuan
JIN_376 = [(122.6, 33.8), (120.5, 33.8), (118.5, 33.2), (116.8, 33.0), (115.0, 32.5), (113.0, 32.5),
           (111.5, 32.6), (110.5, 32.0), (110.0, 31.0), (109.8, 30.0), (108.8, 28.5), (108.5, 26.5), (107.5, 25.2),
           (106.5, 24.8), (105.0, 24.0), (104.0, 23.0), (103.5, 22.5), (105, 17), (110, 17), (117, 22), (122.6, 24)]
# the north after Fei River, 395: Northern Wei, Later Yan, Later Qin and the Liang states
WEI_395 = [(106.5, 43), (116, 43), (115, 41.2), (112.5, 40.6), (111.0, 39.5), (110.0, 38.0), (107.0, 37.5),
           (106.5, 38.5)]
YAN_395 = [(110.5, 39.2), (112.0, 40.2), (114.5, 40.4), (116, 41.5), (118, 42.5), (125, 43), (125, 38.5),
           (121, 38.5), (119, 39.5), (118, 38), (119.2, 37.2), (122.7, 37.5), (122.7, 37.0), (119.5, 36.7),
           (117.0, 36.0), (115.0, 35.5), (113.5, 35.0), (112.0, 34.8), (111.0, 35.2), (110.5, 36.0)]
QIN_395 = [(104.5, 34.2), (104.5, 36.3), (106.5, 37.0), (108.5, 37.5), (110.4, 36.5), (110.5, 34.6),
           (109.5, 33.8), (106.5, 33.6)]
LIANG_395 = LIANG[:4] + [(104.5, 36.3), (104.5, 34.2), (103, 34.5)] + LIANG[5:]
# Eastern Jin in 395, back on the Yellow River after Xie Xuan's northern campaign
JIN_395 = [(122.7, 37.0), (119.5, 36.7), (117.0, 36.0), (115.0, 35.5), (113.5, 35.0), (112.0, 34.8), (111.0, 34.5),
           (110.5, 34.0), (109.5, 33.8), (106.5, 33.6), (104.5, 34.2), (103, 34.5), (102.0, 31.5), (100.5, 30.0),
           (98.5, 28.5), (97.5, 24.5), (100.0, 22.0), (103.5, 22.5), (105, 17), (110, 17), (117, 22), (122.7, 24)]
# Liu Song in 439: south of the Huai and Qinling, with Shandong and Hanzhong
SONG_439 = [(122.7, 38.0), (118.8, 37.4), (117.0, 36.0), (116.0, 35.2), (114.5, 34.0), (113.5, 33.5),
            (112.0, 33.0), (110.5, 33.0), (107.5, 33.0), (105.5, 33.2), (104.0, 33.0), (103.0, 32.5), (102.0, 31.5),
            (100.5, 30.0), (98.5, 28.5), (97.5, 24.5), (100.0, 22.0), (103.5, 22.5), (105, 17), (110, 17),
            (117, 22), (122.7, 24)]

JIN = (300, ["Jin", "Han Zhao"])

# ---------------------------------------------------------------- War of Resistance (base: 1930)

MANCHUKUO_1932 = [(119.8, 40.0), (120.9, 41.0), (121.7, 42.3), (121.3, 43.8), (120.0, 45.0), (117.5, 46.3),
                  (115.5, 47.0), (115.5, 54), (136, 54), (136, 38), (121, 38)]
# with Rehe, taken in 1933
MANCHUKUO_1933 = [(119.8, 40.0), (118.5, 40.2), (117.2, 40.4), (116.4, 40.7), (116.2, 41.8), (117.0, 43.5),
                  (117.6, 45.0), (117.5, 46.3), (115.5, 47.0), (115.5, 54), (136, 54), (136, 38), (121, 38)]
# end of 1937: Chahar and Suiyuan to Baotou, northern Shanxi, Hebei, northern Shandong
NORTH_1937 = [(109.5, 42.5), (109.5, 40.3), (110.8, 39.5), (111.3, 38.3), (112.0, 37.5), (113.5, 37.0),
              (114.5, 36.2), (115.5, 36.4), (116.8, 36.5), (118.5, 36.9), (119.5, 37.4), (122.7, 37.5),
              (122.7, 40.0), (119.5, 42.5)]
# Shanghai - Nanjing - Hangzhou
JIANGNAN_1937 = [(121.9, 31.9), (120.5, 32.3), (119.0, 32.4), (118.3, 32.2), (118.4, 31.3), (119.4, 30.9),
                 (119.9, 30.2), (120.6, 30.0), (121.9, 30.6)]
# October 1938, after Xuzhou, Kaifeng, Wuhan and Guangzhou fell
EAST_1938 = [(110.0, 42.5), (109.8, 40.8), (110.6, 39.5), (111.2, 38.2), (111.3, 36.5), (110.8, 35.4),
             (111.6, 34.9), (113.5, 34.9), (114.2, 34.4), (114.6, 33.4), (114.3, 32.4), (113.8, 31.4),
             (113.3, 30.4), (113.0, 29.4), (114.5, 29.3), (116.2, 29.3), (117.3, 30.0), (118.3, 30.4),
             (119.6, 30.1), (120.6, 29.9), (122.6, 29.9), (122.6, 40.0), (119.5, 42.5)]
CANTON = [(112.7, 23.6), (113.8, 23.6), (114.3, 22.6), (113.9, 22.2), (113.0, 22.0), (112.6, 22.6)]
HAINAN = [(108.4, 20.3), (111.2, 20.3), (111.2, 18.0), (108.4, 18.0)]
# end of 1941: Nanchang and Yichang added
EAST_1941 = EAST_1938[:12] + [(111.2, 30.8), (111.4, 30.4), (113.0, 29.4), (114.5, 29.3), (115.0, 29.0),
                              (115.6, 28.4), (116.2, 28.6), (116.2, 29.3)] + EAST_1938[15:]
# end of 1944, after Operation Ichi-Go: western Henan and a corridor through Hunan and Guangxi
EAST_1944 = EAST_1941[:6] + [(110.5, 34.6), (111.3, 34.0), (112.5, 33.5), (113.6, 32.6)] + EAST_1941[10:]
CORRIDOR_1944 = [(113.0, 29.4), (111.5, 29.8), (112.0, 29.0), (111.5, 27.8), (111.2, 26.5), (110.0, 26.0),
                 (108.8, 25.3), (107.8, 24.6), (107.4, 23.5), (106.6, 22.5), (108.5, 21.5), (110.5, 21.8),
                 (112.0, 22.5), (113.6, 23.5), (113.8, 24.5), (113.5, 25.5), (114.0, 27.0), (113.8, 29.0)]

CHINA_1930 = (1930, ["Chinese Warlords", "Manchuria"])

# ---------------------------------------------------------------- Civil War (base: 1945)

# north Manchuria, beyond the Songhua, held by the Northeast Democratic United Army in mid-1946
NE_NORTH = [(119.0, 44.0), (122.5, 44.6), (124.5, 44.5), (126.5, 44.8), (127.8, 43.8), (129.2, 43.0),
            (131.5, 42.5), (136, 47), (136, 54), (115.5, 54), (115.5, 47.0), (117.5, 46.3)]
NE_ALL = [(115.5, 54), (136, 54), (136, 38), (121, 38), (119.7, 39.9), (119.0, 42.0), (117.5, 44.0), (115.5, 47)]
# the Shenyang - Changchun railway and southern Liaoning, held by the Nationalists through 1947
LIAO_CORRIDOR = [(119.8, 40.0), (121.0, 41.5), (123.0, 42.1), (124.5, 43.4), (125.6, 44.2), (126.8, 43.9),
                 (126.4, 43.4), (124.5, 41.6), (123.5, 40.5), (122.2, 39.0), (121.0, 38.7)]
# base areas of 1946
SHAANGANNING = [(106.8, 37.9), (108.0, 38.6), (110.3, 38.2), (110.4, 36.2), (109.5, 35.3), (107.5, 35.5), (106.5, 36.6)]
JINSUI = [(110.5, 39.8), (112.3, 39.5), (112.6, 38.3), (111.8, 37.0), (110.6, 36.8)]
JINCHAJI = [(113.0, 39.0), (113.8, 40.6), (114.9, 41.8), (117.2, 42.6), (119.4, 42.2), (118.9, 40.6), (117.5, 40.5),
            (116.2, 40.3), (115.5, 39.6), (114.6, 38.4), (114.0, 37.4), (113.4, 37.6)]
JINJILUYU = [(112.6, 37.2), (113.8, 37.0), (114.6, 37.6), (115.8, 37.2), (116.3, 35.9), (115.6, 34.9), (114.2, 35.0),
             (113.0, 35.3), (112.3, 36.2)]
SHANDONG = [(116.6, 37.6), (118.3, 38.0), (120.0, 37.7), (122.6, 37.4), (121.6, 36.4), (119.6, 35.4), (118.6, 34.6),
            (117.4, 35.0), (116.8, 36.0)]
SUWAN = [(118.4, 34.6), (120.4, 34.6), (120.9, 33.1), (119.9, 32.5), (118.4, 32.8)]
# end of 1947: the base areas grown together, with Liu-Deng's army in the Dabie Mountains
NORTH_1947 = [(112.0, 39.6), (113.8, 40.6), (114.9, 41.8), (117.2, 42.6), (119.4, 42.2), (118.9, 40.6),
              (117.5, 40.5), (116.2, 40.3), (115.5, 39.6), (116.5, 38.8), (117.6, 38.2), (118.3, 38.0),
              (122.6, 37.4), (121.6, 36.4), (119.6, 35.4), (120.4, 34.6), (120.9, 33.1), (119.9, 32.5),
              (117.0, 33.5), (115.6, 34.0), (113.0, 35.0), (111.8, 37.0), (110.6, 36.8), (110.5, 39.8)]
CENTRAL_PLAINS_1947 = [(113.5, 33.5), (115.0, 34.0), (116.5, 33.5), (116.5, 31.5), (115.5, 30.6), (114.5, 31.0),
                       (113.8, 31.8), (112.5, 32.5)]
# November 1948: everything north of this line except the cities below
NORTH_1948 = [(106.5, 43), (106.5, 38.5), (106.6, 36.5), (107.5, 35.4), (109.5, 35.2), (110.4, 35.3),
              (111.0, 34.6), (112.5, 33.8), (113.5, 33.5), (114.5, 32.6), (115.5, 31.0), (116.5, 33.0),
              (116.0, 34.6), (117.5, 35.0), (118.5, 35.0), (119.5, 34.6), (120.6, 34.4), (122.7, 34.4), (122.7, 43)]
BEIPING_TIANJIN = [(114.5, 40.4), (115.3, 41.0), (118.8, 40.0), (118.6, 38.8), (116.8, 38.6), (115.5, 39.3)]
# January 1949: everything north of the Yangtze
NORTH_1949 = [(106.5, 43), (106.5, 38.5), (106.6, 36.5), (107.5, 35.4), (109.5, 35.2), (110.4, 35.3),
              (111.0, 34.6), (112.0, 33.4), (111.0, 32.3), (112.5, 31.5), (113.5, 31.0), (114.8, 31.0),
              (116.0, 30.2), (117.0, 30.6), (118.3, 31.4), (118.7, 32.2), (119.5, 32.3), (121.0, 32.0),
              (122.7, 31.8), (122.7, 43)]
# still Nationalist on 1 October 1949: the southwest, Guangdong and Guangxi, Hainan
KMT_1949 = [(98.0, 33.0), (102.0, 33.5), (104.0, 33.0), (106.0, 33.6), (107.5, 33.7), (108.5, 33.0),
            (110.0, 31.5), (110.8, 29.0), (111.0, 27.5), (112.0, 26.5), (113.0, 27.0), (113.8, 25.5),
            (114.5, 24.6), (115.5, 24.0), (116.5, 23.3), (116.5, 20), (110, 17), (106, 20), (103.5, 22.5),
            (97.5, 24.0), (97.5, 28.5)]
ILI = [(79.5, 49.5), (90.5, 49.5), (90.5, 43.3), (79.5, 43.3)]  # the Three Districts, outside both sides
CITIES_1946 = [circle(117.0, 36.65, 40), circle(120.4, 36.07, 40), circle(112.55, 37.87, 50),
               circle(113.3, 40.1, 40), circle(114.5, 38.04, 30)]
CITIES_1947 = [circle(117.0, 36.65, 40), circle(120.4, 36.07, 40), circle(112.55, 37.87, 50),
               circle(113.3, 40.1, 40), circle(114.9, 40.8, 50), circle(118.2, 39.63, 30)]
CITIES_1948 = [BEIPING_TIANJIN, circle(112.55, 37.87, 50), circle(113.3, 40.1, 40), circle(111.7, 40.8, 50),
               circle(110.0, 40.6, 40), circle(120.4, 36.07, 40), circle(114.4, 36.1, 25), circle(113.9, 35.3, 20)]
CITIES_1949 = [circle(112.55, 37.87, 50), circle(113.3, 40.1, 40), circle(111.7, 40.8, 50), circle(110.0, 40.6, 40),
               circle(120.4, 36.07, 40), circle(114.4, 36.1, 25)]
ISLANDS_1949 = [circle(118.1, 24.5, 25), circle(122.2, 30.0, 40)]  # Xiamen and Kinmen, Zhoushan
ISLANDS_1950 = [circle(118.35, 24.45, 20), circle(119.95, 26.15, 12), circle(122.2, 30.0, 40)]

CHINA_1945 = (1945, ["China", "Manchuria", "Xinjiang", "Taiwan"])
MAINLAND_1945 = (1945, ["China", "Manchuria", "Xinjiang"])
TAIWAN_1945 = (1945, ["Taiwan"])

# ---------------------------------------------------------------- phases

def L(side, base, within=None, minus=()):
    return (side, base, within, list(minus))


PHASES = {
    "threeKingdoms": [
        ("0200-10-31", "tk_200", [L("caoWei", HAN, [CAO_200]), L("yuanShao", HAN, [YUAN_200]),
                                  L("sunWu", HAN, [SUN_200])]),
        ("0208-12-31", "tk_208", [L("caoWei", HAN, [CAO_208], [LIAODONG]), L("sunWu", HAN, [SUN_200])]),
        ("0215-12-31", "tk_215", [L("caoWei", HAN, None, [LIU_215, SUN_215, LIAODONG]), L("shuHan", HAN, [LIU_215]),
                                  L("sunWu", HAN, [SUN_215])]),
        ("0222-12-31", "tk_222", [L("caoWei", HAN, None, [SHU_222, WU_222, LIAODONG]), L("shuHan", HAN, [SHU_222]),
                                  L("sunWu", HAN, [WU_222])]),
        ("0263-12-31", "tk_263", [L("caoWei", HAN, None, [WU_222]), L("sunWu", HAN, [WU_222])]),
        ("0266-02-08", "tk_266", [L("jinDynasty", HAN, None, [WU_222]), L("sunWu", HAN, [WU_222])]),
        ("0280-05-01", "tk_280", [L("jinDynasty", HAN)]),
    ],
    "wuhu": [
        ("0311-07-31", "wh_311", [L("zhao", JIN, [ZHAO_311]), L("zhao", (300, ["Han Zhao"])),
                                  L("chengHan", JIN, [CHENG]), L("liang", JIN, [LIANG]),
                                  L("jinSouth", JIN, None, [ZHAO_311, CHENG, LIANG, (300, ["Han Zhao"])])]),
        ("0318-03-31", "wh_318", [L("zhao", JIN, [ZHAO_318]), L("yan", JIN, [YAN_MURONG]),
                                  L("chengHan", JIN, [CHENG]), L("liang", JIN, [LIANG]),
                                  L("jinSouth", JIN, None, [ZHAO_318, YAN_MURONG, CHENG, LIANG])]),
        ("0330-12-31", "wh_330", [L("zhao", JIN, [ZHAO_330]), L("yan", JIN, [YAN_MURONG]),
                                  L("chengHan", JIN, [CHENG]), L("liang", JIN, [LIANG]),
                                  L("jinSouth", JIN, None, [ZHAO_330, YAN_MURONG, CHENG, LIANG])]),
        ("0376-12-31", "wh_376", [L("qin", JIN, None, [JIN_376]), L("jinSouth", JIN, [JIN_376])]),
        ("0395-12-31", "wh_395", [L("northernWei", JIN, [WEI_395]), L("yan", JIN, [YAN_395]),
                                  L("qin", JIN, [QIN_395]), L("liang", JIN, [LIANG_395], [QIN_395]),
                                  L("jinSouth", JIN, [JIN_395], [QIN_395])]),
        ("0439-10-31", "wh_439", [L("northernWei", JIN, None, [SONG_439]), L("jinSouth", JIN, [SONG_439])]),
    ],
    "antiJapanese": [
        ("1932-03-01", "aj_1932", [L("japan", CHINA_1930, [MANCHUKUO_1932])]),
        ("1933-05-31", "aj_1933", [L("japan", CHINA_1930, [MANCHUKUO_1933])]),
        ("1937-12-31", "aj_1937", [L("japan", CHINA_1930, [MANCHUKUO_1933, NORTH_1937, JIANGNAN_1937])]),
        ("1938-10-31", "aj_1938", [L("japan", CHINA_1930, [MANCHUKUO_1933, EAST_1938, CANTON])]),
        ("1941-12-31", "aj_1941", [L("japan", CHINA_1930, [MANCHUKUO_1933, EAST_1941, CANTON, HAINAN]),
                                   L("japan", (1930, ["French Indo-China", "Annam"]))]),
        ("1944-12-31", "aj_1944", [L("japan", CHINA_1930, [MANCHUKUO_1933, EAST_1944, CORRIDOR_1944, CANTON, HAINAN]),
                                   L("japan", (1930, ["French Indo-China", "Annam"]))]),
    ],
    "civilWar": [
        ("1946-06-30", "cw_1946", [
            L("ccp", MAINLAND_1945, [NE_NORTH, SHAANGANNING, JINSUI, JINCHAJI, JINJILUYU, SHANDONG, SUWAN], CITIES_1946),
            L("kmt", CHINA_1945, None, [NE_NORTH, SHAANGANNING, JINSUI, JINCHAJI, JINJILUYU, SHANDONG, SUWAN, ILI]),
            L("kmt", MAINLAND_1945, CITIES_1946)]),
        ("1947-12-31", "cw_1947", [
            L("ccp", MAINLAND_1945, [NE_ALL, SHAANGANNING, NORTH_1947, CENTRAL_PLAINS_1947], [LIAO_CORRIDOR] + CITIES_1947),
            L("kmt", CHINA_1945, None, [NE_ALL, SHAANGANNING, NORTH_1947, CENTRAL_PLAINS_1947, ILI]),
            L("kmt", MAINLAND_1945, [LIAO_CORRIDOR] + CITIES_1947, [ILI])]),
        ("1948-11-02", "cw_1948", [
            L("ccp", MAINLAND_1945, [NE_ALL, NORTH_1948], CITIES_1948),
            L("kmt", CHINA_1945, None, [NE_ALL, NORTH_1948, ILI]),
            L("kmt", MAINLAND_1945, CITIES_1948)]),
        ("1949-01-31", "cw_1949a", [
            L("ccp", MAINLAND_1945, [NE_ALL, NORTH_1949], CITIES_1949),
            L("kmt", CHINA_1945, None, [NE_ALL, NORTH_1949, ILI]),
            L("kmt", MAINLAND_1945, CITIES_1949)]),
        ("1949-10-01", "cw_1949b", [
            L("ccp", MAINLAND_1945, None, [KMT_1949] + ISLANDS_1949),
            L("kmt", MAINLAND_1945, [KMT_1949] + ISLANDS_1949),
            L("kmt", TAIWAN_1945)]),
        ("1950-05-01", "cw_1950", [
            L("ccp", MAINLAND_1945, None, ISLANDS_1950),
            L("kmt", MAINLAND_1945, ISLANDS_1950),
            L("kmt", TAIWAN_1945)]),
    ],
}

# Simplified Chinese titles; translations live in data/i18n/<lang>.json under "phases"
TITLES = {
    "tk_200": "200年：官渡之战，曹操与袁绍争夺北方",
    "tk_208": "208年底：赤壁之战，曹操据有北方",
    "tk_215": "215年：刘备据益州，孙刘湘水划界",
    "tk_222": "222年：夷陵之战后，三国鼎立",
    "tk_263": "263年：魏灭蜀汉",
    "tk_266": "266年：司马炎代魏建晋",
    "tk_280": "280年：晋灭吴，三国归晋",
    "wh_311": "311年：永嘉之乱，汉赵攻陷洛阳",
    "wh_318": "318年：西晋亡，东晋立于建康",
    "wh_330": "330年：后赵据有北方大部",
    "wh_376": "376年：前秦统一北方",
    "wh_395": "395年：淝水之战后北方再度分裂",
    "wh_439": "439年：北魏统一北方，南北朝对峙",
    "aj_1932": "1932年3月：伪满洲国成立",
    "aj_1933": "1933年5月：热河失陷，《塘沽协定》",
    "aj_1937": "1937年底：华北与京沪杭沦陷",
    "aj_1938": "1938年10月：武汉、广州失守，进入相持阶段",
    "aj_1941": "1941年底：太平洋战争爆发，日军进驻印度支那",
    "aj_1944": "1944年底：豫湘桂战役后日军占领区最大",
    "cw_1946": "1946年6月：全面内战爆发",
    "cw_1947": "1947年底：解放军转入战略进攻",
    "cw_1948": "1948年11月：辽沈战役结束，东北全境易手",
    "cw_1949a": "1949年1月：淮海、平津战役结束",
    "cw_1949b": "1949年10月1日：中华人民共和国成立",
    "cw_1950": "1950年5月：海南岛战役，国民政府退守台湾",
}


def main():
    snaps = {s["year"]: s for s in json.load(open(os.path.join(DATA, "boundaries.json"), encoding="utf-8"))["snapshots"]}

    def outline(base):
        year, names = base
        feats = [f for f in snaps[year]["features"] if f["n"] in names]
        assert {f["n"] for f in feats} == set(names), f"{names} not all in {year} snapshot"
        polys = [make_valid(Polygon(_pts(poly[0]), [_pts(h) for h in poly[1:]])) for f in feats for poly in f["p"]]
        return make_valid(unary_union(polys))

    def region(r):
        if isinstance(r, tuple) and r and r[0] == "circle":
            x, y = laea(r[1], r[2])
            return Point(float(x), float(y)).buffer(r[3], 32)
        if isinstance(r, tuple):  # (year, names): another outline
            return outline(r)
        x, y = laea(np.array([p[0] for p in r]), np.array([p[1] for p in r]))
        return make_valid(Polygon(zip(x, y)))

    out = {"wars": {}}
    for war, phases in PHASES.items():
        out["wars"][war] = []
        for date, key, items in phases:
            by_side = {}
            for side, base, within, minus in items:
                g = outline(base)
                if within:
                    g = g.intersection(unary_union([region(r) for r in within]))
                if minus:
                    g = g.difference(unary_union([region(r) for r in minus]))
                by_side.setdefault(side, []).append(g)
            layers = []
            for side, gs in by_side.items():
                g = unary_union(gs).simplify(1.5, preserve_topology=True)
                parts = [p for p in polygons_of(g) if p.area >= 60]
                layers.append({"side": side, "a": int(sum(p.area for p in parts)),
                               "p": [[ring_ints(p.exterior.coords)] + [ring_ints(h.coords) for h in p.interiors]
                                     for p in parts]})
            out["wars"][war].append({"date": date, "key": key, "layers": layers})
            print(f"{date} {key}: " + ", ".join(f"{l['side']} {l['a']:,} km²" for l in layers))
    assert set(TITLES) == {k for ps in PHASES.values() for _, k, _ in ps}
    out["titles"] = TITLES
    with open(os.path.join(DATA, "war_layers.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))


def _pts(ring):
    return [(ring[i], ring[i + 1]) for i in range(0, len(ring), 2)]


if __name__ == "__main__":
    main()
