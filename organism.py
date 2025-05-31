from genome import Genome
from gene_decoder import decode_simple_attribute, decode_interacting_genes

class Organism:
    # Predefined gene locations and options for demonstration
    # These could be made more flexible (e.g., passed to constructor or class variables)
    COLOR_GENE_START = 0
    COLOR_GENE_LENGTH = 4
    COLOR_OPTIONS = ['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'pink', 'brown', 'black', 'white']

    SIZE_GENE1_START = COLOR_GENE_START + COLOR_GENE_LENGTH # Ensure no overlap, start after color gene
    SIZE_GENE1_LENGTH = 2
    SIZE_GENE2_START = SIZE_GENE1_START + SIZE_GENE1_LENGTH # Start after size gene 1
    SIZE_GENE2_LENGTH = 2
    SIZE_MAX_VALUE = 100 # For scaling the size attribute

    # Ensure gene locations are valid for a minimum genome size
    MIN_GENOME_SIZE = SIZE_GENE2_START + SIZE_GENE2_LENGTH

    def __init__(self, genome_size: int = 1024, genome_instance: Genome | None = None):
        if genome_instance is not None and isinstance(genome_instance, Genome):
            if len(genome_instance) < self.MIN_GENOME_SIZE:
                raise ValueError(
                    f"Provided genome is too small ({len(genome_instance)} bytes). "
                    f"Minimum required size is {self.MIN_GENOME_SIZE} bytes for predefined attributes."
                )
            self.genome = genome_instance
        else:
            if genome_size < self.MIN_GENOME_SIZE:
                print(
                    f"Warning: Requested genome_size ({genome_size}) is less than MIN_GENOME_SIZE "
                    f"({self.MIN_GENOME_SIZE}). Adjusting to minimum size."
                )
                genome_size = self.MIN_GENOME_SIZE
            self.genome = Genome(size=genome_size)

        self.attributes = {}
        self.decode_attributes()

    def decode_attributes(self):
        """
        Decodes the organism's genome to populate its attributes.
        """
        # Decode 'color'
        self.attributes['color'] = decode_simple_attribute(
            self.genome,
            self.COLOR_GENE_START,
            self.COLOR_GENE_LENGTH,
            self.COLOR_OPTIONS
        )

        # Decode 'size'
        self.attributes['size'] = decode_interacting_genes(
            self.genome,
            self.SIZE_GENE1_START,
            self.SIZE_GENE1_LENGTH,
            self.SIZE_GENE2_START,
            self.SIZE_GENE2_LENGTH,
            self.SIZE_MAX_VALUE
        )

        # Add more attribute decoding here as needed

    def display_attributes(self) -> None:
        """
        Prints the organism's attributes in a readable format.
        """
        print("Organism Attributes:")
        if not self.attributes:
            print("  No attributes decoded.")
            return
        for key, value in self.attributes.items():
            print(f"  {key.capitalize()}: {value if value is not None else 'N/A'}")

    def __str__(self) -> str:
        genome_str_preview = str(self.genome)[:32] + "..." if len(str(self.genome)) > 32 else str(self.genome)
        return f"Organism(Genome: {genome_str_preview}, Attributes: {self.attributes})"

if __name__ == '__main__':
    print("Creating a new organism with default genome size (1024)...")
    org1 = Organism()
    print(org1)
    org1.display_attributes()

    print("\nCreating a new organism with a specific small genome size (e.g., 50)...")
    # Note: MIN_GENOME_SIZE is 8. If 50 is given, it's fine.
    # If a size less than MIN_GENOME_SIZE is given, it will be adjusted.
    org2 = Organism(genome_size=50)
    print(org2)
    org2.display_attributes()

    print("\nCreating a new organism with a custom (predictable) genome...")
    # Minimum size for these attributes is 4+2+2 = 8 bytes
    # Data: [0,1,2,3, 10,11, 20,21, ...]
    # Color gene: 0,1,2,3. Sum = 6. 6 % 10 colors = 6 (pink)
    # Size gene1: 10,11. Sum = 21.
    # Size gene2: 20,21. Sum = 41.
    # Size combined: 21 * 41 = 861. 861 % 100 = 61.
    custom_data = bytes([0,1,2,3, 10,11, 20,21, 0, 0]) # 10 bytes long
    custom_genome = Genome(data=custom_data)
    org3 = Organism(genome_instance=custom_genome)
    print(org3)
    org3.display_attributes()
    # Expected: Color: pink, Size: 61

    print("\nTesting organism with genome smaller than MIN_GENOME_SIZE (creation should warn/adjust)...")
    org4 = Organism(genome_size=4) # Will be adjusted to MIN_GENOME_SIZE = 8
    print(org4) # Genome will be of size 8
    org4.display_attributes()


    print("\nTesting organism with a provided genome that is too small (should raise ValueError)...")
    try:
        small_custom_data = bytes([0,1,2,3]) # Only 4 bytes
        small_custom_genome = Genome(data=small_custom_data)
        org5 = Organism(genome_instance=small_custom_genome)
        print(org5)
    except ValueError as e:
        print(f"Correctly caught error: {e}")

    print("\nDemonstrating mutation and re-decoding (optional advanced concept)...")
    # Mutate org3's genome and see if attributes change
    # Original org3: Color: pink (idx 6), Size: 61
    # Mutate the first byte (part of color gene) to a large value.
    # e.g., data[0] = 255. Color gene: 255,1,2,3. Sum = 261. 261 % 10 = 1 (green)
    if org3.genome:
        org3.genome.mutate_byte(0, 255) # Mutate first byte
        print(f"Mutated genome for org3 (first byte to 255): {str(org3.genome)[:32]}...")
        org3.decode_attributes() # Re-decode attributes
        print("After mutation and re-decoding:")
        print(org3)
        org3.display_attributes()
        # Expected: Color: green, Size: 61 (size genes unchanged)

    print("\nOrganism with default random genome (attributes will vary):")
    org_random = Organism(genome_size=Organism.MIN_GENOME_SIZE)
    print(org_random)
    org_random.display_attributes()
