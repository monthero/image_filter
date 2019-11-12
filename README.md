# Image filtering using Pillow

This is an exercise intended to create a command line tool to apply 1 or more filters to an image.

#### Requirements
python 3.5+

```shell script
pip install numpy==1.17.4
pip install Pillow==6.2.1
```
or
```shell script
pip install -r requirements.txt
```

#### Example of usage
```shell script
(venv) python filter_image.py -i <path_to_input_image> -f gray_scale -o output:PNG
```

#### Available commands and rules
* -i or --input, expects a valid image as input. If this flag is not specified, the script will try the first argument as a possible image path. Example `filter_image.py example.jpg -f rotate:45` will work but `filter_image.py -f gray_scale example.jpg` won't;

* -h or --help, shows the list of available commands;

* -o or --output (optional argument), you can choose the name of the output/resulting image by giving it a path and, optionally, a format which should be either PNG or JPG.
Examples: `filter_image.py input.jpg -o result.png -f rotate:45` or `filter_image.py -f gray_scale -o result:JPG -f overlay:python.png -i input.jpg -f rotate:90`. If this tag is not specified, the resulting image will be saved in results/result_<current_time_stamp>.jpg

* -f or --filter, you can have as many of these tags as you want, knowing that the order in which you write them is the order in which they'll be applied to the original image. Every filter you want/need to apply most be preceded by a `-f` or `--filter` tag.

#### Available filters
Applying the filters, it is important to understand the arguments that are mandatory and the ones that are not. Also, the order of the arguments is strict, otherwise the filter will not recognize the argument and will be skipped in the execution.
* **gray_scale**, converts the input image to gray scale mode, no extra arguments.
    ```shell script
    -f gray_scale
    ```

* **rotate**, rotates the input image in the given angle. Arguments:
    - angle, [number, optional, default=45]: Defines the angle of rotation (in degrees). Examples: 45, 220.25, -30.75
    - expand, [string, optional, default=false]: Tells the program if it should resize the image to make sure the rotation is not cropped. If you want this to happen make sure to write either 1, yes or true (case insensitive), else it will be considered false
    - center, [string, optional, default=none]: If omitted, the rotation will happen in the center of the picture (normal behaviour). To specify a different center specify a string with two int number separated by a comma, like "100,500"
    ```shell script
    -f rotate # will rotate the default 45 degrees
    -f rotate:45 # will rotate 45 degrees because it was specified
    -f rotate:45:yes # will rotate 45 degrees and expand the image to avoid cropping
    -f rotate:45:1 # will rotate 45 degrees and expand the image to avoid cropping
    -f rotate:45:true # will rotate 45 degrees and expand the image to avoid cropping
    -f rotate:45:<anything_else> # will rotate 45 degrees and NOT expand the image, resulting in image cropping
    -f rotate:45:false:100,450 # will rotate 45 degrees and expand the image to avoid cropping and rotate the image based on the new specified center in the coordinates (100, 450)
    ```
* **flip**, flips the image in an axis. Arguments:
    - direction, [string, optional, default=horizontal]: Defines the axis on which the flip will occur. Values: "horizontal" or "vertical"
    ```shell script
    -f flip # will flip the image from left to right
    -f flip:h # will flip the image from left to right
    -f flip:horizontal # will flip the image from left to right
    -f flip:v # will flip the image from top to bottom (upside down)
    -f flip:vertical # will flip the image from top to bottom (upside down)
    
    -f flip:<any other thing> # will fail
    ```
  
* **sepia**, applies a sepia filter to the image. Arguments:
    - ratio, [number, optional, default=1.0]: Defines the percentage, expressed from 0 to 1, of the strength of the sepia filter to be applied to the image.
    ```shell script
    -f sepia # will apply sepia filter with total strength
    -f sepia:0.25 # will apply sepia filter with 25% strength
    -f sepia:-1 # will convert ratio to 0
    -f sepia:1.2 # will convert ratio to 1
  
    -f sepia:ola # will fail
    ```
   
* **black_and_white**, converts the image into a bit map, considering the threshold. Arguments:
    - threshold, [number, optional, default=150]: Defines the threshold to decided what is converted to black and what is converted to white. Expecting an int number between 0 and 255
    ```shell script
    -f black_and_white # will create a bit map where the pixels that are above 150 (default value) will be white and the rest will be black
    -f black_and_white:200 # will create a bit map where the pixels that are above 200 will be white and the rest will be black
    -f black_and_white:-100 # will convert threshold to 0, the whole image will be black
    -f black_and_white:300 # will convert threshold to 255, the whole image will be white
  
    -f black_and_white:ola # will fail
    -f black_and_white:200.05 # will fail
    ```
  
* **resize**, resizes input image with the given dimensions. Arguments:
    - new_width, [number]: Int number for the desired new width of the resulting image
    - new_height, [number, optional, default=proportion]: Int number for the new height. If this field is omitted, the value for the new height will be a calculated from "new width" to keep the image's proportions
    ```shell script
    -f resize:500 # will resize the image to 500 pixels wide and a proportional height
    -f resize:500:300 # will resize the image to 500 pixels wide and 300 pixels high
  
    -f resize:250.95 # will fail
    -f resize:100:50.25 # will fail
    -f resize:100:gibberish # will fail
    -f resize # will fail
    ```
* **overlay**, applies an image with transparency over the original image. Arguments:
    - path_to_overlay_image, [string]: Path to an image that has transparency (example, png or gif). If overlay image does not have transparency it will fail
    - coordinates, [string, optional, default=0,0]: The anchor in the original image where the program will place the overlay. Defaults to top left corner in the coordinate (0, 0). To work, this field expects to int numbers separated by a comma, like "100,400". If any of the coordinates exceeds the dimensions of the original image, they are adjusted to the very max limit to fit the image
    ```shell script
    -f overlay:<path_to_overlay_image> # will fail if image does not have transparency, else will apply the overlay with the anchor 0,0 (top left corner of the original)
    -f overlay:python.png:100,400
    
    -f overlay:python.png:100,AAA # will fail
    -f overlay:python.png:BBB,1000 # will fail
    -f overlay:<every thing that is not a valid path to an image> # will fail
    -f overlay # will fail
    ```