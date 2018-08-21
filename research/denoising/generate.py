import cv2
import numpy as np
from data.steps.pipes.affine import AffineTransformation
from data.steps.pipes.convert import _cv2pil, _pil2cv2
from data.steps.pipes.warp import _warp
from lib.Configuration import Configuration


class PageHandwritingBlender(object):

    DEFAULTS = Configuration({
        "background": 255,
        "augmentation": {
            "line": {
                "scale": {
                    "prob": 1.0,
                    "center": -.25,
                    "stdv": 0.03
                }
            },
            "page": [
                {
                    'type': 'blur',
                    'prob': 0.5,
                    'kernel': (3, 3),
                    'sigma': 1
                },
                {
                    'type': 'sharpen',
                    'prob': 0.5,
                    'kernel': (3, 3),
                    'sigma': 1
                },
                {
                    'type': 'warp',
                    'prob': 0.5,
                    'config': {
                        'deviation': 2.7,
                        'gridsize': [100, 30]
                    }
                }
            ]
        },
        "filters": {
            'blur': lambda i, c: cv2.GaussianBlur(i, c['kernel'], c['sigma']),
            'sharpen': lambda i, c: PageHandwritingBlender._unsharp_mask_filter(i,  c['kernel'], c['sigma']),
            'warp': lambda i, c: PageHandwritingBlender._warp_filter(i, c['config']),
            'affine': lambda i, c: PageHandwritingBlender._affine_filter(i, c['config'])
        }
    })

    #################################
    # PUBLIC METHODS
    ###############################

    def __init__(self, page, config={}):
        self.page = page
        self.config = Configuration(config)
        self.truth = np.full(page.shape, self['background'])
        self._augment_page()

    def __call__(self, line):
        line = self._augment_line(line)
        h, w, _ = line.shape
        x, y = self._random_position(h, w)
        self._insert(line, x, y)

    def save(self, pagefile, truthfile):
        cv2.imwrite(pagefile, self.page)
        cv2.imwrite(truthfile, self.truth)

    def __getitem__(self, key):
        return self.config.default(key, self.DEFAULTS.default(key, None))

    ############################
    # PRIVATE METHODS
    ################################

    def _random_position(self, h, w):
        ph, pw, pc = self.page.shape

        def rand(mx):
            return int(np.random.uniform(0, mx+1))

        return rand(pw-w), rand(ph-h)

    def _insert(self, line, x, y):
        ph, pw, pc = self.page.shape
        lh, lw, lc = line.shape
        off_x = x if lw+x <= pw else x - (lw+x-pw)
        off_y = y if lh+y <= ph else y - (lh+y-ph)
        self.page[off_y:off_y+lh, off_x:off_x+lw, :] &= line
        self.truth[off_y:off_y+lh, off_x:off_x+lw, :] &= line

    def _augment_line(self, line):
        at = AffineTransformation(line)
        at.configure(self['augmentation.line'])
        return at(background=[self['background']]*3)

    def _augment_page(self):
        for _filter in self['augmentation.page']:
            if _filter['prob'] > np.random.rand():
                self.page = self['filters'][_filter['type']](
                    self.page, _filter)

    #######################################
    # STATIC METHODS
    #######################################

    @staticmethod
    def _affine_filter(image, config):
        at = AffineTransformation(image)
        at.configure(config)
        return at()

    @staticmethod
    def _warp_filter(image, config):
        image = _cv2pil(image, 'RGB')
        image = _warp(image, config['gridsize'], config['deviation'])
        return _pil2cv2(image, 'RGB')

    @staticmethod
    def _unsharp_mask_filter(image, kernel, sigma):
        gaussian_3 = cv2.GaussianBlur(image, kernel, sigma)
        return cv2.addWeighted(image, 1.5, gaussian_3, -0.5, 0, image)


page = cv2.imread("research/denoising/png/10.1.1.716.6158-0.png")
line = cv2.imread("research/denoising/lines/a01-000u-00.png")

hpg = PageHandwritingBlender(page)
hpg(line)
hpg.save("research/denoising/output/output_page.png",
         "research/denoising/output/output_truth.png")
