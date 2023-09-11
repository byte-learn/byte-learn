from abc import ABC, abstractmethod
import numpy as np
import torch
import json
import fasttext
from joblib import load
from gensim.models import KeyedVectors
from nlplay.models.pytorch.classifiers.dpcnn import DPCNN
from nlplay.models.pytorch.pretrained import get_pretrained_vecs
from keras_preprocessing import sequence

import warnings
warnings.simplefilter(action='ignore', category=Warning)


class Classifier(ABC):
	@abstractmethod
	def __init__(self, model_path: str):
		self.model_path = model_path

	@abstractmethod
	def _load_model(self):
		pass

	def _transform_input(self, bytecode):
		pass

	@abstractmethod
	def predict(self, bytecode):
		pass


class DPCNNClassifier(Classifier):
	def __init__(self, model_path: str, pretrained_vec: str, target_vocab_file: str, device: str = "cuda:0"):
		super().__init__(model_path)
		self.max_seq = 280000
		self.embedding_size = 100
		self.kernel_size=51
		self.stride=15
		self.device = device
		self.checkpoint_file = model_path 
		self.pretrained_vec = pretrained_vec 
		self.target_vocab_file = target_vocab_file 
		self.model = self._load_model()
		self.model.eval()

	def _load_model(self):
		torch.cuda.empty_cache()
		use_cuda = torch.cuda.is_available()
		device = torch.device(self.device if use_cuda else "cpu")
		torch.cuda.set_device(device)

		with open(self.target_vocab_file, 'r') as f:
			self.target_vocab = json.load(f)

		vectors = get_pretrained_vecs(input_vec_file=self.pretrained_vec, target_vocab=self.target_vocab, dim=self.embedding_size, output_file=None)
		row_len = len(vectors[0])
		vectors = np.concatenate((vectors, [np.zeros(row_len)]))
		vocab_size = len(self.target_vocab) + 1
		self.pad_index = vocab_size - 1
		model = DPCNN(
			vocabulary_size=vocab_size, 
			num_classes=2, 
			embedding_size=self.embedding_size,
			kernel_size=self.kernel_size, 
			pooling_stride=self.stride, 
			pretrained_vec=vectors, 
			one_by_one=True)

		checkpoint = torch.load(self.checkpoint_file, map_location=device)
		checkpoint["model"] = {k.replace("module.", ""): v for k,v in checkpoint["model"].items()}

		model.load_state_dict(checkpoint["model"])
		model = model.to(device)
		self.device = device
		return model

	def _transform_input(self, bytecode):
		bytecode = [_.strip() for _ in bytecode.split()]
		ix_bytecode = [int(self.target_vocab[word]) for word in bytecode if word in self.target_vocab]
		return ix_bytecode

	def predict(self, bytecode):
		bytecode = self._transform_input(bytecode)
		X = np.array(bytecode[:self.max_seq], dtype=int)
		X = sequence.pad_sequences([X], maxlen=self.max_seq, padding='post', value=self.pad_index)
		X = torch.tensor(X[0], dtype=torch.long)
		X = X.reshape((1, self.max_seq))
		X = X.to(self.device)
		with torch.set_grad_enabled(False):
			out = self.model(X)
			_, predicted_label = torch.max(out.data, 1)
		
		return predicted_label.item() 


class FastTextClassifier(Classifier):
	def __init__(self, model_path: str):
		super().__init__(model_path)
		self.model = self._load_model()

	def _load_model(self):
		return fasttext.load_model(self.model_path)

	def predict(self, bytecode):
		predicted_label = self.model.predict(bytecode)[0][0]
		return 1 if predicted_label == '__label__1' else 0


class RFClassifier(Classifier):
	def __init__(self, model_path: str, keyed_vector_path: str):
		super().__init__(model_path)
		self.keyed_vector_path = keyed_vector_path
		self.model = self._load_model()

	def _load_model(self):	
		self.keyed_vector = KeyedVectors.load(self.keyed_vector_path)
		return load(self.model_path)

	def _mean(self, bytecode):
		return np.mean([self.keyed_vector.get_vector(_) for _ in bytecode.split()], axis=0)

	def _transform_input(self, bytecode):
		return self._mean(bytecode)

	def predict(self, bytecode):
		bytecode = self._transform_input(bytecode)
		predicted_label = self.model.predict([bytecode])
		return 1 if predicted_label[0] == 1 else 0




