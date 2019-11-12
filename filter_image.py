# coding: utf-8

import sys
from os.path import exists, isfile
from os import mkdir
import collections
from PIL import Image
import time
import numpy as np


def has_transparency(image: Image) -> bool:
    return image.mode in ['RGBA', 'LA'] or (image.mode == 'P' and 'transparency' in image.info)


class KeyFlagInvokedMoreThanOnceError(Exception):
    """Raised when input or output flags are invoked more than once"""
    pass


class InvalidNumberOfArgumentsError(Exception):
    """Raised when input or output flags are invoked more than once"""
    pass


class InvalidFlipDirectionError(Exception):
    """Raised when a wrong value for flip filter is provided"""
    pass


class ImageWithoutTransparencyError(Exception):
    """Raised when an overlay image without transparency is provided"""
    pass


class InvalidOverlayCoordinatesError(Exception):
    """Raised when invalid coordinates where provided to overlay filter"""
    pass


class InvalidPILImageCreatedError(Exception):
    """Raised when the program cannot create a valid PIL Image from user input"""
    pass


class InvalidOutputFileExtensionProvidedError(Exception):
    """Raised when the program cannot identify a proper extension for the output file"""
    pass


class OutputFlagEvokedWithoutValueError(Exception):
    """Raised when the program finds the output flag but no value to match it"""
    pass


class InvalidCommandEvokedError(Exception):
    """Raised when the user calls a command that is not available in the command list"""
    pass


class InputParser:
    help_message = "-i or --input (required), arguments <path_to_original_image>. Example, -i input.jpg. " \
                   "If this flag is not specified, first argument will be looked at as a possible path.\n" \
                   "-f or --filter (optional), arguments <name_of_filter>, additional parameters possible separated " \
                   "by :, example --filter rotate:30 will rotate the input image 30 degrees\n" \
                   "-h or --help, will show this message with the available commands\n" \
                   "-o or --output (optional), arguments <path_to_output_image>, additional parameters possible " \
                   "separated by ':'. Example, -o ola:PNG will save the result in a PNG file called ola.png." \
                   " If this flag is omitted result will be saved in result.jpg"
    allowed_commands = {
        '-h': {'aliases': ['--help']},
        '-i': {'aliases': ['--input']},
        '-f': {'aliases': ['--filter']},
        '-o': {'aliases': ['--output']},
    }
    accepted_output_formats = ['png', 'jpg', 'jpeg']
    arguments = None

    def __init__(self, untreated_arguments: list):
        self.requested_operation = self.translate(arguments=untreated_arguments)

    def get_input_image(self):
        if '-i' in self.arguments:
            try:
                candidate = self.arguments[self.arguments.index('-i') + 1]
            except IndexError:
                candidate = ""
        else:
            # if no flag -i is found, the program assumes the first argument should be the image
            candidate = self.arguments[0]

        if exists(candidate) and isfile(candidate):
            try:
                return Image.open(candidate)
            except OSError:
                raise InvalidPILImageCreatedError('No proper input image was given. Run with'
                                                  ' -h or --help flag for list of available commands.')
        else:
            return candidate

    def get_filters_to_apply(self):
        requested_filters = []
        for index, arg in enumerate(self.arguments):
            if arg == '-f':
                try:
                    value = self.arguments[index + 1]
                    if value and not value.startswith('-'):
                        requested_filters.append(value)
                except IndexError:
                    pass
        return requested_filters

    def get_output_image_name(self):
        if '-o' in self.arguments:
            try:
                name = self.arguments[self.arguments.index('-o') + 1]
                if ":" in name:
                    parts = name.split(':')
                    name = parts[0]
                    file_format = parts[1].lower()

                    if '.' in name:
                        name_parts = name.split('.')

                        if name_parts[-1] in self.accepted_output_formats:
                            name_parts.pop(-1)

                        output_filename = "_".join([part.strip() for part in name_parts])
                    else:
                        output_filename = name

                else:
                    if '.' in name:
                        name_parts = name.split('.')
                        file_format = name_parts.pop(-1)
                        output_filename = "_".join([part.strip() for part in name_parts])
                    else:
                        raise InvalidOutputFileExtensionProvidedError('Invalid output file extension error:'
                                                                      ' no extension provided')

                if file_format not in self.accepted_output_formats:
                    raise InvalidOutputFileExtensionProvidedError('Invalid output file extension error: provided '
                                                                  'extension not acceptable, provide jpg or png')

                output_filename += "." + file_format
                return output_filename

            except IndexError as e:
                raise OutputFlagEvokedWithoutValueError(str(e) + '. No output value was given but -o flag was evoked.')
        else:
            return 'result_' + str(int(time.time())) + '.jpg'

    def translate(self, arguments: list):
        if not arguments:
            raise InvalidNumberOfArgumentsError('Invalid number of arguments.\n' + self.help_message)

        for key, values in self.allowed_commands.items():
            aliases = values.get('aliases', [])
            # for all aliases replace them by their original
            for alias in aliases:
                while alias in arguments:
                    arguments[arguments.index(alias)] = key

        self.arguments = arguments

        # if help is requested, discard all others and present help text
        if '-h' in self.arguments:
            print(self.help_message)
            sys.exit(-1)

        counter = collections.Counter(self.arguments)
        if counter.get('-i', 0) > 1:
            raise KeyFlagInvokedMoreThanOnceError('Input flag evoked more than once. Please check your arguments')
        if counter.get('-o', 0) > 1:
            raise KeyFlagInvokedMoreThanOnceError('Output flag evoked more than once. Please check your arguments')

        # looking for invalid commands
        invalid = [arg for arg in self.arguments if arg.startswith('-') and arg not in self.allowed_commands.keys()]
        if invalid:
            raise InvalidCommandEvokedError('Invalid command ' + invalid[0] + '. Run with -h or --help '
                                                                              'flag for list of available commands.')

        return {
            'input': self.get_input_image(),
            'filters': self.get_filters_to_apply(),
            'output': self.get_output_image_name()
        }


class ImageWorker:

    def __init__(self, operation: dict):
        self.original_image = operation.get('input', None)
        self.filters_to_apply = operation.get('filters', [])
        self.output = operation.get('output')

    @staticmethod
    def rotate(image: Image, angle: str = '45', expand: str = "false", center: str = None) -> Image:
        try:
            angle = float(angle)
        except ValueError:
            raise ValueError('Invalid angle provided for filter rotate: "' + angle + '"')
        expd = True if str(expand).lower() in ['true', '1', 'yes'] else False

        if center and ',' in center:
            try:
                coords = [float(part) for part in center.split(',')][:2]
            except ValueError:
                raise ValueError('Invalid center coordinate values given for '
                                 'filter rotate: "' + center + '", please provide two numbers.')
        else:
            coords = None
        return image.rotate(angle=angle, expand=expd, center=coords)

    @staticmethod
    def flip(image: Image, direction: str = "horizontal") -> Image:
        if not isinstance(direction, str):
            direction = str(direction)
        if direction.lower() not in ['vertical', 'v', 'horizontal', 'h']:
            raise InvalidFlipDirectionError('Invalid direction provided for flip method: "' + direction + '"')
        return image.transpose(
            Image.FLIP_TOP_BOTTOM if direction.lower() in ['v', 'vertical'] else Image.FLIP_LEFT_RIGHT)

    @staticmethod
    def gray_scale(image: Image) -> Image:
        return image.convert('L')

    @staticmethod
    def black_and_white(image: Image, threshold: str = '150') -> Image:
        try:
            th = int(threshold)
        except ValueError:
            raise ValueError('Invalid threshold provided for filter '
                             'black_and_white: "' + threshold + '", please provide an int number')
        if th < 0:
            th = 0
        if th > 255:
            th = 255
        return image.convert('L').point(lambda x: 255 if x >= th else 0, mode='1')

    @staticmethod
    def resize(image: Image, new_width: str, new_height: str = None) -> Image:
        try:
            nw = int(new_width)
        except ValueError:
            raise ValueError('Invalid new width provided '
                             'for filter resize: "' + new_width + '", please provide an int number.')

        if not new_height:
            new_size = (nw, int(nw * image.size[1] / image.size[0]))
        else:
            try:
                nh = int(new_height)
                new_size = (nw, nh)
            except ValueError:
                raise ValueError('Invalid new height provided for filter resize: "'
                                 '' + new_height + '", please provide an int number.')

        return image.resize(new_size, Image.LANCZOS)

    @staticmethod
    def sepia(image: Image, ratio: str = None) -> Image:
        # got this one from here https://yabirgb.com/blog/creating-a-sepia-filter-with-python/ and adapted
        if not ratio:
            ratio = 1.0
        try:
            r = float(ratio)
        except ValueError:
            raise ValueError('Invalid ratio provided for filter sepia: "' + ratio + '"')

        if r < 0:
            r = 0.0
        if r > 1:
            r = 1.0

        np_image = np.array(image)
        matrix = [[0.393 + 0.607 * (1 - r), 0.769 - 0.769 * (1 - r), 0.189 - 0.189 * (1 - r)],
                  [0.349 - 0.349 * (1 - r), 0.686 + 0.314 * (1 - r), 0.168 - 0.168 * (1 - r)],
                  [0.272 - 0.349 * (1 - r), 0.534 - 0.534 * (1 - r), 0.131 + 0.869 * (1 - r)]]

        s_map = np.matrix(matrix)
        filtered = np.array([x * s_map.T for x in np_image])
        filtered[np.where(filtered > 255)] = 255
        return Image.fromarray(filtered.astype('uint8'))

    @staticmethod
    def overlay(image: Image, foreground_path: str, coordinates: str = None) -> Image:
        if exists(foreground_path) and isfile(foreground_path):
            try:
                foreground = Image.open(foreground_path)
            except OSError:
                raise Exception('No proper overlay image was given. Make sure you are providing a png '
                                'image file with transparency.')

            if has_transparency(foreground):
                fg_image_trans = Image.new('RGBA', image.size)
                if not coordinates:
                    # defaults to top left
                    coords = [0, 0]
                else:
                    if ',' in coordinates:
                        try:
                            coords = [int(part) for part in coordinates.split(',')][:2]
                            if coords[0] >= image.size[0] - foreground.size[0] * 0.5:
                                coords[0] = image.size[0] - foreground.size[0]
                            if coords[1] >= image.size[1] - foreground.size[1] * 0.5:
                                coords[1] = image.size[1] - foreground.size[1]
                        except Exception as e:
                            raise InvalidOverlayCoordinatesError(str(e) + '. Invalid coordinates provided, write 2 '
                                                                          'numbers separated by comma, like "100,200"')
                    else:
                        raise InvalidOverlayCoordinatesError('Invalid coordinates provided, write 2 numbers separated '
                                                             'by comma, like "100,200"')
                fg_image_trans.paste(foreground, coords, mask=foreground.convert('RGBA'))
                return Image.alpha_composite(image.convert('RGBA'), fg_image_trans).convert('RGB')
            else:
                raise ImageWithoutTransparencyError('The image provided for the overlay does not have transparency. '
                                                    'Please use an image with transparency to use this filter.')
        else:
            raise FileNotFoundError('Provided overlay path does not represent a path for an existing file')

    def run(self):
        if not self.original_image or isinstance(self.original_image, str):
            raise InvalidPILImageCreatedError('The image provided does not exist or is invalid.')

        result_image = self.original_image
        for fta in self.filters_to_apply:
            fields = fta.split(':')
            filter_name = fields[0]
            parameters = [result_image] + fields[1:]

            if hasattr(self, filter_name):
                try:
                    result_image = getattr(self, filter_name)(*parameters)
                except TypeError:
                    print('Invalid number of arguments passed to filter "' + filter_name + '". \
                    Program will skip applying this filter to the resulting image.')
            else:
                print(filter_name + ' is not implemented (yet!)')

        result_image.show()
        if not exists('results'):
            mkdir('results')
        result_image.save('results/' + self.output)


if __name__ == '__main__':
    parser = InputParser(untreated_arguments=sys.argv[1:])
    ImageWorker(operation=parser.requested_operation).run()
