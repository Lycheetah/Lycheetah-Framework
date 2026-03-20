# FILE: knowledge_genome.py
"""
Knowledge as Genetic Code with Mutation, Selection, Inheritance
"""

import numpy as np
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import hashlib

# =========================
# DNA ENCODING
# =========================

class Base(Enum):
    A = 0
    T = 1
    C = 2
    G = 3

class Codon:
    """Three-base genetic code unit"""
    
    CODON_TABLE = {
        'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M',
        'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T',
        'AAC':'N', 'AAT':'N', 'AAA':'K', 'AAG':'K',
        'AGC':'S', 'AGT':'S', 'AGA':'R', 'AGG':'R',
        'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L',
        'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P',
        'CAC':'H', 'CAT':'H', 'CAA':'Q', 'CAG':'Q',
        'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R',
        'GTA':'V', 'GTC':'V', 'GTG':'V', 'GTT':'V',
        'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A',
        'GAC':'D', 'GAT':'D', 'GAA':'E', 'GAG':'E',
        'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G',
        'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S',
        'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L',
        'TAC':'Y', 'TAT':'Y', 'TAA':'*', 'TAG':'*',
        'TGC':'C', 'TGT':'C', 'TGA':'*', 'TGG':'W',
    }
    
    def __init__(self, bases: Tuple[Base, Base, Base]):
        self.bases = bases
        
    def to_string(self) -> str:
        return ''.join([b.name for b in self.bases])
    
    def to_amino_acid(self) -> str:
        return self.CODON_TABLE.get(self.to_string(), 'X')
    
    @classmethod
    def random(cls) -> 'Codon':
        return cls(tuple(random.choice(list(Base)) for _ in range(3)))

@dataclass
class KnowledgeGene:
    """Fundamental unit of knowable truth encoded in DNA"""
    
    # Core properties
    dna_sequence: List[Base]
    epigenetic_marks: Dict[str, float]
    promoter_region: List[Base]
    terminator_region: List[Base]
    
    # Metadata
    name: str
    evidence_strength: float  # Π score
    expression_level: float = 1.0
    last_expressed: float = 0.0
    
    def __post_init__(self):
        self.gene_id = self._generate_id()
        self.mutation_rate = 0.001 / (self.evidence_strength + 0.1)
        
    def _generate_id(self) -> str:
        """Generate unique gene ID from DNA sequence"""
        seq_str = ''.join([b.name for b in self.dna_sequence])
        return hashlib.md5(seq_str.encode()).hexdigest()[:8]
    
    def transcribe(self) -> List[Codon]:
        """Transcribe DNA to RNA (codons)"""
        codons = []
        for i in range(0, len(self.dna_sequence), 3):
            if i + 2 < len(self.dna_sequence):
                codon = Codon(tuple(self.dna_sequence[i:i+3]))
                codons.append(codon)
        return codons
    
    def translate(self) -> str:
        """Translate to protein (amino acid sequence)"""
        codons = self.transcribe()
        protein = ''.join([codon.to_amino_acid() for codon in codons])
        return protein
    
    def express(self, environmental_factors: Dict[str, float]) -> float:
        """Express gene based on environment"""
        # Base expression modified by epigenetic marks
        base_expression = self.expression_level
        
        # Environmental influence
        env_factor = 1.0
        for factor, value in environmental_factors.items():
            if factor in self.epigenetic_marks:
                env_factor *= 1.0 + (value - 0.5) * self.epigenetic_marks[factor]
        
        # Evidence strength amplifies expression
        evidence_boost = 1.0 + (self.evidence_strength - 0.5)
        
        expression = base_expression * env_factor * evidence_boost
        self.last_expressed = time.time()
        
        return max(0, expression)
    
    def mutate(self, mutation_rate_multiplier: float = 1.0) -> 'KnowledgeGene':
        """Apply mutations to DNA sequence"""
        new_sequence = self.dna_sequence.copy()
        mutation_count = 0
        
        # Point mutations
        for i in range(len(new_sequence)):
            if random.random() < self.mutation_rate * mutation_rate_multiplier:
                # Choose different base
                current = new_sequence[i]
                possible = [b for b in Base if b != current]
                new_sequence[i] = random.choice(possible)
                mutation_count += 1
        
        # Epigenetic mutations
        new_epigenetic = self.epigenetic_marks.copy()
        for mark in new_epigenetic:
            if random.random() < self.mutation_rate * 0.1:
                new_epigenetic[mark] = random.random()
        
        # Create mutated gene
        mutated = KnowledgeGene(
            dna_sequence=new_sequence,
            epigenetic_marks=new_epigenetic,
            promoter_region=self.promoter_region.copy(),
            terminator_region=self.terminator_region.copy(),
            name=f"{self.name}_mut{mutation_count}",
            evidence_strength=self.evidence_strength * (1 - mutation_count * 0.01)
        )
        
        return mutated
    
    def crossover(self, other: 'KnowledgeGene', 
                 crossover_points: int = 1) -> Tuple['KnowledgeGene', 'KnowledgeGene']:
        """Crossover with another gene"""
        
        # Ensure sequences are same length
        min_len = min(len(self.dna_sequence), len(other.dna_sequence))
        seq1 = self.dna_sequence[:min_len]
        seq2 = other.dna_sequence[:min_len]
        
        # Choose crossover points
        points = sorted(random.sample(range(1, min_len-1), crossover_points))
        
        # Perform crossover
        child1_seq = []
        child2_seq = []
        last_point = 0
        
        for i, point in enumerate(points):
            if i % 2 == 0:
                child1_seq.extend(seq1[last_point:point])
                child2_seq.extend(seq2[last_point:point])
            else:
                child1_seq.extend(seq2[last_point:point])
                child2_seq.extend(seq1[last_point:point])
            last_point = point
        
        # Add remaining
        if len(points) % 2 == 0:
            child1_seq.extend(seq1[last_point:])
            child2_seq.extend(seq2[last_point:])
        else:
            child1_seq.extend(seq2[last_point:])
            child2_seq.extend(seq1[last_point:])
        
        # Blend epigenetic marks
        child1_epi = {}
        child2_epi = {}
        all_marks = set(self.epigenetic_marks.keys()) | set(other.epigenetic_marks.keys())
        
        for mark in all_marks:
            val1 = self.epigenetic_marks.get(mark, 0.5)
            val2 = other.epigenetic_marks.get(mark, 0.5)
            
            # Random inheritance
            if random.random() < 0.5:
                child1_epi[mark] = val1
                child2_epi[mark] = val2
            else:
                child1_epi[mark] = val2
                child2_epi[mark] = val1
        
        # Create child genes
        child1 = KnowledgeGene(
            dna_sequence=child1_seq,
            epigenetic_marks=child1_epi,
            promoter_region=self.promoter_region.copy(),
            terminator_region=self.terminator_region.copy(),
            name=f"{self.name}_{other.name}_child1",
            evidence_strength=(self.evidence_strength + other.evidence_strength) / 2
        )
        
        child2 = KnowledgeGene(
            dna_sequence=child2_seq,
            epigenetic_marks=child2_epi,
            promoter_region=self.promoter_region.copy(),
            terminator_region=self.terminator_region.copy(),
            name=f"{self.name}_{other.name}_child2",
            evidence_strength=(self.evidence_strength + other.evidence_strength) / 2
        )
        
        return child1, child2
    
    @classmethod
    def from_knowledge(cls, knowledge: str, evidence: float = 0.5) -> 'KnowledgeGene':
        """Create gene from knowledge text"""
        
        # Convert text to DNA
        dna = []
        for char in knowledge[:100]:  # Limit length
            # Simple encoding: char code mod 4
            code = ord(char) % 4
            dna.append(list(Base)[code])
        
        # Add promoter and terminator
        promoter = [Base.A, Base.T, Base.G]  # Start codon
        terminator = [Base.T, Base.A, Base.A]  # Stop codon
        
        # Epigenetic marks based on evidence
        epigenetic = {
            'citation_count': evidence,
            'replication_success': evidence,
            'theoretical_coherence': evidence,
            'practical_utility': evidence,
            'cultural_acceptance': 0.5
        }
        
        return cls(
            dna_sequence=dna,
            epigenetic_marks=epigenetic,
            promoter_region=promoter,
            terminator_region=terminator,
            name=knowledge[:20],
            evidence_strength=evidence
        )

# =========================
# CHROMOSOMES & GENOMES
# =========================

class KnowledgeChromosome:
    """Collection of related genes (e.g., "Meditation Practices")"""
    
    def __init__(self, name: str, genes: List[KnowledgeGene]):
        self.name = name
        self.genes = genes
        self.linkage_map = self._calculate_linkage()
        self.recombination_rate = 0.01
        
    def _calculate_linkage(self) -> np.ndarray:
        """Calculate linkage between genes (how often they co-inherit)"""
        n = len(self.genes)
        linkage = np.ones((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    # Genes with similar evidence strength are more linked
                    evidence_sim = 1.0 - abs(self.genes[i].evidence_strength - 
                                            self.genes[j].evidence_strength)
                    
                    # Genes expressed together are more linked
                    expression_corr = 1.0 if i == j else random.random() * 0.5
                    
                    linkage[i, j] = (evidence_sim + expression_corr) / 2
        
        return linkage
    
    def evolve(self, environmental_pressure: Dict[str, float], 
               generations: int = 10) -> 'KnowledgeChromosome':
        """Evolve chromosome through selection and mutation"""
        
        current_population = self.genes.copy()
        
        for generation in range(generations):
            # Evaluate fitness
            fitness_scores = []
            for gene in current_population:
                expression = gene.express(environmental_pressure)
                fitness = expression * gene.evidence_strength
                fitness_scores.append(fitness)
            
            # Selection (tournament selection)
            new_population = []
            for _ in range(len(current_population)):
                # Tournament of size 3
                tournament = random.sample(list(zip(current_population, fitness_scores)), 3)
                winner = max(tournament, key=lambda x: x[1])[0]
                new_population.append(winner)
            
            # Crossover
            crossed_population = []
            for i in range(0, len(new_population), 2):
                if i + 1 < len(new_population):
                    parent1 = new_population[i]
                    parent2 = new_population[i + 1]
                    
                    # Crossover probability based on linkage
                    if random.random() < self.recombination_rate:
                        child1, child2 = parent1.crossover(parent2)
                        crossed_population.extend([child1, child2])
                    else:
                        crossed_population.extend([parent1, parent2])
                else:
                    crossed_population.append(new_population[i])
            
            # Mutation
            mutated_population = []
            for gene in crossed_population:
                mutation_multiplier = 1.0 - np.mean(fitness_scores)  # More mutation if fitness low
                mutated = gene.mutate(mutation_multiplier)
                mutated_population.append(mutated)
            
            current_population = mutated_population
        
        return KnowledgeChromosome(f"{self.name}_evolved", current_population)
    
    def calculate_coherence(self) -> float:
        """Calculate chromosomal coherence"""
        evidences = [gene.evidence_strength for gene in self.genes]
        expressions = [gene.expression_level for gene in self.genes]
        
        evidence_coherence = 1.0 - np.std(evidences)
        expression_coherence = 1.0 - np.std(expressions)
        
        return (evidence_coherence + expression_coherence) / 2

class KnowledgeGenome:
    """Complete knowledge system as genome"""
    
    def __init__(self, name: str, chromosomes: List[KnowledgeChromosome]):
        self.name = name
        self.chromosomes = {c.name: c for c in chromosomes}
        self.plasmid_pool = []  # Horizontal gene transfer
        
    def add_gene_horizontally(self, gene: KnowledgeGene, source: str):
        """Add gene via horizontal transfer (like plasmid)"""
        plasmid = {
            'gene': gene,
            'source': source,
            'timestamp': time.time(),
            'integration_probability': gene.evidence_strength
        }
        self.plasmid_pool.append(plasmid)
        
        # Attempt integration
        if random.random() < plasmid['integration_probability']:
            # Find compatible chromosome
            for chrom_name, chromosome in self.chromosomes.items():
                if self._is_compatible(gene, chromosome):
                    chromosome.genes.append(gene)
                    print(f"✓ Gene '{gene.name}' integrated into chromosome '{chrom_name}'")
                    return True
        
        return False
    
    def _is_compatible(self, gene: KnowledgeGene, chromosome: KnowledgeChromosome) -> bool:
        """Check if gene is compatible with chromosome"""
        # Check evidence coherence
        avg_evidence = np.mean([g.evidence_strength for g in chromosome.genes])
        if avg_evidence > 0 and abs(gene.evidence_strength - avg_evidence) > 0.3:
            return False
        
        return True
    
    def express_genome(self, environment: Dict[str, float]) -> Dict[str, float]:
        """Express all genes in genome"""
        expressions = {}
        
        for chrom_name, chromosome in self.chromosomes.items():
            for gene in chromosome.genes:
                expression = gene.express(environment)
                expressions[f"{chrom_name}.{gene.name}"] = expression
        
        return expressions
    
    def evolve(self, environment: Dict[str, float], generations: int = 5):
        """Evolve entire genome"""
        new_chromosomes = []
        
        for chrom_name, chromosome in self.chromosomes.items():
            evolved = chromosome.evolve(environment, generations)
            new_chromosomes.append(evolved)
        
        self.chromosomes = {c.name: c for c in new_chromosomes}
        
        # Process horizontal transfer
        integrated = []
        for plasmid in self.plasmid_pool[:]:
            if random.random() < plasmid['integration_probability']:
                for chrom_name, chromosome in self.chromosomes.items():
                    if self._is_compatible(plasmid['gene'], chromosome):
                        chromosome.genes.append(plasmid['gene'])
                        integrated.append(plasmid['gene'].name)
                        break
        
        return integrated

# =========================
# KNOWLEDGE ECOSYSTEM
# =========================

class KnowledgeEcosystem:
    """Population of knowledge genomes evolving together"""
    
    def __init__(self):
        self.genomes = []
        self.environment = {
            'empirical_rigor': 0.8,
            'practical_utility': 0.7,
            'theoretical_elegance': 0.6,
            'cultural_relevance': 0.5,
            'evolutionary_pressure': 0.3
        }
        self.fitness_history = []
        self.diversity_history = []
        
    def add_genome(self, genome: KnowledgeGenome):
        self.genomes.append(genome)
    
    def calculate_fitness(self, genome: KnowledgeGenome) -> float:
        """Calculate genome fitness in current environment"""
        expressions = genome.express_genome(self.environment)
        
        # Fitness components
        total_expression = sum(expressions.values())
        expression_variance = np.var(list(expressions.values())) if expressions else 0
        
        # High total expression with low variance is best
        fitness = total_expression * (1 - expression_variance)
        
        # Penalize low evidence genes
        evidence_penalty = 0
        for chrom in genome.chromosomes.values():
            for gene in chrom.genes:
                if gene.evidence_strength < 0.3:
                    evidence_penalty += 0.1
        
        return max(0, fitness - evidence_penalty)
    
    def run_generation(self):
        """Run one generation of evolution"""
        
        # Calculate fitness for all genomes
        fitness_scores = [self.calculate_fitness(g) for g in self.genomes]
        self.fitness_history.append(np.mean(fitness_scores))
        
        # Selection (keep top 50%)
        sorted_pairs = sorted(zip(self.genomes, fitness_scores), 
                            key=lambda x: x[1], reverse=True)
        keep_count = max(1, len(self.genomes) // 2)
        survivors = [pair[0] for pair in sorted_pairs[:keep_count]]
        
        # Reproduction
        new_genomes = survivors.copy()
        
        while len(new_genomes) < len(self.genomes):
            # Select parents (fitness proportional)
            parent1 = random.choices(survivors, weights=fitness_scores[:keep_count])[0]
            parent2 = random.choices(survivors, weights=fitness_scores[:keep_count])[0]
            
            # Create child by merging chromosomes
            child_chromosomes = []
            for (name1, chrom1), (name2, chrom2) in zip(
                parent1.chromosomes.items(), parent2.chromosomes.items()):
                
                # Merge genes from both parents
                all_genes = chrom1.genes + chrom2.genes
                child_chrom = KnowledgeChromosome(f"{name1}_{name2}_child", all_genes)
                child_chromosomes.append(child_chrom)
            
            child = KnowledgeGenome(f"child_of_{parent1.name}_{parent2.name}", 
                                  child_chromosomes)
            new_genomes.append(child)
        
        self.genomes = new_genomes
        
        # Horizontal gene transfer
        for i, genome in enumerate(self.genomes):
            for j, other in enumerate(self.genomes):
                if i != j:
                    # Transfer random gene
                    for chrom_name, chromosome in other.chromosomes.items():
                        if chromosome.genes:
                            donor_gene = random.choice(chromosome.genes)
                            genome.add_gene_horizontally(donor_gene, other.name)
        
        # Evolve each genome
        for genome in self.genomes:
            genome.evolve(self.environment, generations=1)
        
        # Update environment based on genome state
        self._update_environment()
        
        # Calculate diversity
        self.diversity_history.append(self.calculate_diversity())
    
    def calculate_diversity(self) -> float:
        """Calculate genetic diversity in ecosystem"""
        if len(self.genomes) < 2:
            return 0.0
        
        # Collect all gene IDs
        all_genes = []
        for genome in self.genomes:
            for chrom in genome.chromosomes.values():
                for gene in chrom.genes:
                    all_genes.append(gene.gene_id)
        
        # Calculate unique genes ratio
        unique_genes = len(set(all_genes))
        total_genes = len(all_genes)
        
        return unique_genes / total_genes if total_genes > 0 else 0.0
    
    def _update_environment(self):
        """Environment evolves based on genome state"""
        # Increase rigor if high evidence genes proliferate
        total_evidence = 0
        total_genes = 0
        
        for genome in self.genomes:
            for chrom in genome.chromosomes.values():
                for gene in chrom.genes:
                    total_evidence += gene.evidence_strength
                    total_genes += 1
        
        if total_genes > 0:
            avg_evidence = total_evidence / total_genes
            # Environment becomes more rigorous if evidence is high
            self.environment['empirical_rigor'] = min(1.0, avg_evidence + 0.1)
            
            # Increase evolutionary pressure based on diversity
            diversity = self.calculate_diversity()
            self.environment['evolutionary_pressure'] = diversity

# =========================
# DEMONSTRATION
# =========================

def create_sample_knowledge_genome() -> KnowledgeGenome:
    """Create sample genome with meditation practices"""
    
    # Create genes for different meditation practices
    genes = [
        KnowledgeGene.from_knowledge("Mindfulness Meditation - present moment awareness", 0.85),
        KnowledgeGene.from_knowledge("Loving-Kindness Meditation - cultivating compassion", 0.80),
        KnowledgeGene.from_knowledge("Vipassana - insight into impermanence", 0.75),
        KnowledgeGene.from_knowledge("Transcendental Meditation - mantra repetition", 0.70),
        KnowledgeGene.from_knowledge("Zen Meditation - just sitting", 0.82),
        KnowledgeGene.from_knowledge("Yoga Nidra - conscious sleep", 0.68),
        KnowledgeGene.from_knowledge("Chakra Meditation - energy centers", 0.55),  # Lower evidence
        KnowledgeGene.from_knowledge("Third Eye Meditation - pineal gland focus", 0.45),  # Controversial
    ]
    
    chromosome = KnowledgeChromosome("Meditation_Practices", genes)
    return KnowledgeGenome("Meditation_Genome", [chromosome])

def run_knowledge_genome_demo(generations: int = 20):
    """Run demonstration of knowledge genome evolution"""
    
    print("=" * 70)
    print("KNOWLEDGE GENOME EVOLUTION DEMONSTRATION")
    print("=" * 70)
    
    # Create ecosystem
    ecosystem = KnowledgeEcosystem()
    
    # Add initial genomes
    for i in range(5):
        genome = create_sample_knowledge_genome()
        genome.name = f"Meditator_{i}"
        ecosystem.add_genome(genome)
    
    print(f"\n🌱 Initial Ecosystem:")
    print(f"• Genomes: {len(ecosystem.genomes)}")
    print(f"• Environment: {ecosystem.environment}")
    print(f"• Initial diversity: {ecosystem.calculate_diversity():.3f}")
    
    # Run evolution
    print(f"\n⚡ Running {generations} generations of evolution...")
    
    for gen in range(generations):
        ecosystem.run_generation()
        
        if gen % 5 == 0 or gen == generations - 1:
            print(f"  Generation {gen:3d}: "
                  f"Fitness={ecosystem.fitness_history[-1]:.3f}, "
                  f"Diversity={ecosystem.diversity_history[-1]:.3f}")
    
    # Analysis
    print(f"\n📊 RESULTS:")
    print(f"• Final average fitness: {ecosystem.fitness_history[-1]:.3f}")
    print(f"• Final diversity: {ecosystem.diversity_history[-1]:.3f}")
    print(f"• Fitness improvement: {ecosystem.fitness_history[-1] - ecosystem.fitness_history[0]:+.3f}")
    
    # Show surviving genes
    print(f"\n🧬 Top Genes in Final Population:")
    
    all_genes = []
    for genome in ecosystem.genomes:
        for chrom in genome.chromosomes.values():
            for gene in chrom.genes:
                all_genes.append((gene, gene.evidence_strength))
    
    # Sort by evidence
    all_genes.sort(key=lambda x: x[1], reverse=True)
    
    for i, (gene, evidence) in enumerate(all_genes[:10]):
        print(f"  {i+1:2d}. {gene.name[:40]:40s} Evidence: {evidence:.3f}")
    
    # Create visualization
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Fitness history
    ax = axes[0, 0]
    ax.plot(ecosystem.fitness_history)
    ax.set_title('Average Fitness Over Generations')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Fitness')
    ax.grid(True)
    
    # Diversity history
    ax = axes[0, 1]
    ax.plot(ecosystem.diversity_history)
    ax.set_title('Genetic Diversity Over Generations')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Diversity')
    ax.grid(True)
    
    # Environment evolution
    ax = axes[1, 0]
    # Would show environment parameters over time
    
    # Gene evidence distribution
    ax = axes[1, 1]
    evidences = [ev for _, ev in all_genes]
    ax.hist(evidences, bins=20, alpha=0.7)
    ax.set_title('Gene Evidence Distribution')
    ax.set_xlabel('Evidence Strength')
    ax.set_ylabel('Frequency')
    
    plt.tight_layout()
    plt.savefig('knowledge_genome_evolution.png', dpi=150)
    
    print(f"\n📈 Visualization saved as 'knowledge_genome_evolution.png'")
    
    # Save results
    results = {
        'fitness_history': [float(f) for f in ecosystem.fitness_history],
        'diversity_history': [float(d) for d in ecosystem.diversity_history],
        'final_top_genes': [
            {'name': gene.name, 'evidence': float(ev)} 
            for gene, ev in all_genes[:20]
        ],
        'environment_final': ecosystem.environment
    }
    
    with open('knowledge_genome_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to 'knowledge_genome_results.json'")
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    
    return ecosystem

# Add missing import
import time

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    ecosystem = run_knowledge_genome_demo(generations=30)
    plt.show()