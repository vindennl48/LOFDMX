def clamp(value, min_value=0, max_value=255):
    value = max(0, min(127, value))
    return (min_value + (value * (max_value - min_value) / 127))

print(clamp(5, 0, 1))
print(clamp(15, 0, 1))
print(clamp(25, 0, 1))
print(clamp(35, 0, 1))
print(clamp(45, 0, 1))
print(clamp(55, 0, 1))
