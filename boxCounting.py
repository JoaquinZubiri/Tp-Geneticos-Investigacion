import numpy as np

#Calcular la dimension fractal
def box_count(data, box_size):
  count = 0
  for i in range(0, len(data), box_size):
    if np.any(data[i:i+box_size]):
      count += 1
  return count

def fractal_dimension(data, max_box_size):
  sizes = np.arange(1, max_box_size)
  counts = [box_count(data, size) for size in sizes]
  coefs = np.polyfit(np.log(sizes), np.log(counts), 1)
  return -coefs[0]


