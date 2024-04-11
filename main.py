import random

class Organism:
    def __init__(self, energy=100):
        self.energy = energy
    
    def is_alive(self):
        return self.energy > 0

class Plant(Organism):
    def grow(self):
        self.energy += 5  # Plants gain energy (grow) every turn

class Animal(Organism):
    def __init__(self, energy=100):
        super().__init__(energy)
        self.age = 0
    
    def age_one_year(self):
        self.age += 1
        self.energy -= 1  # Animals lose energy as they age

    def can_reproduce(self):
        return self.energy >= 50

    def reproduce(self):
        if self.can_reproduce():
            self.energy -= 25  # Energy cost of reproduction
            return type(self)(energy=50)  # A new animal is born with 50 energy
        else:
            return None

class Herbivore(Animal):
    def eat(self, plant):
        if plant.is_alive():
            self.energy += plant.energy  # The herbivore gains the energy of the plant
            plant.energy = 0  # The plant is consumed

class Carnivore(Animal):
    def eat(self, herbivore):
        if herbivore.is_alive():
            self.energy += herbivore.energy
            herbivore.energy = 0  # The herbivore is consumed

def simulation():
    # Initialization of the ecosystem with 2 herbivores, 1 carnivore, and 5 plants
    herbivores = [Herbivore() for _ in range(2)]
    carnivores = [Carnivore() for _ in range(1)]
    plants = [Plant() for _ in range(5)]
    
    results = []
    
    for day in range(1, 11):  # Simulate 10 days
        day_result = f"--- Day {day} ---\n"
        
        # Plants grow
        for plant in plants:
            plant.grow()
        
        # Herbivores randomly eat plants and can reproduce
        for herbivore in herbivores[:]:
            if plants:
                chosen_plant = random.choice(plants)
                herbivore.eat(chosen_plant)
                plants = [plant for plant in plants if plant.energy > 0]
            herbivore.age_one_year()
            if herbivore.can_reproduce():
                herbivores.append(herbivore.reproduce())
        
        # Carnivores randomly eat herbivores and can reproduce
        for carnivore in carnivores[:]:
            if herbivores:
                chosen_herbivore = random.choice(herbivores)
                carnivore.eat(chosen_herbivore)
                herbivores = [herbivore for herbivore in herbivores if herbivore.energy > 0]
            carnivore.age_one_year()
            if carnivore.can_reproduce():
                carnivores.append(carnivore.reproduce())

        # Daily summary
        day_result += f"Herbivores alive: {len(herbivores)}, Carnivores alive: {len(carnivores)}, Plants alive: {len(plants)}"
        results.append(day_result)
    
    return results

# Run the simulation and display the results
corrected_simulation_results = simulation()
corrected_simulation_results
