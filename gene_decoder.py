from genome import Genome # Assuming genome.py is in the same directory or Python path

def decode_simple_attribute(genome: Genome, gene_start: int, gene_length: int, attribute_options: list | tuple) -> str | None:
    """
    Decodes a gene segment to select an attribute from a list of options.

    Args:
        genome: The Genome object to read from.
        gene_start: The starting index of the gene in the genome.
        gene_length: The length of the gene.
        attribute_options: A list or tuple of possible attribute values.

    Returns:
        The selected attribute option string, or None if an error occurs
        (e.g., invalid gene segment, empty attribute_options).
    """
    if not attribute_options:
        # print("Error: attribute_options list is empty.")
        return None

    try:
        gene_bytes = genome.get_gene(gene_start, gene_length)
    except IndexError:
        # print(f"Error: Could not retrieve gene at start {gene_start} with length {gene_length}.")
        return None

    if not gene_bytes: # Should not happen if get_gene raises IndexError or returns valid bytes
        return None

    sum_of_bytes = sum(gene_bytes)
    selected_index = sum_of_bytes % len(attribute_options)
    return attribute_options[selected_index]


def decode_interacting_genes(
    genome: Genome,
    gene1_start: int, gene1_length: int,
    gene2_start: int, gene2_length: int,
    max_value: int
) -> int | None:
    """
    Decodes two interacting gene segments to produce a numerical value scaled by max_value.

    Args:
        genome: The Genome object to read from.
        gene1_start: The starting index of the first gene.
        gene1_length: The length of the first gene.
        gene2_start: The starting index of the second gene.
        gene2_length: The length of the second gene.
        max_value: The maximum value for the resulting attribute (exclusive for modulo).
                   Must be a positive integer.

    Returns:
        The calculated numerical value, or None if an error occurs
        (e.g., invalid gene segments, non-positive max_value).
    """
    if max_value <= 0:
        # print("Error: max_value must be a positive integer.")
        return None

    try:
        gene1_bytes = genome.get_gene(gene1_start, gene1_length)
        gene2_bytes = genome.get_gene(gene2_start, gene2_length)
    except IndexError:
        # print("Error: Could not retrieve one or both gene segments.")
        return None

    if not gene1_bytes or not gene2_bytes: # Should not happen
        return None

    sum_gene1 = sum(gene1_bytes)
    sum_gene2 = sum(gene2_bytes)

    # Combine the information. Using multiplication as an example.
    # Ensure sums are not zero if multiplication is used and could lead to all zeros.
    # For this example, we'll proceed directly.
    combined_value = sum_gene1 * sum_gene2

    # Scale the result to be within 0 and max_value-1
    final_value = combined_value % max_value
    return final_value


if __name__ == '__main__':
    # Example Usage
    print("Setting up a test genome...")
    # Create a predictable genome for testing
    test_data_list = [i for i in range(256)] * 4 # 1024 bytes, repeating 0-255 sequence
    test_data = bytes(test_data_list)
    test_genome = Genome(data=test_data)
    print(f"Test genome length: {len(test_genome)}")

    print("\n--- Testing decode_simple_attribute ---")
    colors = ["red", "green", "blue", "yellow", "purple"]

    # Gene 1: bytes 0-9. Sum = 0+1+...+9 = 45. 45 % 5 = 0 ("red")
    attr1 = decode_simple_attribute(test_genome, gene_start=0, gene_length=10, attribute_options=colors)
    print(f"Gene (0,10) -> Sum=45 -> Index=0: Expected 'red', Got '{attr1}'")

    # Gene 2: bytes 10-14. Sum = 10+11+12+13+14 = 60. 60 % 5 = 0 ("red")
    # This shows how different genes can result in the same attribute
    attr2 = decode_simple_attribute(test_genome, gene_start=10, gene_length=5, attribute_options=colors)
    print(f"Gene (10,5) -> Sum=60 -> Index=0: Expected 'red', Got '{attr2}'")

    # Gene 3: bytes 250-259 (wraps around the 0-255 sequence for test_data)
    # test_data[250:260] will be [250, 251, 252, 253, 254, 255, 0, 1, 2, 3]
    # Sum = 250+251+252+253+254+255+0+1+2+3 = 1521. 1521 % 5 = 1 ("green")
    attr3 = decode_simple_attribute(test_genome, gene_start=250, gene_length=10, attribute_options=colors)
    print(f"Gene (250,10) -> Sum=1521 -> Index=1: Expected 'green', Got '{attr3}'")

    print("\nError handling for decode_simple_attribute:")
    # Empty attribute options
    attr_err1 = decode_simple_attribute(test_genome, 0, 10, [])
    print(f"Empty options: Expected None, Got {attr_err1}")

    # Gene out of bounds
    attr_err2 = decode_simple_attribute(test_genome, 1000, 50, colors) # Genome is 1024 bytes
    print(f"Gene out of bounds: Expected None, Got {attr_err2}")

    print("\n--- Testing decode_interacting_genes ---")
    # Gene A: bytes 0-3. Sum = 0+1+2+3 = 6
    # Gene B: bytes 10-13. Sum = 10+11+12+13 = 46
    # Combined = 6 * 46 = 276
    # Max value = 100. 276 % 100 = 76
    val1 = decode_interacting_genes(test_genome,
                                    gene1_start=0, gene1_length=4,
                                    gene2_start=10, gene2_length=4,
                                    max_value=100)
    print(f"Genes (0,4) Sum=6 and (10,4) Sum=46 -> Combined=276 -> Expected 76 (mod 100), Got {val1}")

    # Max value = 276. 276 % 276 = 0
    val2 = decode_interacting_genes(test_genome,
                                    gene1_start=0, gene1_length=4,
                                    gene2_start=10, gene2_length=4,
                                    max_value=276)
    print(f"Genes (0,4) and (10,4) -> Combined=276 -> Expected 0 (mod 276), Got {val2}")

    # Gene C: bytes 255. Sum = 255
    # Gene D: bytes 256 (value 0). Sum = 0
    # Combined = 255 * 0 = 0
    # Max value = 50. 0 % 50 = 0
    val3 = decode_interacting_genes(test_genome,
                                    gene1_start=255, gene1_length=1,
                                    gene2_start=256, gene2_length=1,
                                    max_value=50)
    print(f"Genes (255,1) Sum=255 and (256,1) Sum=0 -> Combined=0 -> Expected 0 (mod 50), Got {val3}")


    print("\nError handling for decode_interacting_genes:")
    # Gene1 out of bounds
    inter_err1 = decode_interacting_genes(test_genome, 1020, 10, 0, 5, 100)
    print(f"Gene1 out of bounds: Expected None, Got {inter_err1}")

    # Gene2 out of bounds
    inter_err2 = decode_interacting_genes(test_genome, 0, 5, 1020, 10, 100)
    print(f"Gene2 out of bounds: Expected None, Got {inter_err2}")

    # max_value = 0
    inter_err3 = decode_interacting_genes(test_genome, 0, 5, 10, 5, 0)
    print(f"max_value=0: Expected None, Got {inter_err3}")

    # max_value = -10
    inter_err4 = decode_interacting_genes(test_genome, 0, 5, 10, 5, -10)
    print(f"max_value=-10: Expected None, Got {inter_err4}")

    print("\nTesting with a zero-length genome (if possible, though Genome likely prevents this for random)")
    try:
        zero_len_genome_data = Genome(data=b"")
        # This should ideally not work with get_gene if gene_length > 0
        attr_zero = decode_simple_attribute(zero_len_genome_data, 0, 0, ["optionA"])
        print(f"decode_simple_attribute with zero-length genome and zero-length gene: {attr_zero}")
        # The Genome's get_gene method has: `if not (0 < length)` which means length=0 is an error.
        # So this will result in None due to IndexError.
    except Exception as e:
        print(f"Error with zero-length genome test: {e}")


    # Test case: genome.get_gene returns a gene of length less than requested (not possible with current get_gene)
    # or if gene_bytes is empty for some reason (also not likely with current get_gene)
    # This is mostly defensive coding in the decoders.
    print("\nTesting decode_simple_attribute with a gene that is valid but all zeros (sum=0)")
    # Gene: bytes at 256, 257, 258. test_data[256] = 0, test_data[257]=1, test_data[258]=2
    # If we took a gene of all 0s (e.g. by mutating the genome).
    # Let's use a gene segment that sums to a multiple of len(attribute_options)
    # Gene: bytes 0-4 -> sum = 0+1+2+3+4 = 10. colors len = 5. 10 % 5 = 0 ("red")
    attr_sum_multiple = decode_simple_attribute(test_genome, 0, 5, colors)
    print(f"Gene (0,5) -> Sum=10 -> Index=0: Expected 'red', Got '{attr_sum_multiple}'")

    print("\nTesting decode_simple_attribute with a single option")
    single_option = ["lonely_choice"]
    attr_single = decode_simple_attribute(test_genome, 0, 1, single_option) # sum(test_data[0]) % 1 = 0 % 1 = 0
    print(f"Gene (0,1) with single option: Expected '{single_option[0]}', Got '{attr_single}'")

    print("Done with gene_decoder.py examples.")
