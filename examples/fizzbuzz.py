#!/usr/bin/env python3
"""FizzBuzz example for Claude Code SDK."""


def fizzbuzz_generator(limit: int):
    """
    Generator-based FizzBuzz implementation for memory efficiency.

    Yields "Fizz" for multiples of 3, "Buzz" for multiples of 5,
    "FizzBuzz" for multiples of both 3 and 5, and the number as a string otherwise.

    Args:
        limit: The upper limit of the sequence (inclusive)

    Yields:
        str: The FizzBuzz result for each number from 1 to limit
    """
    for i in range(1, limit + 1):
        output = ""
        if i % 3 == 0:
            output += "Fizz"
        if i % 5 == 0:
            output += "Buzz"
        yield output or str(i)


def print_fizzbuzz(limit: int = 100) -> None:
    """
    Print FizzBuzz sequence from 1 to limit using generator.

    Args:
        limit: The upper limit of the sequence (inclusive)
    """
    print(f"=== FizzBuzz Generator (1 to {limit}) ===")
    for result in fizzbuzz_generator(limit):
        print(result)


if __name__ == "__main__":
    print_fizzbuzz()
