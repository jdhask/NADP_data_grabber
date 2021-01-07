def get_sites(network):
	# Function to list valid site names, name of site, and state in a given NADP network. 

	#  Written by Dr. Jessica D. Haskins, 1/6/2021,   github: https://github.com/jdhask/ 
	#  Contact at jhaskins@alum.mit.edu 

	import pandas as pd

	# Check that the network passed by the user is valid. 
	n=['NTN', 'MDN', 'AIRMoN','AMNet', 'AMoN'] # list of valid options. 
	
	if network in n:
		sites='http://nadp.slh.wisc.edu/data/sites/CSV/?net='+network # URL for NTN or MDN site lists 

		s= pd.read_csv(sites) # dataframe containing sites & site info (e.g. lat/long, etc)

		print(s.columns)
		for i in range(0,len(s)):
			print(s.siteid[i], s.siteName[i], ', ', s.state[i])


def NADP_date_string_converter(df):
	# Function to identify "date like" columns in a dataframe (df) scraped from NADP data and 
	# convert them from strings to pandas datetime objects for easy use later. Output is 
	# just a dataframe with same columns as input df, but with date-like columns as datetime objs.
	#
	#  Written by Dr. Jessica D. Haskins, 11/13/2020,   github: https://github.com/jdhask/ 
	#  Contact at jhaskins@alum.mit.edu 
	# ----------------------------------------------------------------------------------------

	import pandas as pd

	#Dictionary containing date related columns in all networks & the format we expect them in: 
	datelist_dict={0:df.filter(like='date'), 1:df.filter(like='modifiedOn'), 2:df.filter(like='yrmonth'),
	3:df.filter(like='CollStart'), 4:df.filter(like='CollEnd'), 5:df.filter(like='DATE'), 6:df.filter(like='dateon'), 
	7:df.filter(like='dateoff'),8:df.filter(like='startdate'),9:df.filter(like='stopdate'),} 

	datefmt_dict= {0:'%Y-%m-%d %H:%M', 1:'%m/%d/%Y %H:%M:%S %p', 2:'%Y%m', 3:'%Y-%m-%d %H:%M' ,
	4:'%Y-%m-%d %H:%M', 5:'%Y-%m-%d %H:%M', 6:'%Y-%m-%d %H:%M:%S', 7:'%Y-%m-%d %H:%M:%S', 8:'%Y-%m-%d %H:%M:%S', 
	9:'%Y-%m-%d %H:%M:%S'   }

	for t in range(0,10): # Loop over number of "like" statements we have... (doesn't include #10)
		datelist=datelist_dict.get(t) # get the column names in this iteration 
		datefmt=datefmt_dict.get(t) # and their expected format in this iteration 

		if len(datelist.columns)>0: # Don't try to convert columns that don't exist in this file. 
			for (columnName, columnData) in datelist.iteritems(): # Convert each name matching this "like" statement 
				df[columnName] = pd.to_datetime(columnData, format=datefmt)

	return df


def NADP_data_grabber(siteid, network, freq='native', valstring='', savepath=''):

	# Function to directly scrape data for indivudal sites or All sites from NADP website at difference 
	# time intervals, and return this as a pandas dataframe. Also combines 
	# data from site info csv (e.g. site lat, long, county, state, etc.) and data csv into a 
	# single data frame. Converts string date-times into pandas datetimes for easy plotting. 
	#
	#  Written by Dr. Jessica D. Haskins, 11/13/2020,   github: https://github.com/jdhask/ 
	#  Contact at jhaskins@alum.mit.edu 
	#
	# NOTE: Data from NADP/NTN used in published works should abide by the NADP data  
	#       use conditions (http://nadp.slh.wisc.edu/nadp/useConditions.aspx)
	#
	# -------------------Inputs: ----------------------------------------------------------
	#		siteid   - String corresponding to the NADP site ID you want data from or 'All' if
	#					you'd like to get data from all sites. Individual site names are typically
	#				    len 4 strings like 'WY99'. Will error if site name doesn't exist. 
	#
	#       network   - String containing which network you'd like to get data from. 
	# 					Will push error if invalid network name. Valid options are: 
	#						'NTN'  : National Trends network data 
	#						'MDN' : Mercury Deposition Network. 
	#                       'AIRMoN': Atmospheric Integrated Research Monitoring Network
	#                       'AMNet' : Atmospheric Mercury Network
	#                       'AMoN' : Ammonia Monitoring Network
	#
	#       freq     - String containing the frequency of the data you'd like to retreive 
	#					for this site. Valid options are dependent on which network is chosen. 
	#                   Only 1 data frequency is available for AIRMon, AMNet, and AMoN. Therefore
	#                   this input is redundant for those networks. If data network is 
	#                   NTN or MDN, then valid options are as follows with brackets indicating the 
	#					supported networks for each data frequency. Valid options are as follows:
	#
	#						'weekly' 		  : weekly deposition data 	[NTN, MDN, ] ** Default if no freq is passed.**  
	#						'annual-cal-dep'  : annual deposition on calendar year 	[NTN, MDN]			
	#						'monthly'         : average monthly deposition data [NTN only]  
	#                       'annual-cal-conc' :  Pecip weighted annual concentrations on calendar year [NTN only]  
	#						'annual-wy'       : annual deposition on water year  [NTN only]  
	#						'seasonal-conc'   : Pecip weighted seasonal concentrations [NTN only]  
	#						'seasonal-dep'    : Seasonal deposition [NTN only] 
	# 
	#     valstring   - Redundant input unless your network is 'MDN'. Options are: 
	#					''   - An empty string which will return only data which the NADP has 
	#                         determined to be valid. This is default. 
	#                   '-i'  - A string that will return all data (valid and invalid). 
	#                           These samples can be identified by the qrCode field, 
	#                           which will have a value of "C".

	#     savepath    - Path to a driectory in which to save a pickle of this datafram. Default is empty which 
	#					does not save a pickle. Name of pickle file is auto generated based on network, siteid, 
	#                   and frequency of selected data. 

	# -------------------Output: --------------------------------------------------------------- 
	#
	#      df       - pandas dataframe containing all csv data from the NADP. 
	#     
	#      NADP_NTN_weekly_WA99.pkl  - (OPTIONAL) a pickle file containing the dataframe, df, if a 
	#                                  savepath was passed as input.  
	# 
	# ---------------- Examples: --------------------------------------------------------------
	#
	#  out= indv_NADP_site_grabber('WY99', 'NTN', freq='monthly') # monthly avg'd data for site WY99 from NTN 
	#  out= indv_NADP_site_grabber('WY96', 'NTN') # weekly data for site WY99 from NTN (native freq)
	#  out= indv_NADP_site_grabber('MS12', 'AMNet') # hourly data for site MS12 from AMNet  (native freq)
	#  out= indv_NADP_site_grabber('CA75', 'MDN', freq='annual-cal-dep', valstring='-i') 
	# 		^ Above Returns Precip weighted Annual avg dep that includes invalid data points. 
	# ----------------------------------------------------------------------------------------

	import pandas as pd
	import numpy as np
	import os

	# Check that the network passed by the user is valid. 
	n=['NTN', 'MDN', 'AIRMoN','AMNet', 'AMoN']
	
	if network in n:
		# Validate that the user input is a real site by cross checking input with the site list. 
		sites='http://nadp.slh.wisc.edu/data/sites/CSV/?net='+network # URL for NTN or MDN site lists 

		s= pd.read_csv(sites) # dataframe containing sites & site info (e.g. lat/long, etc)

		# If user provided site ID is present in the sites list, proceed. Otherwise, exit with error. 
		if s['siteid'].str.contains(siteid).any() or siteid=='All':
			
			# Craft the url based on the sitename & frequency of the pull request. 
			std_url= 'http://nadp.slh.wisc.edu/datalib/'

			# Dictionary containing urls of dif types of data for indv sites: 
			if network=='AMoN': 
				cases={'native': std_url+'/Amon/csv/'+siteid+'-rep.csv'} # is actually a bi-weekly collection
			if network=='AMNet': 
				cases={'native': std_url+network+'/'+'/AMNet-'+siteid+'.csv'} # is actually a daily collection... 
			
			if network=='AIRMoN': 
				cases= {'native': std_url+network+'/'+'/AIRMoN-'+siteid+'.csv'}

			if network=='MDN': 
				cases= {'native': std_url+network+'/'+'weekly/MDN-'+siteid+'-w'+valstring+'.csv', # weekly data is native freq period 
				'weekly': std_url+network+'/'+freq+'/MDN-'+siteid+'-w'+valstring+'.csv', 
				'annual-cal-dep': std_url+network+'/'+'annual/MDN-'+siteid+'-a'+valstring+'.csv'}

			if network =='NTN': 
				cases= {'monthly': std_url+network+'/'+freq+'/NTN-'+siteid+'-m.csv',
				'native': std_url+network+'/'+'weekly/NTN-'+siteid+'-w.csv',  # weekly data is native freq period. 
				'weekly': std_url+network+'/'+freq+'/NTN-'+siteid+'-w.csv', 
				'annual-cal-conc': std_url+network+'/'+'cy/NTN-'+siteid+'-cy.csv', 
				'annual-cal-dep': std_url+network+'/'+'cydep/NTN-'+siteid+'-cydep.csv', 
				'annual-wy' : std_url+network+'/'+'wy/NTN-'+siteid+'-wy.csv', 
				'seasonal-conc': std_url+network+'/'+'seas/NTN-'+siteid+'-s.csv', 
				'seasonal-dep': std_url+network+'/'+'seasdep/NTN-'+siteid+'-sdep.csv'}

			url = cases.get(freq,None) # Set default to None incase there's a user error in freq 

			if url is None: # Check to make sure the url exists: 
				sys.exit('ERROR: frequency not defined. See valid inputs for freq.')
			else:   # Read in data from that site and return it.  
				print('Loading data... This can take ~30s-3mins. Faster for loading 1 site than All site data. Please wait! ')
				df= pd.read_csv(url)

				# Take info from site file and add it into the master data frame (site lat/lon info)
				for (columnName, columnData) in s.iteritems():
					if siteid !='All':
						msk=(s.siteid==siteid) # Only pull data from site list for this site. 
						df[columnName]=np.full((len(df.index),1), columnData[msk]) 
					else: 
						for j in range(0,len(s.siteid)): #Loop over each site and pull data for each. 
							this_site=s.siteid[j]
							msk=(s.siteid==this_site)  
							df[columnName]=np.full((len(df.index),1), columnData[msk]) 

				# Convert all date related columns from strings to date-time objects for easy plotting. 
				df_new= NADP_date_string_converter(df)

				# If the user has passed a savepath variable, check to see if its valid, and save data as a pickle.  
				isValidPath = os.path.isdir(savepath)  
				if isValidPath ==True and len(savepath)>=1: 
					name='\\NADP+'+network+'_'+freq+'_'+siteid+'.pkl'
					df_new.to_pickle(savepath+name)
					print('File saved as: '+ savepath+name)
				 
				if isValidPath ==False and len(savepath)>=1:
					sys.exit('ERROR: Inputted SavePath is not a valid directory.')

				return df_new # Return dataframe to user as output. 


		else:
			sys.exit('ERROR: The site name provided is not a valid site.')
	else: 
		sys.exit('ERROR: The network identified is not supported.')	


