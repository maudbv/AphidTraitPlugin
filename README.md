# AphidTraitPlugin
by Maud Bernard-Verdier, March 2021

**ImageJ Plugin** in Jython for streamlined measurements of aphid traits on microscopic photography.
 
The plugin creates a small user interface to select images, measure length of body parts, store results and open next image efficiently.
It is not generic at this stage, and designed for use in my lab, but could easily be adapted.

<img width="440" alt="Screen Shot 2021-03-25 at 09 59 28" src="https://user-images.githubusercontent.com/6454302/112447006-1b034a80-8d51-11eb-8a7b-0dc2c042445c.png">

## Manual:

### The first time:
- launch FIJI
- menu plugin > install... > select the file: AphidTraitPlugin.py
- it will ask you where to save it within the Fiji library of folders. Save it in the “plugins” folder to find it easily.
- restart Fiji
- you should be able to see the plugin name in the “plugins” menu (probably at the bottom of the list)

### Each time you want to use it:
1) launch plugin from the menu
2) select you main directory
3) in the next window: make sure the three sub-folders in the main directory are correctly identified (i.e.  [...]/images, [...]/results,[...]/measured images) 
4) new window: select the kind of picture you will work with (e.g. "dorsal" views). The “log” window will tell you how many photos of that type were found.
5) new window: select the first picture you want to open in the list (usually the first in the list, but if you ave already measured the first 15 ones, then start at the 16th: you can either select it by file name, or by number in the list)
6) the plugin is launched with the first pic opened automatically.
7) arrange the picture with the "zoom” and/or “hand” fiji tool so you can see well. You can add extra guiding lines (not to be measured), and then menu Image>Overlay>add to overlay: this will draw the line on the image, but it wont be added to the ROIs.
8) select the “line tool” and draw the first ROI (a line element). 
9) when you are happy with it, click “add selected” and choose the type of trait it is.
10) continue until you have all the trait measurements you want. If you need to edit the ROIs by hand (e.g. rename them, delete them), you can do it using the ROI manager buttons. For instance, if one leg is broken in two parts, then you can measure 2 lines, and give them a special name like: "femur_length_1_partA" and “femur_length_1_partB”. You will be able to add them up later in R.
11) click “Measure all” => you will see all the measurements in a new “Results window”

<img width="1148" alt="Screen Shot 2021-03-25 at 10 01 04" src="https://user-images.githubusercontent.com/6454302/112447066-2e161a80-8d51-11eb-94c3-efdeb71ab322.png">

13) if you are happy, click “save results”: this will close the image and save the results. New files should be written in the "results" and "measured images" folders.
14) clear selection (it erases all the ROIs, or else they get transferred to the next picture) - this is also useful if you want to restart on the same picture. you can also erase the measurements in the “result” window by selecting a line and clicking "backspace" on your keyboard.
15) exit when you are done
