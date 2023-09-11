from models import RFClassifier, FastTextClassifier, DPCNNClassifier
import prettytable

model = FastTextClassifier("./artifacts/weights/fasttext_model")

with open("./temp/output-bytecode.log", 'r') as f:
	table = prettytable.PrettyTable(["URL", "Pred", "Filterlist"])
	table.max_width["URL"] = 100
	table.align["URL"] = "l"
	table.hrules = prettytable.ALL
	for line in f:
		url, bytecode, label = line.strip().split('\t')
		table.add_row([url,model.predict(bytecode),label])

print(table)