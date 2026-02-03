# ALS Algorithm

Alternating Least Squares (ALS) is a matrix factorization algorithm for collaborative filtering recommendations.

## Algorithm Overview

ALS decomposes a user-item rating matrix R into two lower-rank matrices:

```
R ≈ U × V^T

Where:
- R: (n_users × n_items) rating matrix
- U: (n_users × rank) user factors
- V: (n_items × rank) item factors
```

## Properties Under Test

### 1. Convergence (ALS-001)

ALS must converge: RMSE should decrease (or stay constant) over iterations.

```python
def test_als_convergence():
    """RMSE must decrease over iterations."""
    model = ALS(rank=10, max_iter=20, reg_param=0.1)

    rmse_history = []
    for i in range(20):
        model.fit_iteration(ratings)
        rmse = evaluate_rmse(model, test_set)
        rmse_history.append(rmse)

    # Verify monotonic decrease (with small tolerance for numerical noise)
    for i in range(1, len(rmse_history)):
        assert rmse_history[i] <= rmse_history[i-1] + 1e-6, \
            f"RMSE increased at iteration {i}"
```

### 2. Factor Shapes (ALS-002, ALS-003)

Factor matrices must have correct dimensions.

```python
def test_user_factor_shape():
    """User factors: (n_users, rank)"""
    model = ALS(rank=10)
    model.fit(ratings)

    assert model.user_factors.shape == (n_users, 10)

def test_item_factor_shape():
    """Item factors: (n_items, rank)"""
    model = ALS(rank=10)
    model.fit(ratings)

    assert model.item_factors.shape == (n_items, 10)
```

### 3. Regularization Effect (ALS-004)

Higher regularization should produce smaller factor norms.

```python
def test_regularization_effect():
    """Higher lambda → smaller factor norms."""
    model_low_reg = ALS(rank=10, reg_param=0.01)
    model_high_reg = ALS(rank=10, reg_param=1.0)

    model_low_reg.fit(ratings)
    model_high_reg.fit(ratings)

    norm_low = np.linalg.norm(model_low_reg.user_factors)
    norm_high = np.linalg.norm(model_high_reg.user_factors)

    assert norm_high < norm_low, \
        "Higher regularization should reduce factor norms"
```

### 4. Prediction Range (ALS-005)

Predictions should stay within reasonable bounds.

```python
def test_prediction_range():
    """Predictions should be within [min_rating, max_rating]."""
    model = ALS(rank=10)
    model.fit(ratings)

    predictions = model.predict_all()

    # Allow small margin for numerical precision
    min_rating, max_rating = 1.0, 5.0
    margin = 0.5

    assert predictions.min() >= min_rating - margin
    assert predictions.max() <= max_rating + margin
```

## ALS Update Equations

### User Factor Update (V fixed)

```
U_i = (V^T V + λI)^{-1} V^T R_i
```

### Item Factor Update (U fixed)

```
V_j = (U^T U + λI)^{-1} U^T R_j
```

## Implementation

```python
import numpy as np

class ALS:
    def __init__(self, rank: int = 10, reg_param: float = 0.1,
                 max_iter: int = 10):
        self.rank = rank
        self.reg_param = reg_param
        self.max_iter = max_iter

    def fit(self, ratings: np.ndarray):
        """Fit ALS model to rating matrix."""
        n_users, n_items = ratings.shape

        # Initialize factors randomly
        self.user_factors = np.random.randn(n_users, self.rank) * 0.01
        self.item_factors = np.random.randn(n_items, self.rank) * 0.01

        for _ in range(self.max_iter):
            # Fix items, update users
            self._update_users(ratings)
            # Fix users, update items
            self._update_items(ratings)

    def _update_users(self, ratings: np.ndarray):
        """Update user factors with item factors fixed."""
        VtV = self.item_factors.T @ self.item_factors
        reg = self.reg_param * np.eye(self.rank)

        for i in range(ratings.shape[0]):
            # Get items rated by user i
            rated_items = np.where(ratings[i] > 0)[0]
            if len(rated_items) == 0:
                continue

            V_subset = self.item_factors[rated_items]
            r_subset = ratings[i, rated_items]

            A = V_subset.T @ V_subset + reg
            b = V_subset.T @ r_subset
            self.user_factors[i] = np.linalg.solve(A, b)

    def _update_items(self, ratings: np.ndarray):
        """Update item factors with user factors fixed."""
        UtU = self.user_factors.T @ self.user_factors
        reg = self.reg_param * np.eye(self.rank)

        for j in range(ratings.shape[1]):
            # Get users who rated item j
            rated_users = np.where(ratings[:, j] > 0)[0]
            if len(rated_users) == 0:
                continue

            U_subset = self.user_factors[rated_users]
            r_subset = ratings[rated_users, j]

            A = U_subset.T @ U_subset + reg
            b = U_subset.T @ r_subset
            self.item_factors[j] = np.linalg.solve(A, b)

    def predict(self, user_idx: int, item_idx: int) -> float:
        """Predict rating for user-item pair."""
        return self.user_factors[user_idx] @ self.item_factors[item_idx]
```

## References

- [Collaborative Filtering for Implicit Feedback Datasets](https://dl.acm.org/doi/10.1109/ICDM.2008.22)
- [Large-scale Parallel Collaborative Filtering](https://dl.acm.org/doi/10.1145/1401890.1401944)
- [Spark MLlib ALS](https://spark.apache.org/docs/latest/ml-collaborative-filtering.html)
