#!/usr/bin/python3
import random
import string
import math
import json
import time

class Organism:
    availableGens = string.ascii_letters + " "
    mutationRate = 0.02

    def __init__(self, dna):
        self.dna = dna
        self.len = len(dna)
        self.fitness = 0
    
    @staticmethod
    def generateRandom(maxLength):
        return Organism(random.choices(Organism.availableGens, k=maxLength))

    def mutate(self):
        if random.random() <= self.mutationRate:
            self.dna[random.randint(0, self.len-1)] = random.choice(self.availableGens)

    def getFitness(self, target):
        self.fitness = 0
        for i in range(self.len):
            if self.dna[i] == target.dna[i]:
                self.fitness += 1
        return self.fitness

    def crossover(self, second):
        #mid = math.floor(self.len/2)
        #newdna = self.dna[:mid] + second.dna[mid:]
        newdna = [a if random.randint(0,1) else b for a,b in zip(self.dna, second.dna)]
        return Organism(newdna)

class Population:
    def __init__(self, popSize, target):
        self.populationSize = popSize
        self.targetOrg = target
        self.targetLen = self.targetOrg.len
        self.targetFitness = self.targetLen
        self.population = []
        self.matchingPool = []
        self.generation = 0
        self.bestOrg = None

    def initPop(self):
        for a in range(self.populationSize):
            self.population.append(Organism.generateRandom(self.targetLen))

    def evaluate(self):
        self.matchingPool = []
        for i in range(self.populationSize):
            self.matchingPool.extend([i]*self.population[i].fitness)

        for a in range(self.populationSize):
            par1 = self.population[random.choice(self.matchingPool)]
            par2 = self.population[random.choice(self.matchingPool)]
            offspring = par1.crossover(par2)
            offspring.mutate()
            self.population[a] = offspring

        self.generation += 1

    def getMaxFitness(self):
        maxFit = 0
        for el in self.population:
            curFit = el.getFitness(self.targetOrg)
            if curFit > maxFit:
                maxFit = curFit
                self.bestOrg = el
        return maxFit

    def experiment(self):
        self.initPop()
        maxFit = self.getMaxFitness()
        while maxFit < self.targetFitness:
            self.evaluate()
            maxFit = self.getMaxFitness()
            print("\rmaxFit: %i, gen: %i, curBest: %s" % (maxFit, self.generation, "".join(self.bestOrg.dna)), end='')
    
        print()

def setupFromCfg(filename):
    cnfg = []
    with open(filename) as f:
        cnfg = json.load(f)
    Organism.mutationRate = cnfg["mutationRate"]
    targetOrg = Organism(cnfg["targetOrg"])
    pop = Population(target=targetOrg, popSize=cnfg["populationSize"])
    return pop

def main():
    pop = setupFromCfg("ga.json")
    #pop = Population(target=Organism("Cotidie Morimur"))
    start = time.time()
    pop.experiment()
    print("Elap: %fs" % (time.time()-start))
    
if __name__ == '__main__':
    main()
