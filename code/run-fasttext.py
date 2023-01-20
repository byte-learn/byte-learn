import fasttext
import argparse



if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--train", help="Path to train file", required=True)
	parser.add_argument("--test",  help="Path to test file", required=True)
	parser.add_argument("--ngram", help="wordNgrams", required=True)
	parser.add_argument("--epoch", help="Number of epochs", required=True)
	args = parser.parse_args()

	print(f"Running with {args.ngram} ngrams and {args.epoch} epochs on {args.train}")
	model = fasttext.train_supervised(args.train, wordNgrams = int(args.ngram), loss='hs', dim=100, lr=1.0, epoch=int(args.epoch), ws=10)
	model.save_model(f"fasttext_model_{args.ngram}_{args.epoch}")
	print(model.test_label(args.test))
	

