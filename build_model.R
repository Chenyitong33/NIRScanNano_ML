#This script reads all data files, builds an SVM model, and writes the model to a file
#This way, when we need to use the model on-the-fly, we do not have to re-train it,
#but we can just read it from a file.

#use pacman to automatically load  or install requried packages.
#this makes the code more transportable.
#check if pacman package exists, if not install it
if (!require("pacman")) install.packages("pacman")
#NOTE:add required pacakages below
pacman::p_load(e1071, signal, prospectr,randomForest)

#Global: the number of frequency bands we have
F <- 228

#For each sample we use 2 spetra to improve classification. The 2nd spectrum uses -1 because we use the diff() filter
FREQ <- 2*F-1

#set the working directory to that of the source file
#this makes the code more transportable
this.dir <- 'C:/Users/frankie/Desktop/research project/ML_part/r'
#this.dir <- dirname(parent.frame(2)$ofile)
setwd(this.dir)

#set the data directory
directory <- 'C:/Users/frankie/Desktop/research project/ML_part/r/data'

#function to read the data files and return one big dataframe
#Also does some processing of the data
createDataFrame <- function(directory) {
  
  # Set working directory and retrieve all the files in it.
  setwd(directory)
  fileList <- list.files(pattern="*.csv")
  
  #create a data frame to hold all absorbance values
  #need an extra column at the start to hold "type" (i.e. the thing we are trying to predict)
  df <- data.frame(matrix(0, ncol = FREQ + 1, nrow = length(fileList)))
  colnames(df)[FREQ+1] <- "Type"
  
  # Loop through all the csv files and read their data.
  for(i in 1:length(fileList)) {
    
    # We only want the "absorbance" data, and we skip some header rows at 
    # the start of the csv file.
    fileName <- fileList[i]
    data <- read.table(fileName, sep=",", fill = TRUE, skip=19, header = TRUE)
    absorbance <- as.numeric(data$Absorbance..AU.)
    
    #How to filter:
    #Initial attempt: apply smoothing filter and svn filter
    #Revision1: add more features than just the bands: apply differentials
    
    #Savitzky-Golay Smoothing Filters:
    #Computes the filter coefficients for all Savitzky-Golay smoothing filters.
    filtered <- filter(sgolay(p=3, n=11, m=0),absorbance)
    
    #scale is generic function whose default method centers and/or scales the columns of a numeric matrix.
    #Transpose filtered?
    filtered <- scale(t(filtered),center=TRUE)
    
    #Access the attribute 'scaled:center'
    filtered <- attr(filtered,"scaled:center")
    features <- c(filtered,diff(filtered))
    
    #set the label of the row to be the class/item/thing that the data represents.
    #as a convention, we assume that the first few characters of the csv filename is the class.
    df[i,] <- c(features,0)
    df[i,FREQ+1] <- strsplit(fileName, "O1")[[1]][1]
  }
  
  # Remove NaN values from data frame
  is.nan.data.frame <- function(x)
    do.call(cbind, lapply(x, is.nan))
  df[is.nan(df)] <- 0
  
  #Make the Type column to be a factor (rather than string)
  #This is needed for machine learning.
  df$Type <- factor(df$Type)
  
  return(df)
}

# Read the data
trainData <- createDataFrame(paste(this.dir,"/data",sep=""))

# Build the SVM model and print some results 
# The model was tweaked by doing a search grid for all possible parameter values
# tuneResult <- tune(svm, Type ~ .,  data = trainData,ranges = list(gamma = seq(0,1,0.1), cost = 2^(2:7)))
# print(tuneresult)
start_time <- Sys.time()
model <- svm(Type ~ ., data = trainData, cost = 2, gamma = 0.5, cross = 10, kernel="polynomial", degree=2, probability=TRUE)
end_time <- Sys.time()
print(end_time-start_time)


#Write the model to a file
setwd(this.dir)
saveRDS(model,"model_svm.rds")

# Use the code below to evaluate how well the classifier works. This is like a benchmark
testData <-  createDataFrame(paste(this.dir,"/test",sep=""))
pred  <- predict(model, testData[1:FREQ], probability = TRUE)
t<-table(pred = pred, true = testData$Type)
sum(diag(t))/sum(t)

#Visualise all data
# trainData$sample <- 1:nrow(trainData)
# df <- gather(trainData, "freq", "absorbtion", 1:FREQ)
# df$freq <- as.numeric(gsub("X","",df$freq))
# ggplot(df, aes(freq,absorbtion, color=sample)) + geom_line(size=0.1) + facet_wrap(~Type,ncol=4) + ylim(0,1) + theme(legend.position="none")

