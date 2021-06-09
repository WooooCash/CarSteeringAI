import numpy as np

class Ecosystem():
    def __init__(self, original_f, scoring_function, population_size=100, holdout = 'sqrt', mating = True):
        #original_F - funkcja tworząca oryginalnych osobników w pierwszej populacji

        self.population_size = population_size
        self.population = [original_f() for _ in range(population_size)]
        self.scoring_function = scoring_function
        if holdout == 'sqrt':
            self.holdout = max(1, int(np.sqrt(population_size)))
        elif holdout == 'log':
            self.holdout = max(1, int(np.log(population_size)))
        elif holdout > 0 and holdout < 1:
            self.holdout = max(1, int(holdout * population_size))
        else:
            self.holdout = max(1, int(holdout))
        self.mating = mating

    def generation(self, repeats=1, keep_best=True):
        # rewards = [np.mean([self.scoring_function(x) for _ in range(repeats)]) for x in self.population]
        rewards = [self.scoring_function(x) for x in self.population]
        # print(np.argsort(rewards)[::-1])
        print(rewards)
        self.population = [self.population[x] for x in np.argsort(rewards)[::-1]]

        new_population = []
        for i in range(self.population_size):
            parent_1_idx = i % self.holdout
            if self.mating:
                parent_2_idx = min(self.population_size - 1, int(np.random.exponential(self.holdout)))
                # parent_2_idx = np.random.random_integers(0, self.population_size-1)
            else:
                parent_2_idx = parent_1_idx
            # print(f'p1 layers: {[self.population[parent_1_idx].layers[x].shape for x in range(len(self.population[parent_1_idx].layers))]}')
            # print(f'p2 layers: {[self.population[parent_2_idx].layers[x].shape for x in range(len(self.population[parent_2_idx].layers))]}')
            print(f'len: {len(self.population)}, p1: {parent_1_idx}, p2: {parent_2_idx}')
            offspring = self.population[parent_1_idx].m8(self.population[parent_2_idx])
            new_population.append(offspring)

        if keep_best:
            new_population[-1] = self.population[0]
            new_population[-1].reset()
            print(new_population[-1].dead)
        print('new gen created')
        self.population = new_population
        return self.population[-1]

    def get_best_organism(self, repeats=1, include_reward=False):
        rewards = [np.mean(self.scoring_function(x)) for _ in range(repeats) for x in self.population]
        if include_reward:
            best = np.argsort(rewards)[-1]
            return self.population[best], rewards[best]
        else:
            return self.population[np.argsort(rewards)[-1]]
