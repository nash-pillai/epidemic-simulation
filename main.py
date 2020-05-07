# python manim.py Nashimations.py s1 -pl

from manimlib.imports import *
from copy import deepcopy


MY_COLOR_MAP = {
  "s": BLUE_E,
  "i": RED_E,
  "r": YELLOW_E,
  "d": GRAY
}


class MyGrid(Rectangle):
  def __init_(self, **kwargs):
    Rectangle.__init__(self, **kwargs)
    for i in range(-3, 4): self.add(Line(7*LEFT + i*UP, 7*RIGHT + i*UP))
    for i in range(-6, 7): self.add(Line(4*UP + i*RIGHT, 4*DOWN + i*RIGHT))
    self.add(Line(7*LEFT, 7*RIGHT, color=YELLOW_E))
    self.add(Line(4*UP, 4*DOWN, color=YELLOW_E))


class MyGraph(Rectangle):
  def __init__(self, data, population, **kwargs):
    Rectangle.__init__(self, **kwargs)
    ref = LEFT * kwargs["width"]/2
    for i in data: 
      bar = MyBar(
        i,
        population, 
        width=kwargs["width"]/len(data), 
        height=kwargs["height"]
      )
      bar.move_to(ref + RIGHT*2/len(data))
      ref = ref + RIGHT*kwargs["width"]/len(data)
      self.add(bar)


class MyBar(Rectangle):
  def __init__(self, data, population, **kwargs):
    Rectangle.__init__(self, **kwargs)
    ref = DOWN * kwargs["height"]/2
    for (i, j) in data.items(): 
      sub_bar = Rectangle(height=3*j/population, width=kwargs["width"])
      sub_bar.set_fill(MY_COLOR_MAP[i], opacity=1)
      sub_bar.set_color(MY_COLOR_MAP[i])
      sub_bar.move_to(ref + UP*3*j/(population*2))
      ref = ref + UP*3*j/population
      self.add(sub_bar)



# Scenes
# ========================================================

class Grid(Scene):
  def construct(self):
    self.add(MyGrid())


class s1(Scene):
  def construct(self):
    # CONFIG
    arena_size = 5
    population = 50
    sick_num = 3
    transmission_radius = 0.5
    transmission_prob = 0.50
    ill_duration = 20
    fatal_prob = 0.25
    people = {"i": [], "s": [], "r": [], "d": []}
    abbreviations = {"i": "Infected", "s": "Suseptable", "r": "Recovered", "d": "Dead"}
    data = []

    # Arena
    arena = Square(side_length=arena_size, color=GREEN_E)
    arena.age = 0
    self.add(arena)

    # People
    for i in range(sick_num):
      person = SmallDot(color=RED_E)
      person.since_infected = 0
      people["i"].append(person)
      self.add(person)
    for i in range(sick_num, population):
      person = SmallDot(color=BLUE_E)
      people["s"].append(person)
      self.add(person)

    # Random Distrabution
    for i in range(10):
      for person in people["s"] + people["i"] + people["r"]: 
        while True:
          next_pos = person.get_arc_center() + (
                      random.randrange(0, 11) /10
                      * random.choice([UP, DOWN, RIGHT, LEFT])
                    )
          if (
            next_pos[0] < (arena_size/2)
            and (next_pos[0] > (arena_size/2)*-1)
            and next_pos[1] < (arena_size/2)
            and (next_pos[1] > (arena_size/2)*-1)
          ): break
        person.move_to(next_pos)
    
    self.wait()
    data.append({i: len(j) for i, j in people.items()})
    people2 = deepcopy(people)
    while len(people["i"]) > 0:

      # Transmission
      for sperson in list(people["s"]): 
        for iperson in list(people["i"]):
          spos = sperson.get_arc_center()
          ipos = iperson.get_arc_center()
          if ((spos[0] - ipos[0])**2 + (spos[1] - ipos[1])**2) < transmission_radius**2:
            if random.random() < transmission_prob: 
              people["s"].remove(sperson)
              people["i"].append(sperson)
              sperson.set_color(RED_E)
              sperson.since_infected = 0
              break
      
      # Advance ill duration
      for person in list(people["i"]): 
        if person.since_infected == ill_duration:
          people["i"].remove(person)
          if random.random() < fatal_prob:
            people["d"].append(person)
            self.remove(person)
          else:
            people["r"].append(person)
            person.set_color(YELLOW_E)
        else: person.since_infected += 1
      
      # Wandering
      for person in people["s"] + people["i"] + people["r"]: 
        while True:
          next_pos = person.get_arc_center() + (
                      (random.randrange(0, 11) / 10)
                      * random.choice([UP, DOWN, RIGHT, LEFT])
                    )
          if (
            next_pos[0] < (arena_size/2)
            and (next_pos[0] > (arena_size/2)*-1)
            and (next_pos[1] < (arena_size/2))
            and (next_pos[1] > (arena_size/2)*-1)
          ): break
        person.move_to(next_pos)

      # Display info
      texts = []
      ref = UP*3 + RIGHT*3
      for i, j in abbreviations.items():
        text = TextMobject(f"{j}: {len(people[i])}", color=MY_COLOR_MAP[i])
        text.move_to(ref , aligned_edge=LEFT)
        ref += DOWN
        texts.append(text)

      # Display Graph
      data.append({i: len(j) for i, j in people.items()})
      graph = MyGraph(data, population, width=4, height=3)
      graph.move_to(LEFT*5 + 2*UP)

      # New Cases
      new_cases = len(people2["s"]) - len(people["s"])
      new_cases_text = TextMobject(f"New Cases: {new_cases}")
      new_cases_text.move_to(ref, aligned_edge=LEFT)

      # Effective Reproductive Number
      ern = np.round(new_cases*ill_duration / len(people2["i"]), 3)
      erntext = TextMobject(f"Effective Reproductive Number: {ern}")
      erntext.move_to(DOWN*3 + LEFT*7, aligned_edge=LEFT)
      people2 = deepcopy(people)

      self.add(*texts, graph, new_cases_text, erntext)
      self.wait(0.2)
      self.remove(*texts, graph, new_cases_text, erntext)
    
    self.add(*texts, graph, new_cases_text, erntext)
    self.wait(2)
