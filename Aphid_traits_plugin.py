"""
ImageJ plugin to measure Aphid traits on microscopic photos
written in Jython
by maud bernard-verdier, March 2021
"""

###____________  Load classes ____________###

# General utilities
import os, sys
from os import path

# Image J specific
from ij import IJ, WindowManager as WM
from ij.io import FileSaver
from ij.gui import Roi
from ij.plugin.frame import RoiManager

from ij.measure.Measurements import *
from ij.plugin.filter import Analyzer
from ij.measure import ResultsTable as RT

# IJ user interface
from ij.io import DirectoryChooser
from ij.gui import GenericDialog
from ij.io import SaveDialog
from fiji.util.gui import GenericDialogPlus

# Java user interface
from javax.swing import JFrame, JButton, JOptionPane
from java.awt import GridLayout

###___________________ SET IMAGEJ OPTIONS _________________________________ ###

# # label the ROI and add to image
# options = LABELS + ADD_TO_OVERLAY
# # see https://imagej.nih.gov/ij/developer/api/ij/measure/Measurements.html
# # Measure only the length of the ROI (= lines)
# Analyzer.setMeasurements(options)



###___________________ MAIN PLUGIN function _______________________________ ###

def runScript():
	""" script asks to choose directories, then loads a user interface,
	with buttons to streamline image opening, measurements, and saving """

		###_________ DEFINE FUNCTIONS for the plugin _____________________ ###



	##### FUNCTION Choose source directory ##########
	def getDirectories():
		""" opens a default directory and asks user to select a root directory
		for the analysis: three sub-folders are then automatically selected,
		but can be modified by user """

		dc = DirectoryChooser("/Users/maud/Documents/Work/Postdoc Berlin local/data BIBS/insects/aphids 2020/Data/ImageJ data")
		root_path = dc.getDirectory()

		if root_path is None:
			IJ.log("User cancelled dialog. Exiting...")
			return

		gdp = GenericDialogPlus("Choose folders...")
		gdp.addDirectoryField("Folder of original images", root_path + "images/")
		gdp.addDirectoryField("Folder to save results", root_path + "results/")
		gdp.addDirectoryField("Folder to save measured images", root_path + "measured images/")
		gdp.showDialog()

		if gdp.wasCanceled():
			IJ.log("User cancelled dialog. Exiting...")
			return

		dir1 = gdp.getNextString()
		dir2 = gdp.getNextString()
		dir3 = gdp.getNextString()
		return dir1, dir2, dir3

	#####  FUNCTION: DEFINE category of photo ############
	def getPhotoCategory(categories):
		""" asks user to select the type of microscopic photos to select """

		gd = GenericDialog("Select photos")
		gd.addChoice("choose the type of photos for today", categories, categories[0])
		gd.showDialog()

		if gd.wasCanceled():
			print "User canceled dialog!"
			return None

		# Read out the options
		photo_cat = gd.getNextChoice()
		return photo_cat # a tuple with the parameters

	##### FUNCTION List all image file paths #######
	def listPaths(directory, label):
		"""" returns a list of paths to all the files in a given directory
		whose name contains a certain string pattern defined by label """
		path_list = []
		filename_list = []
		walkList = os.walk(directory)
		# For loop in recursive walklist
		for root, directories, filenames in walkList:
			for filename in filenames:
				# search for the file label:
				ind = filename.find(label)
				if ind > -1 :
					path_list.append(os.path.join(root, filename))
					filename_list.append(filename)
					print filename
				else :
					continue
		return (path_list, filename_list) # a tupple


	##### FUNCTION List all image file paths #######
	def choosePhotoIndex(file_list):
		"""" selects the index of an image in the list of files """
		gdp = GenericDialogPlus("Choose starting picture")
		gdp.addMessage("Select the name of the image to open," +
		" OR the number of the image in the list if known:")
		gdp.addChoice("file name:", file_list, None)
		gdp.addNumericField("OR file number", 0 , 0)
		gdp.showDialog()

		if gdp.wasCanceled():
			IJ.log("User cancelled dialog. Exiting...")
			return

		new_counter = gdp.getNextChoiceIndex()
		if new_counter is None:
			new_counter = gdp.getNextNumber()
		return new_counter

	##### FUNCTION: OPEN IMAGE from path list ##########
	def openImageIndex(index, paths):

		""" Open image corresponding to a certain index in the list of paths
		returns "none" if index is larger than or equal to length of list """

		if len(paths) > index:
			image_path =  paths[index]
			print "Opening image:", image_path
			IJ.open(paths[index])
		else:
			print "No more valid image paths"
			return None

	#####  FUNCTION: user defined TRAIT label ############
	def getTraitLabel(types):
		""" ask user input to select the aphid trait name
		which will be used as label in the results
		return trait label as a string """
		gd = GenericDialog("Options")
		gd.addChoice("Choose trait label", types, types[0])
		gd.showDialog()

		if gd.wasCanceled():
			print "User canceled dialog!"
			return None

		label = gd.getNextChoice()
		return label

	##### FUNCTION save file safely  NOT USED ##########
	# def safelySave(name_object, folder, ext):
	# 	""" check if filename exists, add number if it does"""
	# 	fs = FileSaver(name_object)
	#
	# 	# Test if the folder exists before attempting to save the image:
	# 	if path.exists(folder) and path.isdir(folder):
	# 		print "folder exists:", folder
	# 		filepath = path.join(folder,name_object, ext) # Operating System-specific
	#
	# 		# Modify version name if name already exists
	# 		i = 1
	# 		while path.exists(filepath):
	# 			print "File exists! adding number"
	# 			filepath = path.join(folder,name_object + "_version"+ i + ext)
	# 			i = i + 1
	#
	# 		# save with the unique file name
	# 		fs.saveAs(filepath)
	# 		print "File saved successfully at ", filepath
	#
	# 	else:
	# 		print "Folder does not exist or it's not a folder!"

	############# EVENT FUNCTION 1 : choose another trait label: ############
	### DOES NOT WORK: DOES NOT MODIFY THE GLOBAL VARIABLE TRAIT _ don't know why
	# def chooseTrait(event):
	# 	""" Event: open dialog for choosing trait label
	# 	returns the chosen trait label as a string """
	# 	global trait
	# 	trait = getTraitLabel(trait_types)
	#
	# 	IJ.log("Trait selected for measurement:" + trait)

	############# EVENT FUNCTION 2: for selecting and labelling ROI
	def select(event):
	  """ Select lines or arrows defined by user and add them to ROI Manager """

	  # Select the trait label
	  global trait
	  trait = getTraitLabel(trait_types)
	  IJ.log("Trait selected for measurement:" + trait)

	  imp = WM.getCurrentImage()

	  if imp:
		# get the ROI manager
		rm = RoiManager().getInstance()

		#count number of ROI
		n = rm.getCount()

		# Add the new ROI
		roi1 = imp.getRoi()
		rm.addRoi(roi1)

		# create name with repetition number (=index + 1)
		name = trait + "_" + str(n + 1)


		rm.select(n)
		rm.runCommand("Rename", name)
		IJ.log("Element " + name + " was added")

	  else:
	    IJ.log("Error: Open an image first")

	############# EVENT FUNCTION 3: Measure
	def measure(event):
		""" measure length of all elements in ROI manager """

		imp = WM.getCurrentImage()
		# get the ROI manager
		rm = RoiManager().getInstance()
		rm.runCommand("show all with labels")
		# Label rois using names does not work...
		#rm.runCommand("Labels...", "font=12 show draw use")

		#count number of ROI
		n = rm.getCount()
		IJ.log(str(n) + "elements selected were measured")

		#select all ROI
		rm.setSelectedIndexes(range(n))
		rm.runCommand("Measure")

	############# EVENT FUNCTION 4: to clear ROI
	def clearROI(event):
		""" Delete all elements in the ROI manager """
		imp = WM.getCurrentImage()
		# clear all ROIs
		rm = RoiManager().getInstance()
		n = rm.getCount()
		rm.setSelectedIndexes(range(n))
		rm.runCommand("Delete")
		rm.runCommand("Show None")

	############# EVENT FUNCTION 5: to save measurements table
	def save(event):
		""" save result table in a text file and close window """
		imp = WM.getCurrentImage()

		results_filepath =  result_directory + imp.title + ".txt"
		measured_image_filepath = measured_directory + imp.title

		IJ.selectWindow("Results")
		IJ.saveAs("Results", results_filepath)
		IJ.log( "Results were saved at:" + results_filepath)
		IJ.run("Close")

		imp2 = imp.flatten()
		imp.close()
		IJ.saveAs(imp2, "Jpeg",measured_image_filepath)
		IJ.log( "Modified image was saved:" + measured_image_filepath)
		imp2.close()

	############# EVENT FUNCTION 6: OPEN Next IMAGE + ADD to counter
	def openNext(event):
		""" Click opens the next image in the list of files
		based on the counter value"""

		global counter
		counter = counter + 1
		print "Count is now: ", counter

		imp = WM.getCurrentImage()
		if imp is not None:
			imp.close()

		openImageIndex(counter, image_paths)

	############# EVENT FUNCTION 7: Reset starting image
	def openChoice(event):
		""" click opens UI to select which photo to open,
		and reset the counter """
		global counter  # This updates the counter globally
		print(image_paths)
		# Choose a starting image
		start_index = choosePhotoIndex(image_names)

		# Update the counter to start where we want
		counter = start_index
		print "New start at:", counter

		# Open image corresponding to counter
		openImageIndex(counter, image_paths)

	############# EVENT FUNCTION 8: EXIT
	def exitScript(event):
		""" closes all windows and logs the index of the last opened image """
		global running
		IJ.log("Last image was number:"+ str(counter))
		rm = RoiManager().getInstance()
		rm.close()
		IJ.run("Close All", "")
		IJ.log("Exiting plugin...")
		#sys.exit() # closes ImageJ
		frame.dispose()
		running = 1

	#_____________________RUNNING Plugin : ___________________________________#

	# 1. Select directories
	dir_paths = getDirectories()
	if dir_paths is not None:
	    source_directory, result_directory, measured_directory = dir_paths
	else:
		IJ.log("Selection cancelled. Exiting plugin...")
		return

	# 2. Select category of pictures
	photoCategories = ["dorsal", "right antenna", "left leg","ventral","mouthpart",
	"left antenna","right leg","ocular tubercles"]

	photo_label =  getPhotoCategory(photoCategories)
	if photo_label is not None:
		photo_cat = photo_label
		IJ.log("Category of photos selected: " + photo_label)
	else:
		IJ.log("Selection cancelled. Exiting plugin...")
		return

	# 3. List all image file paths
	paths = listPaths(source_directory, photo_label)
	image_paths = paths[0]
	image_names = paths[1]

	nb = len(image_paths)
	if nb!=0:
		IJ.log("We found " + str(nb) + " images of " + photo_label)
	else:
		IJ.log("No photos found in this cateogry. Exiting plugin...")
		return

	# 4. Choose first picture to open
	#counter = 0
	global counter
	counter = choosePhotoIndex(image_names)

	# 5. Open first image
	openImageIndex(counter, image_paths)

	#3. Define name of trait to measure
	trait_types = ["body_length", "abdomen_length", "body_width", "siph_width",
	"siph_length","head_width","head_length", "thorax_width",
	"tarsus_length_left","tarsus_length_right",
	"tibia_length_left","tibia_length_right",
	"femur_length_left","femur_length_right",
	"flag_length_left","flag_length_right",
	"rostrum_length"]

	# Apply function to choose trait labels a first time :
	trait = trait_types[0]
	#trait = getTraitLabel(trait_types)
	#if trait is not None:
	#	label = trait # unpack each parameter
	#	IJ.log("Trait selected for measurement:" + trait)
	#else:
	#	IJ.log("No trait label selected. Try again")


	# 4. Create UI panel
	frame = JFrame("Actions", visible=True)
	frame.setLocation(10,10)
	frame.setSize(500,400)
	frame.DISPOSE_ON_CLOSE


	#button1 = JButton("Choose trait...", actionPerformed=chooseTrait)# NOT WORKING
	button2 = JButton("Add selected", actionPerformed=select)
	button3 = JButton("Measure all", actionPerformed=measure)
	button4 = JButton("Save Results", actionPerformed=save)
	button5 = JButton("Clear selection", actionPerformed=clearROI)
	button6 = JButton("Next image", actionPerformed=openNext)
	button7 = JButton("Reset starting image", actionPerformed=openChoice)
	button8 = JButton("Exit", actionPerformed=exitScript)

	frame.setLayout(GridLayout(3,3))

	#frame.add(button1)
	frame.add(button2)
	frame.add(button3)
	frame.add(button4)
	frame.add(button5)
	frame.add(button6)
	frame.add(button7)
	frame.add(button8)

	frame.pack()
	#frame.setVisible(True)

##______________ RUN script____________ ###
runScript()
