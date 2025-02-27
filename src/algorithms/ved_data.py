import numpy as np

# the coefficients proposed by V. Ostromoukhov in his article
# these are not used by hopfer. instead bellow yoou can find the
# normalized list.
OSTROMOUKHOV_COEFF = [
    [13, 0, 5],
    [13, 0, 5],
    [21, 0, 10],
    [7, 0, 4],
    [8, 0, 5],
    [47, 3, 28],
    [23, 3, 13],
    [15, 3, 8],
    [22, 6, 11],
    [43, 15, 20],
    [7, 3, 3],
    [501, 224, 211],
    [249, 116, 103],
    [165, 80, 67],
    [123, 62, 49],
    [489, 256, 191],
    [81, 44, 31],
    [483, 272, 181],
    [60, 35, 22],
    [53, 32, 19],
    [237, 148, 83],
    [471, 304, 161],
    [3, 2, 1],
    [481, 314, 185],
    [354, 226, 155],
    [1389, 866, 685],
    [227, 138, 125],
    [267, 158, 163],
    [327, 188, 220],
    [61, 34, 45],
    [627, 338, 505],
    [1227, 638, 1075],
    [20, 10, 19],
    [1937, 1000, 1767],
    [977, 520, 855],
    [657, 360, 551],
    [71, 40, 57],
    [2005, 1160, 1539],
    [337, 200, 247],
    [2039, 1240, 1425],
    [257, 160, 171],
    [691, 440, 437],
    [1045, 680, 627],
    [301, 200, 171],
    [177, 120, 95],
    [2141, 1480, 1083],
    [1079, 760, 513],
    [725, 520, 323],
    [137, 100, 57],
    [2209, 1640, 855],
    [53, 40, 19],
    [2243, 1720, 741],
    [565, 440, 171],
    [759, 600, 209],
    [1147, 920, 285],
    [2311, 1880, 513],
    [97, 80, 19],
    [335, 280, 57],
    [1181, 1000, 171],
    [793, 680, 95],
    [599, 520, 57],
    [2413, 2120, 171],
    [405, 360, 19],
    [2447, 2200, 57],
    [11, 10, 0],
    [158, 151, 3],
    [178, 179, 7],
    [1030, 1091, 63],
    [248, 277, 21],
    [318, 375, 35],
    [458, 571, 63],
    [878, 1159, 147],
    [5, 7, 1],
    [172, 181, 37],
    [97, 76, 22],
    [72, 41, 17],
    [119, 47, 29],
    [4, 1, 1],
    [4, 1, 1],
    [4, 1, 1],
    [4, 1, 1],
    [4, 1, 1],
    [4, 1, 1],
    [4, 1, 1],
    [4, 1, 1],
    [4, 1, 1],
    [65, 18, 17],
    [95, 29, 26],
    [185, 62, 53],
    [30, 11, 9],
    [35, 14, 11],
    [85, 37, 28],
    [55, 26, 19],
    [80, 41, 29],
    [155, 86, 59],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [305, 176, 119],
    [155, 86, 59],
    [105, 56, 39],
    [80, 41, 29],
    [65, 32, 23],
    [55, 26, 19],
    [335, 152, 113],
    [85, 37, 28],
    [115, 48, 37],
    [35, 14, 11],
    [355, 136, 109],
    [30, 11, 9],
    [365, 128, 107],
    [185, 62, 53],
    [25, 8, 7],
    [95, 29, 26],
    [385, 112, 103],
    [65, 18, 17],
    [395, 104, 101],
    [4, 1, 1],
    [4, 1, 1],
    [395, 104, 101],
    [65, 18, 17],
    [385, 112, 103],
    [95, 29, 26],
    [25, 8, 7],
    [185, 62, 53],
    [365, 128, 107],
    [30, 11, 9],
    [355, 136, 109],
    [35, 14, 11],
    [115, 48, 37],
    [85, 37, 28],
    [335, 152, 113],
    [55, 26, 19],
    [65, 32, 23],
    [80, 41, 29],
    [105, 56, 39],
    [155, 86, 59],
    [305, 176, 119],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [5, 3, 2],
    [155, 86, 59],
    [80, 41, 29],
    [55, 26, 19],
    [85, 37, 28],
    [35, 14, 11],
    [30, 11, 9],
    [185, 62, 53],
    [95, 29, 26],
    [65, 18, 17],
    [4, 1, 1],
    [4, 1, 1],
    [4, 1, 1],
    [4, 1, 1],
    [4, 1, 1],
    [4, 1, 1],
    [4, 1, 1],
    [4, 1, 1],
    [4, 1, 1],
    [119, 47, 29],
    [72, 41, 17],
    [97, 76, 22],
    [172, 181, 37],
    [5, 7, 1],
    [878, 1159, 147],
    [458, 571, 63],
    [318, 375, 35],
    [248, 277, 21],
    [1030, 1091, 63],
    [178, 179, 7],
    [158, 151, 3],
    [11, 10, 0],
    [2447, 2200, 57],
    [405, 360, 19],
    [2413, 2120, 171],
    [599, 520, 57],
    [793, 680, 95],
    [1181, 1000, 171],
    [335, 280, 57],
    [97, 80, 19],
    [2311, 1880, 513],
    [1147, 920, 285],
    [759, 600, 209],
    [565, 440, 171],
    [2243, 1720, 741],
    [53, 40, 19],
    [2209, 1640, 855],
    [137, 100, 57],
    [725, 520, 323],
    [1079, 760, 513],
    [2141, 1480, 1083],
    [177, 120, 95],
    [301, 200, 171],
    [1045, 680, 627],
    [691, 440, 437],
    [257, 160, 171],
    [2039, 1240, 1425],
    [337, 200, 247],
    [2005, 1160, 1539],
    [71, 40, 57],
    [657, 360, 551],
    [977, 520, 855],
    [1937, 1000, 1767],
    [20, 10, 19],
    [1227, 638, 1075],
    [627, 338, 505],
    [61, 34, 45],
    [327, 188, 220],
    [267, 158, 163],
    [227, 138, 125],
    [1389, 866, 685],
    [354, 226, 155],
    [481, 314, 185],
    [3, 2, 1],
    [471, 304, 161],
    [237, 148, 83],
    [53, 32, 19],
    [60, 35, 22],
    [483, 272, 181],
    [81, 44, 31],
    [489, 256, 191],
    [123, 62, 49],
    [165, 80, 67],
    [249, 116, 103],
    [501, 224, 211],
    [7, 3, 3],
    [43, 15, 20],
    [22, 6, 11],
    [15, 3, 8],
    [23, 3, 13],
    [47, 3, 28],
    [8, 0, 5],
    [7, 0, 4],
    [21, 0, 10],
    [13, 0, 5],
    [13, 0, 5],
]

# the normalized coefficients proposed by Ostromoukhov
OSTROMOUKHOV_COEFFN = np.array(
    [
        [0.722222, 0.0, 0.277778],
        [0.722222, 0.0, 0.277778],
        [0.677419, 0.0, 0.322581],
        [0.636364, 0.0, 0.363636],
        [0.615385, 0.0, 0.384615],
        [0.602564, 0.038462, 0.358974],
        [0.589744, 0.076923, 0.333333],
        [0.576923, 0.115385, 0.307692],
        [0.564103, 0.153846, 0.282051],
        [0.551282, 0.192308, 0.25641],
        [0.538462, 0.230769, 0.230769],
        [0.535256, 0.239316, 0.225427],
        [0.532051, 0.247863, 0.220085],
        [0.528846, 0.25641, 0.214744],
        [0.525641, 0.264957, 0.209402],
        [0.522436, 0.273504, 0.20406],
        [0.519231, 0.282051, 0.198718],
        [0.516026, 0.290598, 0.193376],
        [0.512821, 0.299145, 0.188034],
        [0.509615, 0.307692, 0.182692],
        [0.50641, 0.316239, 0.17735],
        [0.503205, 0.324786, 0.172009],
        [0.5, 0.333333, 0.166667],
        [0.490816, 0.320408, 0.188776],
        [0.481633, 0.307483, 0.210884],
        [0.472449, 0.294558, 0.232993],
        [0.463265, 0.281633, 0.255102],
        [0.454082, 0.268707, 0.277211],
        [0.444898, 0.255782, 0.29932],
        [0.435714, 0.242857, 0.321429],
        [0.426531, 0.229932, 0.343537],
        [0.417347, 0.217007, 0.365646],
        [0.408163, 0.204082, 0.387755],
        [0.411777, 0.212585, 0.375638],
        [0.415391, 0.221088, 0.36352],
        [0.419005, 0.229592, 0.351403],
        [0.422619, 0.238095, 0.339286],
        [0.426233, 0.246599, 0.327168],
        [0.429847, 0.255102, 0.315051],
        [0.433461, 0.263605, 0.302934],
        [0.437075, 0.272109, 0.290816],
        [0.440689, 0.280612, 0.278699],
        [0.444303, 0.289116, 0.266582],
        [0.447917, 0.297619, 0.254464],
        [0.451531, 0.306122, 0.242347],
        [0.455145, 0.314626, 0.23023],
        [0.458759, 0.323129, 0.218112],
        [0.462372, 0.331633, 0.205995],
        [0.465986, 0.340136, 0.193878],
        [0.4696, 0.348639, 0.18176],
        [0.473214, 0.357143, 0.169643],
        [0.476828, 0.365646, 0.157526],
        [0.480442, 0.37415, 0.145408],
        [0.484056, 0.382653, 0.133291],
        [0.48767, 0.391156, 0.121173],
        [0.491284, 0.39966, 0.109056],
        [0.494898, 0.408163, 0.096939],
        [0.498512, 0.416667, 0.084821],
        [0.502126, 0.42517, 0.072704],
        [0.50574, 0.433673, 0.060587],
        [0.509354, 0.442177, 0.048469],
        [0.512968, 0.45068, 0.036352],
        [0.516582, 0.459184, 0.024235],
        [0.520196, 0.467687, 0.012117],
        [0.52381, 0.47619, 0.0],
        [0.50641, 0.483974, 0.009615],
        [0.489011, 0.491758, 0.019231],
        [0.471612, 0.499542, 0.028846],
        [0.454212, 0.507326, 0.038462],
        [0.436813, 0.51511, 0.048077],
        [0.419414, 0.522894, 0.057692],
        [0.402015, 0.530678, 0.067308],
        [0.384615, 0.538462, 0.076923],
        [0.441026, 0.464103, 0.094872],
        [0.497436, 0.389744, 0.112821],
        [0.553846, 0.315385, 0.130769],
        [0.610256, 0.241026, 0.148718],
        [0.666667, 0.166667, 0.166667],
        [0.666667, 0.166667, 0.166667],
        [0.666667, 0.166667, 0.166667],
        [0.666667, 0.166667, 0.166667],
        [0.666667, 0.166667, 0.166667],
        [0.666667, 0.166667, 0.166667],
        [0.666667, 0.166667, 0.166667],
        [0.666667, 0.166667, 0.166667],
        [0.666667, 0.166667, 0.166667],
        [0.65, 0.18, 0.17],
        [0.633333, 0.193333, 0.173333],
        [0.616667, 0.206667, 0.176667],
        [0.6, 0.22, 0.18],
        [0.583333, 0.233333, 0.183333],
        [0.566667, 0.246667, 0.186667],
        [0.55, 0.26, 0.19],
        [0.533333, 0.273333, 0.193333],
        [0.516667, 0.286667, 0.196667],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.508333, 0.293333, 0.198333],
        [0.516667, 0.286667, 0.196667],
        [0.525, 0.28, 0.195],
        [0.533333, 0.273333, 0.193333],
        [0.541667, 0.266667, 0.191667],
        [0.55, 0.26, 0.19],
        [0.558333, 0.253333, 0.188333],
        [0.566667, 0.246667, 0.186667],
        [0.575, 0.24, 0.185],
        [0.583333, 0.233333, 0.183333],
        [0.591667, 0.226667, 0.181667],
        [0.6, 0.22, 0.18],
        [0.608333, 0.213333, 0.178333],
        [0.616667, 0.206667, 0.176667],
        [0.625, 0.2, 0.175],
        [0.633333, 0.193333, 0.173333],
        [0.641667, 0.186667, 0.171667],
        [0.65, 0.18, 0.17],
        [0.658333, 0.173333, 0.168333],
        [0.666667, 0.166667, 0.166667],
        [0.666667, 0.166667, 0.166667],
        [0.658333, 0.173333, 0.168333],
        [0.65, 0.18, 0.17],
        [0.641667, 0.186667, 0.171667],
        [0.633333, 0.193333, 0.173333],
        [0.625, 0.2, 0.175],
        [0.616667, 0.206667, 0.176667],
        [0.608333, 0.213333, 0.178333],
        [0.6, 0.22, 0.18],
        [0.591667, 0.226667, 0.181667],
        [0.583333, 0.233333, 0.183333],
        [0.575, 0.24, 0.185],
        [0.566667, 0.246667, 0.186667],
        [0.558333, 0.253333, 0.188333],
        [0.55, 0.26, 0.19],
        [0.541667, 0.266667, 0.191667],
        [0.533333, 0.273333, 0.193333],
        [0.525, 0.28, 0.195],
        [0.516667, 0.286667, 0.196667],
        [0.508333, 0.293333, 0.198333],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.5, 0.3, 0.2],
        [0.516667, 0.286667, 0.196667],
        [0.533333, 0.273333, 0.193333],
        [0.55, 0.26, 0.19],
        [0.566667, 0.246667, 0.186667],
        [0.583333, 0.233333, 0.183333],
        [0.6, 0.22, 0.18],
        [0.616667, 0.206667, 0.176667],
        [0.633333, 0.193333, 0.173333],
        [0.65, 0.18, 0.17],
        [0.666667, 0.166667, 0.166667],
        [0.666667, 0.166667, 0.166667],
        [0.666667, 0.166667, 0.166667],
        [0.666667, 0.166667, 0.166667],
        [0.666667, 0.166667, 0.166667],
        [0.666667, 0.166667, 0.166667],
        [0.666667, 0.166667, 0.166667],
        [0.666667, 0.166667, 0.166667],
        [0.666667, 0.166667, 0.166667],
        [0.610256, 0.241026, 0.148718],
        [0.553846, 0.315385, 0.130769],
        [0.497436, 0.389744, 0.112821],
        [0.441026, 0.464103, 0.094872],
        [0.384615, 0.538462, 0.076923],
        [0.402015, 0.530678, 0.067308],
        [0.419414, 0.522894, 0.057692],
        [0.436813, 0.51511, 0.048077],
        [0.454212, 0.507326, 0.038462],
        [0.471612, 0.499542, 0.028846],
        [0.489011, 0.491758, 0.019231],
        [0.50641, 0.483974, 0.009615],
        [0.52381, 0.47619, 0.0],
        [0.520196, 0.467687, 0.012117],
        [0.516582, 0.459184, 0.024235],
        [0.512968, 0.45068, 0.036352],
        [0.509354, 0.442177, 0.048469],
        [0.50574, 0.433673, 0.060587],
        [0.502126, 0.42517, 0.072704],
        [0.498512, 0.416667, 0.084821],
        [0.494898, 0.408163, 0.096939],
        [0.491284, 0.39966, 0.109056],
        [0.48767, 0.391156, 0.121173],
        [0.484056, 0.382653, 0.133291],
        [0.480442, 0.37415, 0.145408],
        [0.476828, 0.365646, 0.157526],
        [0.473214, 0.357143, 0.169643],
        [0.4696, 0.348639, 0.18176],
        [0.465986, 0.340136, 0.193878],
        [0.462372, 0.331633, 0.205995],
        [0.458759, 0.323129, 0.218112],
        [0.455145, 0.314626, 0.23023],
        [0.451531, 0.306122, 0.242347],
        [0.447917, 0.297619, 0.254464],
        [0.444303, 0.289116, 0.266582],
        [0.440689, 0.280612, 0.278699],
        [0.437075, 0.272109, 0.290816],
        [0.433461, 0.263605, 0.302934],
        [0.429847, 0.255102, 0.315051],
        [0.426233, 0.246599, 0.327168],
        [0.422619, 0.238095, 0.339286],
        [0.419005, 0.229592, 0.351403],
        [0.415391, 0.221088, 0.36352],
        [0.411777, 0.212585, 0.375638],
        [0.408163, 0.204082, 0.387755],
        [0.417347, 0.217007, 0.365646],
        [0.426531, 0.229932, 0.343537],
        [0.435714, 0.242857, 0.321429],
        [0.444898, 0.255782, 0.29932],
        [0.454082, 0.268707, 0.277211],
        [0.463265, 0.281633, 0.255102],
        [0.472449, 0.294558, 0.232993],
        [0.481633, 0.307483, 0.210884],
        [0.490816, 0.320408, 0.188776],
        [0.5, 0.333333, 0.166667],
        [0.503205, 0.324786, 0.172009],
        [0.50641, 0.316239, 0.17735],
        [0.509615, 0.307692, 0.182692],
        [0.512821, 0.299145, 0.188034],
        [0.516026, 0.290598, 0.193376],
        [0.519231, 0.282051, 0.198718],
        [0.522436, 0.273504, 0.20406],
        [0.525641, 0.264957, 0.209402],
        [0.528846, 0.25641, 0.214744],
        [0.532051, 0.247863, 0.220085],
        [0.535256, 0.239316, 0.225427],
        [0.538462, 0.230769, 0.230769],
        [0.551282, 0.192308, 0.25641],
        [0.564103, 0.153846, 0.282051],
        [0.576923, 0.115385, 0.307692],
        [0.589744, 0.076923, 0.333333],
        [0.602564, 0.038462, 0.358974],
        [0.615385, 0.0, 0.384615],
        [0.636364, 0.0, 0.363636],
        [0.677419, 0.0, 0.322581],
        [0.722222, 0.0, 0.277778],
        [0.722222, 0.0, 0.277778],
    ]
).astype(np.float64)

# the coefficients proposed by Zhou and Fang in their article, expanded
# and mirrored. these are not used for processing, just here for reference.
ZF_COEFF = [
    [13, 0, 5],
    [1300249, 0, 499250],
    [213113, 287, 99357],
    [351854, 0, 199965],
    [801100, 0, 490999],
    [784929, 49578, 459782],
    [768758, 99155, 428564],
    [752588, 148733, 397346],
    [736417, 198311, 366129],
    [720246, 247888, 334912],
    [704075, 297466, 303694],
    [649286, 275337, 280175],
    [594498, 253208, 256656],
    [539710, 231079, 233138],
    [484921, 208950, 209619],
    [430132, 186821, 186100],
    [375344, 164692, 162582],
    [320556, 142562, 139063],
    [265767, 120433, 115544],
    [210978, 98304, 92025],
    [156190, 76175, 68506],
    [101402, 54046, 44988],
    [46613, 31917, 21469],
    [46700, 31787, 21512],
    [46787, 31657, 21555],
    [46874, 31527, 21598],
    [46961, 31397, 21641],
    [47048, 31267, 21684],
    [47134, 31137, 21728],
    [47221, 31007, 21771],
    [47308, 30877, 21814],
    [47395, 30747, 21857],
    [47482, 30617, 21900],
    [47110, 31576, 21310],
    [46739, 32536, 20721],
    [46368, 33496, 20132],
    [45996, 34455, 19542],
    [45624, 35414, 18952],
    [45253, 36374, 18363],
    [44882, 37334, 17774],
    [44510, 38293, 17184],
    [44138, 39252, 16594],
    [43767, 40212, 16005],
    [43396, 41172, 15416],
    [43024, 42131, 14826],
    [42693, 42185, 15103],
    [42363, 42240, 15380],
    [42032, 42294, 15657],
    [41701, 42349, 15935],
    [41371, 42403, 16212],
    [41040, 42457, 16489],
    [40709, 42512, 16766],
    [40379, 42566, 17043],
    [40048, 42621, 17320],
    [39718, 42675, 17598],
    [39387, 42729, 17875],
    [39056, 42784, 18152],
    [38726, 42838, 18429],
    [38395, 42893, 18706],
    [38064, 42947, 18983],
    [37734, 43001, 19260],
    [37403, 43056, 19538],
    [37072, 43110, 19815],
    [36742, 43165, 20092],
    [36411, 43219, 20369],
    [36669, 44547, 18783],
    [36928, 45875, 17196],
    [37186, 47203, 15610],
    [37444, 48531, 14024],
    [37702, 49859, 12437],
    [37960, 51187, 10851],
    [38219, 52515, 9264],
    [38477, 53843, 7678],
    [38882, 53384, 7732],
    [39287, 52925, 7786],
    [39693, 52465, 7840],
    [40098, 52006, 7894],
    [40503, 51547, 7948],
    [39923, 49367, 10708],
    [39344, 47187, 13468],
    [38764, 45007, 16227],
    [38184, 42828, 18987],
    [37604, 40648, 21747],
    [37024, 38468, 24506],
    [36445, 36288, 27266],
    [35865, 34108, 30026],
    [35690, 34387, 29922],
    [35515, 34666, 29817],
    [35341, 34945, 29713],
    [35166, 35224, 29609],
    [34991, 35504, 29504],
    [34816, 35783, 29400],
    [34641, 36062, 29296],
    [34467, 36341, 29192],
    [34292, 36620, 29087],
    [34117, 36899, 28983],
    [34309, 36635, 29055],
    [34502, 36370, 29126],
    [34694, 36106, 29198],
    [34887, 35842, 29270],
    [35079, 35578, 29342],
    [35272, 35313, 29413],
    [35464, 35049, 29485],
    [31667, 31801, 26530],
    [27869, 28553, 23576],
    [24072, 25306, 20621],
    [20274, 22058, 17667],
    [16477, 18810, 14712],
    [19854, 22639, 17507],
    [23230, 26468, 20301],
    [26607, 30296, 23096],
    [29983, 34125, 25890],
    [33360, 37954, 28685],
    [33487, 37828, 28684],
    [33615, 37702, 28682],
    [33742, 37576, 28681],
    [33869, 37451, 28679],
    [33996, 37325, 28678],
    [34124, 37199, 28677],
    [34251, 37073, 28675],
    [34378, 36947, 28674],
    [34505, 36821, 28672],
    [34633, 36695, 28671],
    [34760, 36569, 28670],
    [34887, 36444, 28668],
    [35014, 36318, 28667],
    [35142, 36192, 28665],
    [35269, 36066, 28664],
    [35269, 36066, 28664],
    [35142, 36192, 28665],
    [35014, 36318, 28667],
    [34887, 36444, 28668],
    [34760, 36569, 28670],
    [34633, 36695, 28671],
    [34505, 36821, 28672],
    [34378, 36947, 28674],
    [34251, 37073, 28675],
    [34124, 37199, 28677],
    [33996, 37325, 28678],
    [33869, 37451, 28679],
    [33742, 37576, 28681],
    [33615, 37702, 28682],
    [33487, 37828, 28684],
    [33360, 37954, 28685],
    [29983, 34125, 25890],
    [26607, 30296, 23096],
    [23230, 26468, 20301],
    [19854, 22639, 17507],
    [16477, 18810, 14712],
    [20274, 22058, 17667],
    [24072, 25306, 20621],
    [27869, 28553, 23576],
    [31667, 31801, 26530],
    [35464, 35049, 29485],
    [35272, 35313, 29413],
    [35079, 35578, 29342],
    [34887, 35842, 29270],
    [34694, 36106, 29198],
    [34502, 36370, 29126],
    [34309, 36635, 29055],
    [34117, 36899, 28983],
    [34292, 36620, 29087],
    [34467, 36341, 29192],
    [34641, 36062, 29296],
    [34816, 35783, 29400],
    [34991, 35504, 29504],
    [35166, 35224, 29609],
    [35341, 34945, 29713],
    [35515, 34666, 29817],
    [35690, 34387, 29922],
    [35865, 34108, 30026],
    [36445, 36288, 27266],
    [37024, 38468, 24506],
    [37604, 40648, 21747],
    [38184, 42828, 18987],
    [38764, 45007, 16227],
    [39344, 47187, 13468],
    [39923, 49367, 10708],
    [40503, 51547, 7948],
    [40098, 52006, 7894],
    [39693, 52465, 7840],
    [39287, 52925, 7786],
    [38882, 53384, 7732],
    [38477, 53843, 7678],
    [38219, 52515, 9264],
    [37960, 51187, 10851],
    [37702, 49859, 12437],
    [37444, 48531, 14024],
    [37186, 47203, 15610],
    [36928, 45875, 17196],
    [36669, 44547, 18783],
    [36411, 43219, 20369],
    [36742, 43165, 20092],
    [37072, 43110, 19815],
    [37403, 43056, 19538],
    [37734, 43001, 19260],
    [38064, 42947, 18983],
    [38395, 42893, 18706],
    [38726, 42838, 18429],
    [39056, 42784, 18152],
    [39387, 42729, 17875],
    [39718, 42675, 17598],
    [40048, 42621, 17320],
    [40379, 42566, 17043],
    [40709, 42512, 16766],
    [41040, 42457, 16489],
    [41371, 42403, 16212],
    [41701, 42349, 15935],
    [42032, 42294, 15657],
    [42363, 42240, 15380],
    [42693, 42185, 15103],
    [43024, 42131, 14826],
    [43396, 41172, 15416],
    [43767, 40212, 16005],
    [44138, 39252, 16594],
    [44510, 38293, 17184],
    [44882, 37334, 17774],
    [45253, 36374, 18363],
    [45624, 35414, 18952],
    [45996, 34455, 19542],
    [46368, 33496, 20132],
    [46739, 32536, 20721],
    [47110, 31576, 21310],
    [47482, 30617, 21900],
    [47395, 30747, 21857],
    [47308, 30877, 21814],
    [47221, 31007, 21771],
    [47134, 31137, 21728],
    [47048, 31267, 21684],
    [46961, 31397, 21641],
    [46874, 31527, 21598],
    [46787, 31657, 21555],
    [46700, 31787, 21512],
    [46613, 31917, 21469],
    [101402, 54046, 44988],
    [156190, 76175, 68506],
    [210978, 98304, 92025],
    [265767, 120433, 115544],
    [320556, 142562, 139063],
    [375344, 164692, 162582],
    [430132, 186821, 186100],
    [484921, 208950, 209619],
    [539710, 231079, 233138],
    [594498, 253208, 256656],
    [649286, 275337, 280175],
    [704075, 297466, 303694],
    [720246, 247888, 334912],
    [736417, 198311, 366129],
    [752588, 148733, 397346],
    [768758, 99155, 428564],
    [784929, 49578, 459782],
    [801100, 0, 490999],
    [351854, 0, 199965],
    [213113, 287, 99357],
    [1300249, 0, 499250],
    [13, 0, 5],
]

ZF_COEFFN = np.array(
    [
        [0.722222, 0.0, 0.277778],
        [0.722562, 0.0, 0.277438],
        [0.681401, 0.000918, 0.317681],
        [0.637626, 0.0, 0.362374],
        [0.619999, 0.0, 0.380001],
        [0.606456, 0.038305, 0.355239],
        [0.592959, 0.07648, 0.33056],
        [0.579508, 0.114527, 0.305965],
        [0.566101, 0.152446, 0.281452],
        [0.55274, 0.190237, 0.257022],
        [0.539424, 0.227902, 0.232674],
        [0.538917, 0.228534, 0.232549],
        [0.538318, 0.22928, 0.232402],
        [0.537599, 0.230175, 0.232226],
        [0.53672, 0.23127, 0.23201],
        [0.535621, 0.232638, 0.231741],
        [0.534208, 0.234398, 0.231395],
        [0.532325, 0.236743, 0.230932],
        [0.529686, 0.240029, 0.230285],
        [0.525727, 0.24496, 0.229313],
        [0.519126, 0.253182, 0.227692],
        [0.505907, 0.269642, 0.224451],
        [0.466135, 0.319173, 0.214692],
        [0.467005, 0.317873, 0.215122],
        [0.467875, 0.316573, 0.215552],
        [0.468745, 0.315273, 0.215982],
        [0.469615, 0.313973, 0.216412],
        [0.470485, 0.312673, 0.216842],
        [0.471345, 0.311373, 0.217282],
        [0.472215, 0.310073, 0.217712],
        [0.473085, 0.308773, 0.218142],
        [0.473955, 0.307473, 0.218572],
        [0.474825, 0.306173, 0.219002],
        [0.471119, 0.315773, 0.213109],
        [0.467409, 0.325373, 0.207218],
        [0.463699, 0.334973, 0.201328],
        [0.459992, 0.344574, 0.195434],
        [0.456286, 0.354175, 0.189539],
        [0.452575, 0.363776, 0.183648],
        [0.448865, 0.373377, 0.177758],
        [0.445158, 0.38298, 0.171862],
        [0.441451, 0.392583, 0.165967],
        [0.43774, 0.402184, 0.160076],
        [0.434029, 0.411786, 0.154185],
        [0.430322, 0.42139, 0.148288],
        [0.427011, 0.42193, 0.151059],
        [0.423702, 0.422472, 0.153826],
        [0.420391, 0.423012, 0.156597],
        [0.417073, 0.423554, 0.159374],
        [0.413768, 0.424089, 0.162143],
        [0.410457, 0.424629, 0.164913],
        [0.407143, 0.425175, 0.167682],
        [0.403838, 0.425711, 0.17045],
        [0.400524, 0.426257, 0.173219],
        [0.397216, 0.426788, 0.175996],
        [0.393905, 0.427328, 0.178766],
        [0.390591, 0.427874, 0.181535],
        [0.387287, 0.42841, 0.184303],
        [0.383973, 0.428956, 0.187071],
        [0.380663, 0.429496, 0.189841],
        [0.377359, 0.430032, 0.19261],
        [0.374041, 0.430573, 0.195386],
        [0.370731, 0.431113, 0.198156],
        [0.367424, 0.431654, 0.200922],
        [0.364114, 0.432194, 0.203692],
        [0.366694, 0.445474, 0.187832],
        [0.369284, 0.458755, 0.171962],
        [0.371864, 0.472035, 0.156102],
        [0.374444, 0.485315, 0.140241],
        [0.377028, 0.4986, 0.124372],
        [0.379608, 0.51188, 0.108512],
        [0.382198, 0.525161, 0.092642],
        [0.384778, 0.538441, 0.076782],
        [0.388828, 0.533851, 0.077322],
        [0.392878, 0.529261, 0.077862],
        [0.396938, 0.52466, 0.078402],
        [0.400988, 0.52007, 0.078942],
        [0.405038, 0.51548, 0.079482],
        [0.399238, 0.49368, 0.107082],
        [0.393444, 0.471875, 0.134681],
        [0.387648, 0.450079, 0.162273],
        [0.381844, 0.428284, 0.189872],
        [0.376044, 0.406484, 0.217472],
        [0.370247, 0.384688, 0.245065],
        [0.364454, 0.362884, 0.272663],
        [0.358654, 0.341083, 0.300263],
        [0.356904, 0.343873, 0.299223],
        [0.355157, 0.346667, 0.298176],
        [0.353414, 0.349453, 0.297133],
        [0.351664, 0.352244, 0.296093],
        [0.349913, 0.355044, 0.295043],
        [0.348163, 0.357834, 0.294003],
        [0.346413, 0.360624, 0.292963],
        [0.34467, 0.36341, 0.29192],
        [0.342923, 0.366204, 0.290873],
        [0.341173, 0.368994, 0.289833],
        [0.343093, 0.366354, 0.290553],
        [0.345027, 0.363707, 0.291266],
        [0.346947, 0.361067, 0.291986],
        [0.348873, 0.358424, 0.292703],
        [0.350794, 0.355784, 0.293423],
        [0.352727, 0.353137, 0.294136],
        [0.354647, 0.350497, 0.294856],
        [0.351863, 0.353352, 0.294784],
        [0.348371, 0.356921, 0.294707],
        [0.343891, 0.361519, 0.29459],
        [0.337906, 0.367639, 0.294455],
        [0.329547, 0.376208, 0.294246],
        [0.3309, 0.377317, 0.291783],
        [0.331862, 0.37812, 0.290018],
        [0.332592, 0.378705, 0.288704],
        [0.333152, 0.379175, 0.287673],
        [0.333603, 0.379544, 0.286853],
        [0.334873, 0.378284, 0.286843],
        [0.336153, 0.377024, 0.286823],
        [0.337423, 0.375764, 0.286813],
        [0.338693, 0.374514, 0.286793],
        [0.339963, 0.373254, 0.286783],
        [0.34124, 0.37199, 0.28677],
        [0.342513, 0.370734, 0.286753],
        [0.343783, 0.369474, 0.286743],
        [0.345057, 0.368217, 0.286726],
        [0.346333, 0.366954, 0.286713],
        [0.347603, 0.365694, 0.286703],
        [0.348873, 0.364444, 0.286683],
        [0.350144, 0.363184, 0.286673],
        [0.351424, 0.361924, 0.286653],
        [0.352694, 0.360664, 0.286643],
        [0.352694, 0.360664, 0.286643],
        [0.351424, 0.361924, 0.286653],
        [0.350144, 0.363184, 0.286673],
        [0.348873, 0.364444, 0.286683],
        [0.347603, 0.365694, 0.286703],
        [0.346333, 0.366954, 0.286713],
        [0.345057, 0.368217, 0.286726],
        [0.343783, 0.369474, 0.286743],
        [0.342513, 0.370734, 0.286753],
        [0.34124, 0.37199, 0.28677],
        [0.339963, 0.373254, 0.286783],
        [0.338693, 0.374514, 0.286793],
        [0.337423, 0.375764, 0.286813],
        [0.336153, 0.377024, 0.286823],
        [0.334873, 0.378284, 0.286843],
        [0.333603, 0.379544, 0.286853],
        [0.333152, 0.379175, 0.287673],
        [0.332592, 0.378705, 0.288704],
        [0.331862, 0.37812, 0.290018],
        [0.3309, 0.377317, 0.291783],
        [0.329547, 0.376208, 0.294246],
        [0.337906, 0.367639, 0.294455],
        [0.343891, 0.361519, 0.29459],
        [0.348371, 0.356921, 0.294707],
        [0.351863, 0.353352, 0.294784],
        [0.354647, 0.350497, 0.294856],
        [0.352727, 0.353137, 0.294136],
        [0.350794, 0.355784, 0.293423],
        [0.348873, 0.358424, 0.292703],
        [0.346947, 0.361067, 0.291986],
        [0.345027, 0.363707, 0.291266],
        [0.343093, 0.366354, 0.290553],
        [0.341173, 0.368994, 0.289833],
        [0.342923, 0.366204, 0.290873],
        [0.34467, 0.36341, 0.29192],
        [0.346413, 0.360624, 0.292963],
        [0.348163, 0.357834, 0.294003],
        [0.349913, 0.355044, 0.295043],
        [0.351664, 0.352244, 0.296093],
        [0.353414, 0.349453, 0.297133],
        [0.355157, 0.346667, 0.298176],
        [0.356904, 0.343873, 0.299223],
        [0.358654, 0.341083, 0.300263],
        [0.364454, 0.362884, 0.272663],
        [0.370247, 0.384688, 0.245065],
        [0.376044, 0.406484, 0.217472],
        [0.381844, 0.428284, 0.189872],
        [0.387648, 0.450079, 0.162273],
        [0.393444, 0.471875, 0.134681],
        [0.399238, 0.49368, 0.107082],
        [0.405038, 0.51548, 0.079482],
        [0.400988, 0.52007, 0.078942],
        [0.396938, 0.52466, 0.078402],
        [0.392878, 0.529261, 0.077862],
        [0.388828, 0.533851, 0.077322],
        [0.384778, 0.538441, 0.076782],
        [0.382198, 0.525161, 0.092642],
        [0.379608, 0.51188, 0.108512],
        [0.377028, 0.4986, 0.124372],
        [0.374444, 0.485315, 0.140241],
        [0.371864, 0.472035, 0.156102],
        [0.369284, 0.458755, 0.171962],
        [0.366694, 0.445474, 0.187832],
        [0.364114, 0.432194, 0.203692],
        [0.367424, 0.431654, 0.200922],
        [0.370731, 0.431113, 0.198156],
        [0.374041, 0.430573, 0.195386],
        [0.377359, 0.430032, 0.19261],
        [0.380663, 0.429496, 0.189841],
        [0.383973, 0.428956, 0.187071],
        [0.387287, 0.42841, 0.184303],
        [0.390591, 0.427874, 0.181535],
        [0.393905, 0.427328, 0.178766],
        [0.397216, 0.426788, 0.175996],
        [0.400524, 0.426257, 0.173219],
        [0.403838, 0.425711, 0.17045],
        [0.407143, 0.425175, 0.167682],
        [0.410457, 0.424629, 0.164913],
        [0.413768, 0.424089, 0.162143],
        [0.417073, 0.423554, 0.159374],
        [0.420391, 0.423012, 0.156597],
        [0.423702, 0.422472, 0.153826],
        [0.427011, 0.42193, 0.151059],
        [0.430322, 0.42139, 0.148288],
        [0.434029, 0.411786, 0.154185],
        [0.43774, 0.402184, 0.160076],
        [0.441451, 0.392583, 0.165967],
        [0.445158, 0.38298, 0.171862],
        [0.448865, 0.373377, 0.177758],
        [0.452575, 0.363776, 0.183648],
        [0.456286, 0.354175, 0.189539],
        [0.459992, 0.344574, 0.195434],
        [0.463699, 0.334973, 0.201328],
        [0.467409, 0.325373, 0.207218],
        [0.471119, 0.315773, 0.213109],
        [0.474825, 0.306173, 0.219002],
        [0.473955, 0.307473, 0.218572],
        [0.473085, 0.308773, 0.218142],
        [0.472215, 0.310073, 0.217712],
        [0.471345, 0.311373, 0.217282],
        [0.470485, 0.312673, 0.216842],
        [0.469615, 0.313973, 0.216412],
        [0.468745, 0.315273, 0.215982],
        [0.467875, 0.316573, 0.215552],
        [0.467005, 0.317873, 0.215122],
        [0.466135, 0.319173, 0.214692],
        [0.505907, 0.269642, 0.224451],
        [0.519126, 0.253182, 0.227692],
        [0.525727, 0.24496, 0.229313],
        [0.529686, 0.240029, 0.230285],
        [0.532325, 0.236743, 0.230932],
        [0.534208, 0.234398, 0.231395],
        [0.535621, 0.232638, 0.231741],
        [0.53672, 0.23127, 0.23201],
        [0.537599, 0.230175, 0.232226],
        [0.538318, 0.22928, 0.232402],
        [0.538917, 0.228534, 0.232549],
        [0.539424, 0.227902, 0.232674],
        [0.55274, 0.190237, 0.257022],
        [0.566101, 0.152446, 0.281452],
        [0.579508, 0.114527, 0.305965],
        [0.592959, 0.07648, 0.33056],
        [0.606456, 0.038305, 0.355239],
        [0.619999, 0.0, 0.380001],
        [0.637626, 0.0, 0.362374],
        [0.681401, 0.000918, 0.317681],
        [0.722562, 0.0, 0.277438],
        [0.722222, 0.0, 0.277778],
    ]
).astype(np.float64)

# the perturbations for a given index proposed by Zhou and Fang, expanded
# and mirrored for all possible values
ZF_PERT = np.array(
    [
        0.00,
        0.01,
        0.02,
        0.02,
        0.03,
        0.04,
        0.05,
        0.05,
        0.06,
        0.07,
        0.08,
        0.09,
        0.09,
        0.10,
        0.11,
        0.12,
        0.12,
        0.13,
        0.14,
        0.15,
        0.15,
        0.16,
        0.17,
        0.18,
        0.19,
        0.19,
        0.20,
        0.21,
        0.22,
        0.22,
        0.23,
        0.24,
        0.25,
        0.26,
        0.26,
        0.27,
        0.28,
        0.29,
        0.29,
        0.30,
        0.31,
        0.32,
        0.32,
        0.33,
        0.34,
        0.35,
        0.36,
        0.36,
        0.37,
        0.38,
        0.39,
        0.40,
        0.40,
        0.41,
        0.42,
        0.43,
        0.44,
        0.44,
        0.45,
        0.46,
        0.47,
        0.48,
        0.48,
        0.49,
        0.50,
        0.52,
        0.55,
        0.57,
        0.60,
        0.62,
        0.64,
        0.67,
        0.69,
        0.71,
        0.74,
        0.76,
        0.79,
        0.81,
        0.83,
        0.86,
        0.88,
        0.90,
        0.93,
        0.95,
        0.98,
        1.00,
        0.92,
        0.83,
        0.75,
        0.67,
        0.59,
        0.50,
        0.42,
        0.34,
        0.25,
        0.17,
        0.22,
        0.26,
        0.31,
        0.36,
        0.41,
        0.45,
        0.50,
        0.54,
        0.58,
        0.62,
        0.66,
        0.70,
        0.72,
        0.74,
        0.75,
        0.77,
        0.79,
        0.80,
        0.82,
        0.83,
        0.85,
        0.86,
        0.87,
        0.89,
        0.90,
        0.92,
        0.93,
        0.94,
        0.96,
        0.97,
        0.99,
        1.00,
        1.00,
        0.99,
        0.97,
        0.96,
        0.94,
        0.93,
        0.92,
        0.90,
        0.89,
        0.87,
        0.86,
        0.85,
        0.83,
        0.82,
        0.80,
        0.79,
        0.77,
        0.75,
        0.74,
        0.72,
        0.70,
        0.66,
        0.62,
        0.58,
        0.54,
        0.50,
        0.45,
        0.41,
        0.36,
        0.31,
        0.26,
        0.22,
        0.17,
        0.25,
        0.34,
        0.42,
        0.50,
        0.59,
        0.67,
        0.75,
        0.83,
        0.92,
        1.00,
        0.98,
        0.95,
        0.93,
        0.90,
        0.88,
        0.86,
        0.83,
        0.81,
        0.79,
        0.76,
        0.74,
        0.71,
        0.69,
        0.67,
        0.64,
        0.62,
        0.60,
        0.57,
        0.55,
        0.52,
        0.50,
        0.49,
        0.48,
        0.48,
        0.47,
        0.46,
        0.45,
        0.44,
        0.44,
        0.43,
        0.42,
        0.41,
        0.40,
        0.40,
        0.39,
        0.38,
        0.37,
        0.36,
        0.36,
        0.35,
        0.34,
        0.33,
        0.32,
        0.32,
        0.31,
        0.30,
        0.29,
        0.29,
        0.28,
        0.27,
        0.26,
        0.26,
        0.25,
        0.24,
        0.23,
        0.22,
        0.22,
        0.21,
        0.20,
        0.19,
        0.19,
        0.18,
        0.17,
        0.16,
        0.15,
        0.15,
        0.14,
        0.13,
        0.12,
        0.12,
        0.11,
        0.10,
        0.09,
        0.09,
        0.08,
        0.07,
        0.06,
        0.05,
        0.05,
        0.04,
        0.03,
        0.02,
        0.02,
        0.01,
        0.00,
    ]
).astype(np.float64)
