# Script to measure Aphid traits on microscope photos

# Load classes
import os, sys
from ij import IJ, WindowManager as WM  
from ij.gui import Roi
from ij.gui import GenericDialog
from ij.io import SaveDialog
from ij.plugin.frame import RoiManager
from ij.measure.Measurements import *
from ij.plugin.filter import Analyzer
from ij.measure import ResultsTable as RT
from javax.swing import JFrame, JButton, JOptionPane  
from java.awt import GridLayout
from ij.io import DirectoryChooser  
from fiji.util.gui import GenericDialogPlus
	
###____________ FUNCTION running the plugin ____________ ###

def runScript():
	############ Set measurement options ###########
	
	# label the ROI and add to image
	options = LABELS + ADD_TO_OVERLAY  # see https://imagej.nih.gov/ij/developer/api/ij/measure/Measurements.html
	# Measure only the length of the ROI (= lines)
	Analyzer.setMeasurements(options)

	IJ.setTool("Line")

		
	############ FUNCTION Choose source directory ##########
	def getDirectories():
	
		dc = DirectoryChooser("/Users/maud/Desktop/fiji tests/")  
		path = dc.getDirectory()
		
		gdp = GenericDialogPlus("Choose folders...")
		gdp.addDirectoryField("Choose folder of images", path + "images/")
		gdp.addDirectoryField("Choose folder to save results", path + "results/")
		gdp.addDirectoryField("Choose folder to save measured images", path + "measured images/")
		gdp.showDialog()  
	     
		if gdp.wasCanceled():
			print "User canceled. Exiting...."
			return
			
		dir1 = gdp.getNextString()
		dir2 = gdp.getNextString()
		dir3 = gdp.getNextString()
		return dir1, dir2, dir3
	
	#############  FUNCTION: DEFINE category of photo ############ 
	def getPhotoCategory(categories):  
		gd = GenericDialog("Select photos")
		gd.addChoice("choose the type of photos for today", categories, categories[1])  
		gd.showDialog()  
		
		if gd.wasCanceled():  
			print "User canceled dialog!"
			return None
	 
		# Read out the options  
		photo_cat = gd.getNextChoice()  
		return photo_cat # a tuple with the parameters  
	
	
	##### FUNCTION List all image file paths #######
	def listPaths(directory, label):
		path_list = []
		walkList = os.walk(directory)
		# For loop in recursive walklist
		for root, directories, filenames in walkList:  
			for filename in filenames:
				# search for the file label:
				ind = filename.find(label)
				if ind > -1 :
					path_list.append(os.path.join(root, filename))
					print filename
				else :
					continue
		return path_list
	
	
	######### FUNCTION: OPEN IMAGE from path list ##########
	
	def openImageIndex(index, paths):
		if len( paths) > index:
			image_path =  paths[index]
			print "Opening image:", image_path
			IJ.open( paths[index])
		else:
			print "No more valid image paths"
			return None
	
			
	#############  FUNCTION: DEFINE TRAIT label ############ 
	def getOptions(types):  
	  gd = GenericDialog("Options")
	  gd.addChoice("Choose trait label", types, types[1])  
	  gd.showDialog()  
	    
	  if gd.wasCanceled():  
	    print "User canceled dialog!"  
	    return None
	     
	  # Read out the options  
	  label = gd.getNextChoice()  
	  return label # a tuple with the parameters  
	
	#############  EVENT FUNCTION: choose another trait label: ############ 
	def choose_trait(event):
		trait = getOptions()  
		#if trait is not None:  
	  	#	trait_label = trait # unpack each parameter  
		IJ.log("Trait selected for measurement:"+ trait)
		return trait
	
		
	#############  EVENT FUNCTION: for selecting and labelling ROI ############ 
	def select(event):  
	  """ event: the ActionEvent that tells us about the button having been clicked.
	      Select lines or arrows defined by user and add them to ROI Manager """  
	      
	  imp = WM.getCurrentImage()   
	  if imp:      
		# get the ROI manager
		rm = RoiManager().getInstance()
	
		#count number of ROI
		n = rm.getCount() 
	
		roi1 = imp.getRoi()
		rm.addRoi(roi1)
	
		rm.select(n)    
		name = trait + "_" + str(n)
		IJ.log("Element" + name +"was added")
		rm.runCommand("Rename",name)  
	
	  else:  
	    IJ.log("Error: Open an image first")
	
	############ EVENT FUNCTION: Measure ############ 
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
	
	
	############ EVENT FUNCTION: to clear ROI ############ 
	def clearROI(event):
		""" Delete all elements in the ROI manager """
		imp = WM.getCurrentImage()  
		# clear all ROIs
		rm = RoiManager().getInstance()
		n = rm.getCount()
		rm.setSelectedIndexes(range(n))	
		rm.runCommand("Delete")
		rm.runCommand("Show None")
	
	
	############  EVENT FUNCTION: to save measurements table ############ 
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
		IJ.saveAs(imp2, "Jpeg",measured_image_filepath)
		IJ.log( "Modified image was saved:" + measured_image_filepath)
		imp.changes = True

		imp.changes = FALSE
		imp.close()
		imp2.close()
	
	    
	    
	
	######### EVENT FUNCTION: OPEN Next IMAGE + ADD to counter ##########
	def openNext(event):
		global counter
		counter = counter + 1
		openImageIndex(counter, image_paths)
	
	######### EVENT FUNCTION: Start with a new image ##########
	def openChoice(event):
		print(image_paths)
		# Function to select path in a list
		def getIMGnumber(paths_list):  
			gd = GenericDialog("Select where to start again")
			gd.addChoice("First photo to open in the list", paths_list, paths_list[1])  
			gd.addNumericField("Number of the photo", 0)
			gd.showDialog()  
			
			if gd.wasCanceled():  
				print "User canceled dialog!"
				return None
		 
			# Read out the options  
			pathNumber1 = gd.getNextChoiceIndex()  
			pathNumber2 = gd.getNextNumber()  
			return int(pathNumber2)
	
		# Choose a starting image
		start_index = getIMGnumber(image_paths)
	
		# Update the counter to start where we want
		global counter
		counter = start_index
		print "New start at:", counter
	
		# Open image corresponding to counter
		openImageIndex(counter, image_paths)
		
	######### EVENT FUNCTION: EXIT ##########
	def exitScript(event):
		rm = RoiManager().getInstance()
		rm.close()
		IJ.run("Close All", "")
		IJ.log("Exiting plugin...")
		return


	
	# Select directories
	dir_paths = getDirectories() 
	if dir_paths is not None:
	    source_directory, result_directory, measured_directory = dir_paths
	else:
		IJ.log("Selection cancelled. Exiting plugin...")
		return
		
	print(source_directory)
	
	############ Select category of pictures ############ 
	photoCategories = ["dorsal", "right antenna", "left leg","ventral","mouthpart",
	"left antenna","right leg","ocular tubercles"]
	
	photo_label =  getPhotoCategory(photoCategories)
	if photo_label is not None:  
		photo_cat = photo_label # unpack each parameter  
		print "Category of photos selected:", photo_label
	else:
		IJ.log("Selection cancelled. Exiting plugin...")
		return
	
	##### List all image file paths #######
	image_paths = listPaths(source_directory, photo_label)
	global image_paths
	nb = len(image_paths)
	if nb!=0: 
		print "We found", nb, "images of", photo_label
	else:
		IJ.log("No photos found in this cateogry. Exiting plugin...")
		return
	
	############ Start by opening first picture ############
	counter = 0
	global counter
	openImageIndex(counter, image_paths)
	
	############ Define name of trait ############ 
	trait_types = ["Body_length", "Body_width", "Siph_length", 
	"Head_width", "Head_length", 
	"Tarsus_length", "Tibia_length",
	"Right_Flag3_length", "Right_Flag3_diam",
	"Left_Flag3_length", "Left_Flag3_diam",
	"Rostrum_length"]
	
	# Apply function a first time :
	trait = getOptions(trait_types)  
	if trait is not None:
		label = trait # unpack each parameter
		print "Trait selected for measurement:", trait
	else:
		IJ.log("No trait label selected. Try again")
		

	############  Create UI panel ############ 
	frame = JFrame("Actions", visible=True)  
	frame.setLocation(10,10)
	frame.setSize(500,400)
	
	
	button1 = JButton("Choose trait...", actionPerformed=choose_trait) 
	button2 = JButton("Add selected", actionPerformed=select) 
	button3 = JButton("Measure all", actionPerformed=measure)
	button4 = JButton("Save Results", actionPerformed=save)
	button5 = JButton("Clear selection", actionPerformed=clearROI)
	button6 = JButton("Next image", actionPerformed=openNext)
	#button7 = JButton("Reset starting image", actionPerformed=openChoice)  #TO DO NOT WORKING
	button8 = JButton("Exit", actionPerformed=exitScript)
	
	frame.setLayout(GridLayout(2,4))
	
	frame.add(button1)
	frame.add(button2)
	frame.add(button3)
	frame.add(button4)
	frame.add(button5)
	frame.add(button6)
	#frame.add(button7)
	frame.add(button8)
	frame.pack()
	frame.setVisible(True) 



##______________ RUN script____________ ###
runScript()
