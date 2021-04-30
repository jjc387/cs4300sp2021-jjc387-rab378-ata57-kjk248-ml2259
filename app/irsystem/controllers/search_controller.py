from . import *  
import re
import pickle
import os
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from sklearn.metrics.pairwise import cosine_similarity

project_name = "Where to Travel based on Wine Preferences"
net_id = "Jessica Chen: jjc387, Rhea Bansal: rab378, Amani Ahmed: ata57, \
Kylie Kurz: kjk248, Mindy Lee: ml2259"

global wine_dict 
global country_to_idx_dict
#insert kylie's ml stuff 
global tfidf_embedding_matrix # num reviews x 300
global word_embedding_matrix # num terms x 300
global tfidf_weight_dict # word -> tf idf weight
global word_to_idx_dict # word -> idx (for word_embedding_matrix row idx)

@irsystem.route('/', methods=['GET'])
def home():
	unpickle_files()
	return render_template('search.html', name=project_name, netid=net_id, flavors=[])

@irsystem.route('/search', methods=['GET'])
def search():
	query = request.args.get('flavors')
	countries = request.args.get('countries')
	if not query:
		data = []
		output_message = ''
	else:
		output_message = "Your search: " + query
		data = cos_sim_reviews(query)
		if len(data) == 0:
			data = ["We couldn't find results for this query. Try adding more descriptors"]
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)


def unpickle_files():
	global wine_dict
	global tfidf_wine_matrix
	global wine_words_index_dict
	global idf
	#TODO: replace with reduced descriptions dict
	with (open('winedata.pickle', "rb")) as openfile:
		while True:
			try:
				wine_dict = (pickle.load(openfile))
			except EOFError:
				break

	with (open('sparsetfidfmatrix.pickle', "rb")) as openfile:
		while True:
			try:
				tfidf_wine_matrix = (pickle.load(openfile))
			except EOFError:
				break
	
	with (open('idf.pickle', "rb")) as openfile:
		while True:
			try:
				idf = (pickle.load(openfile))
			except EOFError:
				break

	with (open('winedescriptions.pickle', "rb")) as openfile:
		while True:
			try:
				wine_words_index_dict = (pickle.load(openfile))
			except EOFError:
				break


#TODO: query vectorizer function
def query_vectorizer(query_input):
	query_toks = re.findall(r"[a-z]+", input_terms.lower())
	weightedqueryterms = []
	for term in query_toks:
		if term in tfidf_weight_dict:
			tfidfweight = tfidf_weight_dict[term]
			idx = word_to_idx_dict[term]
			word_vector = tfidfweight * word_embedding_matrix(idx).reshape(1,300)
			weightedqueryterms.append(word_vector)
	query_vec = sum(weightedqueryterms)
	#what ????

#TODO: parses through input for country preference and returns list of countries 
def get_country_list(country_input):
	country_list = country_input.split(',')

	if len(country_list) == 0 or (len(country_list) == 1 and 'No preference' in country_list):
		country_list = country_to_idx_dict.keys()
	
	if 'No preference' in country_list:
		country_list.remove('No preference')

	return country_list

def get_cos_sim(query):
	"""
	input: string- the users input
	reviews: user reviews (wine_dict)
	relevant_doc_index: list of relevant docs
	returns: {index: score}
	"""
	query = query.reshape(1, -1) 
	#TODO: do cos sim with tfidf_embeddings_matrix
	cos_sims = cosine_similarity(tfidf_embedding_matrix, query)
	return cos_scores

#TODO: repurpose this to take in cos_sim values and queried countries and return the top 3 distinct regions and associated wineries
def get_top_results(scores_array, country_list):
	"""
	get frequencies of the top 5 locations
	return {location : (frequency, [index])}
	"""
	results = {}
	for country in country_list:
		results[country] = []
		country_idx = country_to_idx_dict[country]
		scores_subset = scores_array[country_idx]
		sorted_args = np.argsort(scores_subset)
		sorted_args = np.flip(sorted_args)
		sorted_idxs = [country_idx[i] for i in sorted_args]

		i = 0
		prov_list = []
		while i < len(sorted_idxs) and results[country] < 3:
			idx = sorted_idxs[i]
			prov_string = ''
			region1 = wine_dict[idx]['region_1']
			prov = wine_dict[idx]['province']
			if region1 == 'NaN':
				prov_string = prov
			else:
				prov_string = "{}, {}".format(region1, prov)
			
			if prov_string not in prov_list:
				prov_list.append(prov_string)
				province_dict = {'province': prov_string, 
				'winery': wine_dict[idx]['winery'], 'variety': wine_dict[idx]['variety'], 
				'review':wine_dict[idx]['description']}

				results[country].append(province_dict)
		
			i = i+1

	return results

def cos_sim_reviews(query_input, country_input):
	"""
	input_terms: string inputted query
	wine_tfidf_matrix: vector of the words in the various

	returns a dictionary of locations in format {location : [(score, row_number)]} 
	"""
	# call create_OR_list and get list of releveant index
	# do cos_sim for the relevant docs  call get_cos_sim (return as a dict)
	# create tuple list from get_cos_sim
	# go through and create  {location : [(score, row_number)]} for top 100 cos_sim results
	# get frequency each location in the top 100 {location : (score, [index])}
	
	
	query_vec = query_vectorizer(query_input)
	country_list = get_country_list(country_input)
	cos_scores = get_cos_sim(query_vec)
	results = get_top_results(cos_scores, country_list)
	results_json = json.dumps(results)
	print("OUTPUTTTTTTTT")
	print(results_json)
	return results_json




