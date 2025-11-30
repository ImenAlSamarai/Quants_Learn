import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { getSectionContent } from '../services/api';
import { InlineMath, BlockMath } from 'react-katex';
import 'katex/dist/katex.min.css';
import '../styles/SectionContent.css';

/**
 * SectionContentPage - Display Claude-generated content in VALIDATED structure
 *
 * Uses the exact structure validated for statistical modeling
 */
const SectionContentPage = () => {
  const { topicSlug, weekNumber, sectionId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const topicName = location.state?.topicName || topicSlug.replace(/-/g, ' ');
  const sectionData = location.state?.sectionData || {};

  const [showNotes, setShowNotes] = useState(false);
  const [notes, setNotes] = useState('');
  const [completed, setCompleted] = useState(false);
  const [contentData, setContentData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load completion status from localStorage (placeholder persistence)
  useEffect(() => {
    const completionKey = `${topicSlug}-${weekNumber}-${sectionId}-completed`;
    const isCompleted = localStorage.getItem(completionKey) === 'true';
    setCompleted(isCompleted);

    // Load notes from localStorage
    const notesKey = `${topicSlug}-${weekNumber}-${sectionId}-notes`;
    const savedNotes = localStorage.getItem(notesKey) || '';
    setNotes(savedNotes);
  }, [topicSlug, weekNumber, sectionId]); // Reset when section changes!

  // Fetch real content from API
  useEffect(() => {
    const fetchContent = async () => {
      try {
        setLoading(true);
        setError(null);

        console.log('🔵 [SectionContent] Fetching content:', {
          topicName,
          sectionId,
          sectionTitle: sectionData.title
        });

        const result = await getSectionContent(
          topicName,
          sectionId,
          sectionData.title || `Section ${sectionId}`,
          sectionData.topics || []
        );

        console.log('✅ [SectionContent] Content received:', {
          cached: result.cached,
          model: result.generation_model,
          hasContent: !!result.content
        });

        setContentData(result);
      } catch (err) {
        console.error('❌ [SectionContent] Error fetching content:', err);
        setError(err.message || 'Failed to load content');
      } finally {
        setLoading(false);
      }
    };

    fetchContent();
  }, [topicName, sectionId, sectionData.title]);

  // PLACEHOLDER DATA - Replace with real API calls
  // Make content dynamic based on sectionId
  const getSectionData = () => {
    const baseData = {
      topicName: location.state?.topicName || topicSlug.replace(/-/g, ' '),
      weekNumber: parseInt(weekNumber) || 1,
      sectionId: sectionId || '1.1',
    };

    // Define content for each section (placeholder)
    const sectionContent = {
      '1.1': {
        sectionTitle: 'Linear Regression (OLS)',
        estimatedTime: '45 minutes',
        content: {
          introduction: "Ordinary Least Squares (OLS) is the foundation of statistical modeling and one of the most commonly tested topics in quant interviews. You'll be expected to derive the OLS estimator, explain its assumptions, and implement it from scratch.",
          sections: [
            {
              title: 'The OLS Problem',
              content: `Given data points $(x_1, y_1), (x_2, y_2), \\ldots, (x_n, y_n)$, we want to find the line that best fits the data.

The linear model assumes:

$y = X\\beta + \\varepsilon$

where:
• $y$ is the $n \\times 1$ vector of responses
• $X$ is the $n \\times p$ design matrix
• $\\beta$ is the $p \\times 1$ vector of coefficients
• $\\varepsilon$ is the $n \\times 1$ vector of errors

The OLS estimator minimizes the sum of squared residuals:

minimize $\\|y - X\\beta\\|^2$`
            },
            {
              title: 'Deriving the OLS Estimator',
              content: `To find the optimal $\\beta$, we take the derivative and set it to zero:

$\\frac{\\partial}{\\partial \\beta} \\|y - X\\beta\\|^2 = 0$

Expanding:

$(y - X\\beta)^T(y - X\\beta) = y^Ty - 2\\beta^TX^Ty + \\beta^TX^TX\\beta$

Taking the derivative:

$\\frac{\\partial}{\\partial \\beta} = -2X^Ty + 2X^TX\\beta = 0$

Solving for $\\beta$:

$X^TX\\beta = X^Ty$

$\\hat{\\beta} = (X^TX)^{-1}X^Ty$

This is the **OLS estimator** - you must memorize this formula!`,
              keyFormula: '\\hat{\\beta} = (X^TX)^{-1}X^Ty'
            }
          ],
          keyTakeaways: [
            'The OLS formula $\\hat{\\beta} = (X^TX)^{-1}X^Ty$ is THE formula you must know',
            'OLS minimizes sum of squared residuals',
            'LINE assumptions required for BLUE property'
          ],
          interviewTips: [
            'Be ready to derive $\\hat{\\beta}$ on a whiteboard in under 5 minutes',
            'Know the difference between unbiased and BLUE'
          ],
          practiceProblems: [
            { id: 1, difficulty: 'Easy', text: 'Show that the OLS estimator is unbiased: $E[\\hat{\\beta}] = \\beta$' },
            { id: 2, difficulty: 'Medium', text: 'Derive the variance: $\\text{Var}(\\hat{\\beta}) = \\sigma^2(X^TX)^{-1}$' }
          ],
          resources: [
            { source: 'Elements of Statistical Learning', chapter: 'Chapter 3, Section 3.2', pages: 'pp. 43-55' }
          ]
        }
      },
      '1.2': {
        sectionTitle: 'Maximum Likelihood Estimation',
        estimatedTime: '40 minutes',
        content: {
          introduction: "Maximum Likelihood Estimation (MLE) is a fundamental method for parameter estimation in statistics. Understanding the connection between MLE and OLS is crucial for interviews.",
          sections: [
            {
              title: 'The MLE Framework',
              content: `The likelihood function measures how likely the observed data is for different parameter values.

Given data x₁, x₂, ..., xₙ and parameter θ:

L(θ | x) = P(x | θ) = ∏ᵢ P(xᵢ | θ)

The MLE finds the parameter that maximizes this likelihood:

θ̂ₘₗₑ = argmax L(θ | x)

In practice, we maximize the log-likelihood:
ℓ(θ) = log L(θ) = ∑ᵢ log P(xᵢ | θ)`,
              keyFormula: 'θ̂ₘₗₑ = argmax ∑ᵢ log P(xᵢ | θ)'
            },
            {
              title: 'Connection to OLS',
              content: `Under the assumption that errors are normally distributed:
εᵢ ~ N(0, σ²)

The likelihood of the data is:
L(β, σ² | y, X) = ∏ᵢ (1/√(2πσ²)) exp(-(yᵢ - xᵢᵀβ)²/(2σ²))

Taking the log and maximizing with respect to β gives:
β̂ₘₗₑ = (XᵀX)⁻¹Xᵀy

This is exactly the OLS estimator! MLE and OLS coincide under normality.`
            }
          ],
          keyTakeaways: [
            'MLE maximizes the likelihood of observed data',
            'Log-likelihood is easier to work with than likelihood',
            'Under normality, MLE = OLS for linear regression',
            'MLE is consistent and asymptotically normal'
          ],
          interviewTips: [
            'Know how to derive MLE for simple distributions (Normal, Bernoulli)',
            'Understand when MLE and OLS give the same answer',
            'Be ready to explain asymptotic properties'
          ],
          practiceProblems: [
            { id: 1, difficulty: 'Easy', text: 'Find the MLE for μ and σ² for Normal(μ, σ²)' },
            { id: 2, difficulty: 'Medium', text: 'Show that OLS = MLE under Gaussian errors' }
          ],
          resources: [
            { source: 'Elements of Statistical Learning', chapter: 'Chapter 4, Section 4.1', pages: 'pp. 101-110' }
          ]
        }
      },
      '2.1': {
        sectionTitle: 'Residual Analysis',
        estimatedTime: '35 minutes',
        content: {
          introduction: "After fitting a regression model, analyzing residuals is crucial for validating model assumptions and detecting problems. Interviewers love asking about residual plots because it tests both statistical knowledge and practical debugging skills.",
          sections: [
            {
              title: 'What are Residuals?',
              content: `Residuals are the differences between observed and predicted values:

eᵢ = yᵢ - ŷᵢ = yᵢ - xᵢᵀβ̂

For OLS, residuals have useful properties:
• Sum to zero: Σeᵢ = 0
• Uncorrelated with predictors: Σxᵢeᵢ = 0
• Mean of fitted values equals mean of observed: ȳ = ŷ̄

These properties are essential for proving unbiasedness.`
            },
            {
              title: 'Residual Plots for Diagnostics',
              content: `Four key plots to check model assumptions:

1. Residuals vs Fitted Values
   - Check for heteroskedasticity (fan shape)
   - Check for non-linearity (patterns)
   - Should look like random scatter

2. QQ Plot (Normal Probability Plot)
   - Check normality assumption
   - Points should follow diagonal line
   - Deviations indicate heavy/light tails

3. Scale-Location Plot
   - Check homoskedasticity
   - Should show horizontal line
   - Spread should be constant

4. Residuals vs Leverage
   - Identify influential outliers
   - Cook's distance > 0.5 is concerning
   - High leverage + large residual = problem`,
              keyFormula: 'e_i = y_i - x_i^T\\hat{\\beta}'
            }
          ],
          keyTakeaways: [
            'Residuals should look like random noise if model is correct',
            'Patterns in residuals indicate model violations',
            'QQ plots check normality; residual plots check homoskedasticity',
            'Cook\'s distance identifies influential outliers'
          ],
          interviewTips: [
            'Be ready to sketch what heteroskedasticity looks like on a plot',
            'Know the difference between outliers and high-leverage points',
            'Understand when violations matter (e.g., normality less critical with large n)'
          ],
          practiceProblems: [
            { id: 1, difficulty: 'Easy', text: 'Identify heteroskedasticity from a residual vs fitted plot' },
            { id: 2, difficulty: 'Medium', text: 'Explain what Cook\'s distance measures and when to worry' }
          ],
          resources: [
            { source: 'Elements of Statistical Learning', chapter: 'Chapter 3, Section 3.3', pages: 'pp. 55-60' }
          ]
        }
      },
      '2.2': {
        sectionTitle: 'Hypothesis Testing (t-tests, F-tests)',
        estimatedTime: '40 minutes',
        content: {
          introduction: "Hypothesis testing is fundamental in regression. You'll be asked to derive test statistics, interpret p-values, and explain the difference between t-tests and F-tests in interviews.",
          sections: [
            {
              title: 'Testing Individual Coefficients (t-test)',
              content: `Test H₀: βⱼ = 0 vs H₁: βⱼ ≠ 0

The t-statistic is:
t = β̂ⱼ / SE(β̂ⱼ)

where SE(β̂ⱼ) = σ̂√[(XᵀX)⁻¹]ⱼⱼ

Under H₀, t ~ t(n-p) where p is number of parameters

Decision rule: Reject H₀ if |t| > t_{α/2}(n-p)

The p-value is: P(|T| > |t_obs|) where T ~ t(n-p)`,
              keyFormula: 't = \\frac{\\hat{\\beta}_j}{SE(\\hat{\\beta}_j)} \\sim t_{n-p}'
            },
            {
              title: 'Testing Multiple Coefficients (F-test)',
              content: `Test H₀: β₁ = β₂ = ... = βₚ₋₁ = 0 (all coefficients zero except intercept)

The F-statistic compares full vs reduced model:

F = [(RSS₀ - RSS₁) / q] / [RSS₁ / (n-p)]

where:
• RSS₀ = residual sum of squares (reduced model)
• RSS₁ = residual sum of squares (full model)
• q = number of restrictions
• n-p = degrees of freedom

Under H₀, F ~ F(q, n-p)

Connection to R²:
F = [R² / (p-1)] / [(1-R²) / (n-p)]`,
              keyFormula: 'F = \\frac{(RSS_0 - RSS_1) / q}{RSS_1 / (n-p)}'
            }
          ],
          keyTakeaways: [
            't-test for individual coefficients; F-test for joint hypotheses',
            'F-test can detect when multiple weak predictors matter jointly',
            'p-values are NOT the probability that H₀ is true!',
            'Multiple testing requires correction (Bonferroni, FDR)'
          ],
          interviewTips: [
            'Know the difference between statistical and practical significance',
            'Be ready to derive the F-statistic from RSS comparison',
            'Understand why you can\'t just run multiple t-tests instead of F-test',
            'Know when t-tests and F-tests give same answer (single coefficient)'
          ],
          practiceProblems: [
            { id: 1, difficulty: 'Medium', text: 'Derive the relationship between F-statistic and R²' },
            { id: 2, difficulty: 'Hard', text: 'Explain why p-values are uniformly distributed under H₀' }
          ],
          resources: [
            { source: 'Elements of Statistical Learning', chapter: 'Chapter 3, Section 3.2.1', pages: 'pp. 47-49' }
          ]
        }
      },
      '2.3': {
        sectionTitle: 'Model Assumptions Validation',
        estimatedTime: '30 minutes',
        content: {
          introduction: "The LINE assumptions (Linearity, Independence, Normality, Equal variance) are critical for OLS. Interviews often ask: what happens when each assumption is violated and how do you fix it?",
          sections: [
            {
              title: 'The LINE Assumptions',
              content: `L - Linearity: E[y|X] = Xβ
I - Independence: errors are independent
N - Normality: εᵢ ~ N(0, σ²)
E - Equal variance (homoskedasticity): Var(εᵢ) = σ²

What breaks when violated?

Linearity violation:
→ Biased estimates, poor predictions
→ Fix: add polynomial terms, transformations

Independence violation:
→ Underestimated standard errors
→ Fix: use clustered/robust standard errors

Normality violation:
→ t-tests, F-tests invalid (small samples)
→ Fix: bootstrap, permutation tests, CLT (large n)

Homoskedasticity violation:
→ Inefficient estimates, wrong standard errors
→ Fix: weighted least squares, robust SEs`
            },
            {
              title: 'Formal Tests for Assumptions',
              content: `Heteroskedasticity Tests:
• Breusch-Pagan test: regress e² on X
• White test: regress e² on X, X², cross-products
• Goldfeld-Quandt test: split sample, compare variances

Normality Tests:
• Shapiro-Wilk test (powerful but sensitive)
• Jarque-Bera test (uses skewness and kurtosis)
• Anderson-Darling test
• Visual: QQ plot (most useful!)

Autocorrelation Tests:
• Durbin-Watson test: d ≈ 2(1-ρ)
• Ljung-Box test: tests multiple lags

Multicollinearity Detection:
• VIF (Variance Inflation Factor) > 10 is problematic
• Condition number of XᵀX > 30 suggests issues`,
              keyFormula: 'VIF_j = \\frac{1}{1 - R^2_j}'
            }
          ],
          keyTakeaways: [
            'Normality matters less with large samples (CLT)',
            'Heteroskedasticity and autocorrelation affect standard errors',
            'Multicollinearity inflates standard errors but doesn\'t bias estimates',
            'Visual diagnostics (plots) often more useful than formal tests'
          ],
          interviewTips: [
            'Know which violations affect bias vs efficiency vs inference',
            'Be ready to recommend fixes for each violation',
            'Understand robust standard errors (heteroskedasticity-consistent)'
          ],
          practiceProblems: [
            { id: 1, difficulty: 'Easy', text: 'Which assumptions are needed for unbiasedness vs BLUE?' },
            { id: 2, difficulty: 'Medium', text: 'Derive the Breusch-Pagan test statistic' }
          ],
          resources: [
            { source: 'Elements of Statistical Learning', chapter: 'Chapter 3', pages: 'pp. 43-70' }
          ]
        }
      },
      '3.1': {
        sectionTitle: 'Regularization (Ridge, Lasso, Elastic Net)',
        estimatedTime: '50 minutes',
        content: {
          introduction: "Regularization is critical for high-dimensional problems and preventing overfitting. Expect to derive the Ridge solution, explain when to use Lasso vs Ridge, and implement from scratch in interviews.",
          sections: [
            {
              title: 'Ridge Regression (L2 Penalty)',
              content: `Ridge adds L2 penalty to least squares objective:

minimize ||y - Xβ||² + λ||β||²

The closed-form solution is:
β̂_ridge = (XᵀX + λI)⁻¹Xᵀy

Compare to OLS: β̂_ols = (XᵀX)⁻¹Xᵀy

Key properties:
• Shrinks coefficients toward zero (but never exactly zero)
• Always has unique solution (even if p > n)
• Improves prediction when features are correlated
• λ controls amount of shrinkage (cross-validate!)

Bayesian interpretation:
Ridge = MAP estimate with Gaussian prior β ~ N(0, σ²/λ I)`,
              keyFormula: '\\hat{\\beta}_{ridge} = (X^TX + \\lambda I)^{-1}X^Ty'
            },
            {
              title: 'Lasso Regression (L1 Penalty)',
              content: `Lasso uses L1 penalty for sparse solutions:

minimize ||y - Xβ||² + λ||β||₁

where ||β||₁ = Σ|βⱼ|

Key differences from Ridge:
• Sets some coefficients exactly to zero → feature selection
• No closed-form solution (use coordinate descent)
• Less stable when features are highly correlated

Bayesian interpretation:
Lasso = MAP estimate with Laplace prior β ~ Laplace(0, λ)

When to use Lasso vs Ridge:
• Lasso: sparse ground truth, feature selection needed
• Ridge: all features somewhat relevant, better with correlation
• Elastic Net: α·L1 + (1-α)·L2 combines both benefits`,
              keyFormula: '\\min_{\\beta} \\|y - X\\beta\\|^2 + \\lambda \\|\\beta\\|_1'
            },
            {
              title: 'Choosing the Regularization Parameter λ',
              content: `Cross-validation is the standard approach:

1. Split data into K folds
2. For each λ in grid:
   - Train on K-1 folds
   - Validate on held-out fold
   - Record prediction error
3. Select λ with minimum CV error

Common choices:
• K = 5 or 10 for standard CV
• Leave-one-out CV for small datasets
• λ grid: exponential spacing (e.g., 10⁻⁴ to 10²)

One-standard-error rule:
Select simplest model within 1 SE of minimum CV error`
            }
          ],
          keyTakeaways: [
            'Ridge shrinks; Lasso shrinks AND selects',
            'Ridge has closed form; Lasso requires iterative optimization',
            'Both reduce overfitting by constraining model complexity',
            'Cross-validation is essential for tuning λ',
            'Elastic Net combines benefits of both'
          ],
          interviewTips: [
            'Be ready to derive Ridge solution from scratch',
            'Explain geometric interpretation (constraint region)',
            'Know how to implement coordinate descent for Lasso',
            'Understand bias-variance tradeoff with λ'
          ],
          practiceProblems: [
            { id: 1, difficulty: 'Medium', text: 'Derive the Ridge regression closed-form solution' },
            { id: 2, difficulty: 'Hard', text: 'Implement Lasso using coordinate descent in Python' }
          ],
          resources: [
            { source: 'Elements of Statistical Learning', chapter: 'Chapter 3, Section 3.4', pages: 'pp. 61-68' }
          ]
        }
      },
      '3.2': {
        sectionTitle: 'Bias-Variance Tradeoff',
        estimatedTime: '40 minutes',
        content: {
          introduction: "The bias-variance tradeoff is fundamental to all of machine learning. This is a top interview topic because it connects overfitting, regularization, model selection, and generalization.",
          sections: [
            {
              title: 'The Bias-Variance Decomposition',
              content: `For any predictor f̂(x), the expected prediction error decomposes:

E[(y - f̂(x))²] = Bias²[f̂(x)] + Var[f̂(x)] + σ²

where:
• Bias[f̂(x)] = E[f̂(x)] - f(x) = systematic error
• Var[f̂(x)] = E[(f̂(x) - E[f̂(x)])²] = variability across datasets
• σ² = irreducible error (noise in y)

Proof outline:
E[(y - f̂)²] = E[(y - f + f - f̂)²]
           = E[(y - f)²] + E[(f - f̂)²]  [cross term vanishes]
           = σ² + MSE[f̂]

MSE[f̂] = E[(f̂ - E[f̂] + E[f̂] - f)²]
        = Var[f̂] + Bias²[f̂]`,
              keyFormula: 'MSE = Bias^2 + Variance + \\sigma^2'
            },
            {
              title: 'The Tradeoff in Practice',
              content: `As model complexity increases:
• Bias decreases (model can fit true function better)
• Variance increases (model overfits to training data)

Examples:

Simple model (high bias, low variance):
• Linear regression with few features
• Underfits: misses important patterns
• Stable across different datasets

Complex model (low bias, high variance):
• Linear regression with many polynomial features
• Overfits: fits noise in training data
• Unstable: changes drastically with new data

Regularization controls this tradeoff:
• Large λ → more bias, less variance (simpler model)
• Small λ → less bias, more variance (complex model)

Optimal λ minimizes: Bias²(λ) + Var(λ)`,
              keyFormula: '\\min_{\\lambda} \\left[ Bias^2(\\lambda) + Var(\\lambda) \\right]'
            }
          ],
          keyTakeaways: [
            'All models face bias-variance tradeoff',
            'Training error always decreases with complexity',
            'Test error has U-shape: sweet spot balances bias and variance',
            'Regularization/complexity hyperparameters control the tradeoff',
            'Cross-validation finds the optimal tradeoff point'
          ],
          interviewTips: [
            'Be able to sketch training vs test error as function of complexity',
            'Derive the bias-variance decomposition from first principles',
            'Give concrete examples of high-bias and high-variance models',
            'Explain how ensembles (bagging, boosting) manage the tradeoff'
          ],
          practiceProblems: [
            { id: 1, difficulty: 'Medium', text: 'Prove the bias-variance decomposition' },
            { id: 2, difficulty: 'Hard', text: 'Show that Ridge regression trades bias for reduced variance' }
          ],
          resources: [
            { source: 'Elements of Statistical Learning', chapter: 'Chapter 7, Section 7.3', pages: 'pp. 219-223' }
          ]
        }
      },
      '3.3': {
        sectionTitle: 'Cross-Validation',
        estimatedTime: '35 minutes',
        content: {
          introduction: "Cross-validation is the gold standard for model evaluation and hyperparameter tuning. Interviews test your understanding of different CV schemes, their computational costs, and potential pitfalls.",
          sections: [
            {
              title: 'K-Fold Cross-Validation',
              content: `Algorithm:
1. Shuffle data and split into K equal-sized folds
2. For k = 1 to K:
   - Train on all folds except k
   - Test on fold k
   - Record error: errₖ
3. CV error = (1/K) Σ errₖ

Variance of CV estimator:
Var(CV) ≈ σ² / (n·K)

Larger K:
• Pros: less bias (uses more training data), better approximation
• Cons: higher variance, more computation

Common choices:
• K = 5: good bias-variance tradeoff, fast
• K = 10: standard in practice
• K = n (LOOCV): unbiased but high variance, expensive`,
              keyFormula: 'CV_K = \\frac{1}{K} \\sum_{k=1}^{K} err_k'
            },
            {
              title: 'Leave-One-Out Cross-Validation (LOOCV)',
              content: `Special case: K = n

CV_LOOCV = (1/n) Σᵢ (yᵢ - f̂₍₋ᵢ₎(xᵢ))²

For linear regression, clever shortcut:

CV_LOOCV = (1/n) Σᵢ (eᵢ / (1 - hᵢᵢ))²

where:
• eᵢ = residual from full model
• hᵢᵢ = leverage (diagonal of hat matrix H = X(XᵀX)⁻¹Xᵀ)

This formula requires only ONE model fit!

Advantages:
• Unbiased estimate of test error
• Deterministic (no randomness in splits)

Disadvantages:
• High variance (training sets very similar)
• Expensive for non-linear models`
            },
            {
              title: 'Common Pitfalls',
              content: `1. Data leakage:
• Standardize INSIDE each fold, not before splitting
• Don't use test fold for any preprocessing

2. Time series:
• Use time series CV (train on past, test on future)
• Never shuffle time series data!

3. Stratification:
• Ensure balanced class distribution in each fold
• Critical for imbalanced datasets

4. Nested CV:
• Outer loop: estimates generalization error
• Inner loop: tunes hyperparameters
• Prevents overfitting to validation set`
            }
          ],
          keyTakeaways: [
            'K-fold CV balances bias and variance; K=5 or 10 typical',
            'LOOCV is unbiased but high variance',
            'Always avoid data leakage between train/test',
            'Use nested CV for unbiased hyperparameter tuning',
            'Time series requires special train/test splits'
          ],
          interviewTips: [
            'Explain why we can\'t just use training error',
            'Derive the LOOCV shortcut formula for linear regression',
            'Know computational complexity: O(K·n) for K-fold',
            'Understand bootstrap vs cross-validation'
          ],
          practiceProblems: [
            { id: 1, difficulty: 'Easy', text: 'Why is LOOCV deterministic but K-fold is not?' },
            { id: 2, difficulty: 'Medium', text: 'Implement K-fold CV from scratch in Python' }
          ],
          resources: [
            { source: 'Elements of Statistical Learning', chapter: 'Chapter 7, Section 7.10', pages: 'pp. 241-249' }
          ]
        }
      },
      '4.1': {
        sectionTitle: 'Coding from Scratch (No Libraries)',
        estimatedTime: '60 minutes',
        content: {
          introduction: "You WILL be asked to implement linear regression from scratch in interviews. No sklearn, no libraries - just NumPy and your understanding of the math. This section prepares you to code Ridge, Lasso, and gradient descent under time pressure.",
          sections: [
            {
              title: 'OLS from Scratch',
              content: `Implement β̂ = (XᵀX)⁻¹Xᵀy in Python:

\`\`\`python
import numpy as np

class LinearRegression:
    def __init__(self):
        self.beta = None

    def fit(self, X, y):
        # Add intercept column
        X = np.column_stack([np.ones(len(X)), X])

        # Compute β̂ = (XᵀX)⁻¹Xᵀy
        self.beta = np.linalg.inv(X.T @ X) @ X.T @ y
        return self

    def predict(self, X):
        X = np.column_stack([np.ones(len(X)), X])
        return X @ self.beta
\`\`\`

Follow-up questions interviewers ask:
• What if XᵀX is singular? (add small λI for stability)
• How to handle large datasets? (use QR decomposition or gradient descent)
• How to compute R²? (1 - RSS/TSS)`
            },
            {
              title: 'Ridge Regression from Scratch',
              content: `Implement β̂ = (XᵀX + λI)⁻¹Xᵀy:

\`\`\`python
class RidgeRegression:
    def __init__(self, lambda_=1.0):
        self.lambda_ = lambda_
        self.beta = None

    def fit(self, X, y):
        X = np.column_stack([np.ones(len(X)), X])
        n, p = X.shape

        # Don't penalize intercept
        penalty = self.lambda_ * np.eye(p)
        penalty[0, 0] = 0  # No penalty on intercept

        self.beta = np.linalg.inv(X.T @ X + penalty) @ X.T @ y
        return self

    def predict(self, X):
        X = np.column_stack([np.ones(len(X)), X])
        return X @ self.beta
\`\`\`

Key detail: Don't penalize the intercept!`
            },
            {
              title: 'Gradient Descent Implementation',
              content: `When matrix inversion is too expensive:

\`\`\`python
class LinearRegressionGD:
    def __init__(self, lr=0.01, n_iters=1000):
        self.lr = lr
        self.n_iters = n_iters
        self.beta = None

    def fit(self, X, y):
        X = np.column_stack([np.ones(len(X)), X])
        n, p = X.shape
        self.beta = np.zeros(p)

        for _ in range(self.n_iters):
            # Gradient: -2Xᵀ(y - Xβ)
            y_pred = X @ self.beta
            gradient = -2/n * X.T @ (y - y_pred)
            self.beta -= self.lr * gradient

        return self
\`\`\`

Complexity: O(np) per iteration vs O(np² + p³) for closed form`
            }
          ],
          keyTakeaways: [
            'Master β̂ = (XᵀX)⁻¹Xᵀy implementation',
            'Don\'t penalize intercept in Ridge/Lasso',
            'Gradient descent when n or p is very large',
            'Always add intercept column to X',
            'Know how to handle edge cases (singular matrices, perfect collinearity)'
          ],
          interviewTips: [
            'Practice coding on whiteboard or shared editor',
            'Explain computational complexity at each step',
            'Discuss numerical stability (use SVD instead of inverse)',
            'Be ready to add cross-validation wrapper'
          ],
          practiceProblems: [
            { id: 1, difficulty: 'Medium', text: 'Implement OLS with R² calculation in 30 minutes' },
            { id: 2, difficulty: 'Hard', text: 'Implement Lasso using coordinate descent from scratch' }
          ],
          resources: [
            { source: 'Elements of Statistical Learning', chapter: 'Chapter 3', pages: 'Full chapter for reference' }
          ]
        }
      },
      '4.2': {
        sectionTitle: 'Derivations & Proofs',
        estimatedTime: '45 minutes',
        content: {
          introduction: "Whiteboard derivations are common in quant interviews. You'll be asked to derive the OLS estimator, prove unbiasedness, compute variances, and derive test statistics - all from first principles.",
          sections: [
            {
              title: 'Essential Derivations',
              content: `1. Derive β̂ = (XᵀX)⁻¹Xᵀy

Start: minimize ||y - Xβ||²
Expand: (y - Xβ)ᵀ(y - Xβ) = yᵀy - 2βᵀXᵀy + βᵀXᵀXβ
Take derivative: ∂/∂β = -2Xᵀy + 2XᵀXβ
Set to zero: XᵀXβ = Xᵀy
Solve: β̂ = (XᵀX)⁻¹Xᵀy ✓

2. Prove E[β̂] = β (unbiasedness)

β̂ = (XᵀX)⁻¹Xᵀy
   = (XᵀX)⁻¹Xᵀ(Xβ + ε)
   = (XᵀX)⁻¹XᵀXβ + (XᵀX)⁻¹Xᵀε
   = β + (XᵀX)⁻¹Xᵀε

E[β̂] = β + (XᵀX)⁻¹XᵀE[ε]
     = β + 0
     = β ✓

3. Derive Var(β̂) = σ²(XᵀX)⁻¹

Var(β̂) = Var[(XᵀX)⁻¹Xᵀy]
       = (XᵀX)⁻¹Xᵀ Var(y) X(XᵀX)⁻¹
       = (XᵀX)⁻¹Xᵀ (σ²I) X(XᵀX)⁻¹
       = σ²(XᵀX)⁻¹XᵀX(XᵀX)⁻¹
       = σ²(XᵀX)⁻¹ ✓`,
              keyFormula: 'E[\\hat{\\beta}] = \\beta, \\quad Var(\\hat{\\beta}) = \\sigma^2(X^TX)^{-1}'
            },
            {
              title: 'Proof Techniques',
              content: `Matrix differentiation rules (memorize these!):

∂/∂β (βᵀa) = a
∂/∂β (βᵀAβ) = 2Aβ (if A symmetric)
∂/∂β (aᵀβ) = a

Variance rules:
Var(Ay) = A Var(y) Aᵀ
Var(y + c) = Var(y)
E[E[X|Y]] = E[X]

Gauss-Markov Theorem (BLUE):
Under assumptions:
• E[ε] = 0
• Var(ε) = σ²I
• X full rank

Then β̂_OLS has minimum variance among all LINEAR unbiased estimators.

Proof uses Lagrange multipliers and the variance formula.`
            },
            {
              title: 'Common Interview Proofs',
              content: `Q: Prove residuals sum to zero

e = y - Xβ̂ = y - X(XᵀX)⁻¹Xᵀy = (I - H)y
where H = X(XᵀX)⁻¹Xᵀ is the hat matrix

1ᵀe = 1ᵀ(I - H)y
Since 1 is in column space of X (intercept), H1 = 1
Therefore: 1ᵀ(I - H) = 0
Thus: 1ᵀe = 0 → Σeᵢ = 0 ✓

Q: Prove R² = correlation²(y, ŷ) for simple linear regression

Start with definitions, expand, use properties of correlation...
(Full proof takes ~5 minutes on whiteboard)

Q: Derive the F-statistic for nested models

Use RSS decomposition, degrees of freedom...`
            }
          ],
          keyTakeaways: [
            'Master the three core proofs: derivation, unbiasedness, variance',
            'Know matrix differentiation rules cold',
            'Gauss-Markov theorem proves BLUE property',
            'Hat matrix H = X(XᵀX)⁻¹Xᵀ appears everywhere'
          ],
          interviewTips: [
            'Write clearly and explain each step out loud',
            'Start with definitions before diving into algebra',
            'Know when to use E[E[X|Y]] = E[X]',
            'Practice time management: 5-7 minutes per proof'
          ],
          practiceProblems: [
            { id: 1, difficulty: 'Medium', text: 'Prove β̂_OLS is unbiased in 5 minutes on whiteboard' },
            { id: 2, difficulty: 'Hard', text: 'Prove the Gauss-Markov theorem (BLUE property)' }
          ],
          resources: [
            { source: 'Elements of Statistical Learning', chapter: 'Chapter 3', pages: 'pp. 43-55' }
          ]
        }
      },
      '4.3': {
        sectionTitle: 'Mock Interviews',
        estimatedTime: '90 minutes',
        content: {
          introduction: "This section simulates real quant interview scenarios combining theory, coding, and problem-solving under time pressure. Practice these end-to-end to build confidence.",
          sections: [
            {
              title: 'Mock Interview #1: Conceptual + Derivation',
              content: `Part 1: Warm-up (5 min)
Q: Explain linear regression to a non-technical person.
Q: What are the assumptions of OLS and why does each matter?
Q: When would you use Ridge vs Lasso?

Part 2: Derivation (15 min)
Q: Derive the OLS estimator from first principles.
Q: Prove it's unbiased.
Q: What happens to the variance if we add a collinear feature?

Part 3: Practical scenario (10 min)
Q: You fit a regression and R² = 0.95 but predictions are terrible. Why?
Q: Your residual plot shows a cone shape. What's wrong and how do you fix it?
Q: You have n=100 observations and p=200 features. What do you do?

Expected depth: Should handle follow-ups and edge cases.`
            },
            {
              title: 'Mock Interview #2: Coding Challenge',
              content: `Part 1: Implement from scratch (30 min)

"Implement linear regression from scratch using only NumPy.
Your class should support fit() and predict() methods.
Then add an R² method to compute goodness of fit."

Follow-ups:
- How would you handle regularization?
- Modify to use gradient descent instead of closed form
- Add cross-validation for hyperparameter tuning
- Handle missing values in X

Part 2: Debugging (10 min)

"Here's broken code for Ridge regression. Find and fix the bugs."

Common bugs to catch:
- Not centering data before regularization
- Penalizing the intercept
- Wrong gradient calculation
- Off-by-one in matrix dimensions`
            },
            {
              title: 'Mock Interview #3: Case Study',
              content: `Scenario: Predicting stock returns

"You're building a model to predict daily stock returns using 50 technical indicators.
You have 5 years of data (1250 observations)."

Part 1: Setup (10 min)
Q: What are potential issues with this dataset?
→ Look for: autocorrelation, non-stationarity, look-ahead bias

Q: How would you split train/test?
→ Expect: time series split, not random shuffle

Q: What preprocessing is needed?
→ Discuss: standardization, outlier handling, stationarity tests

Part 2: Modeling (15 min)
Q: Would you use OLS, Ridge, Lasso, or something else? Why?
Q: How do you prevent overfitting with p=50, n=1250?
Q: How do you handle autocorrelation in errors?

Part 3: Evaluation (10 min)
Q: You get R²=0.6 on train, R²=-0.1 on test. What happened?
Q: What metrics matter for this problem beyond R²?
Q: How would you deploy this model?`
            }
          ],
          keyTakeaways: [
            'Interviews test theory + coding + practical judgment',
            'Expect 3-5 rounds: warm-up → derivation → coding → case study',
            'Time pressure is intentional - practice under constraints',
            'Communication matters as much as correctness'
          ],
          interviewTips: [
            'Think out loud - show your reasoning process',
            'Ask clarifying questions before diving in',
            'Test your code with simple examples',
            'Know when to trade off speed vs accuracy',
            'Practice with a timer to build time management skills'
          ],
          practiceProblems: [
            { id: 1, difficulty: 'Hard', text: 'Complete Mock Interview #2 in 40 minutes' },
            { id: 2, difficulty: 'Hard', text: 'Record yourself doing Mock Interview #1 and review' }
          ],
          resources: [
            { source: 'Elements of Statistical Learning', chapter: 'Full book', pages: 'Review all concepts' }
          ]
        }
      }
    };

    const content = sectionContent[sectionId] || sectionContent['1.1'];

    // Navigation logic - All sections in order
    const allSections = [
      // Week 1: Foundations
      { id: '1.1', title: 'Linear Regression (OLS)' },
      { id: '1.2', title: 'Maximum Likelihood Estimation' },
      // Week 2: Model Diagnostics
      { id: '2.1', title: 'Residual Analysis' },
      { id: '2.2', title: 'Hypothesis Testing (t-tests, F-tests)' },
      { id: '2.3', title: 'Model Assumptions Validation' },
      // Week 3: Advanced Topics
      { id: '3.1', title: 'Regularization (Ridge, Lasso, Elastic Net)' },
      { id: '3.2', title: 'Bias-Variance Tradeoff' },
      { id: '3.3', title: 'Cross-Validation' },
      // Week 4: Interview Prep
      { id: '4.1', title: 'Coding from Scratch (No Libraries)' },
      { id: '4.2', title: 'Derivations & Proofs' },
      { id: '4.3', title: 'Mock Interviews' }
    ];

    const currentIndex = allSections.findIndex(s => s.id === sectionId);
    const previous = currentIndex > 0 ? allSections[currentIndex - 1] : null;
    const next = currentIndex < allSections.length - 1 ? allSections[currentIndex + 1] : null;

    return {
      ...baseData,
      ...content,
      navigation: {
        previous,
        next,
        allSections: allSections.map(s => ({ ...s, current: s.id === sectionId }))
      }
    };
  };

  const fallbackData = getSectionData();

  // Use real data if available, otherwise fall back to placeholder
  const displayData = contentData ? {
    sectionTitle: contentData.sectionTitle || fallbackData.sectionTitle,
    estimatedTime: contentData.estimatedTime || fallbackData.estimatedTime,
    content: contentData.content || fallbackData.content,
    topicName: topicName,
    weekNumber: parseInt(weekNumber) || 1,
    sectionId: sectionId,
    navigation: fallbackData.navigation
  } : fallbackData;

  // Enhanced content renderer for code blocks, LaTeX math, and formulas
  const renderContent = (text) => {
    const lines = text.split('\n');
    const elements = [];
    let i = 0;
    let blockBuffer = [];
    let inCodeBlock = false;

    while (i < lines.length) {
      const line = lines[i];

      // Detect code block start/end
      if (line.trim().startsWith('```')) {
        if (!inCodeBlock) {
          // Start of code block
          inCodeBlock = true;
          blockBuffer = [];
        } else {
          // End of code block
          inCodeBlock = false;
          elements.push(
            <div key={`code-${i}`} className="code-block">
              <pre><code>{blockBuffer.join('\n')}</code></pre>
            </div>
          );
          blockBuffer = [];
        }
        i++;
        continue;
      }

      if (inCodeBlock) {
        blockBuffer.push(line);
        i++;
        continue;
      }

      // Regular paragraph with inline math support
      if (line.trim()) {
        elements.push(<p key={`p-${i}`}>{renderLineWithMath(line)}</p>);
      }
      i++;
    }

    return elements;
  };

  // Render a line with inline LaTeX math
  const renderLineWithMath = (line) => {
    // Split by inline math delimiters $...$
    const parts = [];
    let currentPos = 0;
    let inMath = false;
    let mathStart = -1;

    for (let i = 0; i < line.length; i++) {
      if (line[i] === '$' && (i === 0 || line[i-1] !== '\\')) {
        if (!inMath) {
          // Start of math
          if (i > currentPos) {
            parts.push({ type: 'text', content: line.substring(currentPos, i) });
          }
          mathStart = i + 1;
          inMath = true;
        } else {
          // End of math
          parts.push({ type: 'math', content: line.substring(mathStart, i) });
          currentPos = i + 1;
          inMath = false;
        }
      }
    }

    // Add remaining text
    if (currentPos < line.length) {
      parts.push({ type: 'text', content: line.substring(currentPos) });
    }

    // Render parts
    return parts.map((part, idx) => {
      if (part.type === 'math') {
        return <InlineMath key={idx} math={part.content} />;
      }
      return <span key={idx}>{part.content}</span>;
    });
  };

  const handleComplete = () => {
    const newCompletedState = !completed;
    setCompleted(newCompletedState);

    // Save to localStorage (placeholder persistence)
    const completionKey = `${topicSlug}-${weekNumber}-${sectionId}-completed`;
    localStorage.setItem(completionKey, newCompletedState.toString());

    if (newCompletedState) {
      alert('✅ Section marked as complete! Progress saved.');
    } else {
      alert('Section marked as incomplete.');
    }
  };

  const handleSaveNotes = (newNotes) => {
    setNotes(newNotes);
    // Save to localStorage
    const notesKey = `${topicSlug}-${weekNumber}-${sectionId}-notes`;
    localStorage.setItem(notesKey, newNotes);
  };

  const handleTryProblem = (problemId, problemText) => {
    alert(`Practice Problem #${problemId}\n\n"${problemText}"\n\nTODO: Open practice interface with:\n- Code editor for implementation\n- Test cases\n- Solution checker\n- Hints system`);
  };

  const handleViewPDF = (source, chapter) => {
    alert(`Opening PDF:\n\n${source}\n${chapter}\n\nTODO: Integrate with PDF viewer showing:\n- Exact page/section\n- Highlighting capability\n- Bookmark functionality`);
  };

  const handleNext = () => {
    if (displayData.navigation.next) {
      navigate(`/topic/${topicSlug}/week/${weekNumber}/section/${displayData.navigation.next.id}`, {
        state: { topicName: displayData.topicName }
      });
    }
  };

  const handlePrevious = () => {
    if (displayData.navigation.previous) {
      navigate(`/topic/${topicSlug}/week/${weekNumber}/section/${displayData.navigation.previous.id}`, {
        state: { topicName: displayData.topicName }
      });
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="section-content-page">
        <header className="section-header">
          <button
            onClick={() => navigate(`/topic/${topicSlug}`, { state: { topicName } })}
            className="back-button"
          >
            ← Back to {topicName}
          </button>
        </header>
        <div className="loading-container" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <div className="spinner" style={{ fontSize: '48px', marginBottom: '20px' }}>⏳</div>
          <h2>Generating High-Quality Content...</h2>
          <p style={{ color: '#666', marginTop: '10px' }}>
            {contentData?.cached ? 'Loading cached content...' : 'Using Claude Sonnet 3.5 to create comprehensive learning material...'}
          </p>
          <p style={{ color: '#888', fontSize: '14px', marginTop: '20px' }}>
            First-time generation may take 10-30 seconds
          </p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="section-content-page">
        <header className="section-header">
          <button
            onClick={() => navigate(`/topic/${topicSlug}`, { state: { topicName } })}
            className="back-button"
          >
            ← Back to {topicName}
          </button>
        </header>
        <div className="error-container" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>⚠️</div>
          <h2>Error Loading Content</h2>
          <p style={{ color: '#d32f2f', marginTop: '10px' }}>{error}</p>
          <button
            onClick={() => window.location.reload()}
            style={{
              marginTop: '20px',
              padding: '10px 20px',
              backgroundColor: '#1976d2',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="section-content-page">
      {/* Cache indicator */}
      {contentData?.cached && (
        <div style={{
          position: 'fixed',
          top: '10px',
          right: '10px',
          backgroundColor: '#4caf50',
          color: 'white',
          padding: '8px 16px',
          borderRadius: '4px',
          fontSize: '12px',
          zIndex: 1000,
          boxShadow: '0 2px 8px rgba(0,0,0,0.2)'
        }}>
          ⚡ Cached • {contentData.generation_model}
        </div>
      )}

      {/* Header with Navigation */}
      <header className="section-header">
        <button
          onClick={() => navigate(`/topic/${topicSlug}`, { state: { topicName: displayData.topicName } })}
          className="back-button"
        >
          ← Back to {displayData.topicName}
        </button>

        <div className="section-meta">
          <span className="week-indicator">Week {displayData.weekNumber}</span>
          <span className="section-indicator">Section {displayData.sectionId}</span>
          <span className="time-estimate">⏱️ {displayData.estimatedTime}</span>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="section-progress-bar">
        <div className="progress-track">
          {displayData.navigation.allSections.map((section, index) => (
            <div
              key={section.id}
              className={`progress-node ${section.current ? 'current' : ''} ${index < displayData.navigation.allSections.findIndex(s => s.current) ? 'completed' : ''}`}
              title={section.title}
            >
              {section.id}
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <main className="section-main">
        <div className="content-column">
          <h1>{displayData.sectionTitle}</h1>

          {/* Introduction */}
          <div className="intro-box">
            <p>{displayData.content.introduction}</p>
          </div>

          {/* Content Sections */}
          {displayData.content.sections.map((section, index) => (
            <section key={index} className="content-section">
              <h2>{section.title}</h2>
              <div className="content-text">
                {renderContent(section.content)}
              </div>
              {section.keyFormula && (
                <div className="formula-highlight">
                  <div className="formula-label">KEY FORMULA</div>
                  <div className="formula-text">
                    <BlockMath math={section.keyFormula} />
                  </div>
                </div>
              )}
            </section>
          ))}

          {/* Key Takeaways */}
          <div className="takeaways-box">
            <h3>🎯 Key Takeaways</h3>
            <ul>
              {displayData.content.keyTakeaways.map((takeaway, i) => (
                <li key={i}>{renderLineWithMath(takeaway)}</li>
              ))}
            </ul>
          </div>

          {/* Interview Tips */}
          <div className="interview-tips-box">
            <h3>💼 Interview Tips</h3>
            <ul>
              {displayData.content.interviewTips.map((tip, i) => (
                <li key={i}>{tip}</li>
              ))}
            </ul>
          </div>

          {/* Practice Problems */}
          <div className="practice-box">
            <h3>📝 Practice Problems</h3>
            {displayData.content.practiceProblems.map((problem) => (
              <div key={problem.id} className="practice-item">
                <span className={`difficulty-badge ${problem.difficulty.toLowerCase()}`}>
                  {problem.difficulty}
                </span>
                <span className="problem-text">{problem.text}</span>
                <button
                  className="btn-try"
                  onClick={() => handleTryProblem(problem.id, problem.text)}
                >
                  Try It
                </button>
              </div>
            ))}
          </div>

          {/* Resources */}
          <div className="resources-box">
            <h3>📚 Reading Material</h3>
            {displayData.content.resources.map((resource, i) => (
              <div key={i} className="resource-item">
                <div className="resource-source">{resource.source}</div>
                <div className="resource-details">{resource.chapter} • {resource.pages}</div>
                <button
                  className="btn-view"
                  onClick={() => handleViewPDF(resource.source, resource.chapter)}
                >
                  View PDF
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Sidebar */}
        <aside className="content-sidebar">
          {/* Completion Status */}
          <div className="completion-card">
            <h4>Section Progress</h4>
            {completed ? (
              <>
                <div className="completed-status">
                  <span className="check-icon">✅</span>
                  <span>Completed!</span>
                </div>
                <button onClick={handleComplete} className="btn-uncomplete">
                  Mark as Incomplete
                </button>
              </>
            ) : (
              <button onClick={handleComplete} className="btn-complete">
                ✓ Mark as Complete
              </button>
            )}
          </div>

          {/* Quick Notes */}
          <div className="notes-card">
            <div className="notes-header">
              <h4>Your Notes</h4>
              <button onClick={() => setShowNotes(!showNotes)} className="btn-toggle-notes">
                {showNotes ? '−' : '+'}
              </button>
            </div>
            {showNotes && (
              <textarea
                className="notes-textarea"
                placeholder="Write your notes here..."
                value={notes}
                onChange={(e) => handleSaveNotes(e.target.value)}
                rows={10}
              />
            )}
          </div>

          {/* Navigation */}
          <div className="nav-card">
            <h4>Navigation</h4>
            {displayData.navigation.previous && (
              <button onClick={handlePrevious} className="nav-btn prev">
                ← Previous: {displayData.navigation.previous.title}
              </button>
            )}
            {displayData.navigation.next && (
              <button onClick={handleNext} className="nav-btn next">
                Next: {displayData.navigation.next.title} →
              </button>
            )}
          </div>

          {/* Study Tips */}
          <div className="tips-card">
            <h4>💡 Study Tips</h4>
            <ul>
              <li>Work through derivations by hand</li>
              <li>Code the algorithm yourself</li>
              <li>Explain concepts out loud</li>
              <li>Practice on whiteboard</li>
            </ul>
          </div>
        </aside>
      </main>
    </div>
  );
};

export default SectionContentPage;
