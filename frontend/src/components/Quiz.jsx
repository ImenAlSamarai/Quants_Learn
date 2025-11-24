import { useState } from 'react';
import { CheckCircle, XCircle, ArrowRight } from 'lucide-react';
import { updateProgress } from '../services/api';

const Quiz = ({ questions, nodeId, userId }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [score, setScore] = useState(0);
  const [completed, setCompleted] = useState(false);
  const [answers, setAnswers] = useState([]);

  const question = questions[currentQuestion];

  const handleAnswerSelect = (answer) => {
    if (showExplanation) return; // Already answered

    setSelectedAnswer(answer);
    setShowExplanation(true);

    const isCorrect = answer === question.correct_answer;
    if (isCorrect) {
      setScore(score + 1);
    }

    setAnswers([...answers, { question: question.question, answer, isCorrect }]);
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedAnswer(null);
      setShowExplanation(false);
    } else {
      // Quiz completed
      setCompleted(true);
      const finalScore = ((score + (selectedAnswer === question.correct_answer ? 1 : 0)) / questions.length) * 100;

      // Update user progress
      updateProgress(userId, nodeId, 100, finalScore, 10).catch(console.error);
    }
  };

  if (!questions || questions.length === 0) {
    return (
      <div className="quiz-container">
        <p>No quiz questions available.</p>
      </div>
    );
  }

  if (completed) {
    const finalScore = (score / questions.length) * 100;
    return (
      <div className="quiz-results">
        <div className="results-header">
          <CheckCircle size={48} color="#10b981" />
          <h2>Quiz Completed!</h2>
        </div>
        <div className="score-display">
          <div className="score-circle">
            <span className="score-value">{finalScore.toFixed(0)}%</span>
            <span className="score-label">{score} / {questions.length}</span>
          </div>
        </div>
        <div className="results-summary">
          {answers.map((ans, idx) => (
            <div key={idx} className={`answer-review ${ans.isCorrect ? 'correct' : 'incorrect'}`}>
              {ans.isCorrect ? <CheckCircle size={20} /> : <XCircle size={20} />}
              <span>{ans.question}</span>
            </div>
          ))}
        </div>
        <button
          className="retry-button"
          onClick={() => {
            setCurrentQuestion(0);
            setScore(0);
            setCompleted(false);
            setAnswers([]);
            setSelectedAnswer(null);
            setShowExplanation(false);
          }}
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="quiz-container">
      <div className="quiz-progress">
        <span>Question {currentQuestion + 1} of {questions.length}</span>
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
          />
        </div>
      </div>

      <div className="question-container">
        <h3 className="question-text">{question.question}</h3>

        {question.type === 'multiple_choice' && question.options ? (
          <div className="options-container">
            {question.options.map((option, idx) => (
              <button
                key={idx}
                className={`option-button ${
                  selectedAnswer === option ? 'selected' : ''
                } ${
                  showExplanation && option === question.correct_answer ? 'correct' : ''
                } ${
                  showExplanation && selectedAnswer === option && option !== question.correct_answer ? 'incorrect' : ''
                }`}
                onClick={() => handleAnswerSelect(option)}
                disabled={showExplanation}
              >
                <span className="option-label">{String.fromCharCode(65 + idx)}</span>
                <span className="option-text">{option}</span>
                {showExplanation && option === question.correct_answer && (
                  <CheckCircle size={20} />
                )}
                {showExplanation && selectedAnswer === option && option !== question.correct_answer && (
                  <XCircle size={20} />
                )}
              </button>
            ))}
          </div>
        ) : (
          <div className="conceptual-answer">
            <textarea
              className="answer-textarea"
              placeholder="Type your answer here..."
              rows={6}
              value={selectedAnswer || ''}
              onChange={(e) => setSelectedAnswer(e.target.value)}
            />
            {!showExplanation && (
              <button
                className="submit-button"
                onClick={() => handleAnswerSelect(selectedAnswer)}
                disabled={!selectedAnswer}
              >
                Submit Answer
              </button>
            )}
          </div>
        )}

        {showExplanation && (
          <div className="explanation-box">
            <h4>✨ Explanation</h4>
            <p>{question.explanation}</p>
            {question.type === 'conceptual' && (
              <div className="model-answer">
                <strong>Model Answer:</strong>
                <p>{question.correct_answer}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {showExplanation && (
        <button className="next-button" onClick={handleNext}>
          {currentQuestion < questions.length - 1 ? (
            <>
              Next Question <ArrowRight size={20} />
            </>
          ) : (
            'See Results'
          )}
        </button>
      )}
    </div>
  );
};

export default Quiz;
