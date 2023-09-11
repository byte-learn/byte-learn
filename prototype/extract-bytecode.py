import os
import json
import datetime
import csv
import argparse
from collections import defaultdict
from hashlib import sha1, md5

def get_hash(script):
	return sha1(script.strip().encode('utf-8')).hexdigest()

def get_md5_hash(url):
	return md5(url.strip().encode('utf-8')).hexdigest() 

def save_data(data, word_mapping, output):
	word_map = load_words(word_mapping)
	temp_data = defaultdict(list)
	for d in data:
		temp_data[d["script_url_hash"]].append(d)

	del data
	output_data = list()

	for url_hash in temp_data:
		temp_data[url_hash] = sorted(temp_data[url_hash], key=lambda x: int(x["line_number"]))
		script_bytecode = ' . '.join([''.join(_['bytecode_expression']) for _ in temp_data[url_hash]]) 
		script_bytecode_hash = get_hash(script_bytecode)
		item = temp_data[url_hash][0]
		item["script_bytecode_hash"] = script_bytecode_hash
		script_bytecode = script_bytecode.replace(f" . ", " ")
		item["script_bytecode_expression"] = ' '.join([word_map[word] for word in script_bytecode.split() if word in word_map])
		output_data.append(item)

	# we don't need 2s 
	output_data = [_ for _ in output_data if _["label"] in [0, 1]]
	with open(output, 'w') as f:
		writer = csv.DictWriter(f, fieldnames=["script_url", "script_bytecode_expression", "label"], delimiter='\t', extrasaction='ignore', lineterminator='\n')
		for row in output_data:
			writer.writerow(row)

def extract_byte_expression(bytecode_output): 
	code_start = False
	links, expressions, code_snippets, line_numbers = list(), list(), list(), list()
	code = ""
	for ix, line in enumerate(bytecode_output.split('\n')):
		if code_start:
			code = line.strip()
			code_start = False
		else:
			if line.startswith("[ByteLearn][Bytecode]"):
				expressions.append(' '.join([_.strip() for _ in line.split(':', 1)[1].replace('[', '').replace(']', '').split(',') if _]))
				line_numbers.append(ix)
			
			elif line.startswith("ByteLearn[URL]"):
				link = line.split(':',1)[1].strip()
				links.append(link)
			
		if "ByteLearn[Source][Start]" in line:
			code_start = True	
		elif "ByteLearn[Source][End]" in line:
			code_snippets.append(code)

	return expressions, code_snippets, links, line_numbers


def extract(bytecode_file, puppeteer_links, word_mapping, output):
	with open(bytecode_file, 'r', encoding="utf8", errors='ignore') as f:
		bytecode_output = f.read()
		
	bytecode_expression, code_snippets, links, line_numbers = extract_byte_expression(bytecode_output)
	ad_links, non_ad_links = get_links(puppeteer_links)

	if not ad_links and not non_ad_links:
		return

	data = list()
	for b_e, code, link, line_number in zip(bytecode_expression, code_snippets, links, line_numbers):
		if any(_ in link for _ in ("_puppeteer_", "No URL")) or code == "<No Source>" or any(not _ for _ in  (code ,link)):
			continue 
		if link in non_ad_links:
			label = 0
		elif link in ad_links:
			label = 1
		else:
			label = 2

		data.append({
			"script_url": link, 
			"label": label, 
			"bytecode_expression": b_e, 
			"bytecode_hash": get_hash(b_e), 
			"line_number": line_number,
			"script_url_hash": get_md5_hash(link)
			})

	save_data(data, word_mapping, output)	

def load_words(word_map):
	with open(word_map, 'r') as f:
		return json.load(f)

def get_links(puppeteer_links):
	ads = set()
	non_ads = set()
	with open(puppeteer_links, 'r') as f:
		for line in f:
			item = json.loads(line)
			# ad
			if item["label"]: 
				ads.add(item["script_url"])
			else:
				non_ads.add(item["script_url"])

	return ads, non_ads


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--pup-links", "-p", dest="puppeteer_links", help="File containing puppeteer links.", required=True)
	parser.add_argument("--bytecode-dump", "-b", dest="bytecode_dump", help="bytecode.dump file.", required=True)
	parser.add_argument("--mapping", "-m", dest="word_map", help="File containing word mapping.")
	parser.add_argument("--output", "-o", dest="output", help="Ouput file name storing bytecode.", required=True)
	args = parser.parse_args()

	assert os.path.isfile(args.puppeteer_links)
	assert os.path.isfile(args.bytecode_dump)

	extract(args.bytecode_dump, args.puppeteer_links, args.word_map, args.output)
