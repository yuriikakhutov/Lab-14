import itertools
from datetime import datetime
from functools import wraps
import threading

# Custom exception for insufficient funds
class InsufficientFunds(Exception):
    """ Exception for when the buyer doesn't have enough funds to purchase a car. """
    def __init__(self, message):
        super().__init__(message)

# Decorator for transaction logging
def transaction_logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if result:
            print(f"Transaction successful: {func.__name__} with args {args}, kwargs {kwargs}")
        else:
            print(f"Transaction failed: {func.__name__} with args {args}, kwargs {kwargs}")
        return result
    return wrapper

# Car class with auto-generated ID
class Car:
    _ids = itertools.count(1)

    def __init__(self, make, model, price):
        self.id = next(self._ids)
        self._make = make
        self._model = model
        self._price = price

    @property
    def make(self):
        return self._make

    @property
    def model(self):
        return self._model

    @property
    def price(self):
        return self._price

    def __str__(self):
        return f"{self._make} {self._model}, price: {self._price} UAH."

# Car dealership class implementing an iterator and containing a list of cars
class Dealership:
    def __init__(self):
        self._cars = []
        self._lock = threading.Lock()  # Lock for securing dealership account

    def add_car(self, car):
        self._cars.append(car)

    def __len__(self):
        return len(self._cars)

    @transaction_logger
    def sell_car(self, index, buyer):
        with self._lock:  # Ensure that the transaction is thread-safe
            try:
                car = self._cars[index]
                if buyer.balance >= car.price:
                    buyer.decrease_balance(car.price)
                    self._cars.pop(index)
                    return Contract(buyer, car)
                else:
                    raise InsufficientFunds("You do not have enough funds to purchase this car.")
            except IndexError:
                raise IndexError("The selected car index is out of available options.")

    def __iter__(self):
        return iter(self._cars)

    # Generator for filtering cars by a certain price
    def cars_by_price(self, min_price):
        for car in self._cars:
            if car.price >= min_price:
                yield car

# Buyer class with auto-generated ID
class Buyer:
    _ids = itertools.count(1)

    def __init__(self, name, balance):
        self.id = next(self._ids)
        self._name = name
        self._balance = balance
        self._lock = threading.Lock()  # Lock for securing buyer's account

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError("Name must be a string")
        if not value:
            raise ValueError("Name cannot be empty")
        self._name = value

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("Balance must be a number")
        if value < 0:
            raise ValueError("Balance cannot be negative")
        self._balance = value

    def decrease_balance(self, amount):
        with self._lock:  # Ensure that the operation is thread-safe
            if amount > self._balance:
                raise InsufficientFunds("You do not have enough funds to purchase this car.")
            self._balance -= amount

    def __str__(self):
        return f"Buyer {self._name}, balance: {self._balance} UAH."

# Contract class with auto-generated ID and date
class Contract:
    _ids = itertools.count(1)

    def __init__(self, buyer, car):
        self.id = next(self._ids)
        self._buyer = buyer
        self._car = car
        self._date = datetime.now()

    def __str__(self):
        return f"Contract {self.id}: {self._buyer.name} bought {self._car} on {self._date}"

# Function to simulate car purchase in a thread
def simulate_purchase(dealership, car_index, buyer):
    try:
        contract = dealership.sell_car(car_index, buyer)
        print(contract)
    except (InsufficientFunds, IndexError) as e:
        print(e)

# Function to display available cars and allow user to choose
def user_panel(dealership, buyer):
    while True:
        print("\nAvailable cars:")
        for i, car in enumerate(dealership):
            print(f"{i}: {car}")
        try:
            choice = int(input(f"\n{buyer.name}, enter the number of the car you want to buy (or -1 to skip): "))
            if choice == -1:
                break
            thread = threading.Thread(target=simulate_purchase, args=(dealership, choice, buyer))
            thread.start()
            thread.join()
            break
        except ValueError:
            print("Please enter a valid car number.")
        except (InsufficientFunds, IndexError) as e:
            print(e)

# Testing and demonstration of the system with user panel
if __name__ == "__main__":
    dealership = Dealership()
    dealership.add_car(Car("Tesla", "Model S", 3000000))
    dealership.add_car(Car("Ford", "Fiesta", 500000))

    buyers = [
        Buyer("Alexander", 2500000),
        Buyer("Maria", 3500000),
        Buyer("Ivan", 500000)
    ]

    for buyer in buyers:
        user_panel(dealership, buyer)

    print("\nFinal state of dealership:")
    for i, car in enumerate(dealership):
        print(f"{i}: {car}")
