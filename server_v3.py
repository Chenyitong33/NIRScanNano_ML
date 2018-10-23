# This script runs a listener on the server. It loads a machine learning model from a file. It then reads
# some test data, and makes a prediciton.
# Data needs to be 228 floating point numbers, seperated by commas (no whitespace)
# e.g. "-0.097657,-0.068578,-0.065569,-0.071737,-0.077938,-0.08244,-0.081585,-0.071182,-0.056991,-0.041888,-0.033788,-0.025694,-0.020879,-0.017964,-0.017337,-0.015771,-0.014087,-0.010784,-0.011806,-0.008835,-0.00842,-0.005162,-0.004218,-0.002731,-0.001307,0.001381,0.002795,0.005116,0.00608,0.007526,0.00785,0.00963,0.009461,0.010489,0.011447,0.011534,0.010616,0.011248,0.00987,0.0089,0.008878,0.008562,0.006618,0.005957,0.006645,0.004936,0.003616,0.002573,0.000978,0.001189,0.00053,-0.000871,-0.000171,-0.000536,-0.001192,-0.00149,-0.001872,-0.003204,-0.003866,-0.002586,-0.002182,-0.001138,0.00037,0.001909,0.002338,0.004292,0.004389,0.00514,0.005821,0.004804,0.005547,0.007176,0.007902,0.008155,0.010711,0.012909,0.013234,0.015413,0.016986,0.017247,0.018692,0.018822,0.016636,0.014509,0.012981,0.011102,0.007442,0.004917,0.003922,0.000569,-0.000935,-0.003789,-0.006086,-0.007349,-0.00645,-0.007272,-0.006588,-0.007189,-0.006711,-0.007559,-0.00738,-0.007608,-0.008372,-0.00745,-0.006614,-0.006875,-0.006601,-0.005999,-0.004771,-0.004492,-0.003465,-0.002354,-0.001148,0.000461,0.002015,0.003499,0.006105,0.007674,0.010189,0.011423,0.012906,0.014335,0.015763,0.017506,0.020352,0.023843,0.024843,0.027593,0.028819,0.03221,0.035916,0.040718,0.046646,0.053451,0.059492,0.067458,0.07552,0.083848,0.089829,0.096491,0.105092,0.108913,0.113693,0.117733,0.118138,0.120274,0.1224,0.124786,0.127113,0.127722,0.130313,0.131118,0.130962,0.131566,0.130793,0.130574,0.128423,0.128353,0.126997,0.124077,0.123458,0.122395,0.11905,0.11621,0.115377,0.114021,0.113551,0.11294,0.111525,0.112517,0.113,0.114696,0.115312,0.117795,0.11862,0.121176,0.122472,0.122953,0.125062,0.126158,0.126875,0.129065,0.129026,0.130325,0.130069,0.130907,0.12957,0.130118,0.128781,0.130206,0.12918,0.129423,0.128561,0.128041,0.127329,0.130681,0.128765,0.128203,0.133424,0.130272,0.133343,0.131148,0.13065,0.13047,0.133656,0.131657,0.132822,0.130121,0.135063,0.135115,0.13978,0.143531,0.148926,0.157011,0.167923,0.190163,0.220659,0.241351,0.260513,0.265153,0.272636,0.280147,0.302518,0.291088,0.287712,0.306441,0.289525,0.275613"
# To test this, in the terminal, you can type: echo "the_string_above" | nc nirs.cis.unimelb.edu.au 10000

import socket
import sys
import os
import shutil
import numpy as np
import pandas as pd
import scipy.signal
from sklearn.preprocessing import scale
import pickle
import time
from _thread import *
from io import StringIO
from os.path import dirname
import datetime

# get path of the current script
this_dir = os.path.realpath(__file__)
parent_dir = dirname(this_dir)

# Set working directory
os.chdir(os.path.join(parent_dir, 'model'))

# Load the model
filename = 'finalized_model.sav'
loaded_model = pickle.load(open(filename, 'rb'))
print("model loaded")

globvar = 0
#####################################################################################
#####################################################################################
#####################################################################################

HOST = 'nirs.cis.unimelb.edu.au'  # Symbolic name, meaning all available interfaces
PORT = 10000  # Arbitrary non-privileged port
# dictionary for pharmaceuticals
dict = {
'Calcium': 'Calcium plays a role in strengthening bones and teeth. regulating muscle functioning, such as contraction and relaxation. regulating heart functioning. blood clotting.',
'Vitamin B1':'Vitamin B1, which is also referred to as thiamine, is a coenzyme used by the body to metabolize food for energy and to maintain proper heart and nerve function. Thiamine is used to digest and extract energy from the foods you eat by turning nutrients into useable energy in the form of "ATP".',
'Vitamin B3':'Medication and supplemental niacin are primarily used to treat high blood cholesterol and pellagra (niacin deficiency). ',
'Vitamin B12':'Vitamin B12 is a nutrient that helps keep the body''s nerve and blood cells healthy and helps make DNA, the genetic material in all cells. Vitamin B12 also helps prevent a type of anemia called megaloblastic anemia that makes people tired and weak.',
'Vitamin C':'Vitamin C helps to repair and regenerate tissues, protect against heart disease, aid in the absorption of iron, prevent scurvy, and decrease total and LDL ("bad") cholesterol and triglycerides.',
'Vitamin D':'Vitamin D is important for strong bones, muscles and overall health. Ultraviolet (UV) radiation from the sun is necessary for the production of vitamin D in the skin and is the best natural source of vitamin D.',
'Zinc':'Zinc is vital for a healthy immune system, correctly synthesizing DNA, promoting healthy growth during childhood, and healing wounds.',
'Fish Oil':'Fish oil is oil derived from the tissues of oily fish. Fish oils contain the omega-3 fatty acids EPA and DHA, precursors of certain eicosanoids that are known to reduce inflammation in the body, and have other health benefits, such as treating hypertriglyceridemia.',
'Lecithin':'Lecithin is a fat that is essential in the cells of the body. Lecithin is taken as a medicine and is also used in the manufacturing of medicines. Lecithin is used for treating memory disorders such as dementia and Alzheimer''s disease.',
'Tylenol':'Pain reliever/fever reducer.',
'Amoxicillin':'Amoxicillin is used to treat many different types of infection caused by bacteria, such as tonsillitis, bronchitis, pneumonia, gonorrhea, and infections of the ear, nose, throat, skin, or urinary tract.',
'Celery':'Celery has been used in herbal medicine to treat arthritis, nervousness, hysteria and various other conditions. The juice lowered blood pressure in several patients. Two components reduced tumors in mice.',
'Cranberry':'Cranberry (as juice or in capsules) has been used in alternative medicine as a possibly effective aid in preventing symptoms such as pain or burning with urination.',
'Krill Oil':'Krill oil is most commonly used for heart disease, high levels of certain blood fats (triglycerides), and high cholesterol, but there is limited scientific research to support these uses.'
}

# Listen for incoming requests. This comes from a socket request.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print('Socket created')

# Bind socket to local host and port
try:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
except socket.error as msg:
    print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

print('Socket bind complete')

# Start listening on socket
s.listen(10)
print('Socket now listening')

# now keep talking with the client
while 1:

    #check if necessary to update the model
    path = os.path.join(parent_dir, 'temporary')
    
    print("number of reported predictions in the temporary folder is",globvar)
    if globvar == 3:
        destination = os.path.join(parent_dir, 'feedback')
        for filename in os.listdir(path):
            src = os.path.join(path, filename)
            dst = os.path.join(destination, filename)
            shutil.move(src,dst)
        globvar = 0
        # Set working directory
        os.chdir(parent_dir)
        os.system("python3 train_SVM.py")
        # Set working directory
        os.chdir(os.path.join(parent_dir, 'model'))
        
        # Load the model
        filename = 'finalized_model.sav'
        loaded_model = pickle.load(open(filename, 'rb'))
        print("model loaded")

    # wait to accept a connection - blocking call
    conn, addr = s.accept()
    print('Connected with ' + addr[0] + ':' + str(addr[1]))

    # Receiving data from client
    buff = StringIO()          # Create the buffer
    while True:
        data = conn.recv(1024)
        buff.write(data.decode())                    # Append that segment to the buffer
        if '\n' in data.decode(): break              # If that segment had '\n', break
    
    #print(buff.getvalue())
    # Get the buffer data, split it over newlines, print the first line
    bufferdata = buff.getvalue().splitlines()[0]
    #print(bufferdata)
    data = StringIO(bufferdata)
    #print(bufferdata)
    t1 = time.time()
#-------------------------- Listen for guard's hello -------------------------------------
    #if bufferdata == "Hello":
      #print("accept hello")
    
    
    
#-------------------------- Report Situation for wrong predictions --------------------------
    if bufferdata == "Yes":
      print("accept again")
      print("Correct prediction.")
      globvar = globvar + 1
      right_name = prediction
      print(right_name)
      right_name = right_name[:1].upper() + right_name[1:]
      nametime = datetime.datetime.now().strftime("_%Y%m%d_%H%M%S_")
      name = right_name+"O1"+nametime+".csv"
      
      # Set working directory
      os.chdir(os.path.join(parent_dir, 'temporary'))
      
      f = open(name,'w')
      l = conn.recv(1024)
      while (l):
          print("Receiving...")
          l = str(l, errors='ignore')
          f.write(l)
          l = conn.recv(1024)
      f.close()
      print("Done Receiving")
      conn.close()
    elif bufferdata == "No":
      print("Wrong prediction!")
      globvar = globvar + 1
      
      # Receiving data from client
      buff = StringIO()          # Create the buffer
      while True:
        data = conn.recv(1)
        print(data)
        buff.write(data.decode())                    # Append that segment to the buffer
        if '\n' in data.decode(): break              # If that segment had '\n', break
      
      # Get the buffer data, split it over newlines, print the first line
      right_name = buff.getvalue().splitlines()[0]
      
      #right_name = conn.recv(1024)
      print(right_name)
      #right_name = right_name.decode()
      right_name = right_name[:1].upper() + right_name[1:]
      nametime = datetime.datetime.now().strftime("_%Y%m%d_%H%M%S_")
      name = right_name+"O1"+nametime+".csv"
      # Set working directory
      os.chdir(os.path.join(parent_dir, 'temporary'))
      
      f = open(name,'w')
      l = conn.recv(1024)
      while (l):
          print("Receiving...")
          l = str(l, errors='ignore')
          f.write(l)
          l = conn.recv(1024)
      f.close()
      print("Done Receiving")
          
      conn.close()
#-------------------------- Original part for prediction on server --------------------------
    else:
      try:
  
          # The request has arrived. We reformat the data into a dataframe.
          print("the request has arrived")
          df = pd.read_table(data, sep=",", header=None)
  
          df = pd.to_numeric(df.iloc[0])
          # apply smoothing filter and svn filter
          # filtered <- filter(sgolay(p=3, n=11, m=0),absorbance)
          filtered = scipy.signal.savgol_filter(df, window_length=11, polyorder=3)
  
          # filtered <- scale(t(filtered),center=TRUE)
          filtered = scale(filtered)
  
          # filtered = filtered.reshape(1,228)
          print(filtered.shape)
          features = np.concatenate([filtered, np.diff(filtered)])
          # make the new data frame
          df = pd.DataFrame(data=features).transpose()
          # Now make the prediciton using our model file and the incoming data.
          prediction = loaded_model.predict(df)[0]
          # scatter situation
          if "scatter" in prediction:
            reply = prediction+'\n'
          else:
            # get the most highest probability of results
            #probability = round(np.amax(loaded_model.predict_proba(df)), 3)
            
            
            
            all_prob = loaded_model.predict_proba(df)[0]
            print("probability matrix:", all_prob)
            prob_list = all_prob.tolist()
            
            # initialise the index
            i=0
            for classname in loaded_model.classes_:
              if classname == prediction:
                  prediction_index = i
              i=i+1
              
            probability = prob_list[prediction_index]
            print("prediction result's probability is", round(probability, 3))
            
            predict2 = ""
            for x in all_prob:
              if abs(x - probability) < 0.1 and x != probability :
                index = prob_list.index(x)
                print(index)
                prob_list[index] = 0 # in case of the same probability 
                predict2 = predict2+loaded_model.classes_[index][:1].upper() + loaded_model.classes_[index][1:]+" "
                
            print(prob_list)
            
            
            '''original attempt which could just predict one optional prediction
            # get the list of decision function which is consistent with probability of each classes
            decision_list = loaded_model.decision_function(df)[0].tolist()
            print("decision list:", decision_list)
            # get the most likely prediction
            index1 = decision_list.index(max(decision_list))
            print(index1)
            # make the highest decision to NaN, and then take the second highest prediction
            decision_list[index1] = float('nan')
            # get the second highest prediction class
            index2 = decision_list.index(np.nanmax(decision_list))
            print("decision list:", decision_list)
            print(index2)
            predict2 = loaded_model.classes_[index2]
            print(loaded_model.classes_)
            print(predict2)
            # make 'scatter ...' to 'Scatter ...' which distinguish with situation of first prediction has 'scatter'
            predict2 = predict2[:1].upper() + predict2[1:]
            '''
            if prediction in dict:
              if probability > 0.3:
                reply = prediction+", confident rate is relatively high with probability "+str(round(probability, 3))+'. The optional predictions are: '+predict2+";"+dict.get(prediction)+'\n'
              else:
                reply = prediction+", confident rate is relatively low with probability "+str(round(probability, 3))+'. The optional predictions are: '+predict2+";"+dict.get(prediction)+'\n'
                print(reply)
            else:
              if probability > 0.3:
                reply = prediction+", confident rate is relatively high with probability "+str(round(probability, 3))+'. The optional predictions are: '+predict2+";"+"none"+'\n'
              else:
                reply = prediction+", confident rate is relatively low with probability "+str(round(probability, 3))+'. The optional predictions are: '+predict2+";"+"none"+'\n'
                
  
  
      except:
          reply = "Data not in expected format: \n"
  
      print("Send:",reply)
      conn.sendall(reply.encode())
      print("test time:", time.time() - t1, "s")
      
          
      conn.close()

s.close()
