import math
import random
import time

import matplotlib.pyplot as plt
import numpy as np
from geopy.geocoders import Nominatim


def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def total_distance(points, sequence):
    return sum(
        distance(points[sequence[i]], points[sequence[(i + 1) % len(sequence)]])
        for i in range(len(sequence))
    )


def read_cities(city_names, filename="india_cities.txt"):
    points = []
    geolocator = Nominatim(user_agent="MS2513_TSP_SA_Kunal")

    with open(filename, "r", encoding="utf-8") as file:
        for city in file:
            city = city.strip()

            if not city:
                break

            location = None

            for attempt in range(5):
                try:
                    print(f"Finding location for: {city}")

                    location = geolocator.geocode(
                        f"{city}, India",
                        timeout=100
                    )

                    if location is not None:
                        break

                    print(f"Location not found for: {city}")
                    break

                except Exception as error:
                    print(
                        f"Geocoding error for {city} "
                        f"(attempt {attempt + 1}/5): {error}"
                    )
                    time.sleep(5 * (attempt + 1))

            if location is None:
                print(f"Skipping city: {city}")
                continue

            x = round(location.longitude, 2)
            y = round(location.latitude, 2)

            print(f"City[{len(points):2d}] = {city} ({x:5.2f}, {y:5.2f})")

            points.append([x, y])
            city_names.append(city)

            time.sleep(1.2)

    return points


def plot_route(sequence, points, distance_value, city_names):
    route = [points[i] for i in sequence]
    route.append(points[sequence[0]])

    route = np.array(route)

    plt.figure(figsize=(10, 7))
    plt.plot(route[:, 0], route[:, 1], "-o")

    for i, city in enumerate(city_names):
        plt.annotate(
            city,
            (points[i][0], points[i][1]),
            xytext=(5, 5),
            textcoords="offset points"
        )

    plt.title(f"Total Distance = {distance_value:.4f}")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def swap_move(points, sequence, current_distance, i, j, temperature):
    new_sequence = sequence.copy()
    new_sequence[i], new_sequence[j] = new_sequence[j], new_sequence[i]

    new_distance = total_distance(points, new_sequence)
    delta = new_distance - current_distance

    if delta <= 0 or random.random() < math.exp(-delta / temperature):
        sequence[:] = new_sequence
        return new_distance, True

    return current_distance, False


def reverse_move(points, sequence, current_distance, i, j, temperature):
    new_sequence = sequence.copy()
    new_sequence[i:j + 1] = reversed(new_sequence[i:j + 1])

    new_distance = total_distance(points, new_sequence)
    delta = new_distance - current_distance

    if delta <= 0 or random.random() < math.exp(-delta / temperature):
        sequence[:] = new_sequence
        return new_distance, True

    return current_distance, False


def simulated_annealing(points):
    n_cities = len(points)

    sequence = np.arange(n_cities)
    current_distance = total_distance(points, sequence)

    temperature = 10.0 * current_distance
    cooling_rate = 0.9

    max_temperature_steps = 250
    max_iterations = 2000
    max_convergence_steps = 4

    previous_distance = current_distance
    convergence_count = 0

    print(f"\nCities: {n_cities}")
    print(f"Initial distance: {current_distance:.4f}")
    print(f"Initial temperature: {temperature:.4f}")

    plot_route(
        sequence,
        points,
        current_distance,
        city_names
    )

    for step in range(1, max_temperature_steps + 1):

        if temperature < 1e-6:
            break

        accepted = 0

        for _ in range(max_iterations):
            i, j = sorted(
                random.sample(range(n_cities), 2)
            )

            if random.random() < 0.5:
                current_distance, accepted_move = swap_move(
                    points,
                    sequence,
                    current_distance,
                    i,
                    j,
                    temperature
                )
            else:
                current_distance, accepted_move = reverse_move(
                    points,
                    sequence,
                    current_distance,
                    i,
                    j,
                    temperature
                )

            if accepted_move:
                accepted += 1

        print(
            f"Iteration: {step:3d} | "
            f"Temperature: {temperature:.6f} | "
            f"Distance: {current_distance:.4f} | "
            f"Accepted: {accepted}"
        )

        if abs(current_distance - previous_distance) < 1e-4:
            convergence_count += 1
        else:
            convergence_count = 0

        if convergence_count >= max_convergence_steps:
            break

        if step % 25 == 0:
            plot_route(
                sequence,
                points,
                current_distance,
                city_names
            )

        temperature *= cooling_rate
        previous_distance = current_distance

    return sequence, current_distance


if __name__ == "__main__":
    city_names = []
    points = read_cities(city_names)

    if len(points) < 2:
        print("\nERROR: Not enough cities were found.")
        print("Please check your internet connection and city file.")
        raise SystemExit

    sequence, final_distance = simulated_annealing(points)

    print("\nFinal route:")
    print(" -> ".join(city_names[i] for i in sequence))
    print(f"\nFinal distance: {final_distance:.4f}")

    plot_route(
        sequence,
        points,
        final_distance,
        city_names
    )