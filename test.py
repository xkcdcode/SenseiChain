from itertools import cycle


names_pool = cycle(["Alice", "Bob", "Charlie", "Dave", "Eve"])

for i in range(0, 10):
    sender_name = next(names_pool)  # type: str
    receiver_name = next(names_pool)  # type: str
    print(sender_name)
    print(receiver_name)
    print("##################")

result = []
if not result:
    print("Empty")

if len(result) == 0:
    print("Empty")


