# coding: utf-8

import unittest
from PIL import Image
from filter_image import (ImageWorker, InvalidFlipDirectionError, InvalidOverlayCoordinatesError)
import numpy as np


class ImageFilterTests(unittest.TestCase):

    def setUp(self):
        self.worker = ImageWorker(operation={
            'input': Image.open('input.jpg'),
            'output': 'results/result.jpg',
            'filters': ['sepia', 'overlay:python.png', 'flip:horizontal']
        })

    def test_gray_scale(self):
        img = self.worker.original_image
        result = self.worker.gray_scale(image=img)
        self.assertEqual(len(result.split()), 1, "Should only have one channel")
        self.assertIsInstance(result, Image.Image, "Should result in PIL Image type")

    def test_black_and_white_default_threshold(self):
        img = self.worker.original_image
        result = self.worker.black_and_white(image=img)
        self.assertEqual(result.getextrema(), (0, 255), "Should only have binary values, either 0 or 255")
        self.assertEqual(len(result.split()), 1, "Should only have one channel")
        self.assertIsInstance(result, Image.Image, "Should result in PIL Image type")

    def test_black_and_white_with_valid_threshold(self):
        img = self.worker.original_image
        result = self.worker.black_and_white(image=img, threshold="200")
        self.assertEqual(result.getextrema(), (0, 255), "Should only have binary values, either 0 or 255")
        self.assertEqual(len(result.split()), 1, "Should only have one channel")
        self.assertIsInstance(result, Image.Image, "Should result in PIL Image type")

    def test_black_and_white_with_invalid_threshold(self):
        img = self.worker.original_image
        threshold = "AAA"
        with self.assertRaises(ValueError):
            result = self.worker.black_and_white(image=img, threshold=threshold)

    def test_flip_without_argument(self):
        img = self.worker.original_image
        result = self.worker.flip(image=img)
        self.assertTrue(np.array_equal(np.array(result), np.flip(np.array(img), 1)))
        self.assertIsInstance(result, Image.Image, "Should result in PIL Image type")

    def test_flip_vertical(self):
        img = self.worker.original_image
        result = self.worker.flip(image=img, direction='vertical')
        self.assertTrue(np.array_equal(np.array(result), np.flip(np.array(img), 0)))
        self.assertIsInstance(result, Image.Image, "Should result in PIL Image type")

    def test_flip_invalid_direction(self):
        with self.assertRaises(InvalidFlipDirectionError):
            self.worker.flip(self.worker.original_image, direction='nowhere')
            self.worker.flip(self.worker.original_image, direction=[1, 2, 'a'])
            self.worker.flip(self.worker.original_image, direction=-100)

    def test_resize(self):
        new_width = "200"
        img = self.worker.original_image
        result = self.worker.resize(image=img, new_width=new_width)
        self.assertEqual(result.size, (int(new_width), int(int(new_width) * img.size[1] / img.size[0])))
        self.assertIsInstance(result, Image.Image, "Should result in PIL Image type")

    def test_resize_with_given_height(self):
        new_width = 200
        new_height = 300
        img = self.worker.original_image
        result = self.worker.resize(image=img, new_width=new_width, new_height=new_height)
        self.assertEqual(result.size, (200, 300))
        self.assertIsInstance(result, Image.Image, "Should result in PIL Image type")

    def test_resize_with_invalid_input(self):
        img = self.worker.original_image
        with self.assertRaises(ValueError):
            self.worker.resize(image=img, new_width="ola", new_height=100)
            self.worker.resize(image=img, new_width=False, new_height="nothing")

    def test_sepia(self):
        result = self.worker.sepia(image=self.worker.original_image)
        # there is no easy way to test if output is in sepia
        self.assertIsInstance(result, Image.Image, "Should result in PIL Image type")

    def test_sepia_invalid_ratio(self):
        img = self.worker.original_image
        with self.assertRaises(ValueError):
            self.worker.sepia(image=img, ratio="AAA")
            self.worker.sepia(image=img, ratio=['things', 'and', 23, 'situations'])
            self.worker.sepia(image=img, ratio={'key': 'value'})

    def test_rotate(self):
        img = self.worker.original_image
        self.assertIsInstance(self.worker.rotate(image=img), Image.Image, "Should result in PIL Image type")
        self.assertIsInstance(self.worker.rotate(image=img, expand=True), Image.Image,
                              "Should result in PIL Image type")
        self.assertIsInstance(self.worker.rotate(image=img, expand='true'), Image.Image,
                              "Should result in PIL Image type")
        self.assertIsInstance(self.worker.rotate(image=img, expand='tRuE'), Image.Image,
                              "Should result in PIL Image type")
        self.assertIsInstance(self.worker.rotate(image=img, expand='yEs'), Image.Image,
                              "Should result in PIL Image type")
        self.assertIsInstance(self.worker.rotate(image=img, expand='1'), Image.Image,
                              "Should result in PIL Image type")
        self.assertIsInstance(self.worker.rotate(image=img, expand=1), Image.Image,
                              "Should result in PIL Image type")
        self.assertIsInstance(self.worker.rotate(image=img, center="1,1"), Image.Image,
                              "Should result in PIL Image type")
        self.assertIsInstance(self.worker.rotate(image=img, center=(1, 2)), Image.Image,
                              "Should result in PIL Image type")

    def test_rotate_with_invalid_coordinates(self):
        img = self.worker.original_image
        with self.assertRaises(ValueError):
            self.worker.rotate(image=img, center="1,A")

        with self.assertRaises(TypeError):
            self.worker.rotate(image=img, center=1)
            self.worker.rotate(image=img, center=[1, 2, 4, 5])
            self.worker.rotate(image=img, center={'x': 12, 'y': 23})

    def test_overlay(self):
        img = self.worker.original_image
        overlay_path = 'python.png'

        self.assertIsInstance(self.worker.overlay(image=img, foreground_path=overlay_path), Image.Image,
                              "Should result in PIL Image type")
        self.assertIsInstance(self.worker.overlay(image=img, foreground_path=overlay_path, coordinates=None),
                              Image.Image, "Should result in PIL Image type")
        self.assertIsInstance(self.worker.overlay(image=img, foreground_path=overlay_path, coordinates="10,200"),
                              Image.Image, "Should result in PIL Image type")
        self.assertIsInstance(self.worker.overlay(image=img, foreground_path=overlay_path, coordinates=[]),
                              Image.Image, "Should result in PIL Image type")

        with self.assertRaises(InvalidOverlayCoordinatesError):
            self.worker.overlay(image=img, foreground_path=overlay_path, coordinates=(1, 20))
            self.worker.overlay(image=img, foreground_path=overlay_path, coordinates=100)
            self.worker.overlay(image=img, foreground_path=overlay_path, coordinates="AAA")
            self.worker.overlay(image=img, foreground_path=overlay_path, coordinates=[1, 45])


if __name__ == '__main__':
    unittest.main()
