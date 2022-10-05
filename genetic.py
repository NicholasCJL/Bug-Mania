import struct
import math
import random
import numpy as np


class BugGenome:
    @classmethod
    def new_from_genome(cls, genome):
        colours, weights, biases = genome.get_colour_genes(), genome.get_weight_genes(), genome.get_bias_genes()
        return cls(colours, weights, biases)

    def __init__(self, colours, weights, biases):
        self.genome = colours + weights + biases
        self.colour_segment = (0, len(colours))
        self.weight_segment = (len(colours), len(colours) + len(weights))
        self.bias_segment = (len(self.genome) - len(biases), len(self.genome))

    def get_gene(self, position):
        return self.genome[position]

    def set_gene(self, position, gene):
        self.genome[position] = gene

    def get_colour_genes(self):
        return self.genome[self.colour_segment[0]:self.colour_segment[1]]

    def get_weight_genes(self):
        return self.genome[self.weight_segment[0]:self.weight_segment[1]]

    def get_bias_genes(self):
        return self.genome[self.bias_segment[0]:self.bias_segment[1]]

    def get_gene_segment(self, lower, upper):
        return self.genome[lower:upper]

    def set_gene_segment(self, lower, upper, segment):
        self.genome[lower:upper] = segment

    def get_segment_bounds(self):
        return self.colour_segment, self.weight_segment, self.bias_segment

    def check_NaN(self, default=0):
        """Check if any gene is NaN, changes it to default value if it is"""
        for i, gene in enumerate(self.genome):
            if math.isnan(gene):
                self.genome[i] = default

    def __len__(self):
        return len(self.genome)

    def __eq__(self, other):
        return self.genome == other.genome

    def __str__(self):
        return str(self.genome)


class GeneticController:
    @staticmethod
    def bitflip(x, position):
        """
        :float x: 32-bit float x to flip a single bit in
        :int position: bit position within x to flip the bit in
        :return: 32-bit float with bit flipped
        """
        # convert x to 4 bytes
        floatstring = struct.pack('f', x)
        byte_list = list(struct.unpack('BBBB', floatstring))

        # find byte that bit is in and flip bit with xor
        byte_num, index = divmod(position, 8)
        byte_list[byte_num] ^= 1 << index

        # convert edited bytes back to float
        bytestring = struct.pack('BBBB', *byte_list)
        new_x = struct.unpack('f', bytestring)
        return new_x[0]

    def __init__(self, population, flip_rate=0.0, swap_rate=0.0,
                 shuffle_rate=0.0, shuffle_size=(2, 6),
                 reverse_rate=0.0, reverse_size=(2, 6),
                 noise_rate=0.0, noise_sd=1.0, noise_mean=0.0):
        """
        :param population: List of (individual genomes, fitness)
        :float flip_rate: Rate of bitflip mutation (per gene)
        :float swap_rate: Rate of swap mutation (per gene)
        :float shuffle_rate: Rate of shuffle mutation (per genome)
        :(int, int) shuffle_size: Lower and upper bound of number of genes shuffled
        :float reverse_rate: Rate of reverse mutation (per genome)
        :(int, int) reverse_size: Lower and upper bound of number of genes reversed
        :float noise_rate: Rate of noise added mutation (per gene)
        :float noise_sd: Variance of gaussian distribution noise is sampled from
        :float noise_mean: Mean of gaussian distribution noise is sampled from
        """
        self.population = sorted(population, key=lambda x: x[1], reverse=True)
        self.flip_rate = flip_rate
        self.swap_rate = swap_rate
        self.shuffle_rate = shuffle_rate
        self.shuffle_size = shuffle_size
        self.reverse_rate = reverse_rate
        self.reverse_size = reverse_size
        self.noise_rate = noise_rate
        self.noise_sd = noise_sd
        self.noise_mean = noise_mean

    def generate_children(self):
        print("Performing parent selection.")
        parent_pairs = self.sus_selection()
        print("Performing crossover.")
        children = [(self.crossover(*pair), pair) for pair in parent_pairs]
        print("Mutating genomes.")
        mutated_children = [(self.mutate(child[0]), child[1]) for child in children]
        return mutated_children

    def sus_selection(self):
        """
        Selects and pairs up suitable mates with SUS algorithm
        :return: List of pairs of mates
        """
        total_fitness = sum(f for (_, f) in self.population)
        num_individuals = len(self.population)
        step = total_fitness / num_individuals
        # starting fitness
        start_f = random.random() * step
        # get list of all fitnesses that are selected
        f_list = [start_f + i * step for i in range(num_individuals)]
        # second pass of sus algorithm to pick N more (2N parents for N children)
        start_f_2 = random.random() * step
        f_list.extend([start_f_2 + i * step for i in range(num_individuals)])
        f_list.sort()

        # get individuals that are selected
        keep = {} # dictionary of index of chosen individuals and number of times they appear
        i = 0
        for f in f_list:
            while sum(f for (_, f) in self.population[:i+1]) < f:
                i += 1
            if i in keep:
                keep[i] += 1
            else:
                keep[i] = 1

        # pair them up
        pair_list = []
        keep_list = [[k, v] for k, v in keep.items()]
        while len(keep_list) > 0:
            mate_a = keep_list[0][0]
            # check if mate_a is the only mate left, if so, choose one random individual to mate with
            if len(keep_list) > 1:
                mate_b_index = random.randrange(1, len(keep_list))
                mate_b = keep_list[mate_b_index][0]
                # remove one instance of mate_b from the pool
                keep_list[mate_b_index][1] -= 1
                if keep_list[mate_b_index][1] == 0:
                    keep_list.pop(mate_b_index)
                pair_list.append((self.population[mate_a][0],
                                  self.population[mate_b][0]))
            else:
                other_mate = random.randrange(0, len(self.population))
                while other_mate == mate_a:
                    other_mate = self.population[random.randrange(0, len(self.population))][0]
                pair_list.append((self.population[mate_a][0],
                                  self.population[other_mate][0]))

            # remove one instance of mate_a from the pool
            keep_list[0][1] -= 1
            if keep_list[0][1] == 0:
                keep_list.pop(0)

        return pair_list

    def crossover(self, parent_a, parent_b):
        """
        Performs crossover between genomes of parents A and B
        :BugGenome parent_a: Genome of parent A
        :BugGenome parent_b: Genome of parent B
        :return: Genome of child
        """
        # assign parents to random genes, 50-50 split
        num_genes = len(parent_a)
        random.shuffle(parents := [parent_a, parent_b])
        random.shuffle(random_gene_list := list(range(num_genes)))
        assignments = {}
        split_index = (num_genes + 1) // 2
        for i in range(split_index):
            assignments[random_gene_list[i]] = parents[0]
        for i in range(split_index, num_genes):
            assignments[random_gene_list[i]] = parents[1]

        # assign genes to child genome
        child_genome_flat = []
        for i in range(num_genes):
            child_genome_flat.append(assignments[i].get_gene(i))

        # split child genome into segments
        segments = parent_a.get_segment_bounds() # assume bounds are same for both parents
        child_genome_segmented = []
        for segment in segments:
            child_genome_segmented.append(child_genome_flat[segment[0]:segment[1]])

        return BugGenome(*child_genome_segmented)

    def mutate(self, genome):
        new_genome = BugGenome.new_from_genome(genome)
        genome_length = len(new_genome)
        # gene mutations
        for i in range(genome_length):
            curr_gene = new_genome.get_gene(i)
            if np.random.rand() < self.noise_rate:
                curr_gene += np.random.normal(self.noise_mean, self.noise_sd)
            if np.random.rand() < self.flip_rate:
                curr_gene = GeneticController.bitflip(curr_gene, np.random.randint(0, 32))
            if np.random.rand() < self.swap_rate:
                swap_index = np.random.randint(0, genome_length)
                swap_gene = new_genome.get_gene(swap_index)
                new_genome.set_gene(i, swap_gene)
                new_genome.set_gene(swap_index, curr_gene)
            else:
                new_genome.set_gene(i, curr_gene)

        # sequence mutations
        if np.random.rand() < self.shuffle_rate:
            shuffle_size = np.random.randint(*self.shuffle_size)
            shuffle_start = np.random.randint(0, genome_length - shuffle_size + 1)
            np.random.shuffle(
                shuffled_segment := new_genome.get_gene_segment(shuffle_start, shuffle_start + shuffle_size)
            )
            new_genome.set_gene_segment(shuffle_start, shuffle_start + shuffle_size, shuffled_segment)
        elif np.random.rand() < self.reverse_rate:
            reverse_size = np.random.randint(*self.reverse_size)
            reverse_start = np.random.randint(0, genome_length - reverse_size + 1)
            reversed_segment = reversed(new_genome.get_gene_segment(reverse_start, reverse_start + reverse_size))
            new_genome.set_gene_segment(reverse_start, reverse_start + reverse_size, reversed_segment)

        # check if any mutation caused gene to become NaN
        new_genome.check_NaN()

        return new_genome




