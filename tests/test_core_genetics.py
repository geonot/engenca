import sys
import os
import unittest
import io
from contextlib import redirect_stdout

# Adjust sys.path to include the parent directory (root of the project)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from genome import Genome
from gene_decoder import decode_simple_attribute, decode_interacting_genes
from organism import Organism

class TestCoreGenetics(unittest.TestCase):

    # --- Genome Tests ---
    def test_genome_creation_specific_size(self):
        g = Genome(size=100)
        self.assertEqual(len(g), 100)

    def test_genome_creation_default_size(self):
        g = Genome() # Default size is 1024
        self.assertEqual(len(g), 1024)

    def test_genome_creation_specific_data(self):
        data = b'\x01\x02\x03\x04\x05'
        g = Genome(data=data)
        self.assertEqual(g.data, data)
        self.assertEqual(len(g), len(data))

    def test_genome_creation_negative_size_error(self):
        with self.assertRaises(ValueError):
            Genome(size=-10)

    def test_get_gene_valid(self):
        data = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09'
        g = Genome(data=data)
        self.assertEqual(g.get_gene(start_index=2, length=4), b'\x02\x03\x04\x05')
        self.assertEqual(g.get_gene(start_index=0, length=len(data)), data) # Whole genome

    def test_get_gene_out_of_bounds(self):
        data = b'\x00\x01\x02\x03\x04'
        g = Genome(data=data)
        with self.assertRaises(IndexError):
            g.get_gene(start_index=3, length=3) # Goes past end
        with self.assertRaises(IndexError):
            g.get_gene(start_index=5, length=1) # Starts past end
        with self.assertRaises(IndexError):
            g.get_gene(start_index=-1, length=2) # Negative start
        with self.assertRaises(IndexError):
            g.get_gene(start_index=0, length=0) # Zero length (as per Genome implementation)
        with self.assertRaises(IndexError):
            g.get_gene(start_index=0, length=len(data) + 1) # Length too long

    def test_mutate_byte_random(self):
        g = Genome(size=10)
        original_byte = g.data[5]
        g.mutate_byte(index=5) # Random mutation
        self.assertNotEqual(g.data[5], original_byte, "Byte should ideally change (low chance of random same value)")
        self.assertEqual(len(g.data), 10) # Length should be preserved

    def test_mutate_byte_specific_value(self):
        g = Genome(size=10)
        g.mutate_byte(index=5, new_byte_value=0xAB)
        self.assertEqual(g.data[5], 0xAB)
        self.assertEqual(len(g.data), 10)

    def test_mutate_byte_invalid_index(self):
        g = Genome(size=10)
        with self.assertRaises(IndexError):
            g.mutate_byte(index=10) # Out of bounds
        with self.assertRaises(IndexError):
            g.mutate_byte(index=-1) # Out of bounds

    def test_mutate_byte_invalid_value(self):
        g = Genome(size=10)
        with self.assertRaises(ValueError):
            g.mutate_byte(index=0, new_byte_value=256)
        with self.assertRaises(ValueError):
            g.mutate_byte(index=0, new_byte_value=-1)

    def test_genome_str_representation(self):
        data = b'\x01\x02\x03\x04'
        g = Genome(data=data)
        self.assertEqual(str(g), data.hex())

    # --- Gene Decoder Tests ---
    def test_decode_simple_attribute_valid(self):
        # Color gene: 0,1,2,3. Sum = 6. colors len = 5. 6 % 5 = 1 ("green")
        gene_data = bytes([0,1,2,3, 0,0,0,0]) # Padded to avoid issues if Organism constants are used
        g = Genome(data=gene_data)
        colors = ["red", "green", "blue", "yellow", "purple"]
        # Using fixed indices for this direct test, not Organism constants
        decoded_color = decode_simple_attribute(g, gene_start=0, gene_length=4, attribute_options=colors)
        self.assertEqual(decoded_color, "green")

    def test_decode_simple_attribute_empty_options(self):
        g = Genome(size=10)
        decoded_attr = decode_simple_attribute(g, 0, 4, [])
        self.assertIsNone(decoded_attr)

    def test_decode_simple_attribute_gene_retrieval_fail(self):
        g = Genome(size=2) # Too small for gene_length=4
        colors = ["red", "green", "blue"]
        decoded_attr = decode_simple_attribute(g, 0, 4, colors)
        self.assertIsNone(decoded_attr)

    def test_decode_interacting_genes_valid(self):
        # Gene1: 0,1 (sum=1). Gene2: 2,3 (sum=5). Combined = 1*5=5. Max_value=10. 5%10 = 5
        gene_data = bytes([0,1, 2,3, 0,0,0,0])
        g = Genome(data=gene_data)
        # Using fixed indices for this direct test
        decoded_value = decode_interacting_genes(g, 0, 2, 2, 2, max_value=10)
        self.assertEqual(decoded_value, 5)

    def test_decode_interacting_genes_max_value_zero_or_negative(self):
        g = Genome(size=10)
        self.assertIsNone(decode_interacting_genes(g, 0, 1, 1, 1, max_value=0))
        self.assertIsNone(decode_interacting_genes(g, 0, 1, 1, 1, max_value=-5))

    def test_decode_interacting_genes_retrieval_fail(self):
        g = Genome(size=3) # gene2_start=2, gene2_length=2 is out of bounds
        self.assertIsNone(decode_interacting_genes(g, 0, 2, 2, 2, max_value=10))

    # --- Organism Tests ---
    def test_organism_creation_default_genome(self):
        org = Organism()
        self.assertIsInstance(org.genome, Genome)
        self.assertEqual(len(org.genome), 1024) # Default Organism genome size might differ from Genome default
                                                # Let's check organism.py: default is 1024
        self.assertIn('color', org.attributes)
        self.assertIn('size', org.attributes)

    def test_organism_creation_specific_genome_size(self):
        # Organism.MIN_GENOME_SIZE is 8
        org = Organism(genome_size=Organism.MIN_GENOME_SIZE)
        self.assertIsInstance(org.genome, Genome)
        self.assertEqual(len(org.genome), Organism.MIN_GENOME_SIZE)
        self.assertIn('color', org.attributes)
        self.assertIn('size', org.attributes)

    def test_organism_creation_with_provided_genome(self):
        # For color: bytes 0-3. Sum = 0+1+2+3 = 6. 6 % 10 (COLOR_OPTIONS len) = 6 ('pink')
        # For size: gene1 (bytes 4-5): 10+11=21. gene2 (bytes 6-7): 20+21=41.
        # (21 * 41) % 100 = 861 % 100 = 61.
        custom_data = bytes([0,1,2,3, 10,11, 20,21]) # Exactly MIN_GENOME_SIZE
        custom_genome = Genome(data=custom_data)
        org = Organism(genome_instance=custom_genome)

        self.assertIs(org.genome, custom_genome)
        self.assertEqual(org.attributes.get('color'), Organism.COLOR_OPTIONS[6]) # 'pink'
        self.assertEqual(org.attributes.get('size'), 61)

    def test_organism_creation_genome_size_too_small_for_attributes(self):
        # Organism constructor adjusts size up if genome_size < MIN_GENOME_SIZE
        org = Organism(genome_size=4) # MIN_GENOME_SIZE is 8
        self.assertEqual(len(org.genome), Organism.MIN_GENOME_SIZE)
        self.assertIsNotNone(org.attributes.get('color')) # Should be decodable
        self.assertIsNotNone(org.attributes.get('size'))  # Should be decodable

    def test_organism_creation_provided_genome_too_small(self):
        small_genome = Genome(data=b'\x01\x02\x03') # Too small for default attributes
        with self.assertRaises(ValueError):
            Organism(genome_instance=small_genome)

    def test_organism_display_attributes(self):
        custom_data = bytes([0,1,2,3, 10,11, 20,21])
        custom_genome = Genome(data=custom_data)
        org = Organism(genome_instance=custom_genome)
        # Expected: Color: pink, Size: 61

        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            org.display_attributes()
        output_str = captured_output.getvalue()

        self.assertIn("Organism Attributes:", output_str)
        self.assertIn(f"Color: {Organism.COLOR_OPTIONS[6]}", output_str) # pink
        self.assertIn("Size: 61", output_str)

    def test_organism_str_representation(self):
        org = Organism(genome_size=Organism.MIN_GENOME_SIZE)
        org_str = str(org)
        self.assertIn("Organism(Genome:", org_str)
        self.assertIn("Attributes:", org_str)
        self.assertIn("'color':", org_str)
        self.assertIn("'size':", org_str)

if __name__ == '__main__':
    unittest.main()
