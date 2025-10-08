"""Tests for FizzBuzz example."""

from examples.fizzbuzz import fizzbuzz_generator


def get_fizzbuzz_result(n: int) -> str:
    """Helper function to get FizzBuzz result for a specific number."""
    # Generate results up to n and return the nth result
    results = list(fizzbuzz_generator(n))
    return results[n - 1]


class TestFizzBuzz:
    """Test cases for the FizzBuzz implementation."""

    def test_fizzbuzz_regular_numbers(self):
        """Test that regular numbers return the number as a string."""
        assert get_fizzbuzz_result(1) == "1"
        assert get_fizzbuzz_result(2) == "2"
        assert get_fizzbuzz_result(4) == "4"
        assert get_fizzbuzz_result(7) == "7"
        assert get_fizzbuzz_result(8) == "8"

    def test_fizzbuzz_multiples_of_3(self):
        """Test that multiples of 3 return 'Fizz'."""
        assert get_fizzbuzz_result(3) == "Fizz"
        assert get_fizzbuzz_result(6) == "Fizz"
        assert get_fizzbuzz_result(9) == "Fizz"
        assert get_fizzbuzz_result(12) == "Fizz"

    def test_fizzbuzz_multiples_of_5(self):
        """Test that multiples of 5 return 'Buzz'."""
        assert get_fizzbuzz_result(5) == "Buzz"
        assert get_fizzbuzz_result(10) == "Buzz"
        assert get_fizzbuzz_result(20) == "Buzz"
        assert get_fizzbuzz_result(25) == "Buzz"

    def test_fizzbuzz_multiples_of_15(self):
        """Test that multiples of 15 return 'FizzBuzz'."""
        assert get_fizzbuzz_result(15) == "FizzBuzz"
        assert get_fizzbuzz_result(30) == "FizzBuzz"
        assert get_fizzbuzz_result(45) == "FizzBuzz"
        assert get_fizzbuzz_result(60) == "FizzBuzz"

    def test_fizzbuzz_edge_cases(self):
        """Test edge cases."""
        # Test the first few numbers in sequence
        expected = [
            "1",
            "2",
            "Fizz",
            "4",
            "Buzz",
            "Fizz",
            "7",
            "8",
            "Fizz",
            "Buzz",
            "11",
            "Fizz",
            "13",
            "14",
            "FizzBuzz",
        ]

        # Test using the generator for the sequence
        results = list(fizzbuzz_generator(len(expected)))
        for i, expected_value in enumerate(expected):
            assert results[i] == expected_value

    def test_fizzbuzz_larger_numbers(self):
        """Test larger numbers to ensure pattern holds."""
        assert get_fizzbuzz_result(99) == "Fizz"  # 99 = 3 * 33
        assert get_fizzbuzz_result(100) == "Buzz"  # 100 = 5 * 20
        assert get_fizzbuzz_result(150) == "FizzBuzz"  # 150 = 15 * 10

    def test_fizzbuzz_generator_behavior(self):
        """Test that the generator produces the correct sequence."""
        # Test that we get a generator
        gen = fizzbuzz_generator(5)
        assert hasattr(gen, "__iter__")
        assert hasattr(gen, "__next__")

        # Test the first 5 values
        expected = ["1", "2", "Fizz", "4", "Buzz"]
        results = list(fizzbuzz_generator(5))
        assert results == expected
