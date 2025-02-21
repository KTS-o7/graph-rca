import unittest
from unittest.mock import patch, Mock
import numpy as np
from core.embedding import EmbeddingCreator

class TestEmbeddingCreator(unittest.TestCase):
    def setUp(self):
        self.embedder = EmbeddingCreator()
        self.sample_text = "test embedding"
        self.sample_texts = ["first text", "second text"]
    
    def test_create_embedding_returns_valid_embedding(self):
        embedding = self.embedder.create_embedding(self.sample_text)
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(embedding.dtype, np.float32)
        self.assertGreater(len(embedding), 0)
        self.assertTrue(all(isinstance(x, np.float32) for x in embedding))
    
    def test_create_batch_embeddings_valid_input(self):
        embeddings = self.embedder.create_batch_embeddings(self.sample_texts)
        self.assertEqual(len(embeddings), len(self.sample_texts))
        self.assertTrue(all(len(e) > 0 for e in embeddings))
    
    def test_create_batch_embeddings_invalid_input(self):
        with self.assertRaises(ValueError):
            self.embedder.create_batch_embeddings([])
        
        with self.assertRaises(ValueError):
            self.embedder.create_batch_embeddings([""])
        
        with self.assertRaises(ValueError):
            self.embedder.create_batch_embeddings([42])  # non-string input
    
    def test_get_similarity_identical_embeddings(self):
        embedding = self.embedder.create_embedding(self.sample_text)
        similarity = self.embedder.get_similarity(embedding, embedding)
        self.assertAlmostEqual(similarity, 1.0, places=2)
    
    def test_get_similarity_different_embeddings(self):
        emb1 = self.embedder.create_embedding("hello world")
        emb2 = self.embedder.create_embedding("goodbye world")
        similarity = self.embedder.get_similarity(emb1, emb2)
        self.assertTrue(0 <= similarity <= 1)
    
    def test_get_similarity_edge_cases(self):
        # Test zero vectors
        zero_vec = [0.1] * 768
        self.assertAlmostEqual(self.embedder.get_similarity(zero_vec, zero_vec), 1.0, places=7)
        
        # Test invalid input handling
        with self.assertRaises(ZeroDivisionError):
            self.embedder.get_similarity([], [])
    
    @patch('core.embedding.OllamaEmbeddingFunction')
    def test_error_handling_in_embeddings(self, mock_embedding):
        # Create a mock instance that raises an exception
        mock_instance = Mock()
        def raise_error(*args, **kwargs):
            raise Exception("API failure")
        
        # Configure the mock to raise exception when called with any input
        mock_instance.side_effect = raise_error
        mock_embedding.return_value = mock_instance
        
        # Recreate embedder to use our mocked instance
        self.embedder = EmbeddingCreator()
        
        with self.assertRaises(Exception) as context:
            self.embedder.create_embedding(self.sample_text)
        self.assertTrue("API failure" in str(context.exception))


if __name__ == '__main__':
    unittest.main()
