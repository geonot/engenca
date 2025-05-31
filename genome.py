import os
import random

class Genome:
    def __init__(self, size: int = 1024, data: bytes | None = None):
        if data is not None:
            self.data = data
        else:
            if size < 0:
                raise ValueError("Size cannot be negative")
            self.data = os.urandom(size)

    def get_gene(self, start_index: int, length: int) -> bytes | None:
        if not (0 <= start_index < len(self.data)) or not (0 < length) or not (start_index + length <= len(self.data)):
            raise IndexError("Invalid start_index or length for get_gene")
        return self.data[start_index : start_index + length]

    def mutate_byte(self, index: int, new_byte_value: int | None = None) -> None:
        if not (0 <= index < len(self.data)):
            raise IndexError("Index out of bounds for mutate_byte")

        temp_data = bytearray(self.data)
        if new_byte_value is not None:
            if not (0 <= new_byte_value <= 255):
                raise ValueError("new_byte_value must be between 0 and 255")
            temp_data[index] = new_byte_value
        else:
            temp_data[index] = random.randint(0, 255)
        self.data = bytes(temp_data)

    def __len__(self) -> int:
        return len(self.data)

    def __str__(self) -> str:
        # Represent as a hex string. For very long genomes,
        # a truncated or summarized representation might be better.
        return self.data.hex()

if __name__ == '__main__':
    # Example Usage
    print("Creating a random genome of default size (1024 bytes)...")
    genome1 = Genome()
    print(f"Genome 1 length: {len(genome1)}")
    # print(f"Genome 1 data (first 20 bytes as hex): {genome1.data[:20].hex()}...") # Truncated for display
    print(f"Genome 1 data (first 64 chars of hex string): {str(genome1)[:64]}...")


    print("\nCreating a genome with specific data...")
    custom_data = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a'
    genome2 = Genome(data=custom_data)
    print(f"Genome 2 length: {len(genome2)}")
    print(f"Genome 2 data: {str(genome2)}")

    print("\nGetting a gene from Genome 2...")
    try:
        gene_segment = genome2.get_gene(start_index=2, length=4)
        print(f"Gene segment (index 2, length 4): {gene_segment.hex()}")
    except IndexError as e:
        print(f"Error getting gene: {e}")

    print("\nTrying to get an invalid gene segment...")
    try:
        invalid_gene = genome2.get_gene(start_index=8, length=5) # This will go out of bounds
        print(f"Invalid gene segment: {invalid_gene.hex()}")
    except IndexError as e:
        print(f"Error getting gene: {e}")

    print("\nMutating a byte in Genome 2 (index 3 to 0xff)...")
    genome2.mutate_byte(index=3, new_byte_value=0xff)
    print(f"Genome 2 data after mutation: {str(genome2)}")

    print("\nMutating a byte in Genome 2 (index 0 to a random value)...")
    original_byte_0 = genome2.data[0]
    genome2.mutate_byte(index=0)
    print(f"Genome 2 data after random mutation at index 0 (was {original_byte_0:02x}): {str(genome2)}")

    print("\nTrying to mutate with an invalid byte value...")
    try:
        genome2.mutate_byte(index=1, new_byte_value=300)
    except ValueError as e:
        print(f"Error mutating byte: {e}")

    print("\nTrying to mutate at an invalid index...")
    try:
        genome2.mutate_byte(index=100) # genome2 is small
    except IndexError as e:
        print(f"Error mutating byte: {e}")

    print("\nCreating a zero-size genome (allowed if data is not None, but os.urandom(0) is fine)...")
    genome_zero_random = Genome(size=0)
    print(f"Genome zero_random length: {len(genome_zero_random)}")
    print(f"Genome zero_random data: {str(genome_zero_random)}")

    print("\nTrying to create a genome with negative size...")
    try:
        genome_neg_size = Genome(size=-10)
    except ValueError as e:
        print(f"Error creating genome: {e}")

    print("\nTesting get_gene with edge cases...")
    genome_edge = Genome(data=b"abcdefghij") # 10 bytes
    try:
        print(f"Gene (0,1): {genome_edge.get_gene(0,1).decode()}")
        print(f"Gene (0,10): {genome_edge.get_gene(0,10).decode()}")
        # print(f"Gene (9,1): {genome_edge.get_gene(9,1).decode()}") # This should be fine
    except IndexError as e:
        print(f"Error in edge case test: {e}")

    print("\nTrying get_gene that goes out of bounds...")
    try:
        genome_edge.get_gene(5, 6) # 5+6 = 11, data is 10 bytes
    except IndexError as e:
        print(f"Correctly caught error: {e}")

    print("\nTrying get_gene with zero length...")
    try:
        genome_edge.get_gene(5, 0)
    except IndexError as e:
        print(f"Correctly caught error for zero length: {e}")

    print("\nTrying get_gene with negative start index...")
    try:
        genome_edge.get_gene(-1, 5)
    except IndexError as e:
        print(f"Correctly caught error for negative start index: {e}")
