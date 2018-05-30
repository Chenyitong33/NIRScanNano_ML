#This script loads a machine learning model from a file. It then reads 
#some test data, and makes a prediciton

#use pacman to automatically load  or install requried packages.
#this makes the code more transportable.
#check if pacman package exists, if not install it
if (!require("pacman")) install.packages("pacman")
#NOTE:add required pacakages below
pacman::p_load(e1071)


#set the working directory to that of the source file
#this makes the code more transportable
this.dir <- dirname(parent.frame(2)$ofile)
setwd(this.dir)


#Load the model
model <- readRDS("model_svm.rds")


# Read the data we want to clasify. This may come from an HTTP request, but for now
# jus read it from a file
fileName <- paste(this.dir,"/data/test/CalciumO1_029031_20160307_150218.csv",sep="")
data <- read.table(fileName, sep=",", fill = TRUE, skip=19, header = TRUE)
testData <- as.numeric(data$Absorbance..AU.)

#Now data is in an array format so we need to change its format before we make the classification.
#The data needs to be a single row with 228 columns, and the column names should 
# be "X1", "X2", etc. R does this automatically for arrays.
testData <- data.frame(t(matrix(testData)))


#We input our testData into the model, and we get out a prediction.
prediction  <- predict(model, data.frame(testData), probability = TRUE)

#The result is a class name, stored as a string.
print(paste(as.character(prediction), max(attr(prediction, "probabilities"))))



