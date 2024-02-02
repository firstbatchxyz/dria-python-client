import random


def random_vector(dim: int) -> list:
    """Generate a random vector of a given dimension.

    Args:
        dim (int): Dimension of the vector.

    Returns:
        list: A list of random floats between 0 and 1.
    """
    return [random.random() for _ in range(dim)]


def expect_vectors_to_be_close(a: list, b: list, tol: float = 1e-7):
    """Asserts that values between two vectors are close to each other.

    Args:
        a (list): First vector.
        b (list): Second vector.
        tol (float, optional): Tolerance for the closeness. Defaults to 1e-7.
    """
    assert len(a) == len(b), "Vectors have different lengths"
    for i in range(len(a)):
        assert abs(a[i] - b[i]) < tol, f"Values at index {i} are not close enough: {a[i]} vs {b[i]}"
