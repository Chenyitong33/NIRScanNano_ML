#This script runs a listener on the server. It loads a machine learning model from a file. It then reads 
#some test data, and makes a prediciton.

#If you want to run this server from the terminal, type: Rscript server.R

#use pacman to automatically load  or install requried packages.
#this makes the code more transportable.
#check if pacman package exists, if not install it
if (!require("pacman")) install.packages("pacman")
#NOTE:add required pacakages below
pacman::p_load(e1071,signal)



#Load the model
model <- readRDS("model_svm.rds")


# Listen for incoming requests. This comes from a socket request.
#Data needs to be 228 floating point numbers, seperated by commas (no whitespace)
#e.g. "-0.097657,-0.068578,-0.065569,-0.071737,-0.077938,-0.08244,-0.081585,-0.071182,-0.056991,-0.041888,-0.033788,-0.025694,-0.020879,-0.017964,-0.017337,-0.015771,-0.014087,-0.010784,-0.011806,-0.008835,-0.00842,-0.005162,-0.004218,-0.002731,-0.001307,0.001381,0.002795,0.005116,0.00608,0.007526,0.00785,0.00963,0.009461,0.010489,0.011447,0.011534,0.010616,0.011248,0.00987,0.0089,0.008878,0.008562,0.006618,0.005957,0.006645,0.004936,0.003616,0.002573,0.000978,0.001189,0.00053,-0.000871,-0.000171,-0.000536,-0.001192,-0.00149,-0.001872,-0.003204,-0.003866,-0.002586,-0.002182,-0.001138,0.00037,0.001909,0.002338,0.004292,0.004389,0.00514,0.005821,0.004804,0.005547,0.007176,0.007902,0.008155,0.010711,0.012909,0.013234,0.015413,0.016986,0.017247,0.018692,0.018822,0.016636,0.014509,0.012981,0.011102,0.007442,0.004917,0.003922,0.000569,-0.000935,-0.003789,-0.006086,-0.007349,-0.00645,-0.007272,-0.006588,-0.007189,-0.006711,-0.007559,-0.00738,-0.007608,-0.008372,-0.00745,-0.006614,-0.006875,-0.006601,-0.005999,-0.004771,-0.004492,-0.003465,-0.002354,-0.001148,0.000461,0.002015,0.003499,0.006105,0.007674,0.010189,0.011423,0.012906,0.014335,0.015763,0.017506,0.020352,0.023843,0.024843,0.027593,0.028819,0.03221,0.035916,0.040718,0.046646,0.053451,0.059492,0.067458,0.07552,0.083848,0.089829,0.096491,0.105092,0.108913,0.113693,0.117733,0.118138,0.120274,0.1224,0.124786,0.127113,0.127722,0.130313,0.131118,0.130962,0.131566,0.130793,0.130574,0.128423,0.128353,0.126997,0.124077,0.123458,0.122395,0.11905,0.11621,0.115377,0.114021,0.113551,0.11294,0.111525,0.112517,0.113,0.114696,0.115312,0.117795,0.11862,0.121176,0.122472,0.122953,0.125062,0.126158,0.126875,0.129065,0.129026,0.130325,0.130069,0.130907,0.12957,0.130118,0.128781,0.130206,0.12918,0.129423,0.128561,0.128041,0.127329,0.130681,0.128765,0.128203,0.133424,0.130272,0.133343,0.131148,0.13065,0.13047,0.133656,0.131657,0.132822,0.130121,0.135063,0.135115,0.13978,0.143531,0.148926,0.157011,0.167923,0.190163,0.220659,0.241351,0.260513,0.265153,0.272636,0.280147,0.302518,0.291088,0.287712,0.306441,0.289525,0.275613"
# To test this, in the terminal, you can type: echo "the_string_above" | nc localhost 6011

server <- function(){
  while(TRUE){
    writeLines("Listening...")
    con <- socketConnection(host="localhost", port = 5000, blocking=TRUE,
                            server=TRUE, open="r+", timeout=999999)
    
    
    data <- readLines(con, 1)
    start_time <- Sys.time()
    #The request has arrived. We reformat the data into a dataframe.
    tryCatch({
      
      data <- as.numeric(strsplit(data,split = ",")[[1]])
      #apply smoothing filter and svn filter
      filtered <- filter(sgolay(p=3, n=11, m=0),data)
      filtered <- scale(t(filtered),center=TRUE)
      filtered <- attr(filtered,"scaled:center")
      features <- c(filtered,diff(filtered))

      #make the data frame
      data <- data.frame(t(matrix(features)))
    
      #Now make the prediciton using our model file and the incoming data.
      prediction  <- predict(model, data, probability=TRUE)
      response <- paste(as.character(prediction), round(max(attr(prediction, "probabilities")), digits=3))
      writeLines(response, con) 
      
    }, error = function(e){
      writeLines("Data not in expected format",con)
    })
    end_time <- Sys.time()
    print(end_time-start_time)
    close(con)
    
  }
}
server()


