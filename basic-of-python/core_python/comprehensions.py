# list comprehensions

a = [1,2,3,4,5,6,7,8,9]
res = [num for num in a if num % 2 == 0]
print(res)


res = [num**2 for num in range(1,6)]
print(res)


# dictionary comprehensions

res = {num: num**3 for num in range(1,6)}
print(res)

a = ["Texas", "California", "Florida"]
b = ["Austin", "Sacramento", "Tallahassee"]

res = {state: capital for state, capital in zip(a, b)}
print(res)

# set comprehensions

a = [1, 2, 2, 3, 4, 4, 5, 6, 6, 7]
res = {num for num in a if num % 2 == 0}
print(res)

res = {num**2 for num in range(1,6)}
print(res)

# generator comprehensions

res = (num for num in range(10) if num % 2 == 0)
print(res)

res = (num**2 for num in range(1,6))
print(res)


# nested comprehensions
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

flat = [num for row in matrix for num in row]
print(flat)